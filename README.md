# AI Audit Generator

Run a paid AI audit, from a strong intake form to a premium report your client will actually read: your colours, your logo, a PDF or a link.

Two kinds of audit:
- **Business audit:** how one part of a business runs, and where AI (or a simpler fix) will save time or money first.
- **Setup audit:** a health check of an AI setup someone has already built, usually in Claude Code. It comes with ready-made prompts your client runs on their own computer. The prompts only read their setup and hide their keys. Then you check it against eight areas of best practice.

It drafts. It never sends anything.

## Install

**Claude app (web or desktop):**
1. In Claude's settings, turn on code execution and file creation.
2. Download the zip: https://github.com/BrookeW1988/ai-audit-generator/releases/latest/download/ai-audit-generator.zip
3. Upload it in the Skills section of Claude's settings. Upload it as it is; don't unzip it.

**Cowork or Claude Code:** download the same zip, unzip it, and drop the `ai-audit-generator` folder into your skills folder (in Claude Code, that's `~/.claude/skills/`). Or tell Claude: "Set this up as a skill for me" and point it at the folder.

## Try a practice client first (about 15 minutes)

Say **"Try the practice audit"** and pick one:
1. **Webb Property Advisory** (setup audit): Marcus's routine turns client call recordings into notes and next steps, and it stalls most nights.
2. **Quillmoss Bookkeeping** (business audit): Dana wants to know if AI can write her monthly client reports.

Both are made up. You'll see the prep pack, the call plan, the findings and the finished report.

## Use it with a real client

**The quick way:** after your session, say **"Build my audit report"** and drop in the call transcript. It works out who it's for, asks you only what's missing, writes your findings for you to check, then builds the report.

**The full way (better audits):**
1. **When they book, say "Prep my audit".** Answer three quick questions. You get:
   - an intake form that asks exactly what the report needs
   - your session prep email (E1) and your session runsheet
   - for a setup audit, a snapshot request and the take-stock prompt your client runs
2. **When their intake answers come back, paste them in and say "Plan my call".** You get `call-questions.md`: what you already know, the gaps to fill on the call, vague answers to pin down, and what to get them to show you.
3. **Run the session.** Get them to show you, not tell you.
4. **Say "Build my audit report"** with the transcript (and their snapshot). It writes your findings, then stops so you can check them.
5. **Say "looks right".** It builds the report and your report email (E2).
6. **Send it** as a PDF, or as a link (below). Then book the 30-minute walkthrough. That's where you pitch the fix.

Want to change something? Say **"Change my report"**. Old versions are kept.

## Your brand sheet and your look

Made your brand sheet (`my-consulting-brand.md`) with the Consulting Kit Setup skill? Keep it in your Claude Project's knowledge, or attach it, so your name, links and audit name come through. No brand sheet? It asks for the few things it needs.

The first time you build a report, it asks for two colours and your logo, and saves them in `ai-audit/my-report-style.md` for every report after that.

## Sending the report

- **As a PDF:** if Chrome is on your computer, the PDF is made for you. Otherwise open `report/index.html`, click **Save as PDF**, pick "Save as PDF" as the printer, and untick "Headers and footers".
- **As a link:** log in to Netlify (the free plan is fine for business use), go to app.netlify.com/drop and drag the `report` folder in. Log in first: a site dropped without an account stays password-protected and disappears after an hour. Skip Vercel's free plan for this. It's for personal, non-commercial use only.

Only use a client's recordings, notes or setup files if they've agreed to it, and in an AI tool whose data settings you've checked.

## What's in the folder

| File | What it is |
|---|---|
| `SKILL.md` | What Claude does, step by step |
| `references/setup-audit-method.md` | The setup audit method: eight steps and the eight best-practice areas (facts checked 24/10/2026) |
| `references/business-audit.md` | The business audit method |
| `references/report-content.md` | What goes in each part of the report, with word limits |
| `references/what-a-good-audit-needs.md` | The facts every report depends on: what the intake form asks, and what the call fills in |
| `references/intake-forms/` | The two intake forms, one for each audit |
| `references/session-questions.md` | Your runsheet for the 90-minute session, for both audits |
| `references/templates/` | E1 and E2, word for word from the consulting swipe file, plus the snapshot request email |
| `references/practice/` | The two made-up practice clients |
| `prompts/setup-audit/` | The six prompts your client runs: take stock, trace a routine, start-up check, keys and permissions, test the fix, handover notes |
| `prompts/build-your-own.md` | A prompt to rebuild this skill around your own industry |
| `scripts/build_report.py` | Turns the report content into your branded report (and the PDF) |
| `scripts/make_prep.py` | Makes the whole prep pack for one client in one go |
| `scripts/fill_template.py` | Drops your fill-ins into the emails without changing a word |
| `assets/practice-logo.svg` | The made-up logo for the practice runs |

E1 and E2 come word for word from the consulting swipe file (`swipe-file.md`, Version 1, 14/10/2026). If the swipe file changes, copy the new wording into `references/templates/`. Claude Code changes often, so check `references/setup-audit-method.md` against the official docs every couple of months.

## Goes with

- **Workflow Mapper:** map a client's messy process on the discovery call: https://github.com/BrookeW1988/workflow-mapper
