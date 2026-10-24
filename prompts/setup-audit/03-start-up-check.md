# 03 · Start-up check (in the session)

**What it's for:** seeing what fills Claude's memory before anyone types, and finding instructions that argue with each other.
**Who runs it:** the client. First a fresh session in the routine's folder, then `/context` and a screenshot, then this prompt.

Copy from the line below to the end.

---

Check what loads before I type anything in this folder. Only read. Don't change anything.

1. List every instruction file that loads here (CLAUDE.md, .claude/CLAUDE.md, CLAUDE.local.md, AGENTS.md, ~/.claude/CLAUDE.md, and any in the folders above this one), with line counts. Flag any over 200 lines.
2. Find rules that contradict each other across those files, or rules for one project that sit in the global file. Quote the two lines for each.
3. Count my skills (personal and project). Flag any with very long descriptions, any that look unused or duplicated, and any skill and command with the same name.
4. Does an auto memory file load here? How many lines?
5. Which model is set for this folder and for my routines?

Give me a short table, then the three changes that would free up the most room.
