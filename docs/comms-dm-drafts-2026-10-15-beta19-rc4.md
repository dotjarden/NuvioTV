# DM: Steven, beta.19-rc4 (2026-10-15) — SENT 22:04Z + 22:10Z on Christian's go (ego-browser space 18, both bubbles verified in the room)

Build 136, tag `tvos-v0.3.0-beta.19-rc4`, from `tvos-shared-extraction` at `943030ea4` (+ the bump). Carries Search & Discover, player P1–P3 and Batch A (his rc3 items and the 10-08/09/14 follow-ups). Two bubbles. Link filled from the cut: filebin until 2026-10-22, gofile backup https://gofile.io/d/NvIR1ioT, IPA 29,224,927 B. SlopMonster: lint 5/5 (below), Codex cleanse skipped (quota).

---

Hey Steven, the new build is up. Install it from here, same way as before: https://filebin.net/nuviotv-beta19-rc4-6d84dd2d/NuvioTV-beta19-rc4.ipa

It replaces whatever copy of my app is on the box. If the other fork uses the same bundle ID it will replace that too, so if it refuses to install, delete the other one first.

This one carries a lot, so here it is by area.

Your reports from rc3 and after:

- Black square on the description page: gone. The title shows as text while the logo loads.
- Trailer tiles in rows: the logo now comes from the same place the big title does, so French and English titles behave the same.
- Collections: opening one hides the top bar and the sidebar, with one row or many, and coming back from a film inside one no longer brings the bar back over the grid.
- Row headings on the new Home: moved down, close to the posters.
- Old Home with the hero on: a collection now shows "Genre · N sources" under its name, next to Open Folder.
- Coming back from a collection or a film: both Homes land on the row and the card you left from. This one needed two fixes on the real Apple TV, so tell me if you still see a jump.
- The white box on the playing trailer card with zoom on: fixed. With zoom off, the ring on that card takes the poster's colour.
- Your add-on with wide posters: the app now reads the shape and draws that catalog as wide cards. I couldn't test it with your add-on, so a photo of that row would help.
- Sidebar: Appearance › Rail has a third option, Hidden. Nothing shows until you press Left from the first card, or Menu. Your current mode is unchanged unless you pick it.
- Profile at launch: Account & Profiles › Profiles › "Open Last Profile at Launch". Off unless you turn it on. Profiles with a PIN still ask.
- Search: a new letter now cancels the requests the previous letters started, and typing no longer redraws the results page. I could not reproduce the cursor sitting a letter behind on my box, so please tell me whether it still does on yours.

Also new in this build:

- A Discover tab, with the Home-style layout per genre, and a Search page with grouped results and people. Appearance › Navigation › Discover picks where it sits (its own tab, under Search, or off).
- The player: a new transport bar with preview-then-commit seeking and swipe to scrub, an aspect pill, a chapter list, and thumbnails while you scrub. Thumbnails are on by default (Settings › Developer › Seek Preview Frames). If you see any stutter during playback, set it to Off and tell me.

Not in this build: the switch for add-on names and source counts on headings, the collection title position, the speed and the background wash, French text on English catalogs, the description page changes, and the app opening on Streaming Services. I could not reproduce that one yet. If it still happens after a full close, a photo of what it opens on helps.
