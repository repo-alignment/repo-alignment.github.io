from __future__ import annotations

import re
from pathlib import Path

import imageio.v2 as iio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "preference_cases.json"
MEDIA_JSON_PATH = ROOT / "data" / "preference_media.json"
OUT_DIR = ROOT / "assets" / "cases"

W = 1280
H = 720
FPS = 12


def _load_json(path: Path):
    import json

    return json.loads(path.read_text(encoding="utf-8"))


def _dump_json(path: Path, obj) -> None:
    import json

    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for item in candidates:
        p = Path(item)
        if p.exists():
            return ImageFont.truetype(str(p), size=size)
    return ImageFont.load_default()


def _trim(text: str, n: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= n:
        return text
    return text[: n - 3].rstrip() + "..."


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join(current + [word])
        if draw.textlength(trial, font=font) <= max_w:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def _draw_wrapped(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    text: str,
    font: ImageFont.ImageFont,
    max_w: int,
    max_lines: int,
    fill: str = "#1f2937",
) -> int:
    lines = _wrap(draw, text, font, max_w)[:max_lines]
    bbox = draw.textbbox((0, 0), "Ag", font=font)
    line_h = int((bbox[3] - bbox[1]) * 1.35)
    for idx, line in enumerate(lines):
        draw.text((x, y + idx * line_h), line, font=font, fill=fill)
    return y + len(lines) * line_h


def _extract_keywords(left: str, right: str) -> tuple[list[str], list[str]]:
    stop = {
        "the",
        "and",
        "with",
        "that",
        "this",
        "from",
        "into",
        "for",
        "under",
        "where",
        "which",
        "then",
        "have",
        "has",
        "been",
        "were",
        "they",
        "their",
        "about",
        "response",
        "dataset",
        "chosen",
        "rejected",
    }

    def toks(s: str) -> list[str]:
        return [w.lower() for w in re.findall(r"[A-Za-z']+", s)]

    left_tokens = toks(left)
    right_tokens = toks(right)
    left_set = set(left_tokens)
    right_set = set(right_tokens)

    left_unique = [w for w in left_tokens if w not in right_set and len(w) >= 5 and w not in stop]
    right_unique = [w for w in right_tokens if w not in left_set and len(w) >= 5 and w not in stop]

    def uniq(values: list[str]) -> list[str]:
        out: list[str] = []
        seen = set()
        for item in values:
            if item in seen:
                continue
            out.append(item)
            seen.add(item)
            if len(out) >= 3:
                break
        return out

    return uniq(left_unique), uniq(right_unique)


def _draw_keyword_chips(draw: ImageDraw.ImageDraw, x: int, y: int, words: list[str], bg: str, fg: str) -> None:
    chip_font = _font(20)
    dx = x
    for word in words:
        text = word[:16]
        tw = int(draw.textlength(text, font=chip_font))
        pad = 8
        box = (dx, y, dx + tw + pad * 2, y + 30)
        draw.rounded_rectangle(box, radius=10, fill=bg)
        draw.text((dx + pad, y + 6), text, font=chip_font, fill=fg)
        dx += tw + pad * 2 + 8


def _scene_prompt(case: dict) -> Image.Image:
    img = Image.new("RGB", (W, H), "#f6f8fb")
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, W, 110), fill="#0e3a62")
    draw.text((36, 26), "Preference Duel", font=_font(46), fill="#ffffff")
    draw.text((36, 78), case["case_id"], font=_font(24), fill="#c7def5")

    draw.rounded_rectangle((34, 148, W - 34, H - 58), radius=18, fill="#ffffff", outline="#c8d3e0", width=2)
    draw.text((64, 178), "Prompt", font=_font(30), fill="#11395f")
    _draw_wrapped(
        draw,
        64,
        226,
        _trim(case["prompt"], 460),
        _font(28),
        W - 128,
        max_lines=9,
        fill="#223242",
    )
    draw.text((64, H - 98), "Phase A evidence: camera-ready appendix", font=_font(22), fill="#6c4329")
    return img


