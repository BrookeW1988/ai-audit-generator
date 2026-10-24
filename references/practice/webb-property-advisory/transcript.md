# Transcript: Webb Property Advisory, setup audit session

Made up for practice. Monday 19/10/2026, 10:00am AEST, about 90 minutes, recorded with Marcus's OK. Trimmed: small talk and long silences are cut. "Consultant" is you.

**00:00:20 Consultant:** Thanks for the snapshot and the form, Marcus. Before we start, are you still happy for me to record this, just for my notes?

**00:00:27 Marcus Webb:** Yep, all good.

**00:00:31 Consultant:** Great. Let's start with what good looks like. When the call notes routine works, what do you get?

**00:00:39 Marcus Webb:** So after every client call I want notes in Notion and a follow-up email ready to go by the next morning. Here, I'll share my screen. This is the Henderson call from the 14th. Summary up the top, the properties we talked about, decisions, then next steps with who and by when. And the follow-up's sitting in Gmail as a draft. That one's perfect.

**00:01:18 Consultant:** That's a really clear standard. When did it last run all the way through on its own?

**00:01:24 Marcus Webb:** Honestly? June was great. I had three or four calls a day then. Since September it's eight to ten, and it stalls most nights.

**00:01:37 Consultant:** Your form said you restart it in the morning and it "takes a while". Walk me through what that looks like.

**00:01:45 Marcus Webb:** I open Claude Code, type /call-notes, wait. At some point it says it's running out of room, so I type /compact, then "continue". Sometimes twice. Most mornings it's 30 to 45 minutes before I can start my day.

**00:02:03 Consultant:** And across a week?

**00:02:06 Marcus Webb:** Probably three to four hours. I've never actually timed it.

**00:02:11 Consultant:** That's fine. It's a starting number, and we can time this week's. Can you run it now, the way you normally would? Use yesterday's calls if that's easier.

**00:02:20 Marcus Webb:** Sure. These are from Friday the 16th. Nine calls. Running /call-notes now.

**00:09:52 Consultant:** It's just said "Compacting conversation". Which call is it up to?

**00:09:58 Marcus Webb:** Just finished the fifth.

**00:24:40 Marcus Webb:** Okay, done. Hang on. Call 7's next steps say "book a building inspection for 14 Carina Street". That wasn't call 7. That was call 3. Call 7 was the Morningside unit.

**00:24:58 Consultant:** Good catch. That's the compacting at work: once it summarises itself to keep going, details from different calls can blur together. How long did that run take?

**00:25:06 Marcus Webb:** About 26 minutes.

**00:25:10 Consultant:** And the notes for calls 6 to 9, compared with 1 to 5?

**00:25:15 Marcus Webb:** Shorter. Less detail on the properties.

**00:25:30 Consultant:** I'll paste a prompt in the chat. It traces the routine step by step and only reads things. It doesn't change anything.

**00:27:42 Marcus Webb:** It says one run reads all of the day's transcripts in one session. For Friday that's about 85,000 words. Plus everything that loads at the start. And it says the routine only looks at today's folder.

**00:28:05 Consultant:** That's the heart of it. Now open a fresh session in the same folder and type /context before anything else.

**00:28:40 Marcus Webb:** It says about 31% used already, of 200K. The biggest bits are memory files and skills.

**00:28:52 Consultant:** Your snapshot showed the model is Sonnet 4.6, which has a 200K window. So roughly a third is gone before any work starts, then 85,000 words of calls on top, plus everything it writes. It can't fit, so it compacts partway through.

**00:29:20 Marcus Webb:** So more calls equals more stalling.

**00:29:23 Consultant:** Exactly. Next prompt: the start-up check.

**00:31:10 Marcus Webb:** Huh. It says call-notes is a skill and also a command. I made the command in March and forgot it was there.

**00:31:18 Consultant:** When the names match, the skill wins, so the old command doesn't run. It's clutter more than the cause. What else did it find?

**00:31:30 Marcus Webb:** My global CLAUDE.md is 412 lines. And it's quoting two rules: "Always write in dot points" and "Format meeting notes as full paragraphs".

**00:31:44 Consultant:** Those two disagree, so it has to guess. Now the keys and permissions prompt. It never shows the keys themselves.

**00:34:02 Marcus Webb:** Oh no. The Fathom key's pasted on line 12 of the project CLAUDE.md. And the .env file's been committed to my GitHub repo since the 2nd of May. It's a private repo, but still.

**00:34:20 Consultant:** Your form said it's all backed up on GitHub. That's a good habit. The catch is the keys went up with it. The fix is quick: change the keys, keep them only in .env, and stop .env going to GitHub. What does the nightly run use for permissions?

**00:34:41 Marcus Webb:** The cron line has --dangerously-skip-permissions. I added that because it kept asking me things at 7pm when I wasn't there.

**00:34:52 Consultant:** And it has Gmail and Notion access. Does it ever send anything?

**00:34:57 Marcus Webb:** Never. Drafts only. I read every one before I send it.

**00:35:03 Consultant:** Keep that. It's the best decision in the whole setup. Has it ever gone wrong in a way a client saw?

**00:35:12 Marcus Webb:** Not quite. On the 8th it stalled, I re-ran it by hand, and four clients got two drafts each. I nearly sent one twice. And on the 13th the run stopped before the Gmail step, so seven calls got nothing. I didn't notice until the 15th.

**00:35:35 Consultant:** Is that in the log?

**00:35:38 Marcus Webb:** Yeah, the log shows both. I just never look at it.

**00:36:10 Consultant:** Who records the calls, and do clients know?

**00:36:15 Marcus Webb:** Fathom joins every Zoom. My booking confirmation says calls are recorded for notes.

**00:36:24 Consultant:** And Priya?

**00:36:27 Marcus Webb:** She can see the Notion client pages. She doesn't use Claude Code, so if I was away for a week it just wouldn't run.

**00:36:40 Consultant:** Last bit. You said on the form you want it fixed and explained. Tell me more.

**00:36:46 Marcus Webb:** I want this fixed, but I want to understand it, so I can build the next one myself. Next I want a routine for weekly vendor updates.

**00:36:58 Consultant:** And HubSpot?

**00:37:01 Marcus Webb:** Leaving it in December. Don't bother fixing that one.

**00:37:06 Consultant:** Got it. A few good things before we wrap. The whole folder's in git. The Fathom download script ran cleanly every night in the log. Your notes template is really clear. And it never sends on its own.

**00:37:22 Marcus Webb:** That's a relief.

**00:37:25 Consultant:** I'll write it up with what's working, what to fix first and a roadmap, and we'll walk through it together. You'll have it within a week.
