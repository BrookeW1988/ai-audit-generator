# Session notes: Webb Property Advisory

Made up for practice. Numbered so the findings can point back to them. "Seen" means it happened on screen. "Said" means Marcus told you.

## N01: The job
Marcus: "After every client call I want notes in Notion and a follow-up email ready to go by the next morning." He showed the notes for the Henderson call on 14/10: summary, properties discussed, next steps with owners and dates, and a follow-up draft in Gmail. "That one's perfect." Seen.

## N02: When it last worked
Marcus: "It was great in June, when I had three or four calls a day. Since September it's eight to ten, and it stalls most nights." Said.

## N03: The rescue
Most mornings he opens Claude Code, types /call-notes, waits, types /compact when it says it's running out of room, then types "continue". Marcus: "Most mornings it's 30 to 45 minutes before I can start my day. Probably three to four hours a week." Not timed. Said.

## N04: Watched it run
He ran /call-notes on the 9 transcripts from 16/10 while you watched. After the fifth call, Claude Code showed "Compacting conversation". After that, the notes for calls 6 to 9 were shorter, and call 7's next steps listed a property address from call 3. Marcus caught it. It took 26 minutes. Seen.

## N05: Start-up check
In a fresh session in /Users/marcus/webb-ops, before typing anything, /context showed about 31% of a 200K window in use. Memory files (his two CLAUDE.md files and MEMORY.md) and skill descriptions were the biggest parts. Seen (screenshot).

## N06: The trace
The trace prompt said one run reads all of the day's transcripts in one session: about 85,000 words for the 16/10 run (roughly 110,000 tokens), on top of the start-up load (about 62,000 tokens). Add everything it writes and every Notion and Gmail step, and that's more than a 200K window holds, so it compacts partway through. It also flagged that the routine only looks at today's folder. Seen.

## N07: Missed calls and doubles
The log shows the run on 13/10 stopped before step 4. Those 7 calls never got notes or drafts until Marcus noticed on 15/10. On 08/10 he re-ran it by hand after a stall, and 4 clients got two Gmail drafts. Marcus: "I nearly sent one twice." Seen (log) and said.

## N08: Two versions
The start-up check found `call-notes` as both a skill and an old command. Marcus: "I made the command in March and forgot it was there." The skill wins when names match, so the old command doesn't run. His global CLAUDE.md says "Always write in dot points" and also "Format meeting notes as full paragraphs". Seen.

## N09: Keys and permissions
The keys check found the Fathom API key pasted on line 12 of the project CLAUDE.md, and .env (Notion, Fathom and HubSpot keys) committed to his private GitHub repo since 02/05/2026. The nightly run uses --dangerously-skip-permissions, and it has Gmail and Notion access. Gmail is drafts only: Marcus reads and sends every follow-up himself. Seen.

## N10: Recordings and data
Fathom joins every Zoom call. His booking confirmation tells clients calls are recorded for notes. Priya can see the Notion client pages. She doesn't use Claude Code, and couldn't run the routine if Marcus was away. Said.

## N11: What he wants
Marcus: "I want this fixed, but I want to understand it, so I can build the next one myself. Next I want a routine for weekly vendor updates." He's leaving HubSpot in December: "Don't bother fixing that one." Said.

## N12: His time
Not covered on the call. His intake form says about $150 an hour: "That's what I'd bill a client." (I17)

## N13: What's already good
The folder is in git. The Fathom download script ran fine every night in the log. His notes template (summary, properties, decisions, next steps with owner and date) is clear. He never lets it send email. Seen.
