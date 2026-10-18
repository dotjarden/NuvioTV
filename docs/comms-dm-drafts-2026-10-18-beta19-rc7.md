# DM draft: beta.19-rc7 to Steven (2026-10-18)

**Status: DRAFT, NOT SENT.** SlopMonster lint 5/5; Codex cleanse skipped (out of quota until 10-29). IPA: litterbox, 72 h (until about 2026-10-21 21:40Z), 29,562,852 B. Cut 2026-10-18: build 139 `21f618df`, tag `tvos-v0.3.0-beta.19-rc7` pushed, outer pointer `b3f52cd`. Before sending, fetch the room against the watermark `2026-10-18T19:39:59.706Z` and amend the draft if he wrote again.

Facts behind it:
- rc7 = build 139, tag `tvos-v0.3.0-beta.19-rc7`, from `tvos-shared-extraction` (Batch F tip `b11140ecd` + the build bump).
- Over rc6 it adds:
  - BUG-170 HDR start on mpv (`0980c8ec8`);
  - Batch E (Top Shelf bar, speed-ups, BUG-156 one-move return; `67c928e7d`);
  - the mpv queue-stall fix and BUG-171 (`619f85cef`);
  - Batch F (`b11140ecd`).
- Batch F device-checked in Test 2, Christian watching for the last three:
  - wide-card z-order in ring mode;
  - the pulsing loading title;
  - Classic Rows + the folder hold menu;
  - Search on one letter;
  - fit pages on Home and in a folder;
  - a wide trailer row as Home's last row.
- Native Player's grey screen is that app's own; Nuvio can't draw over it after the hand-off.
- New settings and defaults:
  - Collections Layout on both Homes (Rows on the new Home, Grid on Classic);
  - a folder's own layout from its hold menu (Default);
  - Developer › Short Rows Fit (On);
  - Developer › Home Speed (Standard).

---

Hi Steven, rc7 is ready: https://litter.catbox.moe/ycyaju.ipa (build 139).

Everything I said was coming last time is in:
- HDR on mpv: the TV switches to HDR before the film starts.
- The fix for mpv thumbnails and late HDR on Dolby Vision files like Animals. Could you check Animals again on mpv? Thumbnails should show up within the first seconds, and the HDR switch should happen before the picture.
- "No subtitles" on mpv now turns subtitles off.
- Going back from a collection to Home lands in one move.
- The Top Shelf shows a progress bar for things you're partway through.

From your rc6 list:
- A focused wide poster now sits on top of its neighbour instead of sliding behind it.
- The gap under rows: each row is now only as tall as its cards, so the next heading sits right under wide posters, Continue Watching and collections. A wide poster's row grows only while its trailer plays, then shrinks back. If you prefer the old spacing, it's under Settings › Developer › Short Rows Fit (on by default).
- The loading screen in Nuvio's own player now shows the title logo in the middle, slowly pulsing, like the official apps.
- Native Player's grey screen: once Nuvio hands the film over, Native Player draws everything until it starts playing, so I can't put our loading animation on top of it, sorry.
- Home smoothness: Settings › Developer › Home Speed has Standard, Faster and Fastest. Pick one, then close and reopen the app. Tell me which feels best and I'll make it the default.
- Collections on Classic: Settings › Home Screen › Collections Layout now works on Classic too (Grid stays the default there). You can also hold any collection on Home to give it its own layout, Rows or Grid, which covers your Genres-as-a-grid idea.

Also new: Search waits for a second letter before searching, and a slow add-on no longer holds the results.
