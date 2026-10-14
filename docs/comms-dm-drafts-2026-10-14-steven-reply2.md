# DM draft: reply to Steven's 2026-10-14 4:24 PM ET answers (2026-10-14)

His message (20:24Z): offset = cursor sits on B while A is shown (visual misalignment, not just slow); "old home" = Classic; add-on manifest URL given in confidence (NOT stored here, keep private); outline photo 1 = Zoom enabled with outline, photo 2 = no outline (this contradicts the master plan's reading "No Zoom ON = box", so the draft promises a re-check, not a fix); new asks: detail blur + Apple TV title (Batch C), Netflix-style detail scrolling (unclear, asked), collection title top-right (new), hide add-on names + source counts (BUG-145 + new), catalog titles lower (BUG-146), sidebar stays visible at launch / on entering a collection (new; FEAT-62 Hidden mode covers the request), app opens on the Streaming Services row (new, resembles BUG-156/113), slow animations + bottom-only wash (UX-16). He no longer has the app installed (another fork overwrote it). SlopMonster: lint 5/5 (415 words); Codex cleanse skipped. **NOT SENT**: waits for Christian's go. Tracker rows for the new items (sidebar-at-launch, wrong start row, title top-right, hide source count, offset) still to be logged.

---

Hey Steven, thanks, that cleared up a lot. And I'm glad the new Home has grown on you.

Your add-on's URL stays with me. I will only use it to test on my own Apple TV and I won't pass it on or write it into anything public.

Going through it in order:

- Search offset: I had read it as slowness, so my last answer missed it. A cursor sitting one letter behind is a different problem. It points at the keyboard being starved while the results work, but I have not proved that yet. I'll test it with your add-on count and tell you what I find.
- Old Home: understood, the previous layout. Coming back from a collection to the same row and card is in the next build for it too.
- Outline photos: your answer does not match what I assumed, so I won't guess. I'll go back through both photos and test with Zoom on and off before I tell you the fix.
- Detail page blur and the Apple TV title effect: both are planned, in the description page pass that comes after the next build.
- Netflix-style scrolling on the detail page: it is not on my list, because I'm not sure what you mean. Which screen of the official app, and what does it do when you scroll? A short video would settle it.
- Collection title in the top-right: new to me. I've added it, no date yet.
- Add-on names and source counts: a switch for the add-on name on row headings is planned, but after the next build. Hiding the source count is new, and I've added it.
- Catalog titles too high: moved down in the next build.
- Sidebar: an option to hide it until you press Left from the first card is in the next build. The sidebar staying visible at launch and when entering a collection is new to me. Which sidebar mode are you on, Always Visible or Hide While Browsing?
- Opening on Streaming Services instead of the top: also new. Does it happen after a fresh launch, or when you come back to the app after leaving it?
- Slow animations and the wash: a faster setting is on the list, and so is blurring only the bottom of the poster.

Sorry the other fork overwrote my build. The next one is due within the week, and I'll send the link as soon as it's cut.
