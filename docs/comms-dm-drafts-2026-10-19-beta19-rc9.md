# DM draft: beta.19-rc9 to Steven (2026-10-19)

**Status: SENT 2026-10-19T16:05:00.060Z** as one bubble on Christian's go, after a quiet pre-send fetch (16:04Z). Verified in the room and by `fetch-dms.sh` (one copy). DM watermark now `2026-10-19T16:05:00.060Z`. Was: DRAFT, NOT SENT. IPA: litterbox, 72 h (until about 2026-10-22), 29,826,428 B. Cut 2026-10-19: build 141 `2baa390f`, tag `tvos-v0.3.0-beta.19-rc9` pushed, outer pointer `73918d4`. His rc8 verdict is still owed (DM watermark 2026-10-19T02:59:51.233Z). Fetch DMs right before sending and add a line for anything new. Per Christian 10-19: the DM says his rc8 report isn't in yet and that rc9 carries every rc8 fix, so he can test rc9 for all of them.

Facts behind it:
- rc9 = build 141, tag `tvos-v0.3.0-beta.19-rc9`, from `tvos-shared-extraction` `fb55a50e8` + the build bump.
- Over rc8 (`09b901c20`) it adds Batches H, I, J and K plus UX-16:
  - H: FEAT-79 Classic rows page inside collections (Classic + Rows), focus returns to the card left. BUG-184 localized title logo on the loading screen (both engines). Device-checked in Test 2.
  - I: FEAT-73 Discover grid-first (Type + Genre pills, Browse pill opens the per-genre rows). BUG-151 localized Stage text. Black-poster fix. BUG-147 OLED wash snap. Device-checked in Test 2 (Rail mode).
  - UX-16: wash cap 0.17, max gain 1.25 (Christian on the TV).
  - J: NuvioTV Android ports: language aliases (spn/sp/esp, hbs-*), next-episode filename matching, Trakt CW keeps shows on a failed page, JS plugin `series` type, Top Shelf custom posters.
  - K: MDBList external/dynamic/liked lists (read-only). FEAT-61 Synopsis Length. BUG-153 Detail first-Down stutter (trailer mount deferred, Time Profiler on the TV 305 → 247 ms).
- New settings and defaults:
  - Settings › Home Screen › Synopsis Length: Standard / Long, default Standard, Classic only.
- Still open from rc7: BUG-180 (choppy film behind menus), BUG-181 (Animals thumbnails/Atmos), BUG-182 (logo restarts its pulse), BUG-183 (stream list flashes with auto-select). Not in rc9, so don't promise them.

---

Hi Steven, rc9 is ready: https://litter.catbox.moe/6ukggu.ipa (build 141).

I know you haven't had a chance to report back on rc8 yet, no worries. rc9 has every fix from rc8 too, so you can skip rc8 and test this one for all of them. Tell me anything you see.

New since rc8, from your notes:
- Collections with Classic Home: with the Rows layout, a collection now keeps Classic's look, and going back from a title puts you on the card you left.
- The loading screen's title logo is now in your language, not always the English one.
- Discover opens on a poster grid. Pick Movies or Series and a genre at the top. The Browse pill still gives you one row per genre.
- Catalog text on the Stage now follows your language too.
- The black poster you saw in rc3 should be fixed.
- With OLED True Black on, the background no longer brightens and then snaps darker. I also toned down the grey haze behind the hero.
- The longer synopsis on Classic: Settings › Home Screen › Synopsis Length, Standard or Long (Standard by default). Long shows up to four lines.
- The first Down on a big Detail page (Monstre and the like) should be smoother: the trailer now loads after the page stops scrolling.

Also new:
- MDBList's external, dynamic and liked lists show up in the Library.
- Auto-play of the next episode picks the file from the same release when it can.
- Spanish and Serbian/Croatian/Bosnian audio and subtitle languages are recognized better.
- Continue Watching keeps your shows when Trakt has a bad moment.

Still on my list from rc7: the choppy film behind menus, Animals thumbnails, the logo restarting its pulse, and the stream list flashing with auto-select.
