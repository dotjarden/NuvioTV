# DM draft: beta.19-rc12 to Steven (2026-10-22) — DRAFT, NOT SENT

**Status: NOT SENT.** Written before the cut; `<LINK>`, `<BACKUP>` and `<BUILD>` are filled from the cut log. Send only on Christian's go, after a quiet pre-send fetch (`fetch-dms.sh --since 2026-10-22T02:12:42.971Z`). Since his 10-21 23:04Z message his feedback is general-use feedback, so the DM is shorter and asks for nothing beyond what he offered.

Facts behind it (all on `claude/wave3-all`, gated, device pass owed before the cut):
- Corner rail per his spec: flush top-left, opens downward only (W3-11).
- Detail icon sizes: the three glyphs he could see differ measured 28 / 25 / 20 pt on the rig in his settings; now one size. Start Over and Shuffle still to be measured on the box.
- Back from an actor: rc11 did NOT fix it (the rig's "fixed" was the studios row). The real mechanism: focus lands on the actor's card, the system's own late focus restore pulls it up to Play for a quarter second, then it comes back. Fixed in code; the DM says "found and fixed" only if the device pass shows `away≤50` and the recording shows no Play highlight; else "found, fix in testing".
- Cinematic Detail choppier: CONFIRMED as a regression (rc7 5 hitches vs 65 now, same walk). Cause being hunted (`docs/research/bug206-cause-hunt-2026-10-22.md`). The DM says it is measured and real; promises nothing dated.
- Card Depth: three cheaper renderings behind a switch; the R1 walks pick one before the cut. The DM names it only if one ships.
- Classic Home: heading drop fixed (BUG-209); catalog name under the logo gone, logo larger (BUG-211, his ask); the logo-over-old-text frame could not be reproduced with cached art (BUG-210), camera blend likely.
- Search: Cinemeta search retried once and a failed state shown (BUG-208); voice search filed with it.
- Stream picker: rows rebuilt cheaper; a row now expands after half a second of rest, not at once (a visible change: say it).
- Watched / In Library icons: colour on the glyph, no lag; Shuffle shows a filled symbol when on.
- First Down on Detail: the glide now takes its time from the distance.
- Hold menus on seasons and episodes (GitHub ask, FEAT-83).
- New settings, defaults: Settings › Subtitles & Audio › **Fallback Audio Language** = None; **Fallback Subtitle Language** = None (hidden while Subtitles is Off); the language lists are now 78 languages A–Z on their own page. Rail Style row hidden while Rail Position = Corner (it has no effect there). No other new settings.
- Native player: the remux failure on the Netflix DV MP4 fixed (BUG-199); his Animals / Spider-Man question still open (mpv at once vs after seconds).
- BUG-165 (short Back ejects the player): four presses on rc11 did not eject on the rig; ask him to confirm on his remote.
- README now documents `local.properties` (promised 02:12Z).
- No numbers, no dates, no redesign promise (D2: after beta.19).

SlopMonster: the body below lints **5/5 CLEAN** (434 words, first pass); cleanse skipped (Codex quota out until 10-29).

---

Hi Steven, rc12 is ready: <LINK> (build <BUILD>). Backup link: <BACKUP>

From your notes:
- Corner rail: it sits against the top and the left edge now and opens downward. Centre is unchanged.
- The three icons next to Play are one size. They were drawn at three sizes before, which I only saw once I measured them in your setup.
- Back from an actor: you were right, and rc11 had not fixed it. Focus lands on the card, then the system's own focus restore pulls it up to Play for a moment, then it comes back. That is the second move you saw. <It is fixed in this build | I have a fix for it in testing>.
- The description page getting choppier: measured, and it is real. The same walk that stalls five times on rc7 stalls sixty-five times now. I am tracking down which change did it.
- Classic Home: the row heading no longer lands high and drops; the catalog name under the logo is gone and the logo is bigger, as you asked. The logo-over-old-text frame I could not reproduce; it may be the phone blending two frames.
- Search: a search that comes back empty is retried once, and when it still fails you see that instead of an empty page. Voice search is filed with it.
- The stream list is lighter, and a row now expands half a second after you rest on it instead of at once.
- Watched and In Library change colour on the icon itself now, so they recover at the same speed as the others. Shuffle shows a filled icon when it is on.
- The first Down on the description page eases in instead of jumping.

New in Settings › Subtitles & Audio: Fallback Audio Language and Fallback Subtitle Language, both None by default, and the language lists are 78 languages in alphabetical order on their own page. Seasons and episodes have a hold menu for marking watched.

Player: the Netflix Dolby Vision file that fell over to mpv a few seconds in plays through now. If you can tell me whether Animals opens in mpv from the first frame or switches after a few seconds, that still decides where I look next. And one small check when you have a minute: a short Back press in the player on your remote, since I cannot make it eject here.

The README now explains the local.properties file for anyone building from source.

Nothing in this build is the redesign; that stays a question for after this release.
