# Writing audit.json (the report's content)

You write the words into `audit.json`. `scripts/build_report.py` does the design: a full-page cover in her colours, "the short version" summary page, the map, the health check, the ranked fixes, a roadmap timeline and the numbers page, with page numbers when printed. Never write the report's HTML by hand.

## Rules for every word in it

- **Written to the client, as "you".** It's their report. ("Your routine reads every call in one go", never "Marcus's routine" or "the client".)
- **Short.** Word limits are below. The report should take ten minutes to read.
- **Plain English, Australian spelling.** If a technical word has to appear, explain it in the same sentence.
- **Never invent.** Numbers, prices, times, tools, results and quotes only come from the session notes, the snapshot, the prep form or the consultant's answers. An estimate says "about" or "roughly", and how it was worked out goes in `assumptions`.
- **No note numbers** ([N03]), no notes meant for the consultant, and no bare [FILL-INS] anywhere in it. The build refuses note numbers and warns about brackets.
- **Copy numbers exactly.** Use the figure as it appears in the notes or snapshot, with its unit. Say words, not tokens, to clients (a token is about three-quarters of a word): "about 85,000 words of transcripts", never "110,000 words".
- **Evidence is what was seen.** `evidence` says what you actually saw ("Your global CLAUDE.md is 412 lines"). If they only told you, say "You said...".
- **Kind about what they built.** The owner usually built this themselves. Name what works. Describe problems as things that happen, not as mistakes they made.
- **Dates** as DD/MM/YYYY.

## The fields

`*` = required. Word limits are maximums.

```json
{
  "audit_type": "setup",                      // * "setup" or "business"
  "audit_name": "Claude Code Setup Audit",    // shown on the cover and in E2. Setup: [SETUP AUDIT NAME]. Business: [AUDIT NAME]
  "date": "24/10/2026",
  "consultant": {                             // * from the brand sheet
    "name": "…", "business": "…", "email": "…", "website": "…"
  },
  "client": { "business": "…", "name": "…" }, // * business. name = the person it's for
  "style": {                                  // from my-report-style.md
    "main_colour": "#1F4D3A", "accent_colour": "#F2A65A",
    "logo": "../my-logo.png"                  // path from this file, a web address, or leave out
  },
  "cover_line": "…",                          // optional, 20 words: the italic line under the client's name on the cover. Leave out for the default
  "headline": "…",                            // * ONE sentence, 30 words. The one thing to read. It also becomes [THE MAIN FINDING IN ONE SENTENCE] in E2
  "the_number": {                             // the one number you'll track
    "label": "Calls that got notes on their own last week",
    "now": "3 of 9", "target": "9 of 9", "note": "Counted from your log, 13/10 to 17/10"
  },
  "where_things_are_now": ["…", "…"],          // * 2 to 3 paragraphs, 60 words each. In their own words where you can
  "whats_working": ["…", "…"],                 // 2 to 4 items, 20 words each
  "map": {                                    // optional for business, expected for setup
    "title": "How your setup fits together",  // optional, this is the default for setup
    "intro": ["…"],                           // optional, 40 words
    "columns": [                              // 3 or 4 columns, up to 6 items each
      { "title": "What starts it", "items": [
        { "id": "cron", "label": "Every night at 7pm", "note": "a schedule on your Mac", "status": "tidy-up" } ] },
      { "title": "The routine", "items": [ { "id": "notes", "label": "Call notes routine", "status": "fix-first" } ] }
    ],
    "links": [ { "from": "cron", "to": "notes", "label": "all calls at once", "status": "fix-first" } ]
  },                                          // label 8 words, note 10 words, link label 4 words. status: fix-first, tidy-up, working, or leave it out. Arrows only join NEIGHBOURING columns (the build warns otherwise)
  "health_check_intro": ["…"],                 // optional, 30 words
  "health_check": [                           // * for setup: all 8 areas from setup-audit-method.md, in that order
    { "area": "One job per run",
      "status": "fix-first",                  // fix-first, tidy-up or working
      "finding": "…",                         // 20 words, the plain verdict
      "evidence": "…",                        // 20 words, what you saw
      "fix": "…" }                            // 25 words, leave out when working
  ],
  "priorities_intro": ["…"],                   // optional, 30 words
  "priorities": [                             // * 3 (up to 5 for setup). Fixes (setup) or opportunities (business), ranked
    { "title": "…",                           // 8 words
      "what": "…",                            // 30 words
      "saves": "about 3 hours a week",        // only real or clearly estimated numbers
      "effort": "Quick win",                  // Quick win, Medium or Bigger job
      "timeline": "about an hour",
      "uses_what_you_have": "…" }             // optional, 20 words
  ],
  "leave_alone": ["…"],                        // 1 to 3 items, 25 words each. What NOT to do yet, and why
  "careful_with": ["…"],                       // 1 to 3 items, 25 words each. Include one plain line on keeping their data safe
  "roadmap": {                                // * at least one item. 12 words per item
    "intro": ["…"], "now": ["…"], "next": ["…"], "later": ["…"]
  },
  "roi": {                                    // optional (expected for business). Only from real or clearly estimated numbers
    "title": "The numbers, on one page",
    "problem": "about 3.5 hours a week", "cost_a_year": "about $15,000", "frees_up": "…",
    "maths": "3.5 hours × 48 weeks × $90 an hour (your rate)"
  },
  "next_step": {                              // *
    "heading": "Let's walk through it together",
    "detail": ["30 minutes to go through the report, answer your questions and decide what's first."],
    "button": "Book the walkthrough",
    "link": "[BOOKING LINK] from the brand sheet"
  },
  "assumptions": ["…"]                         // every estimate and how you got it, 20 words each
}
```

## Status words

| status | Shows as | Use for |
|---|---|---|
| `fix-first` | Fix first (red) | Broken now, or a risk to client data, keys or money |
| `tidy-up` | Tidy up (amber) | Works, but will cause trouble or waste time |
| `working` | Working well (green) | Genuinely fine. Always find at least one |

## Building it

```
python3 scripts/build_report.py <client-folder>/audit.json --pdf
```

- Writes `<client-folder>/report/index.html`. An existing one moves to `report/earlier-versions/` first.
- `--pdf` also saves a PDF beside `audit.json` when Chrome, Edge, Brave or Chromium is on the computer. If none is, it says so: open the report and click **Save as PDF**.
- `--check` only checks `audit.json` and builds nothing.
- If it prints `NOT BUILT`, fix what it lists and run it again. It never half-builds.
