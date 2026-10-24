# Session questions (the consultant's runsheet)

For the paid 90-minute working session. Save the right half into the client folder as `04-session-questions.md`, with the client's name and [THE WORKFLOW] filled in. These are the consultant's own notes, never sent to the client.

Golden rule for both: **get them to show you, not tell you.** Screen share, and have them do it while you watch.

## Setup audit (an existing Claude Code or AI setup)

**Before the session:** read their `setup-snapshot.md` and `/context` screenshot. Bring a first sketch of the map (what starts each routine, the routine, the tools it uses, where results go) and three questions it raised.

**First 15 minutes: the job**
1. "What should [THE WORKFLOW] give you? Show me a good one." (Get an example of a good result.)
2. "When did it last run all the way through without you stepping in?"
3. "Who else relies on what it makes?"

**Next 30 minutes: watch it fail**
4. "Run it now, the way you normally would." Watch for: when it slows down, any 'compacting' message, any approval prompt, and what they type to rescue it.
5. Have them paste prompt `02-trace-a-routine.md`, then compare its likely stall points with what you just saw.
6. "What do you do when it stalls? How long does that take you each time, and how often?" (This is the number you'll track.)

**Next 30 minutes: the checks**
7. Prompt `03-start-up-check.md` (after a fresh `/context`).
8. Prompt `04-keys-and-permissions.md`.
9. "Where do the recordings or files come from, and has everyone on them agreed to that?"

**Last 15 minutes: what they want next**
10. "If this ran perfectly, what would you do with the time?"
11. "What do you want to be able to build yourself after this?" (This shapes the lessons in the fix package.)
12. "Anything you'd rather I didn't touch?"

**Never in the session:** change their setup, run `/doctor` fixes, or open their `.env` file. The audit looks. The fix (paid, later) changes things.

## Business audit (how one part of the business runs)

**First 15 minutes: the job and the people**
1. "Walk me through [THE WORKFLOW] from the very start. What kicks it off?"
2. "Who does each step? Who signs it off?"
3. "Roughly how often does it happen, and how many each week or month?"

**Next 40 minutes: watch it happen**
4. "Show me the last one you did, on screen, step by step." Note what you SAW versus what they TOLD you.
5. "Where does it get stuck, or come back for a redo?"
6. "How long does that part take? Has anyone timed it?" (If not, ask them to time the next one. Don't guess.)
7. "What have you tried already? What happened?"

**Next 20 minutes: tools and data**
8. "Which tools does this touch?" (List them. Note which ones you saw.)
9. "Is there any information here you'd never want in an AI tool?"
10. "What must a person always check before it goes out?"

**Last 15 minutes: what good looks like**
11. "If this was sorted, what would you do with the time?"
12. "What would make you say this audit was worth it?"
