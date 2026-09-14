"""Generate the loose-ends wordmark in the identity of the personal site.

Palette and type are taken from Desktop/Projects/my-site: #fafafa ground, #111111 text,
Lora for headings with a Georgia fallback, Inter for body with a system-ui fallback, and
the neutral greys used for secondary text.

The mark is a spiral that unwinds into a horizontal rule and frays at the end, which is
the name drawn literally. Geometry is computed rather than hand-written so the tangent
where the spiral meets the rule is actually continuous.
"""
import math
from pathlib import Path

OUT = Path(__file__).parent

INK = "#111111"
GROUND = "#fafafa"
MUTED = "#a3a3a3"
HAIR = "#e5e5e5"

INK_D = "#ededed"          # dark-mode ink
GROUND_D = "#0d1117"       # GitHub dark canvas
MUTED_D = "#8b949e"
HAIR_D = "#30363d"

SERIF = "Lora, Georgia, 'Times New Roman', serif"
SANS = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif"


def spiral(cx, cy, r0, r1, t0, t1, steps=180):
    """Archimedean spiral sampled as a polyline, returned as points."""
    pts = []
    for i in range(steps + 1):
        f = i / steps
        t = t0 + (t1 - t0) * f
        r = r0 + (r1 - r0) * f
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return pts


def unwinding_path(cx, cy, end_x, baseline):
    """A spiral that leaves its last turn and settles onto a horizontal rule.

    The spiral is sampled to its exit point, then a single cubic carries it to the rule.
    The first control point continues the spiral's tangent, so the join has no corner.
    """
    # End at 315 degrees, where the tangent already points right and down, so the curve
    # onto the rule is a settle rather than a turn. Ending anywhere else makes the exit
    # double back over the loop it just came out of.
    pts = spiral(cx, cy, 10, 30, math.radians(215), math.radians(675))
    ex, ey = pts[-1]
    px, py = pts[-2]
    dx, dy = ex - px, ey - py
    n = math.hypot(dx, dy) or 1
    dx, dy = dx / n, dy / n

    lead = 30                      # how far the exit tangent is carried
    c1x, c1y = ex + dx * lead, ey + dy * lead
    join_x = cx + 92
    c2x, c2y = join_x - 34, baseline

    d = "M " + " L ".join(f"{x:.2f} {y:.2f}" for x, y in pts)
    d += f" C {c1x:.2f} {c1y:.2f} {c2x:.2f} {c2y:.2f} {join_x:.2f} {baseline:.2f}"
    d += f" L {end_x:.2f} {baseline:.2f}"
    return d


def banner(ink, ground, muted, hair, frame=True):
    """Variant A. Mark at the left, wordmark beside it, rule running under both."""
    W, H = 660, 204
    baseline = 126
    rule_end = 512
    d = unwinding_path(96, 80, rule_end, baseline)
    fray = "".join(
        f'<line x1="{rule_end + 14 + i * 16:.0f}" y1="{baseline}" '
        f'x2="{rule_end + 14 + i * 16 + 9 - i * 2:.0f}" y2="{baseline}" '
        f'stroke="{ink}" stroke-width="2" stroke-linecap="round" '
        f'opacity="{0.55 - i * 0.12:.2f}"/>'
        for i in range(4)
    )
    box = (f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="10" fill="{ground}" '
           f'stroke="{hair}"/>') if frame else f'<rect width="{W}" height="{H}" fill="{ground}"/>'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="loose-ends">
  <title>loose-ends</title>
  {box}
  <path d="{d}" fill="none" stroke="{ink}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
  {fray}
  <text x="212" y="108" font-family="{SERIF}" font-size="58" fill="{ink}" letter-spacing="-1.2">loose-ends</text>
  <text x="214" y="160" font-family="{SANS}" font-size="15.5" fill="{muted}" letter-spacing="0.2">records what you know, tracks what you said you would do</text>
</svg>
'''


def wordmark(ink, ground, muted, hair):
    """Variant B. Type only, with the rule and fray carrying the idea instead of a mark."""
    W, H = 520, 176
    baseline = 118
    fray = "".join(
        f'<line x1="{404 + i * 17:.0f}" y1="{baseline}" x2="{404 + i * 17 + 10 - i * 2:.0f}" '
        f'y2="{baseline}" stroke="{ink}" stroke-width="2" stroke-linecap="round" '
        f'opacity="{0.55 - i * 0.12:.2f}"/>'
        for i in range(4)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="loose-ends">
  <title>loose-ends</title>
  <rect width="{W}" height="{H}" fill="{ground}"/>
  <text x="56" y="96" font-family="{SERIF}" font-size="62" fill="{ink}" letter-spacing="-1.4">loose-ends</text>
  <path d="M 58 {baseline} L 392 {baseline}" fill="none" stroke="{ink}" stroke-width="2.4" stroke-linecap="round"/>
  {fray}
  <text x="58" y="150" font-family="{SANS}" font-size="15" fill="{muted}" letter-spacing="0.2">records what you know, tracks what you said you would do</text>
</svg>
'''


def stacked(ink, ground, muted, hair):
    """Variant C. Mark above the wordmark, centred, for a narrower header."""
    W, H = 560, 300
    d = unwinding_path(214, 96, 380, 142)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="loose-ends">
  <title>loose-ends</title>
  <rect width="{W}" height="{H}" fill="{ground}"/>
  <path d="{d}" fill="none" stroke="{ink}" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="280" y="218" text-anchor="middle" font-family="{SERIF}" font-size="52" fill="{ink}" letter-spacing="-1.1">loose-ends</text>
  <text x="280" y="252" text-anchor="middle" font-family="{SANS}" font-size="14.5" fill="{muted}" letter-spacing="0.2">records what you know, tracks what you said you would do</text>
</svg>
'''


LIGHT = (INK, GROUND, MUTED, HAIR)
DARK = (INK_D, GROUND_D, MUTED_D, HAIR_D)

for name, fn in (("banner", banner), ("wordmark", wordmark), ("stacked", stacked)):
    (OUT / f"{name}.svg").write_text(fn(*LIGHT), encoding="utf-8")
    (OUT / f"{name}-dark.svg").write_text(fn(*DARK), encoding="utf-8")
    print(f"  {name}.svg + {name}-dark.svg")
