"""Generate a fastfetch-style profile card as SVG.

Usage: python3 fetchcard.py LOGO.txt OUT.svg

The logo is scaled so it is as tall as the info column, the way fastfetch fits a big logo.
"""
import html
import sys

INFO = [
    ("title", "bazz", "sirius"),
    ("sep", "-----------", None),
    ("kv", "OS", "CachyOS (Arch Linux) x86_64"),
    ("kv", "WM", "niri (Wayland)"),
    ("kv", "Shell", "zsh + DankMaterialShell"),
    ("kv", "Terminal", "kitty · Ghostty · Alacritty"),
    ("kv", "Multiplexer", "byobu · herdr"),
    ("blank", "", None),
    ("kv", "Role", "Infra · SysAdmin · DevOps"),
    ("kv", "Focus", "Datacenter · Backup & DR"),
    ("kv", "Virtualization", "VMware · OLVM · Hyper-V"),
    ("kv", "Backup", "Veeam B&R · ONE · Cloud Connect"),
    ("kv", "Storage", "Spectrum Virtualize · Wasabi S3"),
    ("kv", "Monitoring", "Zabbix · Grafana · Telegraf"),
    ("kv", "Automation", "Bash · PowerShell · Rust"),
    ("kv", "AI", "Claude Code · MCP · Skills"),
    ("blank", "", None),
    ("kv", "Languages", "PT-BR · EN"),
    ("kv", "Uptime", "since 2021, always on call"),
    ("blank", "", None),
    ("colors", "", None),
]

FONT = 14
CW = 8.4          # glyph advance as a share of FONT, enforced with textLength
LH = 19
PAD = 24
GAP = 36          # space between logo and info
BAR = 34          # title bar height
LOGO_COLOR = "#c0caf5"
KEY = "#7aa2f7"
VAL = "#c0caf5"
DIM = "#565f89"
USER = "#bb9af7"
BG = "#1a1b26"
BAR_BG = "#16161e"
PALETTE = ["#414868", "#f7768e", "#9ece6a", "#e0af68", "#7aa2f7", "#bb9af7", "#7dcfff", "#a9b1d6"]

logo = open(sys.argv[1], encoding="utf-8").read().rstrip("\n").split("\n")
info_h = len(INFO) * LH
logo_lh = info_h / len(logo)          # logo line height that matches the info column
logo_font = logo_lh                   # braille cells fill the em box, so font size = line height
logo_cw = logo_font * CW / FONT
logo_w = max(map(len, logo)) * logo_cw

info_x = PAD + logo_w + GAP
info_w = max(len(f"{k}: {v}") for t, k, v in INFO if t == "kv") * CW
width = int(info_x + info_w + PAD)
prompt_y = BAR + PAD + FONT
body_top = prompt_y + LH * 0.9
height = int(body_top + info_h + PAD)


def text(x, y, s, color, bold=False, size=None, cw=CW):
    weight = ' font-weight="700"' if bold else ""
    fsize = f' font-size="{size:.2f}"' if size else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}"{weight}{fsize} textLength="{len(s) * cw:.1f}" '
            f'lengthAdjust="spacingAndGlyphs" xml:space="preserve">{html.escape(s)}</text>')


out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
    f'role="img" aria-label="bazz@sirius fastfetch">',
    f'<style>text{{font-family:"JetBrains Mono","DejaVu Sans Mono",Menlo,Consolas,"Segoe UI Symbol",monospace;font-size:{FONT}px}}</style>',
    f'<rect width="{width}" height="{height}" rx="12" fill="{BG}"/>',
    f'<path d="M0 12a12 12 0 0 1 12-12h{width - 24}a12 12 0 0 1 12 12v{BAR - 12}h-{width}z" fill="{BAR_BG}"/>',
]
for i, c in enumerate(["#f7768e", "#e0af68", "#9ece6a"]):
    out.append(f'<circle cx="{20 + i * 20}" cy="{BAR / 2}" r="6" fill="{c}"/>')
out.append(f'<text x="{width / 2}" y="{BAR / 2 + 5}" fill="{DIM}" text-anchor="middle">bazz@sirius: ~</text>')

out.append(text(PAD, prompt_y, "bazz@sirius:~$", USER, bold=True))
out.append(text(PAD + 15 * CW, prompt_y, "fastfetch", VAL))

for i, line in enumerate(logo):
    if line.strip("⠀ "):
        y = body_top + (i + 1) * logo_lh - logo_lh * 0.2
        out.append(text(PAD, y, line, LOGO_COLOR, size=logo_font, cw=logo_cw))

for i, (kind, k, v) in enumerate(INFO):
    y = body_top + i * LH + FONT
    if kind == "title":
        out.append(text(info_x, y, k, USER, bold=True))
        out.append(text(info_x + len(k) * CW, y, "@", VAL))
        out.append(text(info_x + (len(k) + 1) * CW, y, v, KEY, bold=True))
    elif kind == "sep":
        out.append(text(info_x, y, k, DIM))
    elif kind == "kv":
        out.append(text(info_x, y, f"{k}:", KEY, bold=True))
        out.append(text(info_x + (len(k) + 2) * CW, y, v, VAL))
    elif kind == "colors":
        for j, c in enumerate(PALETTE):
            out.append(f'<rect x="{info_x + j * 3 * CW:.1f}" y="{y - FONT + 2:.1f}" width="{3 * CW:.1f}" height="{LH - 2}" fill="{c}"/>')

out.append("</svg>")
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out) + "\n")
print(width, height)
