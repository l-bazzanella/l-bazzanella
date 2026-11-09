"""Generate a fastfetch-style profile card as SVG.

Usage: python3 fetchcard.py LOGO.txt OUT.svg

The logo is scaled so it is as tall as the info column, the way fastfetch fits a big logo.
Brand icons come from icons/, copied from Simple Icons (CC0). Brands that Simple Icons no
longer carries, and the generic glyphs, are drawn in CUSTOM below.
"""
import html
import re
import sys
from pathlib import Path

# (kind, key, value, icon)
INFO = [
    ("title", "bazz", "sirius", None),
    ("sep", "-----------", None, None),
    ("kv", "OS", "CachyOS (Arch Linux) x86_64", "archlinux"),
    ("kv", "WM", "niri (Wayland)", "wayland"),
    ("kv", "Shell", "zsh + DankMaterialShell", "zsh"),
    ("kv", "Terminal", "kitty · Ghostty · Alacritty", "ghostty"),
    ("kv", "Multiplexer", "byobu · herdr", "tmux"),
    ("blank", "", None, None),
    ("kv", "Role", "Infra · SysAdmin · DevOps", "linux"),
    ("kv", "Focus", "Datacenter · Backup & DR", "server"),
    ("kv", "Virtualization", "VMware · OLVM · Hyper-V", "layers"),
    ("kv", "Backup", "Veeam B&R · ONE · Cloud Connect", "restore"),
    ("kv", "Storage", "Spectrum Virtualize · Wasabi S3", "wasabi"),
    ("kv", "Monitoring", "Zabbix · Grafana · Telegraf", "grafana"),
    ("kv", "Automation", "Bash · PowerShell · Rust", "gnubash"),
    ("kv", "AI", "Claude Code · MCP · Skills", "claude"),
    ("blank", "", None, None),
    ("kv", "Languages", "PT-BR · EN", "globe"),
    ("kv", "Uptime", "since 2021, always on call", "clock"),
    ("blank", "", None, None),
    ("colors", "", None, None),
]

# The row of logos along the bottom of the card.
STACK = ["archlinux", "debian", "redhat", "windows", "vmware", "veeam", "wasabi", "zabbix", "grafana",
         "gnubash", "powershell", "rust", "git", "1password", "claude", "modelcontextprotocol"]

BRAND = {
    "1password": "#145FE4", "archlinux": "#1793D1", "claude": "#D97757", "debian": "#D70A53",
    "ghostty": "#3551F3", "git": "#F03C2E", "gnubash": "#4EAA25", "grafana": "#F46800",
    "linux": "#FCC624", "redhat": "#EE0000", "tmux": "#1BB91F", "veeam": "#00B336",
    "vmware": "#A9B1D6", "wasabi": "#01CD3E", "wayland": "#FFBC00", "zsh": "#F15A24",
    # Black in Simple Icons, which vanishes on the dark card.
    "modelcontextprotocol": "#C0CAF5", "rust": "#C0CAF5",
    # Hand-drawn glyphs.
    "layers": "#7DCFFF", "restore": "#00B336",
}

# Wordmarks, drawn twice as large so the lettering stays readable in the bottom row.
WIDE = {"vmware", "veeam"}

# Hand-drawn 24x24 icons. {c} is the icon color, {bg} the card background.
CUSTOM = {
    "windows": '<path fill="#00A4EF" d="M2 4.5 10 3.4v7.8H2zM11 3.3 22 2v9.2H11zM2 12.2h8V20l-8-1.1zM11 12.2h11V22l-11-1.5z"/>',
    "powershell": '<rect x="1" y="3" width="22" height="18" rx="3" fill="#2671BE"/>'
                  '<path fill="#fff" d="m5.5 7.5 6 4.5-6 4.5-1.2-1.6L8.3 12 4.3 9.1zM12 15h7v2h-7z"/>',
    "zabbix": '<rect x="1" y="1" width="22" height="22" rx="2" fill="#D40000"/>'
              '<path fill="#fff" d="M6 6h12v2.4L9.6 15.6H18V18H6v-2.4l8.4-7.2H6z"/>',
    "server": '<path fill="{c}" fill-rule="evenodd" d="M3 3h18v7H3zm3 2.5v2h2v-2zM3 14h18v7H3zm3 2.5v2h2v-2z"/>',
    "globe": '<g fill="none" stroke="{c}" stroke-width="2"><circle cx="12" cy="12" r="9.5"/>'
             '<path d="M2.5 12h19M12 2.5c3 3 3 16 0 19M12 2.5c-3 3-3 16 0 19"/></g>',
    "layers": '<g fill="none" stroke="{c}" stroke-width="2" stroke-linejoin="round">'
              '<path d="M12 3 2 8l10 5 10-5z"/><path d="m2 12 10 5 10-5"/><path d="m2 16 10 5 10-5"/></g>',
    "restore": '<g fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
               '<path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l3 2"/></g>',
    "clock": '<g fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9.5"/>'
             '<path d="M12 6.5V12l3.5 2.5"/></g>',
}

