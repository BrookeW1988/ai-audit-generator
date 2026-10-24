# 02 · Trace a routine (in the session)

**What it's for:** finding where a routine stalls, step by step, before anyone runs it.
**Who runs it:** the client, on screen share. Then they run the routine for real while you watch.

Copy from the line below to the end.

---

Trace one routine for me, step by step, without running it. Only read files. Don't change anything. Never show a key, token or password: write HIDDEN instead.

The routine: [THE WORKFLOW]

1. Find everything it uses: its skill, command or script, anything those call, and the instruction files that load with it.
2. Walk through it in order. For each step: what it reads (and roughly how big, in words or lines), what it does, what it writes, and what has to be true for the next step to work.
3. Add it up. Roughly how much does one run read in total? Does it handle many items in one session, or one item per session?
4. Mark every step that could stall or fail: too much to read at once, output that could be very long, a command that could take more than 2 minutes, anything that needs approval when nobody's watching, anything that depends on today's date, and anything that would happen twice if it's restarted.
5. Finish with the three most likely reasons it stalls, most likely first, each with its step number.

Plain English, short. Don't fix anything yet.
