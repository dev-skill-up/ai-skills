#!/usr/bin/env python3
"""Mux a still image + narration WAV into a calm, portable MP4.

Key choices baked in (see references/kokoro-and-ffmpeg.md for the why):
  * Low frame rate (default 10 fps). The image never moves, so a high fps just
    multiplies encode time for no benefit. Even a 5-minute video encodes in a
    few seconds this way.
  * -preset ultrafast -tune stillimage: fast encode tuned for a single frame.
  * yuv420p + even dimensions: required for the video to play in browsers,
    QuickTime, phones, etc.
  * Gentle fades: a slow visual fade-in/out, and an audio fade-out placed in the
    trailing silence so it never clips a spoken word.
  * +faststart: moves the moov atom to the front for instant web playback.

Usage:
    python3 render_video.py IMAGE AUDIO.wav [--out meditation.mp4] [--fps 10]
        [--fade-in 2] [--video-fade-out 2] [--audio-fade-out 0.6]
        [--audio-bitrate 192k]
"""
import argparse
import os
import subprocess

import soundfile as sf


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("image")
    ap.add_argument("audio")
    ap.add_argument("--out", default="meditation.mp4")
    ap.add_argument("--fps", type=int, default=10)
    ap.add_argument("--fade-in", type=float, default=2.0)
    ap.add_argument("--video-fade-out", type=float, default=2.0)
    ap.add_argument("--audio-fade-out", type=float, default=0.6,
                    help="kept short and inside the trailing silence to avoid clipping speech")
    ap.add_argument("--audio-bitrate", default="192k",
                    help="AAC bitrate; on a static image the audio is nearly the whole "
                         "file, so use 96k for 15+ minute essays to stay under the "
                         "30 MiB delivery limit")
    args = ap.parse_args()

    info = sf.info(args.audio)
    dur = info.frames / info.samplerate
    vfo = max(0.0, dur - args.video_fade_out)
    afo = max(0.0, dur - args.audio_fade_out)

    vf = (
        "scale=trunc(iw/2)*2:trunc(ih/2)*2,"
        f"fade=t=in:st=0:d={args.fade_in},"
        f"fade=t=out:st={vfo:.2f}:d={args.video_fade_out}"
    )
    af = f"afade=t=out:st={afo:.2f}:d={args.audio_fade_out}"

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", str(args.fps), "-i", args.image,
        "-i", args.audio,
        "-c:v", "libx264", "-preset", "ultrafast", "-tune", "stillimage",
        "-pix_fmt", "yuv420p", "-r", str(args.fps),
        "-vf", vf, "-af", af,
        "-c:a", "aac", "-b:a", args.audio_bitrate,
        "-movflags", "+faststart", "-shortest", args.out,
    ]
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)
    size = os.path.getsize(args.out) / 2**20
    print(f"wrote {args.out} ({dur:.1f}s = {int(dur // 60)}:{int(dur % 60):02d}, "
          f"{size:.1f} MiB)"
          + ("" if size <= 30 else
             " — over the 30 MiB delivery limit; re-render with a lower "
             "--audio-bitrate or compress before sending (SKILL.md step 6)"))


if __name__ == "__main__":
    main()
