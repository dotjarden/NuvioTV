# DM draft — reply to Steven's beta.19-rc5 verdict (2026-10-17)

**Status: DRAFT, NOT SENT.** SlopMonster 5/5 on the body (one hit, "landscape", rewritten to "wide posters"); Codex cleanse SKIPPED: `cleanse.sh` exited 1 with no output although `codex login status` reports logged in. Answers his 03:05Z verdict + 3 photos and the 03:15Z add-on (record
`docs/steven-beta19-rc5-verdict-2026-10-17.md`). One bubble. Fetch the room against the watermark
(`2026-10-17T03:15:17.266Z`) right before sending; amend if he wrote again.

Facts behind it: B6 (BUG-146) shipped in build 137 and moved heading → posters 28 → 24 pt; B4 (BUG-162) made a
landscape card the trailer tile's size, 624 × 351 at Medium+, and a landscape collection tile is 416 × 234 at
Medium+ (`FolderTile`); the title-twice line is the folder's stage meta line (`collection.title`) above a row
heading with the same text (BUG-173, root-caused); the return detour is the focus engine's own late restoration
moving the row before the app's correction (BUG-156, cause known, fix is medium); native preview boxes are empty
because Apple's player never asks for a preview frame while paused on tvOS 27 (P3 spike); the HDR delay has a
candidate cause on mpv only (display mode requested before mpv knows the colour format), engine unknown
(BUG-170); the watched tick is Library-only, never on Home (FEAT-64); BUG-143 came from a device session.
Promises kept to what is root-caused and small: the heading move, the title shown once, no empty native preview
box. Landscape rest size is his own ask and stated as the plan; the rest is "working on it" or "noted".

---

Hi Steven, thanks for going through rc5 so quickly, and glad the headings, the opening of collections, Best Result, the No Zoom posters and the colours are where you want them. Good news on the white outline too, though I didn't target it directly.

Headings: you're right that you can't see a change. rc5 moved them 4 points, which is too little to notice from the sofa. The next build halves the remaining gap between the heading and the posters, and I'll check it on my TV with your settings (Medium+, titles hidden, zoom on, Card Depth on) before sending it.

The wide posters from your add-on: going from too small to too big was me overcorrecting. Your suggestion makes sense, so that's the plan: at rest they'll be the same size as your collection tiles (at Medium+ that's about two thirds of what you see now), and they'll grow to the big size when the trailer starts, the same way portrait posters do. That also brings the heading down on those rows, since the cards will sit right under it.

The title shown twice: found it. When a collection is focused, the area at the top prints the collection's name under its logo, and the row heading right below says the same thing. The next build drops the one at the top, so the name appears once.

Going back to a film or to Home: the app now lands where you were, but you see two moves because tvOS first puts focus on its own default spot and the app then brings it back. I know where that comes from and I'm working on holding the first move so you only see the return. It's a bigger change than the others, so I won't promise it for the next build.

Thumbnails: the Animals case on mpv is next on my list, on the same kind of file. The transparent box on the Apple TV player comes from tvOS itself: when the film is paused, Apple's player never asks for a preview picture, so the box stays empty. The next build won't show an empty box there, only the time.

HDR starting late: I'm looking into it. Which player were you on when it happened? The info panel line starts with "Native" or "mpv".

Watched checkmark: you didn't imagine it, it's planned but not built yet. Today it only shows in the Library. It's in the next batch for Home and collections.

The link failures over the network: that was a general change in the app, not something you reported, so nothing to check.

A layout per collection (Genres as a grid, the rest as rows) and the pulsing title on the loading screen are both noted as requests. No need for a video, I know the effect from the official app.

SenPlayer: no problem, Infuse is the one that matters for you.
