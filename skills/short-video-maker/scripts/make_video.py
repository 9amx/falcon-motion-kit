"""Build a vertical short video from a script and a folder of local clips.

Pipeline:
    1. Generate narration with gTTS
    2. Normalize the narration loudness
    3. Mix in one music track with light ducking
    4. Cut local clips into fixed-length shots and crop to 9:16
    5. Burn in captions built from the script
    6. Export the final mp4
"""

import argparse
import sys
from pathlib import Path

from gtts import gTTS
from pydub import AudioSegment
from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    TextClip,
    VideoFileClip,
    concatenate_videoclips,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from captions import build_captions, split_into_chunks  # noqa: E402

WIDTH, HEIGHT = 1080, 1920
FPS = 24
VIDEO_BITRATE = "2500k"
SHOT_LENGTH = 5.0          # seconds per shot (4-6 s works best)
TARGET_LOUDNESS = -8.0     # approximate LUFS target for the voice
MUSIC_DUCK_DB = -3.0       # music reduction while the voice plays
CAPTION_MARGIN = 40        # pixels from the bottom edge
VIDEO_EXTS = {".mp4", ".mov"}


def generate_voice(script_text, out_path, lang="en"):
    """Create the narration mp3 with gTTS."""
    tts = gTTS(text=script_text, lang=lang, slow=False)
    tts.save(str(out_path))
    return out_path


def normalize_voice(in_path, out_path, target=TARGET_LOUDNESS):
    """Normalize the voice so its average level sits near the target."""
    voice = AudioSegment.from_file(in_path)
    gain = target - voice.dBFS
    voice = voice.apply_gain(gain)
    voice.export(out_path, format="mp3")
    return out_path


def mix_music(voice_path, music_path, out_path, duck_db=MUSIC_DUCK_DB):
    """Lay one music track at full volume under the voice with light ducking."""
    voice = AudioSegment.from_file(voice_path)
    if not music_path:
        voice.export(out_path, format="mp3")
        return out_path

    music = AudioSegment.from_file(music_path)
    # Loop the music so it covers the whole narration.
    while len(music) < len(voice):
        music += music
    music = music[:len(voice)]

    ducked = music.apply_gain(duck_db)
    mixed = ducked.overlay(voice)
    mixed.export(out_path, format="mp3")
    return out_path


def list_clips(clips_dir):
    """Return local clip paths in alphabetical order."""
    clips = sorted(p for p in Path(clips_dir).iterdir() if p.suffix.lower() in VIDEO_EXTS)
    if not clips:
        raise SystemExit(f"No video clips found in {clips_dir}")
    return clips


def crop_vertical(clip):
    """Resize and center-crop a clip to 1080x1920."""
    scale = max(WIDTH / clip.w, HEIGHT / clip.h)
    clip = clip.resize(scale)
    x_center, y_center = clip.w / 2, clip.h / 2
    return clip.crop(x_center=x_center, y_center=y_center, width=WIDTH, height=HEIGHT)


def build_shots(clips_dir, total_duration, shot_length=SHOT_LENGTH):
    """Cut fixed-length shots from local clips until the duration is filled."""
    paths = list_clips(clips_dir)
    shots = []
    elapsed = 0.0
    index = 0
    while elapsed < total_duration:
        source = VideoFileClip(str(paths[index % len(paths)])).without_audio()
        length = min(shot_length, source.duration, total_duration - elapsed)
        shots.append(crop_vertical(source.subclip(0, length)))
        elapsed += length
        index += 1
    return concatenate_videoclips(shots, method="compose")


def caption_clips(script_text):
    """Create TextClips for each caption, placed near the bottom edge."""
    clips = []
    for start, end, text in build_captions(split_into_chunks(script_text)):
        txt = TextClip(text, fontsize=48, color="white", method="caption", size=(WIDTH - 120, None))
        y = HEIGHT - txt.h - CAPTION_MARGIN
        clips.append(txt.set_start(start).set_end(end).set_position(("center", y)))
    return clips


def render(args):
    """Run the full pipeline and write the output video."""
    work = Path(args.workdir)
    work.mkdir(parents=True, exist_ok=True)
    script_text = Path(args.script).read_text(encoding="utf-8")

    raw_voice = generate_voice(script_text, work / "voice_raw.mp3", lang=args.lang)
    voice = normalize_voice(raw_voice, work / "voice.mp3")
    if args.tts_only:
        print(f"Voiceover written to {voice}")
        return

    mix = mix_music(voice, args.music, work / "mix.mp3")
    audio = AudioFileClip(str(mix))

    video = build_shots(args.clips, audio.duration)
    layers = [video] + caption_clips(script_text)
    final = CompositeVideoClip(layers, size=(WIDTH, HEIGHT)).set_audio(audio)
    final = final.set_duration(audio.duration)

    final.write_videofile(
        args.out,
        fps=FPS,
        codec="libx264",
        bitrate=VIDEO_BITRATE,
        audio_codec="aac",
        audio_bitrate="128k",
    )
    print(f"Done: {args.out}")


def parse_args():
    parser = argparse.ArgumentParser(description="Make a vertical short video.")
    parser.add_argument("--script", required=True, help="path to script.txt")
    parser.add_argument("--clips", default="./clips", help="folder of local clips")
    parser.add_argument("--music", default=None, help="optional music track")
    parser.add_argument("--out", default="short.mp4", help="output video path")
    parser.add_argument("--workdir", default="./build", help="folder for temp files")
    parser.add_argument("--lang", default="en", help="TTS language code")
    parser.add_argument("--tts-only", action="store_true", help="only generate the voiceover")
    return parser.parse_args()


if __name__ == "__main__":
    render(parse_args())
