#!/usr/bin/env python3
"""Turn audit.json into one branded report file the client can open, save as a
PDF, or put online.

Why this exists: the report is the thing the client actually sees, so it has to
look the same every time, print cleanly to A4, and carry the consultant's own
colours and logo. Claude writes the words into audit.json; this script does
the layout, so nothing drifts and nobody hand-writes HTML.

Usage:
  python3 build_report.py audit.json                # writes report/index.html beside audit.json
  python3 build_report.py audit.json --pdf          # also makes a PDF (needs Chrome, Edge, Brave or Chromium)
  python3 build_report.py audit.json --check        # only checks audit.json, writes nothing

It never overwrites: an existing report/index.html is moved into
report/earlier-versions/ first. Standard library only.
"""
import argparse
import base64
import datetime
import html
import json
import math
import pathlib
import random
import re
import shutil
import subprocess
import sys

STATUS = {
    # Words as well as colours, so the report still reads in black and white.
    "fix-first": {"label": "Fix first", "colour": "#B83A26", "tint": "#FBEAE6"},
    "tidy-up": {"label": "Tidy up", "colour": "#A86B00", "tint": "#FBF1DC"},
    "working": {"label": "Working well", "colour": "#2E7A4B", "tint": "#E5F3EA"},
}
STATUS_ALIASES = {
    "red": "fix-first", "fix first": "fix-first", "fix": "fix-first",
    "amber": "tidy-up", "yellow": "tidy-up", "tidy up": "tidy-up",
    "green": "working", "working well": "working", "ok": "working",
}
NEUTRAL = "#8A9099"


# ---------- small helpers ----------

def esc(value):
    return html.escape(str(value), quote=True)


def status_key(value):
    if not value:
        return None
    key = str(value).strip().lower()
    key = STATUS_ALIASES.get(key, key)
    return key if key in STATUS else None


def hex_to_rgb(value):
    value = value.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c))):02X}" for c in rgb)


def mix(colour, other, amount):
    """amount = how much of `other` to blend in (0 to 1)."""
    a, b = hex_to_rgb(colour), hex_to_rgb(other)
    return rgb_to_hex(tuple(x + (y - x) * amount for x, y in zip(a, b)))


def luminance(colour):
    def channel(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(c) for c in hex_to_rgb(colour))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def ink_on(colour):
    """White or near-black text, whichever reads better on this colour."""
    return "#FFFFFF" if contrast("#FFFFFF", colour) >= contrast("#16181D", colour) else "#16181D"


def readable_on_white(colour):
    """Darken a colour until it can be used for text on white (4.5:1)."""
    out = colour
    for _ in range(20):
        if contrast(out, "#FFFFFF") >= 4.5:
            return out
        out = mix(out, "#000000", 0.12)
    return out


def valid_hex(value):
    return isinstance(value, str) and re.fullmatch(r"#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", value.strip())


def as_list(value):
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    return [v for v in value if v not in (None, "")]


def wrap(text, width):
    """Rough word wrap for SVG text (SVG can't wrap by itself)."""
    words, lines, line = str(text).split(), [], ""
    for word in words:
        if len(line) + len(word) + (1 if line else 0) <= width:
            line = f"{line} {word}".strip()
        else:
            if line:
                lines.append(line)
            while len(word) > width:
                lines.append(word[:width - 1] + "-")
                word = word[width - 1:]
            line = word
    if line:
        lines.append(line)
    return lines or [""]


def logo_src(logo, base):
    """Embed a local logo so the report stays one self-contained file."""
    if not logo:
        return None, None
    logo = str(logo).strip()
    if logo.startswith(("http://", "https://", "data:")):
        return logo, None
    path = pathlib.Path(logo).expanduser()
    if not path.is_absolute():
        path = (base / path).resolve()
    if not path.exists():
        return None, f"Logo not found at {path}. Using your business name instead."
    kinds = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
             ".svg": "image/svg+xml", ".webp": "image/webp", ".gif": "image/gif"}
    kind = kinds.get(path.suffix.lower())
    if not kind:
        return None, f"Logo must be PNG, JPG, SVG or WEBP (got {path.suffix}). Using your business name instead."
    if path.stat().st_size > 3_000_000:
        return None, "Logo file is over 3 MB. Use a smaller copy. Using your business name for now."
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{kind};base64,{data}", None


# ---------- checking audit.json ----------

def check(audit):
    problems, warnings = [], []
    if audit.get("audit_type") not in ("setup", "business"):
        problems.append('audit_type must be "setup" or "business".')
    for path in ("consultant.name", "consultant.business", "client.business", "headline"):
        node = audit
        for part in path.split("."):
            node = node.get(part) if isinstance(node, dict) else None
        if not node:
            problems.append(f"{path} is missing.")
    if not as_list(audit.get("where_things_are_now")):
        problems.append("where_things_are_now needs at least one paragraph.")
    if not audit.get("priorities"):
        problems.append("priorities needs at least one item (your ranked fixes or opportunities).")
    roadmap = audit.get("roadmap") or {}
    if not any(as_list(roadmap.get(k)) for k in ("now", "next", "later")):
        problems.append("roadmap needs at least one item under now, next or later.")
    if not (audit.get("next_step") or {}).get("heading"):
        problems.append("next_step.heading is missing.")
    if audit.get("audit_type") == "setup" and not audit.get("health_check"):
        problems.append("A setup audit needs health_check (one entry per area).")
    for i, item in enumerate(audit.get("health_check") or [], 1):
        if not status_key(item.get("status")):
            problems.append(f'health_check item {i} ("{item.get("area", "?")}") needs a status: fix-first, tidy-up or working.')
    style = audit.get("style") or {}
    for key in ("main_colour", "accent_colour"):
        if style.get(key) and not valid_hex(style[key]):
            problems.append(f"style.{key} must be a hex colour like #1F4D3A (got {style[key]!r}).")
    the_map = audit.get("map")
    if the_map:
        ids = {}
        for col in the_map.get("columns", []):
            for item in col.get("items", []):
                if item.get("id") in ids:
                    problems.append(f'map item id "{item.get("id")}" is used twice.')
                ids[item.get("id")] = col
        for link in the_map.get("links", []):
            for end in ("from", "to"):
                if link.get(end) not in ids:
                    problems.append(f'map link points to "{link.get(end)}", which isn\'t a map item id.')
        for link in the_map.get("links", []):
            a, b = ids.get(link.get("from")), ids.get(link.get("to"))
            if a is not None and b is not None:
                cols = the_map.get("columns", [])
                gap_cols = abs(cols.index(a) - cols.index(b))
                if gap_cols > 1:
                    warnings.append(f'The map arrow from "{link.get("from")}" to "{link.get("to")}" skips a column, so it can pass behind other boxes. Link it through a box in the column between.')
        if len(the_map.get("columns", [])) > 5:
            warnings.append("The map has more than 5 columns. It will be cramped; 3 or 4 reads best.")
    # Brackets left in client-facing text mean a fill-in was never filled.
    leftover = sorted(set(re.findall(r"\[[A-Z][A-Z0-9 '’&,./\-]{2,}\]", json.dumps(audit))))
    if leftover:
        warnings.append("Still in brackets (fill these before sending): " + ", ".join(leftover))
    if re.search(r"\[(?:N\d{1,3}|brief)\b", json.dumps(audit), re.IGNORECASE):
        problems.append("A note number like [N03] is in the report. Take note numbers out of client-facing text.")
    return problems, warnings


