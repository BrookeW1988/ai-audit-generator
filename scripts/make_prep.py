#!/usr/bin/env python3
"""Make the prep pack for one client: the intake form, the emails, the session
questions and (for a setup audit in Claude Code) the prompts the client runs.

Why this exists: every prep file has to be filled the same way, word for word,
and the prompts have to be cut cleanly out of their instruction files. Doing
that by hand is where mistakes creep in, so it's one command instead.

Usage:
  python3 make_prep.py --client-folder ai-audit/webb-property-advisory --type setup --brand my-consulting-brand.md
  python3 make_prep.py --client-folder ai-audit/northside-physio --type business --brand my-consulting-brand.md
  Add --no-snapshot for a setup audit that isn't in Claude Code.

The client folder must already hold fill-ins.md. It never overwrites: an
existing file gets a -v2 beside it. Standard library only.
"""
import argparse
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import fill_template as ft  # noqa: E402  (same folder, shares the fill rules)

SKILL = pathlib.Path(__file__).resolve().parent.parent


def prompt_body(name):
    """Just the part the client pastes: everything after the --- line."""
    text = (SKILL / "prompts" / "setup-audit" / name).read_text(encoding="utf-8")
    return text.split("\n---\n", 1)[1].strip() + "\n"


def intake_form(kind):
    """The client-facing part of the intake form: between the two --- lines."""
    name = "setup-audit-intake.md" if kind == "setup" else "business-audit-intake.md"
    text = (SKILL / "references" / "intake-forms" / name).read_text(encoding="utf-8")
    return text.split("\n---\n")[1].strip() + "\n"


def fill(text, value_files):
    """Swap fill-ins for values, using the same rules as fill_template.py."""
    wanted = sorted(set(ft.TOKEN_RE.findall(text)), key=len, reverse=True)
    raw = ft.read_values(value_files, wanted)
    left = []
    for token in wanted:
        value = ft.client_ready(token, raw.get(token))
        if value is None:
            left.append(token)
        else:
            text = text.replace(token, value)
    return text, left


def save(folder, name, text):
    out = ft.next_free(folder / name)
    out.write_text(text, encoding="utf-8")
    return out


def session_questions(kind, client, when):
    source = (SKILL / "references" / "session-questions.md").read_text(encoding="utf-8")
    if kind == "setup":
        part = re.search(r"## Setup audit.*?(?=\n## Business audit)", source, re.S).group(0)
    else:
        part = re.search(r"## Business audit.*", source, re.S).group(0)
    body = part.split("\n", 1)[1].strip()
    label = "setup audit" if kind == "setup" else "business audit"
    head = (f"# Session questions: {client} ({label})\n\n"
            f"Your runsheet{' for ' + when if when else ''}. Your notes only, never sent to the client."
            + (" The prompts to paste are in `session-prompts.md`." if kind == "setup" else "")
            + "\n\nGolden rule: **get them to show you, not tell you.** Screen share, and have them do it while you watch.\n\n")
    return head + body + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--client-folder", required=True)
    parser.add_argument("--type", choices=("setup", "business"), required=True)
    parser.add_argument("--brand", action="append", default=[], help="brand sheet (can repeat; later files win)")
    parser.add_argument("--no-snapshot", action="store_true", help="setup audit that isn't in Claude Code")
    args = parser.parse_args()

    folder = pathlib.Path(args.client_folder)
    fill_ins = folder / "fill-ins.md"
    if not fill_ins.exists():
        sys.exit(f"Can't find {fill_ins}. Write the client's fill-ins first.")
    values = [*args.brand, str(fill_ins)]
    known = ft.read_values(values, ["[CLIENT BUSINESS]", "[CALL DATE]", "[CALL TIME]"])
    client = ft.client_ready("[CLIENT BUSINESS]", known.get("[CLIENT BUSINESS]")) or "this client"
    when = ", ".join(v for v in (ft.client_ready("[CALL DATE]", known.get("[CALL DATE]")),
                                 ft.client_ready("[CALL TIME]", known.get("[CALL TIME]"))) if v)

    written, left_all = [], set()

    def make(name, text):
        filled, left = fill(text, values)
        written.append(save(folder, name, filled))
        left_all.update(left)

    templates = SKILL / "references" / "templates"
    make("intake-form.md", intake_form(args.type))
    make("session-prep-email.md", (templates / "e1-session-prep-email.md").read_text(encoding="utf-8"))
    questions = session_questions(args.type, client, when)
    if args.type == "setup" and args.no_snapshot:
        questions += ("\n**No snapshot this time:** take stock on screen share, using the eleven headings in "
                      "the take-stock prompt as your checklist.\n")
    make("session-questions.md", questions)

    if args.type == "setup" and not args.no_snapshot:
        make("snapshot-request-email.md", (templates / "snapshot-request-email.md").read_text(encoding="utf-8"))
        make("take-stock-prompt.md", prompt_body("01-take-stock.md"))
        prompts = [f"# Prompts for the session: {client}\n",
                   "Paste each one to the client in the session chat when your runsheet says. "
                   "They run them in their own Claude Code. They only read the setup.\n"]
        for name, title, when_used in (
                ("02-trace-a-routine.md", "Trace a routine", "After they've run the routine while you watch (runsheet question 5)"),
                ("03-start-up-check.md", "Start-up check", "After a fresh session and /context (runsheet question 7)"),
                ("04-keys-and-permissions.md", "Keys and permissions", "Runsheet question 8")):
            prompts.append(f"## {title}\n\n**When:** {when_used}\n\n```\n{prompt_body(name)}```\n")
        make("session-prompts.md", "\n".join(prompts))

    for path in written:
        print("Written:", path)
    print("Still in brackets:", ", ".join(sorted(left_all)) or "none")


if __name__ == "__main__":
    main()
