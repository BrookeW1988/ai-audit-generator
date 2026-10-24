# Setup snapshot: Marcus Webb (Webb Property Advisory)

Made by the take-stock prompt, read-only. Keys and passwords show as HIDDEN. Practice file: made up, and trimmed in places (marked "trimmed for practice").

## 1. The basics
- Claude Code version: 2.1.305
- Operating system: macOS 15.6
- Folder: /Users/marcus/webb-ops
- Model: `claude-sonnet-4-6`, set in ~/.claude/settings.json. The nightly script doesn't set a model, so it uses the same one.

## 2. Instruction files
| File | Lines |
|---|---|
| ~/.claude/CLAUDE.md | 412 |
| /Users/marcus/webb-ops/CLAUDE.md | 138 |
| CLAUDE.local.md, .claude/CLAUDE.md, AGENTS.md | not found |
| Parent folders (/Users/marcus, /Users) | not found |

**~/.claude/CLAUDE.md** (412 lines, so the first 150 are included; trimmed further for practice):
```
# MY RULES (READ EVERY TIME)
You are an elite executive assistant and world-class copywriter.
Always write in dot points. Keep everything short.
...
## Meeting notes
Format meeting notes as full paragraphs, not dot points, so they read well in Notion.
...
## Webb Property clients
Client notes go in the Notion database "Clients". Use the client's surname as the page title.
Follow-up emails: warm, sign off "Cheers, Marcus".
...
## ULTIMATE PROMPT (from YouTube, March)
[a 180-line copied prompt about "thinking step by step like a McKinsey consultant", trimmed for practice]
...
```

**/Users/marcus/webb-ops/CLAUDE.md** (138 lines, trimmed for practice):
```
# Webb Ops
This folder runs my client call notes.
Fathom API key: HIDDEN
Transcripts land in transcripts/YYYY-MM-DD/ (one folder per day).
Notes: summary, properties discussed, decisions, next steps (owner + date), follow-up email draft.
Never send emails. Drafts only. I check every one.
...
```

## 3. Memory
Auto memory (MEMORY.md) loads for this folder: 61 lines.

## 4. Skills and commands
- **Personal skills (~/.claude/skills): 31.** Including: ultimate-copywriter, seo-god-mode, viral-hooks-pro, linkedin-ghostwriter, youtube-script-machine, notion-helper, email-wizard, pdf-tools, and 23 more downloaded in March and April. Several have descriptions over 60 words.
- **Project skills (.claude/skills): 2.**
  - `call-notes`: "Turn today's Fathom transcripts into client notes in Notion and follow-up drafts in Gmail."
  - `weekly-report`: "Every Friday, summarise the week's client calls into a Google Doc."
- **Commands (.claude/commands): 1.**
  - `call-notes.md`: "Read the transcripts and write meeting notes as paragraphs."
- **Same name:** `call-notes` is both a skill and a command.

## 5. Subagents
None found.

## 6. Connections (claude mcp list)
| Server | Status |
|---|---|
| fathom | connected |
| gmail | connected |
| notion | connected |
| google-drive | connected |
| hubspot | failed to connect |

No .mcp.json in this folder. All five are set for every project (user scope).

## 7. Settings, permissions and hooks
- **~/.claude/settings.json:** model `claude-sonnet-4-6`. Allow: `Bash(*)`, `Read(*)`, `Write(*)`, `mcp__gmail__*`, `mcp__notion__*`. Ask: none. Deny: none. No defaultMode. No hooks. No env settings.
- **.claude/settings.local.json:** allow `Bash(python3:*)`.
- **.claude/settings.json:** not found.
- **Skip-permissions search:** found `--dangerously-skip-permissions` in the crontab entry below.

## 8. Anything that runs on its own
crontab -l:
```
45 18 * * 1-5 cd ~/webb-ops && python3 scripts/pull_fathom.py >> logs/cron.log 2>&1
0 19 * * 1-5 cd ~/webb-ops && /usr/local/bin/claude -p "/call-notes" --dangerously-skip-permissions >> logs/cron.log 2>&1
```
- ~/Library/LaunchAgents: nothing that runs claude.
- Scripts that call `claude -p`: none (only the crontab entry).
- Asked Marcus about Desktop or cloud scheduled tasks. His answer: "No, just the cron ones."

## 9. The routine to fix: call notes
**Skill: .claude/skills/call-notes/SKILL.md** (full):
```
---
name: call-notes
description: Turn today's Fathom transcripts into client notes in Notion and follow-up drafts in Gmail.
---
1. Read every transcript in transcripts/<today's date>/.
2. For each call, write: summary, properties discussed, decisions, next steps (owner + date), and a follow-up email.
3. Append all of today's notes to notes/daily-notes.md.
4. For each client, create a Gmail draft of the follow-up email.
5. Update the client's Notion page in "Clients" with the notes.
6. When done, write a one-line summary of the day.
```
- **Input:** `scripts/pull_fathom.py` downloads the day's transcripts into transcripts/YYYY-MM-DD/ at 6:45pm.
- **Items per run:** 6 to 11 transcripts a day over the last 4 weeks. Last 5 working days: 9, 8, 11, 7, 9.
- **Three largest (last 5 days):** 11,840 words, 10,205 words, 9,960 words.
- **Results go to:** Notion "Clients" pages, Gmail drafts, notes/daily-notes.md (2,940 lines).
- **Done list:** none. It works from today's folder name only.
- **Log: logs/cron.log, last 40 lines (trimmed for practice):**
```
[13/10 19:00] call-notes: 7 transcripts found
[13/10 19:31] Context limit reached. Compacting conversation...
[13/10 19:58] Error: process exited before completing step 4
[14/10 19:00] call-notes: 9 transcripts found
[14/10 19:24] Context limit reached. Compacting conversation...
[14/10 20:05] Done: 9 calls
[15/10 18:45] pull_fathom: 11 transcripts saved
[15/10 19:00] call-notes: 11 transcripts found
[15/10 19:22] Context limit reached. Compacting conversation...
[15/10 19:49] Context limit reached. Compacting conversation...
[15/10 20:12] Error: process exited before completing step 5
[15/10 20:12] hubspot: failed to connect
```

## 10. Keys and safety
- **.env** (in /Users/marcus/webb-ops): NOTION_TOKEN, FATHOM_API_KEY, HUBSPOT_TOKEN
- **Git:** yes, this folder is a git repo. Remote: yes, GitHub (private repo).
- **.gitignore:** exists, but .env is not in it. `git log` shows .env was first committed on 02/05/2026.
- **Pasted keys found:** /Users/marcus/webb-ops/CLAUDE.md, line 12 (the Fathom API key).

## 11. How it fits together
| What starts it | The routine | Tools and connections | Where results go |
|---|---|---|---|
| Schedule, weekdays 6:45pm | pull_fathom.py | Fathom (key in .env) | transcripts/YYYY-MM-DD/ |
| Schedule, weekdays 7pm | call-notes skill (all of today's calls in one session) | Notion, Gmail, transcripts folder | Notion "Clients" pages, Gmail drafts, notes/daily-notes.md |
| Marcus typing /call-notes | call-notes skill (when the nightly run stalls) | same | same |
| Marcus typing /weekly-report (Fridays) | weekly-report skill | notes/daily-notes.md, Google Drive | a Google Doc in Drive |
