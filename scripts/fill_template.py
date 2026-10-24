#!/usr/bin/env python3
"""Fill one proposal template with the fill-ins from scope.md, word for word.

Why this exists: the proposal and email templates must keep their exact
wording. This script only swaps [FILL-INS] for values, so nothing else can
drift. It also stops note numbers (like [N03]) or notes meant for the
consultant from leaking into client-facing copy, and it never overwrites a file.

Usage:
  python3 fill_template.py --template TEMPLATE --values scope.md --out proposal.md
  (--values can be given more than once; later files win)

Value rules (same as the by-hand rules in references/step-3-scope.md):
  - a value containing TO AGREE becomes just "TO AGREE"
  - "(from my offer: check it fits)" is removed
  - an empty value, or one that starts with the fill-in itself, stays as the
    bare fill-in, e.g. [PROPOSAL LINK]
Standard library only.
"""
import argparse
import pathlib
import re
import sys

TOKEN_RE = re.compile(r"\[[A-Z0-9][A-Z0-9 '’&,./\-]*\]")
OFFER_MARK_RE = re.compile(r"\(\s*from my offer:\s*check it fits\s*\)", re.IGNORECASE)
# Note references: [N03], [N04, N05], [N02-N04], [brief], (N03)
NOTE_REF_RE = re.compile(r"\[(?:N\d{1,3}|brief)[^\]]*\]|\(N\d{1,3}[^)]*\)", re.IGNORECASE)
CONSULTANT_ONLY_RE = re.compile(r"my offer|brand sheet|check it fits|for you to confirm", re.IGNORECASE)


def fill_in_lines(text):
    """If the file has a 'Fill-ins' heading (scope.md), read only that section.
    Otherwise (a brand sheet), read the whole file."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^(#+)\s.*fill-ins", line, re.IGNORECASE)
        if m:
            level = len(m.group(1))
            section = []
            for later in lines[i + 1:]:
                h = re.match(r"^(#+)\s", later)
                if h and len(h.group(1)) <= level:
                    break
                section.append(later)
            return section
    return lines


def read_values(paths, wanted):
    """Return {token: raw value} for the tokens the template needs. Later lines win."""
    values = {}
    for path in paths:
        for line in fill_in_lines(pathlib.Path(path).read_text(encoding="utf-8")):
            clean = line.replace("**", "").strip()
            clean = re.sub(r"^[-*•]\s+", "", clean)
            for token in wanted:
                if clean.startswith(token):
                    rest = clean[len(token):].lstrip()
                    if rest.startswith(":"):
                        values[token] = rest[1:].strip()
    return values


def client_ready(token, raw):
    """Turn a scope.md value into the words that go in front of the client."""
    if raw is None or raw == "" or raw.startswith(token):
        return None  # leave the bare fill-in
    if "TO AGREE" in raw:
        return "TO AGREE"
    value = OFFER_MARK_RE.sub("", raw)
    value = re.sub(r"\s{2,}", " ", value).strip()
    value = re.sub(r"\s+([.,;])$", r"\1", value)
    return value or None


def next_free(path):
    """Never overwrite: proposal.md -> proposal-v2.md -> proposal-v3.md ..."""
    if not path.exists():
        return path
    n = 2
    while True:
        candidate = path.with_name(f"{path.stem}-v{n}{path.suffix}")
        if not candidate.exists():
            return candidate
        n += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--template", required=True)
    parser.add_argument("--values", required=True, action="append")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    template = pathlib.Path(args.template).read_text(encoding="utf-8")
    wanted = sorted(set(TOKEN_RE.findall(template)), key=len, reverse=True)
    raw_values = read_values(args.values, wanted)

    problems, filled, to_agree, left = [], [], [], []
    final = {}
    for token in wanted:
        value = client_ready(token, raw_values.get(token))
        if value is None:
            left.append(token)
            continue
        if NOTE_REF_RE.search(value):
            problems.append(f"{token} has a note number in it: {value!r}")
        if CONSULTANT_ONLY_RE.search(value):
            problems.append(f"{token} has a note meant for the consultant in it: {value!r}")
        if TOKEN_RE.search(NOTE_REF_RE.sub("", value)):
            problems.append(f"{token} has another [FILL-IN] inside it: {value!r}")
        final[token] = value
        (to_agree if value == "TO AGREE" else filled).append(token)

    if problems:
        print("NOT WRITTEN. Fix these values in scope.md, then run again:")
        for p in problems:
            print("  -", p)
        sys.exit(1)

    text = template
    for token, value in final.items():
        text = text.replace(token, value)

    out = next_free(pathlib.Path(args.out))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")

    print(f"Written: {out}")
    print("Filled:", ", ".join(sorted(filled)) or "none")
    print("TO AGREE:", ", ".join(sorted(to_agree)) or "none")
    print("Still in brackets:", ", ".join(sorted(left)) or "none")


if __name__ == "__main__":
    main()
