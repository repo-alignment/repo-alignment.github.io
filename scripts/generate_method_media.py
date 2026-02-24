from __future__ import annotations

import math
from pathlib import Path

import imageio.v2 as iio
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
IMG_DIR = ASSETS / "img"
MEDIA_DIR = ASSETS / "media"

W, H = 1280, 720
FPS = 12


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for p in candidates:
        fp = Path(p)
        if fp.exists():
            return ImageFont.truetype(str(fp), size=size)
    return ImageFont.load_default()


def _fit_to_canvas(path: Path, canvas_size: tuple[int, int], zoom: float = 1.0) -> Image.Image:
    base = Image.new("RGB", canvas_size, "#f5f6f8")
    img = Image.open(path).convert("RGB")
    target_w = int(canvas_size[0] * zoom)
    target_h = int(canvas_size[1] * zoom)
    fit = ImageOps.contain(img, (target_w, target_h))
    x = (canvas_size[0] - fit.width) // 2
    y = (canvas_size[1] - fit.height) // 2
    base.paste(fit, (x, y))
    return base


def _pill(draw: ImageDraw.ImageDraw, box, text: str, active: bool) -> None:
    if active:
        fill, outline, text_color = "#0b5cab", "#0b5cab", "#ffffff"
    else:
        fill, outline, text_color = "#ffffffd8", "#b7c7d8", "#223244"
    draw.rounded_rectangle(box, radius=14, fill=fill, outline=outline, width=2)
    tw, th = draw.textbbox((0, 0), text, font=_font(24))[2:]
    tx = (box[0] + box[2] - tw) // 2
    ty = (box[1] + box[3] - th) // 2 - 2
    draw.text((tx, ty), text, fill=text_color, font=_font(24))


def build_flow_frames() -> list[np.ndarray]:
    frames: list[np.ndarray] = []
    base = _fit_to_canvas(IMG_DIR / "flow_chart.png", (W, H))
    steps = ["Input Noisy Preferences", "E-step", "M-step", "Updated Policy/Reliability"]

    for idx, step in enumerate(steps):
        for t in range(14):
            img = base.copy()
            draw = ImageDraw.Draw(img, "RGBA")
            draw.rectangle((0, 0, W, 118), fill=(247, 250, 255, 228))

            start_x = 22
            gap = 12
            box_w = (W - start_x * 2 - gap * (len(steps) - 1)) // len(steps)
            for s_idx, s in enumerate(steps):
                x0 = start_x + s_idx * (box_w + gap)
                y0, y1 = 26, 92
                active = s_idx == idx
                if active:
                    pulse = int(18 * (0.5 + 0.5 * math.sin(t / 14 * 2 * math.pi)))
                    draw.rounded_rectangle((x0 - 2, y0 - 2, x0 + box_w + 2, y1 + 2), radius=16, outline=(11, 92, 171, 130 + pulse), width=3)
                _pill(draw, (x0, y0, x0 + box_w, y1), s, active)

            subtitle = f"Stage {idx + 1}/{len(steps)}: {step}"
            draw.text((26, 102), subtitle, fill="#26374a", font=_font(23))
            frames.append(np.asarray(img))

    return frames


def _blend(a: Image.Image, b: Image.Image, alpha: float) -> Image.Image:
    return Image.blend(a, b, alpha=alpha)


def build_reliability_frames() -> list[np.ndarray]:
    frames: list[np.ndarray] = []

    for i in range(26):
        zoom = 1.0 + 0.05 * (i / 25)
        img = _fit_to_canvas(IMG_DIR / "one_annotator_eta.png", (W, H), zoom=zoom)
        draw = ImageDraw.Draw(img, "RGBA")
        draw.rectangle((0, 0, W, 90), fill=(250, 252, 255, 220))
        draw.text((24, 24), "Reliability Dynamics: Single-Annotator Tracking", fill="#223244", font=_font(30))
        frames.append(np.asarray(img))

    a = _fit_to_canvas(IMG_DIR / "one_annotator_eta.png", (W, H), zoom=1.03)
    b = _fit_to_canvas(IMG_DIR / "two_annotators_eta.png", (W, H), zoom=1.03)
    for i in range(18):
        alpha = i / 17
        img = _blend(a, b, alpha)
        draw = ImageDraw.Draw(img, "RGBA")
        draw.rectangle((0, 0, W, 90), fill=(250, 252, 255, 220))
        draw.text((24, 24), "Transition: Two-Annotator Divergence", fill="#223244", font=_font(30))
        frames.append(np.asarray(img))

    for i in range(26):
        zoom = 1.04 - 0.03 * (i / 25)
        img = _fit_to_canvas(IMG_DIR / "two_annotators_eta.png", (W, H), zoom=zoom)
        draw = ImageDraw.Draw(img, "RGBA")
        draw.rectangle((0, 0, W, 90), fill=(250, 252, 255, 220))
        draw.text((24, 24), "Reliability Dynamics: Two-Annotator Setting", fill="#223244", font=_font(30))
        frames.append(np.asarray(img))

    return frames


def write_triplet(stem: str, frames: list[np.ndarray], fps: int = FPS) -> None:
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    mp4 = MEDIA_DIR / f"{stem}.mp4"
    webm = MEDIA_DIR / f"{stem}.webm"
    gif = MEDIA_DIR / f"{stem}.gif"

    with iio.get_writer(mp4, format="FFMPEG", fps=fps, codec="libx264", ffmpeg_log_level="error") as w:
        for frame in frames:
            w.append_data(frame)

    webm_done = False
    for codec in ("libvpx-vp9", "libvpx"):
        try:
            with iio.get_writer(webm, format="FFMPEG", fps=fps, codec=codec, ffmpeg_log_level="error") as w:
                for frame in frames:
                    w.append_data(frame)
            webm_done = True
            break
        except Exception:
            continue

    if not webm_done:
        raise RuntimeError("Failed to generate WEBM output with libvpx-vp9/libvpx")

    iio.mimsave(gif, frames, format="GIF", duration=int(1000 / fps), loop=0)


if __name__ == "__main__":
    flow_frames = build_flow_frames()
    reliability_frames = build_reliability_frames()
    write_triplet("flow_method", flow_frames)
    write_triplet("reliability_method", reliability_frames)
    print("Generated method media under assets/media")