FONT = 14
CW = 8.4          # glyph advance, enforced with textLength
LH = 19
PAD = 24
GAP = 36          # space between logo and info
BAR = 34          # title bar height
ICON = 14         # icon size in the info column
STACK_ICON = 24   # icon size in the bottom row
STACK_GAP = 18
LOGO_COLOR = "#c0caf5"
KEY = "#7aa2f7"
VAL = "#c0caf5"
DIM = "#565f89"
USER = "#bb9af7"
BG = "#1a1b26"
BAR_BG = "#16161e"
PALETTE = ["#414868", "#f7768e", "#9ece6a", "#e0af68", "#7aa2f7", "#bb9af7", "#7dcfff", "#a9b1d6"]

ICON_DIR = Path(__file__).resolve().parent / "icons"


def icon(name, x, y, size):
    """Place a 24x24 icon with its top-left corner at x, y."""
    color = BRAND.get(name, VAL)
    if name in CUSTOM:
        body = CUSTOM[name].format(c=color, bg=BG)
    else:
        svg = (ICON_DIR / f"{name}.svg").read_text(encoding="utf-8")
        path = re.search(r'<path d="([^"]+)"', svg).group(1)
        body = f'<path fill="{color}" d="{path}"/>'
    s = size / 24
    return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.4f})">{body}</g>'


def text(x, y, s, color, bold=False, size=None, cw=CW):
    weight = ' font-weight="700"' if bold else ""
    fsize = f' font-size="{size:.2f}"' if size else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}"{weight}{fsize} textLength="{len(s) * cw:.1f}" '
            f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">{html.escape(s)}</text>')


logo = open(sys.argv[1], encoding="utf-8").read().rstrip("\n").split("\n")
info_h = len(INFO) * LH
logo_lh = info_h / len(logo)          # logo line height that matches the info column
logo_font = logo_lh                   # braille cells fill the em box, so font size = line height
logo_cw = logo_font * CW / FONT
logo_w = max(map(len, logo)) * logo_cw

info_x = PAD + logo_w + GAP
text_x = info_x + ICON + 8            # keys start after the icon
info_w = ICON + 8 + max(len(f"{k}: {v}") for t, k, v, _ in INFO if t == "kv") * CW
width = int(info_x + info_w + PAD)
body_top = BAR + PAD * 0.75
stack_top = body_top + info_h + PAD
height = int(stack_top + STACK_ICON + PAD)

out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
    f'role="img" aria-label="bazz@sirius fastfetch">',
    f'<style>text{{font-family:"JetBrains Mono","DejaVu Sans Mono",Menlo,Consolas,"Segoe UI Symbol",monospace;font-size:{FONT}px}}</style>',
    f'<rect width="{width}" height="{height}" rx="12" fill="{BG}"/>',
    f'<path d="M0 12a12 12 0 0 1 12-12h{width - 24}a12 12 0 0 1 12 12v{BAR - 12}h-{width}z" fill="{BAR_BG}"/>',
]
for i, c in enumerate(["#f7768e", "#e0af68", "#9ece6a"]):
    out.append(f'<circle cx="{20 + i * 20}" cy="{BAR / 2}" r="6" fill="{c}"/>')

for i, line in enumerate(logo):
    if line.strip("⠀ "):
        y = body_top + (i + 1) * logo_lh - logo_lh * 0.2
        out.append(text(PAD, y, line, LOGO_COLOR, size=logo_font, cw=logo_cw))

for i, (kind, k, v, ico) in enumerate(INFO):
    y = body_top + i * LH + FONT
    if ico:
        out.append(icon(ico, info_x, y - FONT + 1.5, ICON))
    if kind == "title":
        out.append(text(text_x, y, k, USER, bold=True))
        out.append(text(text_x + len(k) * CW, y, "@", VAL))
        out.append(text(text_x + (len(k) + 1) * CW, y, v, KEY, bold=True))
    elif kind == "sep":
        out.append(text(text_x, y, k, DIM))
    elif kind == "kv":
        out.append(text(text_x, y, f"{k}:", KEY, bold=True))
        out.append(text(text_x + (len(k) + 2) * CW, y, v, VAL))
    elif kind == "colors":
        for j, c in enumerate(PALETTE):
            out.append(f'<rect x="{text_x + j * 3 * CW:.1f}" y="{y - FONT + 2:.1f}" width="{3 * CW:.1f}" height="{LH - 2}" fill="{c}"/>')

# A thin rule, then the stack row centered under the whole card.
out.append(f'<line x1="{PAD}" y1="{stack_top - PAD / 2:.1f}" x2="{width - PAD}" y2="{stack_top - PAD / 2:.1f}" stroke="#24283b"/>')
sizes = [STACK_ICON * 2 if name in WIDE else STACK_ICON for name in STACK]
x = (width - sum(sizes) - (len(STACK) - 1) * STACK_GAP) / 2
for name, size in zip(STACK, sizes):
    # A wide icon keeps its vertical center on the row.
    out.append(icon(name, x, stack_top - (size - STACK_ICON) / 2, size))
    x += size + STACK_GAP

out.append("</svg>")
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out) + "\n")
print(width, height)
