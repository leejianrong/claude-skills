#!/usr/bin/env python3
"""Mux a silent captured video with bundled music, cued SFX, and optional captions.

Run directly, do not import. See ../references/audio-mixing.md for the cue sheet
and caption JSON schemas, and for worked example invocations.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
MUSIC_DIR = SKILL_DIR / "assets" / "music"
SFX_DIR = SKILL_DIR / "assets" / "sfx"

AUDIO_KBPS = 160
CONTAINER_OVERHEAD = 0.92  # fraction of the size budget left after container/mux overhead
MIN_VIDEO_KBPS = 150
MAX_ENCODE_ATTEMPTS = 3
FADE_OUT_SECONDS = 1.5

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
]


def fail(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def require_tool(name: str) -> None:
    if shutil.which(name) is None:
        fail(f"'{name}' not found on PATH")


def ffprobe_json(path: Path, entries: str) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-of", "json", "-show_entries", entries, str(path)],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        fail(f"ffprobe failed on {path}:\n{out.stderr}")
    return json.loads(out.stdout)


def video_duration(path: Path) -> float:
    data = ffprobe_json(path, "format=duration")
    return float(data["format"]["duration"])


def resolve_music(mood: str) -> Path:
    path = MUSIC_DIR / f"{mood}.mp3"
    if not path.exists():
        available = sorted(p.stem for p in MUSIC_DIR.glob("*.mp3"))
        fail(f"unknown music mood '{mood}'. Available: {', '.join(available)}")
    return path


def resolve_sfx(name: str) -> Path:
    path = SFX_DIR / f"{name}.mp3"
    if not path.exists():
        available = sorted(p.stem for p in SFX_DIR.glob("*.mp3"))
        fail(f"unknown sfx '{name}'. Available: {', '.join(available)}")
    return path


def load_cues(path: str | None, duration: float) -> list[dict]:
    if not path:
        return []
    cues = json.loads(Path(path).read_text())
    for cue in cues:
        if "sfx" not in cue or "t" not in cue:
            fail(f"cue entry missing 'sfx' or 't': {cue}")
        resolve_sfx(cue["sfx"])
        if not (0 <= cue["t"] <= duration):
            fail(f"cue t={cue['t']} is outside video duration 0-{duration:.2f}s")
    return cues


def load_captions(path: str | None, duration: float) -> list[dict]:
    if not path:
        return []
    caps = json.loads(Path(path).read_text())
    for cap in caps:
        for key in ("text", "start", "end"):
            if key not in cap:
                fail(f"caption entry missing '{key}': {cap}")
        if not (0 <= cap["start"] < cap["end"] <= duration):
            fail(f"caption timing invalid against duration {duration:.2f}s: {cap}")
    return caps


def escape_drawtext(text: str) -> str:
    for ch in ("\\", ":", "'", "%"):
        text = text.replace(ch, "\\" + ch)
    return text


def find_font_file(explicit: str | None) -> str | None:
    if explicit:
        return explicit
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return candidate
    return None


def build_video_filter(width: int, captions: list[dict], font_file: str | None) -> str:
    chain = [f"scale={width}:-2"]
    for cap in captions:
        text = escape_drawtext(cap["text"])
        font_part = f"fontfile='{font_file}':" if font_file else "font='DejaVu Sans':"
        chain.append(
            "drawtext="
            f"{font_part}text='{text}':fontsize=42:fontcolor=white:"
            "borderw=3:bordercolor=black@0.7:"
            "x=(w-text_w)/2:y=h-th-60:"
            f"enable='between(t,{cap['start']},{cap['end']})'"
        )
    return ",".join(chain)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--video", required=True, help="path to the silent captured video")
    parser.add_argument("--music", required=True, help="mood name matching assets/music/<mood>.mp3")
    parser.add_argument("--cues", help="path to a JSON cue sheet (see references/audio-mixing.md)")
    parser.add_argument("--captions", help="path to a JSON captions list (see references/audio-mixing.md)")
    parser.add_argument("--out", required=True, help="output mp4 path")
    parser.add_argument("--width", type=int, default=1280, help="output width in pixels (default 1280)")
    parser.add_argument("--max-size-mb", type=float, default=8.0, help="target size ceiling (default 8.0, well under GitHub's 10MB free-tier cap)")
    parser.add_argument("--music-volume", type=float, default=0.5, help="relative gain applied to the music bed (default 0.5)")
    parser.add_argument("--font-file", help="explicit font file for captions; auto-detected if omitted")
    args = parser.parse_args()

    require_tool("ffmpeg")
    require_tool("ffprobe")

    video_path = Path(args.video)
    if not video_path.exists():
        fail(f"video not found: {video_path}")

    duration = video_duration(video_path)
    if duration <= 0:
        fail(f"could not read a valid duration from {video_path}")

    music_path = resolve_music(args.music)
    cues = load_cues(args.cues, duration)
    captions = load_captions(args.captions, duration)
    font_file = find_font_file(args.font_file)
    if captions and font_file is None:
        print("warning: no bundled font found and none passed via --font-file; "
              "relying on ffmpeg's fontconfig default, which may fail on some machines", file=sys.stderr)

    # Build ffmpeg inputs: 0=video, 1=music, 2..N=one input per cue (duplicates allowed)
    inputs = ["-i", str(video_path), "-i", str(music_path)]
    for cue in cues:
        inputs += ["-i", str(resolve_sfx(cue["sfx"]))]

    video_filter = build_video_filter(args.width, captions, font_file)
    video_graph = f"[0:v]{video_filter}[vout]"

    fade_start = max(0.0, duration - FADE_OUT_SECONDS)
    audio_parts = [
        f"[1:a]atrim=0:{duration:.3f},asetpts=PTS-STARTPTS,"
        f"afade=t=out:st={fade_start:.3f}:d={FADE_OUT_SECONDS},volume={args.music_volume}[bed]"
    ]
    mix_labels = ["[bed]"]
    for i, cue in enumerate(cues):
        idx = i + 2  # ffmpeg input index for this cue's sfx file
        ms = int(round(cue["t"] * 1000))
        label = f"sfx{i}"
        audio_parts.append(f"[{idx}:a]adelay={ms}|{ms},asetpts=PTS-STARTPTS[{label}]")
        mix_labels.append(f"[{label}]")
    audio_parts.append(
        "".join(mix_labels)
        + f"amix=inputs={len(mix_labels)}:duration=first:dropout_transition=0:normalize=0,"
        + "loudnorm=I=-16:TP=-1.5:LRA=11[aout]"
    )
    audio_graph = ";".join(audio_parts)

    filter_complex = video_graph + ";" + audio_graph

    total_kbits = args.max_size_mb * 8192 * CONTAINER_OVERHEAD
    video_kbps = max(MIN_VIDEO_KBPS, int(total_kbits / duration - AUDIO_KBPS))
    if total_kbits / duration - AUDIO_KBPS < MIN_VIDEO_KBPS:
        print(f"warning: {args.max_size_mb}MB budget over {duration:.1f}s only leaves "
              f"~{video_kbps}kbps video bitrate; consider a shorter clip or a larger budget", file=sys.stderr)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(1, MAX_ENCODE_ATTEMPTS + 1):
        cmd = [
            "ffmpeg", "-y", "-v", "error",
            *inputs,
            "-filter_complex", filter_complex,
            "-map", "[vout]", "-map", "[aout]",
            "-t", f"{duration:.3f}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "medium",
            "-b:v", f"{video_kbps}k", "-maxrate", f"{int(video_kbps * 1.5)}k", "-bufsize", f"{video_kbps * 2}k",
            "-c:a", "aac", "-b:a", f"{AUDIO_KBPS}k",
            "-movflags", "+faststart",
            str(out_path),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            fail(f"ffmpeg encode failed (attempt {attempt}):\n{result.stderr}")

        size_mb = out_path.stat().st_size / (1024 * 1024)
        if size_mb <= args.max_size_mb or attempt == MAX_ENCODE_ATTEMPTS:
            probe = ffprobe_json(out_path, "format=duration,size:stream=width,height")
            actual_duration = float(probe["format"]["duration"])
            width = height = None
            for stream in probe.get("streams", []):
                if "width" in stream:
                    width, height = stream["width"], stream["height"]
                    break
            print(f"wrote {out_path} — {actual_duration:.1f}s, {width}x{height}, {size_mb:.2f}MB "
                  f"(budget {args.max_size_mb}MB)")
            if size_mb > args.max_size_mb:
                print(f"warning: final size {size_mb:.2f}MB exceeds the {args.max_size_mb}MB budget "
                      f"after {attempt} attempts — lower --max-size-mb expectations or shorten the clip", file=sys.stderr)
            return
        video_kbps = max(MIN_VIDEO_KBPS, int(video_kbps * 0.8))
        print(f"size {size_mb:.2f}MB over budget, re-encoding at {video_kbps}kbps (attempt {attempt + 1})", file=sys.stderr)


if __name__ == "__main__":
    main()
