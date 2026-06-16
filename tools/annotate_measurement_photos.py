from __future__ import annotations

from math import atan2, cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = Path(
    r"C:\Users\scwmf\.codex\codex-remote-attachments\019ece30-5936-7f50-9623-3e62856770ba\9E3B38E9-57D9-4A35-AC90-6DBBD641AFE0"
)
OUT_DIR = ROOT / "docs" / "photo-guides"

PHOTO_1 = SOURCE_DIR / "1-写真1.jpg"
PHOTO_2 = SOURCE_DIR / "2-写真2.jpg"

YELLOW = (255, 207, 74)
BLUE = (87, 203, 255)
PINK = (255, 112, 170)
WHITE = (248, 250, 255)
BLACK = (10, 12, 18)
PANEL = (15, 18, 26, 215)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\meiryob.ttc" if bold else r"C:\Windows\Fonts\meiryo.ttc",
        r"C:\Windows\Fonts\YuGothB.ttc" if bold else r"C:\Windows\Fonts\YuGothR.ttc",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


FONT_TITLE = font(42, True)
FONT_LABEL = font(34, True)
FONT_NOTE = font(25)
FONT_SMALL = font(22)


def draw_arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int],
    width: int = 8,
    both: bool = True,
) -> None:
    draw.line([start, end], fill=color, width=width)
    draw_arrow_head(draw, start, end, color, width)
    if both:
        draw_arrow_head(draw, end, start, color, width)


def draw_arrow_head(
    draw: ImageDraw.ImageDraw,
    tip: tuple[int, int],
    tail: tuple[int, int],
    color: tuple[int, int, int],
    width: int,
) -> None:
    angle = atan2(tip[1] - tail[1], tip[0] - tail[0])
    size = width * 4.3
    left = angle + pi * 0.82
    right = angle - pi * 0.82
    points = [
        tip,
        (int(tip[0] + cos(left) * size), int(tip[1] + sin(left) * size)),
        (int(tip[0] + cos(right) * size), int(tip[1] + sin(right) * size)),
    ]
    draw.polygon(points, fill=color)


def draw_label(
    img: Image.Image,
    xy: tuple[int, int],
    title: str,
    note: str,
    color: tuple[int, int, int],
    w: int = 430,
) -> None:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    x, y = xy
    h = 106 if note else 70
    od.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=PANEL, outline=color + (255,), width=3)
    od.text((x + 18, y + 12), title, fill=color, font=FONT_LABEL)
    if note:
        od.text((x + 18, y + 58), note, fill=WHITE, font=FONT_NOTE)
    img.alpha_composite(overlay)


def draw_top_banner(img: Image.Image, title: str, subtitle: str) -> None:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle([34, 34, img.width - 34, 158], radius=22, fill=(10, 12, 18, 230))
    od.text((62, 52), title, fill=WHITE, font=FONT_TITLE)
    od.text((62, 108), subtitle, fill=(210, 218, 232), font=FONT_SMALL)
    img.alpha_composite(overlay)


def annotate_photo_1() -> Path:
    img = Image.open(PHOTO_1).convert("RGBA")
    draw = ImageDraw.Draw(img)
    draw_top_banner(
        img,
        "写真1: 上面から見える外形を測る",
        "A/Bが最重要。ノブや端の凹凸も、スロット干渉に効きます。",
    )

    # A: short edge/depth of one half when stored short-edge down.
    draw_arrow(draw, (1338, 952), (1178, 1462), YELLOW, width=9)
    draw_label(
        img,
        (865, 1280),
        "A 短辺外形",
        "前端から奥端まで",
        YELLOW,
        w=360,
    )

    # Optional long edge / widest outline.
    draw_arrow(draw, (138, 1040), (1195, 1452), BLUE, width=8)
    draw_label(
        img,
        (130, 840),
        "A2 長辺/最大幅",
        "左右差確認用",
        BLUE,
        w=390,
    )

    # Knob location and size.
    draw.ellipse([320, 760, 470, 910], outline=PINK, width=8)
    draw_arrow(draw, (394, 760), (540, 570), PINK, width=7, both=False)
    draw_label(
        img,
        (540, 470),
        "E ノブ",
        "径・高さ・端からの位置",
        PINK,
        w=420,
    )

    # Curved thumb edge / irregular outline.
    draw.line([(122, 1038), (420, 1172), (655, 1300)], fill=YELLOW, width=7)
    draw_label(
        img,
        (90, 1215),
        "G 外形の凹凸",
        "角丸R/くびれ位置",
        YELLOW,
        w=390,
    )

    # Need side photos for ports.
    draw_label(
        img,
        (850, 180),
        "D USB-C / 電源",
        "この写真だと追加側面写真が必要",
        PINK,
        w=530,
    )

    out = OUT_DIR / "photo1-measurement-annotated.jpg"
    img.convert("RGB").save(out, quality=92)
    return out


def annotate_photo_2() -> Path:
    img = Image.open(PHOTO_2).convert("RGBA")
    draw = ImageDraw.Draw(img)
    draw_top_banner(
        img,
        "写真2: 厚みと高さを測る",
        "B/Cはぴったり感に直結。底の足や保護材厚みもここで確認します。",
    )

    # B: max thickness including keys.
    draw_arrow(draw, (1088, 860), (1088, 1148), BLUE, width=9)
    draw_label(
        img,
        (920, 930),
        "B 最大厚み",
        "底面からキー/ノブ上端まで",
        BLUE,
        w=460,
    )

    # C: case body thickness.
    draw_arrow(draw, (1012, 990), (1012, 1148), YELLOW, width=8)
    draw_label(
        img,
        (760, 1168),
        "C ケース厚",
        "アルミ筐体だけの高さ",
        YELLOW,
        w=420,
    )

    # H: feet / bottom protrusion.
    draw_arrow(draw, (570, 1128), (570, 1194), PINK, width=8)
    draw_label(
        img,
        (165, 1170),
        "H 底面の足/保護材",
        "足の高さ・貼るシート厚",
        PINK,
        w=490,
    )

    # G: corner radius.
    draw.arc([1015, 1000, 1258, 1235], 275, 360, fill=YELLOW, width=8)
    draw_label(
        img,
        (850, 760),
        "G 角丸R",
        "前角の丸み",
        YELLOW,
        w=330,
    )

    # Front short edge in this view.
    draw_arrow(draw, (430, 1095), (1080, 1018), YELLOW, width=7)
    draw_label(
        img,
        (95, 885),
        "A 短辺外形",
        "この前後方向も確認",
        YELLOW,
        w=385,
    )

    out = OUT_DIR / "photo2-measurement-annotated.jpg"
    img.convert("RGB").save(out, quality=92)
    return out


def build_contact_sheet(paths: list[Path]) -> Path:
    images = [Image.open(path).convert("RGB") for path in paths]
    width = 900
    scaled = []
    for image in images:
        ratio = width / image.width
        scaled.append(image.resize((width, int(image.height * ratio)), Image.Resampling.LANCZOS))

    sheet_w = width * 2 + 36
    sheet_h = max(image.height for image in scaled)
    sheet = Image.new("RGB", (sheet_w, sheet_h), BLACK)
    sheet.paste(scaled[0], (0, 0))
    sheet.paste(scaled[1], (width + 36, 0))
    out = OUT_DIR / "photo-measurement-contact-sheet.jpg"
    sheet.save(out, quality=92)
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    photo1 = annotate_photo_1()
    photo2 = annotate_photo_2()
    sheet = build_contact_sheet([photo1, photo2])
    for path in (photo1, photo2, sheet):
        print(path)


if __name__ == "__main__":
    main()
