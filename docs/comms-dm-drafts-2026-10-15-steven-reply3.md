# DM draft: reply 3 to Steven (2026-10-15)

Answers his 23:49Z and 06:40Z / 07:28Z messages: search both halves real; sidebar = Hide While Browsing (bug); Streaming Services start = cold launch only (~85 %); Netflix-style scrolling = Wako fixed-slot row; reinstall question (hedged: bundle-id overlap with the other fork is unknown); Orivio v0.13 view (video watched and re-read against the Detail pass: scrolled compact logo header = FEAT-60; frames in `docs/research/orivio-v0.13-steven-2026-10-15/`); owns the repeats. SlopMonster: lint 5/5 (435 words); Codex cleanse skipped. **SENT 2026-10-15 14:07Z** on Christian's go, verified in the room; watermark moved to 2026-10-15T14:07:24.785Z.

---

Hey Steven, thanks for the answers.

You're right about the repeats. Several things I called new were things you had already told me, and I should have checked our earlier messages before saying so. I've gone back through them now, and what you reported is on my list as one set.

What your answers settled:

- Search: both halves are real, the cursor sitting a letter behind and the slow results. I'm testing both with your add-on count. I'll put the fix in the next build if the test shows it's safe to.
- Sidebar: you're on Hide While Browsing, so it should leave on your first move and when you open a collection. That's a bug, not a setting. Opening a collection is fixed in the next build. The launch case needs its own check, and I'll say what I find.
- Opening on Streaming Services: thanks, closing the app completely narrows it a lot. I'll try to reproduce it that way. If I can, it goes in the next build.
- Netflix-style scrolling: that's the Home row from the Wako clip you sent before, with the first movie staying wide. It belongs to the Home rework, after the next build.

On reinstalling: I can't tell for sure. If the other fork uses the same bundle ID as mine, installing mine will replace it, which is probably what happened to you. If the IDs differ, both will sit side by side. If mine doesn't install cleanly, delete the other one first. I'll check how it behaves when the build is out.

I watched your Orivio clip and read their release notes. The notes never mention titles, but the clip does. When you scroll down the description page, the big logo fades into a small centred one at the top, and the backdrop goes blurred and darker behind the trailers, cast and sources. That's the Apple TV app effect you showed me before, and I think it's what you mean. It is already on my list for the description page, along with the darker area behind the synopsis, and comes after the next build. Their Home row headings are also plain, with no add-on name or source count, which matches what you asked for on ours.

Their full-screen view is a description page where Left and Right slide to the next title's page, with no trip back to the row in between. That is a bigger change than the rest, so it's noted and not scheduled.

The next build is still due within the week, and I'll send the link as soon as it's cut.
