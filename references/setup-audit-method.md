# The setup audit: method and best-practice checklist

How to audit someone's existing AI setup like a proper system review: take stock, map it, trace what breaks, check it against best practice, rank the risks, plan the fixes. Written for Claude Code setups. Most checks also work for other AI setups (Claude Projects, Cowork, ChatGPT), just without the snapshot prompt.

**Facts checked 24/10/2026** against the official Claude Code docs (code.claude.com/docs). Claude Code changes often. If something here doesn't match what you see on screen, trust the screen and tell the consultant.

## The eight steps

Steps 1 to 6 are the audit. Steps 7 and 8 are the fix, which is paid work after the audit.

| # | Step | What happens | Prompt |
|---|---|---|---|
| 1 | Take stock | The client runs a read-only prompt that lists everything in their setup and hides their keys. | `prompts/setup-audit/01-take-stock.md` |
| 2 | Map it | Draw how it fits together: what starts each routine, what it reads, what it uses, where results go. | Built from the snapshot |
| 3 | Trace the broken bit | In the session, Claude walks the stalling routine step by step, then the client runs it while you watch. | `02-trace-a-routine.md` |
| 4 | Check it against best practice | Score the eight areas below: Fix first, Tidy up or Working well, each with what you saw. | `03-start-up-check.md`, `04-keys-and-permissions.md` |
| 5 | Rank the risks | How likely is it to break or leak, and how bad would that be? Client data and money come first. | — |
| 6 | Plan the fixes | Broken first, then what makes it break again, then nice-to-haves. Now, next, later. | — |
| 7 | Fix it and check it | Fix one thing at a time, then test it on one real item and compare before and after. | `05-test-the-fix.md` |
| 8 | Hand it over | A one-page note per routine: what it does, when it runs, how to tell it worked, what to do when it doesn't. | `06-handover-notes.md` |

## The eight areas

For each area: what to check, what each score means, and where to look. Score from evidence only (the snapshot, what the client showed you, what they said). If you didn't see it, say "Reported" in the findings, not "Seen".

### 1. A clear job
- **Check:** can the owner say, in one sentence each, what every routine produces, who it's for, and how they know it worked?
- **Fix first:** nobody can say what a good result looks like, or one routine does several unrelated jobs.
- **Tidy up:** the job is clear, but there's no example of a good result to check against.
- **Working well:** one sentence per routine, plus an example of a good result.