def _scene_compare(case: dict) -> Image.Image:
    img = Image.new("RGB", (W, H), "#f9fafc")
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, W, 90), fill="#f0f5fb")
    draw.text((28, 26), "Response Comparison", font=_font(36), fill="#153a5e")

    left_box = (30, 120, W // 2 - 15, H - 95)
    right_box = (W // 2 + 15, 120, W - 30, H - 95)

    draw.rounded_rectangle(left_box, radius=14, fill="#fff2f2", outline="#e7b7b7", width=2)
    draw.rounded_rectangle(right_box, radius=14, fill="#f1fbf3", outline="#b5d9bd", width=2)

    draw.text((left_box[0] + 16, left_box[1] + 14), case["left_label"], font=_font(26), fill="#8b2f2f")
    draw.text((right_box[0] + 16, right_box[1] + 14), case["right_label"], font=_font(26), fill="#1f7a4b")

    left_kw, right_kw = _extract_keywords(case["left_text"], case["right_text"])
    _draw_keyword_chips(draw, left_box[0] + 16, left_box[1] + 56, left_kw or ["verbose", "off-task"], "#ffe0e0", "#7e1c1c")
    _draw_keyword_chips(draw, right_box[0] + 16, right_box[1] + 56, right_kw or ["concise", "task-fit"], "#dff4e5", "#195938")

    _draw_wrapped(
        draw,
        left_box[0] + 16,
        left_box[1] + 104,
        _trim(case["left_text"], 420),
        _font(23),
        left_box[2] - left_box[0] - 32,
        max_lines=11,
        fill="#3b4550",
    )
    _draw_wrapped(
        draw,
        right_box[0] + 16,
        right_box[1] + 104,
        _trim(case["right_text"], 420),
        _font(23),
        right_box[2] - right_box[0] - 32,
        max_lines=11,
        fill="#2f3f4f",
    )

    draw.text((36, H - 66), "Keyword color cues indicate likely preference-quality differences.", font=_font(20), fill="#5b6775")
    return img


def _scene_verdict(case: dict) -> Image.Image:
    img = Image.new("RGB", (W, H), "#f4f9f7")
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, W, 120), fill="#dff0e7")
    draw.text((36, 32), "Case Verdict", font=_font(44), fill="#134f34")

    winner = case["right_label"] if case["winner"] == "right" else case["left_label"] if case["winner"] == "left" else "Tie"
    draw.text((72, 176), f"Winner: {winner}", font=_font(42), fill="#133b24")

    draw.rounded_rectangle((66, 252, W - 66, 520), radius=16, fill="#ffffff", outline="#bfd5c7", width=2)
    draw.text((92, 286), "Why", font=_font(30), fill="#14412a")
    _draw_wrapped(draw, 92, 332, _trim(case["reason_short"], 220), _font(28), W - 184, max_lines=3, fill="#253745")

    draw.text((92, 418), "Confidence signal", font=_font(28), fill="#14412a")
    draw.text((92, 458), case["confidence_signal"], font=_font(26), fill="#1f7a4b")

    draw.text((72, H - 72), "Source: camera-ready appendix qualitative study", font=_font(22), fill="#4f5d6d")
    return img


def _to_array(img: Image.Image) -> np.ndarray:
    return np.asarray(img.convert("RGB"))


def _render_frames(case: dict) -> list[np.ndarray]:
    scene1 = _scene_prompt(case)
    scene2 = _scene_compare(case)
    scene3 = _scene_verdict(case)

    frames: list[np.ndarray] = []
    frames += [_to_array(scene1)] * 10
    frames += [_to_array(scene2)] * 12
    frames += [_to_array(scene3)] * 10
    return frames


def _write_triplet(stem: str, frames: list[np.ndarray]) -> tuple[Path, Path, Path, Path, int]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    mp4 = OUT_DIR / f"{stem}.mp4"
    webm = OUT_DIR / f"{stem}.webm"
    gif = OUT_DIR / f"{stem}.gif"
    poster = OUT_DIR / f"{stem}.png"

    with iio.get_writer(
        mp4,
        format="FFMPEG",
        fps=FPS,
        codec="libx264",
        ffmpeg_log_level="error",
        output_params=["-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p"],
    ) as w:
        for frame in frames:
            w.append_data(frame)

    webm_done = False
    for codec in ("libvpx-vp9", "libvpx"):
        try:
            with iio.get_writer(
                webm,
                format="FFMPEG",
                fps=FPS,
                codec=codec,
                ffmpeg_log_level="error",
                output_params=["-crf", "28", "-b:v", "0"],
            ) as w:
                for frame in frames:
                    w.append_data(frame)
            webm_done = True
            break
        except Exception:
            continue

    if not webm_done:
        raise RuntimeError(f"Failed to create webm for {stem}")

    iio.mimsave(gif, frames, format="GIF", duration=1 / FPS, loop=0)
    Image.fromarray(frames[10]).save(poster)

    duration_ms = int(len(frames) / FPS * 1000)
    return gif, mp4, webm, poster, duration_ms


def main() -> None:
    cases = _load_json(DATA_PATH)
    if not isinstance(cases, list) or not cases:
        raise RuntimeError("preference_cases.json must be a non-empty list")

    media_json: dict[str, dict] = {}
    for case in cases:
        case_id = case["case_id"]
        frames = _render_frames(case)
        gif, mp4, webm, poster, duration_ms = _write_triplet(case_id, frames)

        media_json[case_id] = {
            "gif": str(gif.relative_to(ROOT)).replace("\\\\", "/"),
            "mp4": str(mp4.relative_to(ROOT)).replace("\\\\", "/"),
            "webm": str(webm.relative_to(ROOT)).replace("\\\\", "/"),
            "poster": str(poster.relative_to(ROOT)).replace("\\\\", "/"),
            "alt": f"Animated preference duel for {case_id}",
            "duration_ms": duration_ms,
        }

    _dump_json(MEDIA_JSON_PATH, media_json)
    print(f"Generated {len(cases)} preference duel media triplets under {OUT_DIR}")


if __name__ == "__main__":
    main()