# ---------- the setup map (SVG) ----------

def render_map(the_map, main, accent):
    columns = the_map.get("columns", [])
    links = the_map.get("links", [])
    if not columns:
        return ""
    n = len(columns)
    # Labelled arrows need a wider gap between columns, so their labels fit between the boxes.
    has_labels = any(link.get("label") for link in links)
    width, gap, top = 860, (84 if has_labels else 52), 46
    box_w = (width - gap * (n - 1)) / n
    label_chars = max(10, int((box_w - 24) / 7.0))
    note_chars = max(12, int((box_w - 24) / 6.1))

    boxes, col_heights = {}, []
    for ci, col in enumerate(columns):
        y = 0
        placed = []
        for item in col.get("items", []):
            label_lines = wrap(item.get("label", ""), label_chars)
            note_lines = wrap(item["note"], note_chars) if item.get("note") else []
            h = 14 + 17 * len(label_lines) + (5 + 14.5 * len(note_lines) if note_lines else 0) + 10
            placed.append((item, label_lines, note_lines, y, h))
            y += h + 16
        col_heights.append(max(0, y - 16))
        for item, label_lines, note_lines, iy, h in placed:
            boxes[item["id"]] = {"col": ci, "x": ci * (box_w + gap), "y": iy, "h": h,
                                 "item": item, "label": label_lines, "note": note_lines}
    tallest = max(col_heights) if col_heights else 0
    # Centre each column against the tallest one, so short columns don't hug the top.
    for b in boxes.values():
        b["y"] += top + (tallest - col_heights[b["col"]]) / 2

    # Spread several arrows leaving (or arriving at) one box so they don't overlap.
    outs, ins = {}, {}
    for li, link in enumerate(links):
        outs.setdefault(link["from"], []).append(li)
        ins.setdefault(link["to"], []).append(li)

    def anchor(box_id, li, table):
        group = table.get(box_id, [li])
        k = group.index(li)
        b = boxes[box_id]
        span = b["h"] * 0.5
        offset = 0 if len(group) == 1 else -span / 2 + span * k / (len(group) - 1)
        return b["y"] + b["h"] / 2 + offset

    height = top + tallest + 20
    parts = []
    marker_colours = {NEUTRAL: "n"}
    for key, s in STATUS.items():
        marker_colours[s["colour"]] = key
    defs = "".join(
        f'<marker id="arrow-{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{colour}"/></marker>'
        for colour, name in marker_colours.items())
    parts.append(f"<defs>{defs}</defs>")

    for ci, col in enumerate(columns):
        cx = ci * (box_w + gap) + box_w / 2
        parts.append(f'<text x="{cx:.1f}" y="18" text-anchor="middle" class="map-col">{esc(col.get("title", "").upper())}</text>')
        parts.append(f'<line x1="{ci * (box_w + gap):.1f}" y1="28" x2="{ci * (box_w + gap) + box_w:.1f}" y2="28" stroke="{main}" stroke-width="1"/>')

    label_layer = []
    placed_labels = {}  # gap centre x -> [(top, bottom)], so labels in one gap never sit on each other

    def point_at_x(p0, p1, p2, p3, target_x):
        # Find where a curve crosses target_x (curves here always run one way across).
        lo, hi = 0.0, 1.0
        for _ in range(40):
            t = (lo + hi) / 2
            x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t ** 2 * p2[0] + t ** 3 * p3[0]
            if (x < target_x) == (p0[0] < p3[0]):
                lo = t
            else:
                hi = t
        t = (lo + hi) / 2
        return (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t ** 2 * p2[1] + t ** 3 * p3[1]

    for li, link in enumerate(links):
        a, b = boxes[link["from"]], boxes[link["to"]]
        st = status_key(link.get("status"))
        colour = STATUS[st]["colour"] if st else NEUTRAL
        marker = marker_colours[colour]
        y1, y2 = anchor(link["from"], li, outs), anchor(link["to"], li, ins)
        if b["col"] > a["col"]:
            x1, x2 = a["x"] + box_w, b["x"] - 2
            dx = (x2 - x1) * 0.5
            d = f"M{x1:.1f},{y1:.1f} C{x1 + dx:.1f},{y1:.1f} {x2 - dx:.1f},{y2:.1f} {x2:.1f},{y2:.1f}"
            mx = a["x"] + box_w + gap / 2
            my = point_at_x((x1, y1), (x1 + dx, y1), (x2 - dx, y2), (x2, y2), mx)
        elif b["col"] < a["col"]:
            x1, x2 = a["x"], b["x"] + box_w + 2
            dx = (x1 - x2) * 0.5
            d = f"M{x1:.1f},{y1:.1f} C{x1 - dx:.1f},{y1:.1f} {x2 + dx:.1f},{y2:.1f} {x2:.1f},{y2:.1f}"
            mx = a["x"] - gap / 2
            my = point_at_x((x1, y1), (x1 - dx, y1), (x2 + dx, y2), (x2, y2), mx)
        else:
            x = a["x"] + box_w
            bend = x + gap * 0.45
            d = f"M{x:.1f},{y1:.1f} C{bend:.1f},{y1:.1f} {bend:.1f},{y2:.1f} {x + 2:.1f},{y2:.1f}"
            mx, my = bend - 6, (y1 + y2) / 2
        dash = ' stroke-dasharray="5 4"' if link.get("dashed") else ""
        parts.append(f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{2.2 if st else 1.6}"{dash} marker-end="url(#arrow-{marker})"/>')
        if link.get("label"):
            per_line = max(6, int((gap - 14) / 5.6))
            lines = wrap(str(link["label"]), per_line)
            if len(lines) > 2:
                lines = lines[:2]
                lines[1] = lines[1][:per_line - 1] + "…"
            w = min(gap - 4, max(len(l) for l in lines) * 5.6 + 12)
            h = 7 + 11.5 * len(lines)
            top_y = my - h / 2
            taken = placed_labels.setdefault(round(mx), [])
            moved = True
            while moved:
                moved = False
                for t0, t1 in taken:
                    if top_y < t1 + 3 and top_y + h > t0 - 3:
                        top_y = t1 + 3
                        moved = True
            taken.append((top_y, top_y + h))
            height = max(height, top_y + h + 10)
            text = "".join(f'<tspan x="{mx:.1f}" y="{top_y + 12 + 11.5 * k:.1f}">{esc(l)}</tspan>' for k, l in enumerate(lines))
            label_layer.append(
                f'<rect x="{mx - w / 2:.1f}" y="{top_y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="7" fill="#FFFFFF" stroke="{colour}" stroke-width="1"/>'
                f'<text text-anchor="middle" class="map-link" fill="{colour}">{text}</text>')

    for b in boxes.values():
        st = status_key(b["item"].get("status"))
        stripe = STATUS[st]["colour"] if st else mix(main, "#FFFFFF", 0.35)
        x, y, h = b["x"], b["y"], b["h"]
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{box_w:.1f}" height="{h:.1f}" rx="5" fill="#FFFFFF" stroke="#DCD9D2"/>')
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="4" height="{h:.1f}" rx="2" fill="{stripe}"/>')
        ty = y + 14 + 12
        for line in b["label"]:
            parts.append(f'<text x="{x + 16:.1f}" y="{ty:.1f}" class="map-label">{esc(line)}</text>')
            ty += 17
        if b["note"]:
            ty += 3
            for line in b["note"]:
                parts.append(f'<text x="{x + 16:.1f}" y="{ty:.1f}" class="map-note">{esc(line)}</text>')
                ty += 14.5
    parts.extend(label_layer)

    used = {status_key(i.get("status")) for c in columns for i in c.get("items", [])}
    used |= {status_key(l.get("status")) for l in links}
    legend = "".join(
        f'<span class="legend-item"><i style="background:{s["colour"]}"></i>{esc(s["label"])}</span>'
        for k, s in STATUS.items() if k in used)
    svg = (f'<svg viewBox="0 0 {width} {height:.0f}" role="img" aria-label="Map of how the setup fits together" '
           f'xmlns="http://www.w3.org/2000/svg">{"".join(parts)}</svg>')
    return f'<div class="map-wrap">{svg}</div>' + (f'<div class="legend">{legend}</div>' if legend else "")


# ---------- the page ----------

# A serif for headings and numbers, a clean sans for reading. Both are free
# Google Fonts; the fallbacks keep it looking right offline.
FONTS_URL = ("https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..700;"
             "1,6..72,300..600&family=Instrument+Sans:wght@400..700&display=swap")
# Status colours dark enough to read as text on white.
STATUS_TEXT = {"fix-first": "#A63A25", "tidy-up": "#8A5A06", "working": "#25683F"}


def contours(seed, width, height, line_colour, accent):
    """Topographic rings for the cover. Seeded by the client's name, so every
    client gets their own pattern, and the same one every rebuild."""
    rnd = random.Random(seed)
    big = max(width, height)
    centres = [
        (width * rnd.uniform(0.66, 0.92), height * rnd.uniform(0.58, 0.86), big * rnd.uniform(0.58, 0.78), 17),
        (width * rnd.uniform(0.04, 0.26), height * rnd.uniform(0.04, 0.22), big * rnd.uniform(0.22, 0.34), 8),
    ]
    paths = []
    for ci, (cx, cy, rmax, rings) in enumerate(centres):
        p1, p2, p3 = (rnd.uniform(0, 2 * math.pi) for _ in range(3))
        for k in range(1, rings + 1):
            r = rmax * k / rings
            pts = []
            for i in range(145):
                t = 2 * math.pi * i / 144
                wobble = (1 + 0.07 * math.sin(3 * t + p1 + k * 0.35) + 0.045 * math.sin(5 * t + p2 - k * 0.2)
                          + 0.03 * math.sin(2 * t + p3))
                pts.append(f"{cx + r * wobble * math.cos(t):.1f},{cy + r * wobble * math.sin(t) * 0.84:.1f}")
            highlight = ci == 0 and k == rings - 4
            colour, opacity, stroke = (accent, 0.7, 1.6) if highlight else (line_colour, 0.14 if ci == 0 else 0.1, 1)
            paths.append(f'<path d="M{" L".join(pts)} Z" fill="none" stroke="{colour}" '
                         f'stroke-opacity="{opacity}" stroke-width="{stroke}"/>')
    return (f'<svg class="contours" viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid slice" '
            f'aria-hidden="true" xmlns="http://www.w3.org/2000/svg">{"".join(paths)}</svg>')


def section(number, title, body, extra_class="", index=0):
    return (f'<section class="block {extra_class}" style="--i:{index}"><header class="sec-head">'
            f'<span class="sec-num">{number:02d}</span><h2>{esc(title)}</h2></header>'
            f'<div class="sec-body">{body}</div></section>')


def paragraphs(items, lead=False):
    items = as_list(items)
    return "".join(f'<p{" class=lead" if lead and i == 0 else ""}>{esc(p)}</p>' for i, p in enumerate(items))


def bullet_list(items, cls="list"):
    items = as_list(items)
    if not items:
        return ""
    return f'<ul class="{cls}">' + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"


def tick_icon():
    return ('<svg class="tick" viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="9.2" fill="none" '
            f'stroke="{STATUS_TEXT["working"]}" stroke-width="1.2"/><path d="M6 10.4l2.7 2.7L14.2 7.4" fill="none" '
            f'stroke="{STATUS_TEXT["working"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def css_string(text):
    """Text for a CSS content: "..." value (used in the PDF page footer)."""
    return '"' + str(text).replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_html(audit, base):
    kind = audit["audit_type"]
    style = audit.get("style") or {}
    consultant = audit.get("consultant") or {}
    client = audit.get("client") or {}
    main = "#" + style.get("main_colour", "#1F3A5F").strip().lstrip("#")
    accent = "#" + style.get("accent_colour", "#C9A24B").strip().lstrip("#")
    main_ink = ink_on(main)
    accent_ink = ink_on(accent)
    accent_text = readable_on_white(accent)
    main_text = readable_on_white(main)
    tint = mix(main, "#FFFFFF", 0.94)
    # On the cover, the accent sits on the main colour, so make sure it reads.
    eyebrow = accent if contrast(accent, main) >= 3 else main_ink
    src, logo_warning = logo_src(style.get("logo"), base)

    audit_name = audit.get("audit_name") or ("AI Setup Audit" if kind == "setup" else "AI Opportunity Audit")
    date = audit.get("date") or datetime.date.today().strftime("%d/%m/%Y")
    business = client["business"]
    seed = f'{business}|{audit_name}'
    cover_line = audit.get("cover_line") or (
        "An honest look at your setup: what's working, what isn't, and what to fix first." if kind == "setup"
        else "Where AI, or a simpler fix, will save you time first, and what to leave alone.")

    logo_html = (f'<div class="logo-chip"><img src="{esc(src)}" alt="{esc(consultant.get("business", ""))}"></div>'
                 if src else f'<div class="wordmark">{esc(consultant.get("business", ""))}</div>')
    prepared_for = client.get("name") or business
    out = []

    # ----- Cover -----
    out.append(
        f'<section class="cover">{contours(seed, 1050, 1485, main_ink, accent)}<div class="cover-inner">'
        f'<div class="cover-top">{logo_html}<div class="confidential">Confidential</div></div>'
        f'<div class="cover-main"><div class="eyebrow" style="color:{eyebrow}">{esc(audit_name)}</div>'
        f'<h1>{esc(business)}</h1><p class="cover-line">{esc(cover_line)}</p></div>'
        f'<div class="cover-meta"><div><span>Prepared for</span><b>{esc(prepared_for)}</b></div>'
        f'<div><span>Prepared by</span><b>{esc(consultant["name"])}</b><i>{esc(consultant["business"])}</i></div>'
        f'<div><span>Date</span><b>{esc(date)}</b></div></div></div></section>')

    # ----- The short version -----
    number = audit.get("the_number") or {}
    stat = ""
    if number.get("now"):
        value_class = "stat-value long" if len(str(number["now"])) > 12 else "stat-value"
        stat = (f'<div class="stat"><div class="label">{esc(number.get("label", "The number we will track"))}</div>'
                f'<div class="{value_class}">{esc(number["now"])}</div>'
                + (f'<div class="stat-target"><span>Aiming for</span> {esc(number["target"])}</div>' if number.get("target") else "")
                + (f'<p class="stat-note">{esc(number["note"])}</p>' if number.get("note") else "") + "</div>")
    glance = ""
    if audit.get("health_check"):
        rows = "".join(
            f'<li><i style="background:{STATUS[status_key(h["status"])]["colour"]}"></i><span>{esc(h.get("area", ""))}</span>'
            f'<em style="color:{STATUS_TEXT[status_key(h["status"])]}">{esc(STATUS[status_key(h["status"])]["label"])}</em></li>'
            for h in audit["health_check"])
        glance = f'<div class="glance"><div class="label">Your health check at a glance</div><ul>{rows}</ul></div>'
    elif as_list(audit.get("whats_working")):
        glance = (f'<div class="glance"><div class="label">Already working in your favour</div>'
                  f'<ul class="glance-working">{"".join(f"<li>{tick_icon()}<span>{esc(w)}</span></li>" for w in as_list(audit["whats_working"])[:3])}</ul></div>')
    top = audit["priorities"][:3]
    start = ("<div class=\"start\"><div class=\"label\">Start here</div><ol>"
             + "".join(f'<li><span class="n">{i}</span><span>{esc(p.get("title", ""))}</span></li>' for i, p in enumerate(top, 1))
             + "</ol></div>")
    out.append(f'<section class="summary" style="--i:1"><div class="kicker">The short version</div>'
               f'<p class="headline">{esc(audit["headline"])}</p>'
               f'<div class="summary-grid">{stat}{glance}</div>{start}</section>')

    n, i = 0, 2

    # ----- 01 Where things are now -----
    n += 1
    working = as_list(audit.get("whats_working"))
    working_html = ""
    if working:
        working_html = ('<div class="working"><div class="label">What\'s already working</div><ul>'
                        + "".join(f"<li>{tick_icon()}<span>{esc(w)}</span></li>" for w in working) + "</ul></div>")
    out.append(section(n, "Where things are now", paragraphs(audit.get("where_things_are_now"), lead=True) + working_html, "chapter", index=i))
    i += 1

    # ----- The map -----
    if audit.get("map"):
        n += 1
        title = audit["map"].get("title") or ("How your setup fits together" if kind == "setup" else "How the work happens now")
        caption = " ".join(as_list(audit["map"].get("intro"))) or "Each box is one part of the picture. The coloured edge shows what needs work."
        figure = (f'<figure class="figure">{render_map(audit["map"], main, accent)}'
                  f'<figcaption><span>Figure 1</span>{esc(caption)}</figcaption></figure>')
        # A big map gets its own page in print; a small one flows on from the section before.
        boxes = sum(len(c.get("items", [])) for c in audit["map"].get("columns", []))
        out.append(section(n, title, figure, "keep-together chapter" if boxes >= 10 else "keep-together", index=i))
        i += 1

    # ----- Health check -----
    if audit.get("health_check"):
        n += 1
        counts = {k: sum(1 for h in audit["health_check"] if status_key(h["status"]) == k) for k in STATUS}
        summary = " · ".join(f'<span style="color:{STATUS_TEXT[k]}"><b>{counts[k]}</b> {esc(STATUS[k]["label"].lower())}</span>'
                             for k in STATUS if counts[k])
        rows = []
        for h in audit["health_check"]:
            key = status_key(h["status"])
            detail = ""
            if h.get("evidence"):
                detail += f'<div class="hc-line"><span>What I saw</span><p>{esc(h["evidence"])}</p></div>'
            if h.get("fix"):
                detail += f'<div class="hc-line"><span>The fix</span><p>{esc(h["fix"])}</p></div>'
            rows.append(f'<div class="hc-row"><div class="hc-left"><div class="hc-status" style="color:{STATUS_TEXT[key]}">'
                        f'<i style="background:{STATUS[key]["colour"]}"></i>{esc(STATUS[key]["label"])}</div>'
                        f'<h3>{esc(h.get("area", ""))}</h3></div><div class="hc-right"><p class="hc-finding">{esc(h.get("finding", ""))}</p>'
                        f'{detail}</div></div>')
        intro = paragraphs(audit.get("health_check_intro"))
        out.append(section(n, "The health check", intro + f'<p class="counts">{summary}</p><div class="hc">{"".join(rows)}</div>', "chapter", index=i))
        i += 1

    # ----- Ranked priorities -----
    n += 1
    entries = []
    for k, p in enumerate(audit["priorities"], 1):
        spec = "".join(f'<div><span>{esc(label)}</span><b>{esc(p[key])}</b></div>'
                       for key, label in (("saves", "What it saves"), ("effort", "Effort"), ("timeline", "Time to do")) if p.get(key))
        uses = (f'<p class="pr-uses"><span>Uses what you\'ve got:</span> {esc(p["uses_what_you_have"])}</p>'
                if p.get("uses_what_you_have") else "")
        entries.append(f'<div class="pr"><div class="pr-num">{k}</div><div class="pr-body"><h3>{esc(p.get("title", ""))}</h3>'
                       f'<p>{esc(p.get("what", ""))}</p>{"<div class=pr-spec>" + spec + "</div>" if spec else ""}{uses}</div></div>')
    title = "Your top fixes, ranked" if kind == "setup" else "Your top opportunities, ranked"
    # Setup audits start the fixes on a fresh page after the long health check; business audits flow on.
    out.append(section(n, title, paragraphs(audit.get("priorities_intro")) + "".join(entries),
                       "chapter" if kind == "setup" else "", index=i))
    i += 1

    # ----- Leave alone + careful with -----
    leave, careful = as_list(audit.get("leave_alone")), as_list(audit.get("careful_with"))
    if leave or careful:
        n += 1
        body = '<div class="two">'
        if leave:
            body += f'<div><div class="label">Leave alone, for now</div>{bullet_list(leave, "rule-list")}</div>'
        if careful:
            body += f'<div><div class="label">Be careful with</div>{bullet_list(careful, "rule-list")}</div>'
        out.append(section(n, "What I'd leave alone, and why", body + "</div>", index=i))
        i += 1

    # ----- Roadmap -----
    n += 1
    road = audit.get("roadmap") or {}
    lanes = "".join(f'<div class="tl-col tl-{k}"><div class="tl-node"></div><div class="tl-label">{esc(label)}</div>'
                    f'{bullet_list(road.get(k), "tl-list")}</div>'
                    for k, label in (("now", "Now"), ("next", "Next"), ("later", "Later")) if as_list(road.get(k)))
    out.append(section(n, "Your roadmap", paragraphs(road.get("intro")) + f'<div class="tl">{lanes}</div>', "keep-together", index=i))
    i += 1

    # ----- The numbers -----
    roi = audit.get("roi") or {}
    if roi.get("problem"):
        n += 1
        rows = [(roi.get("problem_label", "The problem, in a number"), roi.get("problem")),
                (roi.get("cost_label", "What that costs a year"), roi.get("cost_a_year")),
                (roi.get("frees_label", "What fixing it frees up"), roi.get("frees_up"))]
        stats = "".join(f'<div class="roi-stat"><div class="label">{esc(label)}</div>'
                        f'<div class="roi-value{" long" if len(str(value)) > 14 else ""}">{esc(value)}</div></div>'
                        for label, value in rows if value)
        maths = f'<p class="maths">{esc(roi["maths"])}</p>' if roi.get("maths") else ""
        out.append(section(n, roi.get("title", "The numbers, on one page"), f'<div class="roi">{stats}</div>{maths}', "keep-together", index=i))
        i += 1

    # ----- Next step -----
    step = audit.get("next_step") or {}
    button = ""
    if step.get("link"):
        link = step["link"] if re.match(r"^(https?:|mailto:)", step["link"]) else "https://" + step["link"]
        button = (f'<a class="button" href="{esc(link)}" style="background:{accent};color:{accent_ink}">{esc(step.get("button", "Book a time"))}</a>'
                  f'<span class="print-link">{esc(step["link"])}</span>')
    out.append(f'<section class="next" style="--i:{i}">{contours(seed + "|next", 1200, 520, main_ink, accent)}'
               f'<div class="next-inner"><div class="kicker" style="color:{eyebrow}">Your next step</div>'
               f'<h2>{esc(step.get("heading", ""))}</h2>{paragraphs(step.get("detail"))}{button}</div></section>')

    # ----- Colophon -----
    contact = "".join(f"<p>{esc(v)}</p>" for v in (consultant.get("email"), consultant.get("website")) if v)
    assumptions = as_list(audit.get("assumptions"))
    notes = ('<div class="notes"><div class="label">Notes on the numbers</div>' + "".join(f"<p>{esc(a)}</p>" for a in assumptions) + "</div>"
             if assumptions else "")
    out.append(f'<footer class="colophon"><div class="sign"><div class="label">Prepared by</div>'
               f'<p class="sign-name">{esc(consultant["name"])}</p><p>{esc(consultant["business"])}</p>'
               f'{contact}</div>{notes}</footer>')

    footer_text = css_string(f'{consultant["business"]}  ·  {audit_name}  ·  {business}')
    css = CSS.format(main=main, accent=accent, accent_text=accent_text, main_text=main_text, tint=tint,
                     main_ink=main_ink, accent_ink=accent_ink, page_bg=mix("#F3F1EC", main, 0.05),
                     hair=mix("#E4E1DA", main, 0.06), footer_text=footer_text)
    title = f"{audit_name}: {business}"
    page = (f'<!doctype html><html lang="en-AU"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title>'
            f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link rel="stylesheet" href="{FONTS_URL}"><style>{css}</style></head><body>'
            f'<main class="doc">{"".join(out)}</main>'
            f'<div class="toolbar"><span>Untick "Headers and footers" in the print window.</span>'
            f'<button type="button" onclick="window.print()">Save as PDF</button></div></body></html>')
    return page, logo_warning


CSS = """
:root {{ --main: {main}; --accent: {accent}; --accent-text: {accent_text}; --main-text: {main_text}; --tint: {tint};
  --main-ink: {main_ink}; --ink: #17191E; --muted: #5C616B; --hair: {hair};
  --serif: "Newsreader", "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  --sans: "Instrument Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }}
* {{ box-sizing: border-box; }}
html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ margin: 0; background: {page_bg}; color: var(--ink); font: 16px/1.65 var(--sans); padding: 0 16px; }}
h1, h2, h3 {{ font-family: var(--serif); font-weight: 400; color: var(--ink); margin: 0; }}
p {{ margin: 0 0 12px; }}
.label {{ font: 600 11px/1.3 var(--sans); letter-spacing: .16em; text-transform: uppercase; color: var(--muted); margin-bottom: 12px; }}
.kicker {{ font: 600 11.5px/1.3 var(--sans); letter-spacing: .2em; text-transform: uppercase; color: var(--accent-text); margin-bottom: 14px; }}

.doc {{ max-width: 920px; margin: 40px auto 96px; background: #fff; box-shadow: 0 1px 2px rgba(20,20,20,.05), 0 24px 60px rgba(20,20,20,.08); }}

/* Cover */
.cover {{ position: relative; overflow: hidden; background: var(--main); color: var(--main-ink); min-height: 660px; display: flex; }}
.contours {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
.cover-inner {{ position: relative; display: flex; flex-direction: column; justify-content: space-between; gap: 48px; padding: 44px 56px 48px; width: 100%; }}
.cover-top {{ display: flex; justify-content: space-between; align-items: center; gap: 16px; }}
.logo-chip {{ background: #fff; border-radius: 10px; padding: 10px 14px; display: inline-flex; box-shadow: 0 6px 18px rgba(0,0,0,.12); }}
.logo-chip img {{ max-height: 44px; max-width: 190px; display: block; }}
.wordmark {{ font: 500 22px/1.2 var(--serif); }}
.confidential {{ font: 600 10.5px/1 var(--sans); letter-spacing: .22em; text-transform: uppercase; opacity: .75; border: 1px solid currentColor; border-radius: 999px; padding: 7px 12px; }}
.cover-main {{ margin-top: auto; }}
.eyebrow {{ font: 600 12px/1.3 var(--sans); letter-spacing: .24em; text-transform: uppercase; margin-bottom: 18px; }}
.cover h1 {{ color: var(--main-ink); font-size: clamp(44px, 7vw, 72px); line-height: 1.02; letter-spacing: -.02em; font-weight: 400; max-width: 12ch; }}
.cover-line {{ font: italic 300 21px/1.45 var(--serif); opacity: .88; max-width: 34ch; margin: 22px 0 0; }}
.cover-meta {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; border-top: 1px solid currentColor; padding-top: 18px; }}
.cover-meta span {{ display: block; font: 600 10px/1.3 var(--sans); letter-spacing: .18em; text-transform: uppercase; opacity: .7; margin-bottom: 6px; }}
.cover-meta b {{ display: block; font: 500 17px/1.3 var(--serif); }}
.cover-meta i {{ display: block; font: italic 300 14px/1.4 var(--serif); opacity: .8; }}

/* The short version */
.summary {{ padding: 64px 64px 56px; border-bottom: 1px solid var(--hair); }}
.headline {{ font: 400 31px/1.3 var(--serif); letter-spacing: -.01em; margin: 0 0 40px; max-width: 30ch; position: relative; }}
.headline::before {{ content: "\\201C"; position: absolute; left: -.55em; top: -.12em; color: var(--accent); font-size: 1.6em; line-height: 1; }}
.summary-grid {{ display: grid; grid-template-columns: minmax(220px, 300px) 1fr; gap: 48px; align-items: start; }}
.stat {{ border-top: 2px solid var(--main); padding-top: 16px; }}
.stat-value {{ font: 400 46px/1.05 var(--serif); color: var(--main-text); letter-spacing: -.02em; margin: 2px 0 12px; }}
.stat-value.long {{ font-size: 34px; }}
.stat-target {{ font: 500 15px/1.4 var(--sans); }}
.stat-target span {{ color: var(--muted); font-weight: 400; }}
.stat-note {{ font: italic 400 15px/1.5 var(--serif); color: var(--muted); margin-top: 8px; }}
.glance {{ border-top: 1px solid var(--hair); padding-top: 16px; }}
.glance ul {{ list-style: none; margin: 0; padding: 0; }}
.glance li {{ display: grid; grid-template-columns: 10px 1fr auto; align-items: center; gap: 12px; padding: 7px 0; border-bottom: 1px solid var(--hair); font-size: 14.5px; }}
.glance li:last-child {{ border-bottom: 0; }}
.glance li i {{ width: 8px; height: 8px; border-radius: 50%; display: block; }}
.glance li em {{ font: 600 10.5px/1 var(--sans); letter-spacing: .12em; text-transform: uppercase; font-style: normal; }}
.glance-working li {{ grid-template-columns: 20px 1fr; align-items: start; }}
.start {{ margin-top: 44px; }}
.start ol {{ list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; border-top: 1px solid var(--hair); }}
.start li {{ padding: 18px 20px 4px 0; display: flex; gap: 14px; align-items: baseline; font: 500 16px/1.35 var(--sans); }}
.start li + li {{ padding-left: 20px; border-left: 1px solid var(--hair); }}
.start .n {{ font: 300 34px/1 var(--serif); color: var(--accent-text); }}

/* Sections */
.block {{ padding: 56px 64px; border-bottom: 1px solid var(--hair); }}
.sec-head {{ display: grid; grid-template-columns: 56px 1fr; align-items: baseline; margin-bottom: 26px; }}
.sec-num {{ font: italic 300 22px/1 var(--serif); color: var(--accent-text); }}
.sec-head h2 {{ font-size: 34px; line-height: 1.15; letter-spacing: -.015em; }}
.sec-body {{ margin-left: 56px; }}
.sec-body > p {{ max-width: 66ch; }}
.lead {{ font: 400 21px/1.5 var(--serif); color: var(--ink); max-width: 40ch !important; }}
.working {{ margin-top: 30px; background: var(--tint); padding: 24px 26px 14px; }}
.working ul {{ list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 6px 28px; }}
.working li, .glance-working li {{ display: grid; grid-template-columns: 20px 1fr; gap: 10px; font-size: 15px; margin-bottom: 10px; }}
.tick {{ width: 18px; height: 18px; margin-top: 3px; }}

/* Map */
.figure {{ margin: 0; background: #FBFAF8; border: 1px solid var(--hair); padding: 26px 24px 18px; }}
.map-wrap {{ overflow-x: auto; }}
.map-wrap svg {{ width: 100%; min-width: 640px; height: auto; display: block; }}
.map-col {{ font: 600 11px var(--sans); letter-spacing: .14em; fill: var(--muted); }}
.map-label {{ font: 600 13px var(--sans); fill: var(--ink); }}
.map-note {{ font: 400 11.5px var(--sans); fill: var(--muted); }}
.map-link {{ font: 700 9.5px var(--sans); }}
.legend {{ display: flex; gap: 20px; flex-wrap: wrap; font-size: 12.5px; color: var(--muted); margin-top: 12px; }}
.legend-item {{ display: inline-flex; align-items: center; gap: 8px; }}
.legend-item i {{ width: 14px; height: 4px; border-radius: 2px; display: inline-block; }}
figcaption {{ font: italic 400 14.5px/1.5 var(--serif); color: var(--muted); margin-top: 12px; }}
figcaption span {{ font: 600 10.5px/1 var(--sans); letter-spacing: .16em; text-transform: uppercase; font-style: normal; color: var(--ink); margin-right: 10px; }}

/* Health check */
.counts {{ font-size: 14.5px; margin-bottom: 18px; }}
.hc {{ border-top: 1px solid var(--ink); }}
.hc-row {{ display: grid; grid-template-columns: 32% 1fr; gap: 28px; padding: 22px 0; border-bottom: 1px solid var(--hair); break-inside: avoid; page-break-inside: avoid; }}
.hc-status {{ font: 600 10.5px/1 var(--sans); letter-spacing: .14em; text-transform: uppercase; display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }}
.hc-status i {{ width: 9px; height: 9px; border-radius: 50%; display: block; }}
.hc-left h3 {{ font-size: 23px; line-height: 1.2; }}
.hc-finding {{ font-weight: 600; font-size: 16px; margin-bottom: 12px; }}
.hc-line {{ display: grid; grid-template-columns: 92px 1fr; gap: 14px; font-size: 14.5px; }}
.hc-line span {{ font: 600 10px/2.1 var(--sans); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); }}
.hc-line p {{ margin-bottom: 6px; }}

/* Priorities */
.pr {{ display: grid; grid-template-columns: 64px 1fr; gap: 8px; padding: 26px 0; border-top: 1px solid var(--hair); break-inside: avoid; page-break-inside: avoid; }}
.pr:first-of-type {{ border-top: 1px solid var(--ink); }}
.pr-num {{ font: 300 54px/.9 var(--serif); color: var(--accent-text); }}
.pr-body h3 {{ font-size: 24px; line-height: 1.2; margin-bottom: 8px; }}
.pr-body > p {{ max-width: 62ch; }}
.pr-spec {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin: 14px 0 6px; padding-top: 12px; border-top: 1px dashed var(--hair); }}
.pr-spec span {{ display: block; font: 600 10px/1.3 var(--sans); letter-spacing: .14em; text-transform: uppercase; color: var(--muted); margin-bottom: 4px; }}
.pr-spec b {{ font: 500 15px/1.35 var(--sans); }}
.pr-uses {{ font: italic 400 15px/1.5 var(--serif); color: var(--muted); margin: 10px 0 0; }}
.pr-uses span {{ font: 600 10px/1 var(--sans); letter-spacing: .14em; text-transform: uppercase; font-style: normal; color: var(--ink); margin-right: 6px; }}

/* Leave alone */
.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 40px; }}
.rule-list {{ list-style: none; margin: 0; padding: 0; border-top: 1px solid var(--ink); }}
.rule-list li {{ padding: 14px 0; border-bottom: 1px solid var(--hair); font-size: 15px; }}

/* Roadmap */
.tl {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 0; position: relative; margin-top: 8px; }}
.tl::before {{ content: ""; position: absolute; left: 0; right: 0; top: 7px; border-top: 1px solid var(--hair); }}
.tl-col {{ position: relative; padding-right: 24px; }}
.tl-node {{ width: 15px; height: 15px; border-radius: 50%; border: 1.5px solid var(--main); background: #fff; position: relative; }}
.tl-now .tl-node {{ background: var(--main); }}
.tl-next .tl-node {{ background: var(--accent); border-color: var(--accent); }}
.tl-label {{ font: 600 11px/1 var(--sans); letter-spacing: .2em; text-transform: uppercase; margin: 16px 0 10px; color: var(--main-text); }}
.tl-list {{ list-style: none; margin: 0; padding: 0; }}
.tl-list li {{ font-size: 15px; padding: 8px 0; border-bottom: 1px solid var(--hair); }}

/* Numbers */
.roi {{ display: grid; grid-template-columns: repeat(3, 1fr); border-top: 1px solid var(--ink); border-bottom: 1px solid var(--hair); }}
.roi-stat {{ padding: 22px 22px 22px 0; }}
.roi-stat + .roi-stat {{ padding-left: 22px; border-left: 1px solid var(--hair); }}
.roi-value {{ font: 400 40px/1.1 var(--serif); color: var(--main-text); letter-spacing: -.02em; }}
.roi-value.long {{ font-size: 28px; }}
.maths {{ font: italic 400 15px/1.5 var(--serif); color: var(--muted); margin-top: 16px; }}

/* Next step */
.next {{ position: relative; overflow: hidden; background: var(--main); color: var(--main-ink); break-inside: avoid; page-break-inside: avoid; }}
.next-inner {{ position: relative; padding: 60px 64px; }}
.next h2 {{ color: var(--main-ink); font-size: 40px; line-height: 1.1; letter-spacing: -.015em; margin-bottom: 14px; max-width: 18ch; }}
.next p {{ max-width: 52ch; opacity: .92; }}
.button {{ display: inline-block; margin-top: 12px; padding: 14px 28px; border-radius: 999px; font: 600 15px/1 var(--sans); text-decoration: none; letter-spacing: .01em; }}
.print-link {{ display: none; }}

/* Colophon */
.colophon {{ display: grid; grid-template-columns: 1fr 1.4fr; gap: 40px; padding: 44px 64px 52px; font-size: 14px; color: var(--muted); }}
.colophon p {{ margin: 0 0 4px; }}
.sign-name {{ font: 500 20px/1.3 var(--serif); color: var(--ink); }}
.notes p {{ font-size: 13px; }}

/* Floating save button (screen only) */
.toolbar {{ position: fixed; right: 20px; bottom: 20px; display: flex; align-items: center; gap: 12px; background: #fff; border: 1px solid var(--hair);
  border-radius: 999px; padding: 6px 6px 6px 16px; box-shadow: 0 10px 30px rgba(0,0,0,.12); font-size: 12.5px; color: var(--muted); }}
.toolbar button {{ font: 600 13.5px/1 var(--sans); border: 0; border-radius: 999px; padding: 11px 18px; cursor: pointer; background: var(--main); color: var(--main-ink); }}

@media (prefers-reduced-motion: no-preference) {{
  .summary, .block, .next {{ animation: rise .7s cubic-bezier(.2,.7,.2,1) both; animation-delay: calc(var(--i, 0) * 70ms); }}
  @keyframes rise {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
}}

@media (max-width: 720px) {{
  body {{ padding: 0; }}
  .doc {{ margin: 0 0 80px; }}
  .cover-inner, .summary, .block, .next-inner, .colophon {{ padding-left: 22px; padding-right: 22px; }}
  .cover {{ min-height: 560px; }}
  .cover-meta, .summary-grid, .start ol, .working ul, .two, .tl, .roi, .colophon, .hc-row, .pr-spec {{ grid-template-columns: 1fr; }}
  .start li + li, .roi-stat + .roi-stat {{ border-left: 0; padding-left: 0; }}
  .sec-head {{ grid-template-columns: 1fr; gap: 6px; }}
  .sec-body {{ margin-left: 0; }}
  .headline {{ font-size: 25px; }}
  .headline::before {{ position: static; display: block; margin-bottom: -10px; }}
  .tl::before {{ display: none; }}
  .toolbar span {{ display: none; }}
}}

@page {{ size: A4; margin: 17mm 15mm 19mm;
  @bottom-left {{ content: {footer_text}; font: 7.5pt "Instrument Sans", Helvetica, Arial, sans-serif; color: #8A8F98; letter-spacing: .04em; }}
  @bottom-right {{ content: counter(page); font: 7.5pt "Instrument Sans", Helvetica, Arial, sans-serif; color: #8A8F98; }} }}
@page :first {{ margin: 0; @bottom-left {{ content: none; }} @bottom-right {{ content: none; }} }}
@media print {{
  body {{ background: #fff; padding: 0; font-size: 10.2pt; }}
  .toolbar {{ display: none; }}
  .doc {{ max-width: none; margin: 0; box-shadow: none; }}
  .summary, .block, .next {{ animation: none !important; }}
  .cover {{ width: 210mm; height: 297mm; min-height: 0; break-after: page; page-break-after: always; }}
  .cover-inner {{ padding: 20mm 18mm 18mm; }}
  .cover h1 {{ font-size: 50pt; }}
  .summary {{ padding: 4mm 2mm 10mm; border-bottom: 0; }}
  .headline {{ font-size: 21pt; margin-left: 6mm; }}
  .block {{ padding: 9mm 2mm; }}
  .sec-head h2 {{ font-size: 21pt; }}
  .keep-together {{ break-inside: avoid; page-break-inside: avoid; }}
  .chapter {{ break-before: page; page-break-before: always; }}
  .sec-head {{ margin-bottom: 5mm; }}
  .hc-row {{ padding: 3.4mm 0; gap: 6mm; }}
  .hc-left h3 {{ font-size: 15.5pt; }}
  .hc-status {{ margin-bottom: 2mm; }}
  .hc-finding {{ font-size: 10.6pt; margin-bottom: 1.6mm; }}
  .hc-line {{ font-size: 9.6pt; }}
  .hc-line p {{ margin-bottom: 1mm; }}
  .pr {{ padding: 5mm 0; }}
  .pr-num {{ font-size: 38pt; }}
  .pr-body h3 {{ font-size: 16pt; }}
  .tl-list li, .rule-list li {{ font-size: 9.8pt; padding: 2.2mm 0; }}
  .roi-value {{ font-size: 26pt; }}
  .roi-value.long {{ font-size: 19pt; }}
  .sec-head {{ break-after: avoid; page-break-after: avoid; }}
  .map-wrap {{ overflow: visible; }}
  .map-wrap svg {{ min-width: 0; }}
  .next {{ margin-top: 4mm; }}
  .next-inner {{ padding: 9mm 11mm; }}
  .next h2 {{ font-size: 21pt; }}
  .next p {{ font-size: 10pt; }}
  .print-link {{ display: block; margin-top: 10px; font-size: 9pt; opacity: .85; }}
  .colophon {{ padding: 8mm 2mm 0; }}
  a {{ color: inherit; }}
}}
"""


# ---------- PDF ----------

def find_browser():
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for c in candidates:
        if pathlib.Path(c).exists():
            return c
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "microsoft-edge", "msedge", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    return None


def make_pdf(html_path, pdf_path):
    browser = find_browser()
    if not browser:
        return False, "No Chrome, Edge, Brave or Chromium found, so no PDF this time. Open the report and click Save as PDF instead."
    # The virtual time budget gives the web fonts a moment to load before printing.
    cmd = [browser, "--headless=new", "--disable-gpu", "--no-first-run", "--no-pdf-header-footer",
           "--print-to-pdf-no-header", "--run-all-compositor-stages-before-draw", "--virtual-time-budget=10000",
           f"--print-to-pdf={pdf_path}", html_path.resolve().as_uri()]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=90)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as err:
        return False, f"The browser couldn't make the PDF ({type(err).__name__}). Open the report and click Save as PDF instead."
    if not pdf_path.exists() or pdf_path.stat().st_size < 1000:
        return False, "The PDF came out empty. Open the report and click Save as PDF instead."
    return True, str(pdf_path)


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-") or "report"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("audit_json")
    parser.add_argument("--pdf", action="store_true", help="also make a PDF beside the report")
    parser.add_argument("--check", action="store_true", help="only check audit.json")
    args = parser.parse_args()

    source = pathlib.Path(args.audit_json)
    try:
        audit = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"Can't find {source}.")
    except json.JSONDecodeError as err:
        sys.exit(f"{source} isn't valid JSON (line {err.lineno}, column {err.colno}): {err.msg}")

    problems, warnings = check(audit)
    if problems:
        print("NOT BUILT. Fix these in audit.json, then run again:")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    if args.check:
        print("audit.json looks complete.")
        for w in warnings:
            print("Note:", w)
        return

    page, logo_warning = build_html(audit, source.parent)
    report_dir = source.parent / "report"
    report_dir.mkdir(parents=True, exist_ok=True)
    target = report_dir / "index.html"
    if target.exists():
        older = report_dir / "earlier-versions"
        older.mkdir(exist_ok=True)
        k = 1
        while (older / f"index-v{k}.html").exists():
            k += 1
        shutil.move(str(target), str(older / f"index-v{k}.html"))
        print(f"Earlier version kept: {older / f'index-v{k}.html'}")
    target.write_text(page, encoding="utf-8")
    print(f"Report: {target}")

    if args.pdf:
        name = f"{slug(audit['client']['business'])}-{slug(audit.get('audit_name') or audit['audit_type'] + '-audit')}.pdf"
        pdf_path = source.parent / name
        if pdf_path.exists():
            k = 2
            while (source.parent / f"{pdf_path.stem}-v{k}.pdf").exists():
                k += 1
            pdf_path = source.parent / f"{pdf_path.stem}-v{k}.pdf"
        ok, message = make_pdf(target, pdf_path)
        print(("PDF: " if ok else "PDF skipped: ") + message)

    if logo_warning:
        print("Note:", logo_warning)
    for w in warnings:
        print("Note:", w)


if __name__ == "__main__":
    main()
