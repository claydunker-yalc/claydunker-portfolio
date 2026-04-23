"""
Generates sites/beauty-nook/og-image.png — the 1200x630 social card shown in
iMessage, Facebook, LinkedIn, Slack, etc.

Why this exists:
- OG preview services recommend 1200x630 landscape (2:1-ish) images.
- The bare logo.png is 1024x1024 — square — so platforms letterbox or crop it.
- This script composites the logo on a brand-colored background with a
  readable headline and CTA so the preview reads as a mini business card.

Re-run any time you change the logo, headline, or CTA copy. The output is
committed — not generated at build time — so CF Pages just serves the PNG.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BEAUTY_NOOK = ROOT / "sites" / "beauty-nook"

# ───── Brand constants ─────────────────────────────────────────
SPRUCE = (44, 64, 51)       # #2C4033 — deep spruce green
CREAM = (251, 248, 243)      # #FBF8F3 — warm off-white
GOLD = (214, 184, 136)       # #D6B888 — antique gold
TERRA = (196, 127, 101)      # #C47F65 — burnt terra

WIDTH, HEIGHT = 1200, 630
LOGO_SIZE = 420              # rendered size of the logo on the card
PADDING = 80

# ───── Font lookup ─────────────────────────────────────────────
# Cormorant / Inter aren't on macOS by default, so fall back to Georgia
# (serif, similar feel to Cormorant) and Helvetica (clean sans, like Inter).
SERIF_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
SERIF_ITALIC = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
SANS = "/System/Library/Fonts/Helvetica.ttc"


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


# ───── Compose ─────────────────────────────────────────────────
def main():
    # Base canvas in cream
    img = Image.new("RGB", (WIDTH, HEIGHT), CREAM)
    draw = ImageDraw.Draw(img)

    # Right-side spruce panel (the "card" feel) — logo sits on cream, text on spruce
    panel_x = 560
    draw.rectangle([(panel_x, 0), (WIDTH, HEIGHT)], fill=SPRUCE)

    # A thin gold vertical divider
    draw.rectangle([(panel_x - 2, 0), (panel_x + 2, HEIGHT)], fill=GOLD)

    # ── Logo on the cream side, centered ──
    logo_path = BEAUTY_NOOK / "logo.png"
    logo = Image.open(logo_path).convert("RGBA")
    logo.thumbnail((LOGO_SIZE, LOGO_SIZE), Image.LANCZOS)
    lx = (panel_x - logo.width) // 2
    ly = (HEIGHT - logo.height) // 2
    img.paste(logo, (lx, ly), logo)

    # ── Text on the spruce side ──
    title_font = load_font(SERIF_BOLD, 56)
    tagline_font = load_font(SERIF_ITALIC, 34)
    location_font = load_font(SANS, 22)
    cta_font = load_font(SANS, 26)

    text_x = panel_x + 60
    text_w = WIDTH - text_x - 60

    # Eyebrow — small, gold, spaced
    eyebrow = "NOW OPEN · MONTICELLO, IL"
    draw.text((text_x, 130), eyebrow, font=location_font, fill=GOLD,
              spacing=4)

    # Headline
    title = "The Beauty Nook"
    draw.text((text_x, 175), title, font=title_font, fill=CREAM)

    # Tagline
    tagline = "Your hair. Your nook."
    draw.text((text_x, 260), tagline, font=tagline_font, fill=GOLD)

    # Body copy (two lines, wrapped manually for tight control)
    body_font = load_font(SANS, 22)
    body_lines = [
        "Cuts, custom color, and treatments",
        "from Nikki — in a warm little nook.",
    ]
    by = 330
    for line in body_lines:
        draw.text((text_x, by), line, font=body_font, fill=(210, 220, 214))
        by += 32

    # CTA pill at the bottom
    cta_text = "Book an appointment  ›"  # › renders in Helvetica; → does not
    cta_pad_x = 28
    cta_pad_y = 14
    cta_bbox = draw.textbbox((0, 0), cta_text, font=cta_font)
    cta_w = cta_bbox[2] - cta_bbox[0]
    cta_h = cta_bbox[3] - cta_bbox[1]
    cta_x = text_x
    cta_y = HEIGHT - 110
    draw.rounded_rectangle(
        [(cta_x, cta_y),
         (cta_x + cta_w + cta_pad_x * 2, cta_y + cta_h + cta_pad_y * 2)],
        radius=999,
        fill=GOLD,
    )
    draw.text((cta_x + cta_pad_x, cta_y + cta_pad_y - 4), cta_text,
              font=cta_font, fill=SPRUCE)

    # Small domain text under CTA
    domain_font = load_font(SANS, 18)
    draw.text((text_x, HEIGHT - 50), "nikkisbeautynook.com",
              font=domain_font, fill=(180, 195, 186))

    # ───── Save ─────
    out = BEAUTY_NOOK / "og-image.png"
    img.save(out, "PNG", optimize=True)
    print(f"Wrote {out} ({out.stat().st_size} bytes, {WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()
