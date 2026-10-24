# 01 · Take stock (the client runs this before the session)

**What it's for:** a read-only list of everything in the setup, with keys hidden, so you can map it before you meet.
**Who runs it:** the client, in their own Claude Code, in the folder where the routine lives. Send it with the snapshot request email.
**Before they paste it:** a fresh session, then `/context` and a screenshot.

Copy from the line below to the end.

---

I'm getting my Claude Code setup audited. Please make a read-only snapshot of it.

The routine I most want fixed: [THE WORKFLOW]

Rules:
- Only read. Don't create, change, move or delete anything except the one snapshot file below. Don't run any of my routines, scripts or scheduled jobs.
- Never show a key, token, password or secret. Write HIDDEN in its place. For .env files, list the variable names only, never the values.
- Don't copy the contents of client files (transcripts, notes, emails). Give file names, how many there are, and rough sizes only.
- If something needs my approval, ask me. If you can't find something, write "not found" and move on.

Save everything to setup-snapshot.md in this folder, with these sections:

1. The basics: the Claude Code version (run claude --version), the operating system, this folder's path, and which model my routines use (check my settings files and any scripts that start Claude).
2. Instruction files: every CLAUDE.md, .claude/CLAUDE.md, CLAUDE.local.md and AGENTS.md that loads here (in ~/.claude/, in this folder, and in the folders above it). For each one: where it is, how many lines, and the full contents with keys hidden. If one is over 300 lines, include the first 150 lines and say how long it is.
3. Memory: does an auto memory file (MEMORY.md) load for this folder? How many lines?
4. Skills and commands: every skill in ~/.claude/skills and .claude/skills (its name and one-line description), and every file in ~/.claude/commands and .claude/commands (its name and first line). Flag any skill and command with the same name.
5. Subagents: anything in ~/.claude/agents and .claude/agents (name and description).
6. Connections: run claude mcp list and give each server's name and whether it's connected. Names only, no web addresses or keys. Say whether there's a .mcp.json file here.
7. Settings, permissions and hooks: from ~/.claude/settings.json, .claude/settings.json and .claude/settings.local.json, list the permission rules (allow, ask, deny), any defaultMode, any hooks (which event and what they run), and any env settings with values hidden. Search my scripts for --dangerously-skip-permissions and bypassPermissions.
8. Anything that runs on its own: run crontab -l (Mac or Linux) and list entries that start Claude. On a Mac, also check ~/Library/LaunchAgents for anything that runs claude. On Windows, list Task Scheduler tasks that mention claude. List any script that calls claude -p. Then ask me: "Do you have any scheduled tasks in the Claude desktop app, or cloud scheduled tasks (/schedule)?" and write down my answer.
9. The routine I want fixed: include its skill, command or script in full (keys hidden). Say where its input comes from (a folder, an app or a connection), roughly how many items it handles per run and how big they are (word counts for the three largest), where its results go, and whether it keeps a list of what it has already done. If it has a log file, include the last 40 lines (keys hidden).
10. Keys and safety: list every .env file (variable names only). Is this folder a git repo? If it is: is .env in .gitignore, and is there a remote (yes or no, and the host, like GitHub)? Search instruction files, skills and scripts for anything that looks like a pasted key, and say which file and line (never the key itself).
11. How it fits together: a list in four columns. What starts each routine (me typing it, a schedule, another app), then the routine, then the tools and connections it uses, then where its results go.

When you're done, show me a short summary, then say: "Read setup-snapshot.md before you send it, and delete anything you'd rather keep private."