### 2. Room to think
- **What it means:** Claude can only hold so much in one session (its context window). Everything that loads at the start (every CLAUDE.md file, auto memory, every skill's description) takes room before any work starts. Everything the routine reads (each transcript, each file) takes more. When it fills up, Claude summarises the conversation to keep going (compacting), and detail gets lost.
- **Check:** in a fresh session, in the folder the routine runs from, the client types `/context`. It shows what's taking room. Also check which model runs the routine. Current models (Opus 4.7 and later, Sonnet 5 and later, Fable 5 and later, Haiku 5.5) have a 1M-token window by default. Older ones like Sonnet 4.6 and Opus 4.6 have 200K unless the `[1m]` version is picked. A one-hour call transcript is roughly 10,000 words, around 13,000 tokens.
- **Fix first:** the routine reads many big files into one session, or needs a manual `/compact` to finish.
- **Tidy up:** a big slice is used before anyone types, from a long CLAUDE.md, dozens of skills, or a large auto memory file.
- **Working well:** a fresh session starts light, and the routine finishes without compacting.

### 3. One set of instructions
- **What it means:** Claude Code loads `~/.claude/CLAUDE.md` (every project), the project's `CLAUDE.md` (or `.claude/CLAUDE.md`), `CLAUDE.local.md`, and any CLAUDE.md in parent folders, all at once. If they disagree, Claude has to guess. The docs say to aim for under 200 lines per CLAUDE.md file.
- **Check:** line counts, rules that contradict each other, rules for one project sitting in the global file, old copy-pasted prompts, and duplicate instructions in skills or commands. Custom commands (`.claude/commands/`) have been merged into skills. They still work, but if a command and a skill share a name, the skill wins. Two versions of the same routine is a common cause of "it does something different every time".
- **Fix first:** contradictions that change what the routine produces, or two versions of a routine that can both run.
- **Tidy up:** files over 200 lines, project rules in the global file, stale rules, or an old version that never runs (a command shadowed by a skill of the same name).
- **Working well:** short files, each rule in one place, project rules in the project.

### 4. One job per run
- **What it means:** batch work (ten calls, thirty reports) should give each item its own fresh session. Two official ways: a subagent per item (each subagent gets its own context window and hands back only its result), or a separate headless run per file (`claude -p`, which starts a new session each time). Each item's result goes in its own file.
- **Check:** does the routine loop over every file in one conversation? Does one giant output file collect everything?
- **Fix first:** many items are handled in one session.
- **Tidy up:** one item per run, but results land in one shared file that's hard to check.
- **Working well:** one item per fresh session, one result file per item.

### 5. Safe to re-run, starts on its own
- **What it means:** running it twice shouldn't double anything (two sets of notes, two email drafts). A "done list" (a processed log) records what's finished, so the next run only picks up new items, including any a failed run missed.
- **Official ways to run on a schedule:** cloud scheduled tasks (`/schedule`, formerly called routines, which run without the computer on), Desktop scheduled tasks (run on the computer), and GitHub Actions. `/loop` only runs while that session stays open, and recurring session tasks expire after seven days. Cron or launchd calling `claude -p` works, but the docs don't list it as a scheduling option.
- **Headless runs (`claude -p`):** from Claude Code v2.1.302, a `-p` run with no permission mode set starts in Manual mode, so anything that needs approval is denied. A scheduled routine that worked last month can start failing this way. Set its permissions on purpose (an `--allowedTools` list or a permission mode). The docs also recommend `--bare` for scripts. It skips loading CLAUDE.md, skills, hooks, MCP servers and memory, so test first if the routine relies on any of those.
- **Fix first:** no done list ("files from today" style), so failures drop items and re-runs duplicate them. Or a headless routine with no permissions set.
- **Tidy up:** a done list exists but isn't checked before each item.
- **Working well:** a done list, safe to re-run, a schedule from the official list.

### 6. Keys and permissions
- **Check:**
  - API keys live in a `.env` file. Never in CLAUDE.md, skills, prompts or chat.
  - `.env` is listed in `.gitignore` (if it isn't, a git push sends the keys to GitHub).
  - A `Read` deny rule for `.env` stops Claude reading it. The docs suggest this.
  - Permissions are narrow: specific allowed tools, not `Bash(*)`.
  - No `bypassPermissions` or `--dangerously-skip-permissions` on anything that touches client data, email or money.
  - Client recordings: who agreed to recording, where they're stored, who can see them.
- **Fix first:** a key in an instruction file, a key pushed to GitHub, or "skip all permissions" on a routine that touches client data or sends anything.
- **Tidy up:** broad permissions on low-risk work, or `.env` not blocked from reading.
- **Working well:** keys only in `.env`, narrow permissions, and a person checks anything that leaves the business.

### 7. You can tell when it breaks
- **Check:** is there a log per run that a person can read? Does one failed item stop the whole batch? Does anyone get told when it fails? Does a person check anything before it reaches a client? (AI drafts, a person decides.)
- **Known reasons routines stall:**
  - Command output over about 30,000 characters gets cut to a 2,000-character preview.
  - Commands time out after 2 minutes by default.
  - A `-p` run waits up to 10 minutes for background work, then drops the unfinished result.
  - After compacting, only the most recent files get re-read.
- **Fix first:** failures are silent, or one failure stops everything.
- **Tidy up:** a log exists that nobody reads, or no alert.
- **Working well:** a short log per run, failures skip and get flagged, and someone's told.

### 8. Someone else could look after it
- **Check:**
  - Are CLAUDE.md files, skills and scripts in git, or at least backed up?
  - Is there a short note per routine?
  - Do names say what things do?
  - Could the owner explain it to a new team member?
  - Read-only health checks: `claude --version` (the version) and `claude doctor` (install health and settings errors). The `/doctor` command inside a session can also propose fixes. Only use it in the fix session, with the owner's OK.
- **Fix first:** no backups of the setup at all.
- **Tidy up:** backed up, but no notes, or names nobody understands.
- **Working well:** in git or backed up, a note per routine, plain names.

## Scoring rules

- Every area gets a score, with "What I saw" evidence from the snapshot or the session. No evidence, no score: mark it "Tidy up" and say what to check in the finding.
- Fix first means it's broken now, or it puts client data, keys or money at risk. Keep it to the ones that really are.
- Always find what's working. A real "Working well" builds trust, and the owner built this themselves.
- Rank the fixes by: broken now, then risks, then what makes it break again, then tidy-ups. Quick wins first inside each group.
- Never recommend a change you can't explain in one sentence to the owner.
