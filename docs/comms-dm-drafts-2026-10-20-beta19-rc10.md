# DM draft: beta.19-rc10 to Steven (2026-10-20)

**Status: SENT 2026-10-20T12:52:02.385Z** as one bubble on Christian's go, after a quiet pre-send fetch (12:50Z). The two photos followed as `m.image` through the Matrix media API at 12:52:42.183Z (`mxc://reddit.com/0w1nte42dmwh1`) and 12:52:46.001Z (`mxc://reddit.com/4xafmmi2dmwh1`). Verified in the room and by `fetch-dms.sh` (one copy each). DM watermark now `2026-10-20T12:52:46.001Z`. Was: DRAFT, NOT SENT. The photos, in order:
1. `docs/research/batch-o-device-2026-10-20/shots/o-rest-icons.png`: Corner at rest, the bare Home icon.
2. `docs/research/batch-o-device-2026-10-20/shots/o-open-labels.png`: Corner open, Labels Shown.

SlopMonster: the DM text below the line lints 5/5 CLEAN (419 words). No cleanse pass: Codex quota is out until 10-29.

Pre-draft fetch at 2026-10-20T12:30Z: one new message since the last read. At 22:17:40Z Steven confirmed the loading-screen titles now show in his language (BUG-184). The DM watermark stays `2026-10-19T21:02:45.018Z` until a send; the last event read is 22:17:40.524Z.

Facts behind it:
- **rc10:** build 142 `1bf7866aa`, tag `tvos-v0.3.0-beta.19-rc10`, from `tvos-shared-extraction` `b40985264` plus the build bump. Outer pointer `53159fb`.
- **IPA:** 29,940,249 B, sha256 prefix `577d62e96a7f376e`. Litterbox failed 3 times (it returned an HTML page). Filebin until 2026-10-27, size checked against the bin's JSON; gofile backup.
- **Over rc9 (build 141) it adds:**
  - **Batch L:** next episode matched by infoHash in season packs; Simkl and MDBList library titles localized.
  - **Batch M:**
    - BUG-153: the ring-on Detail cost, re-measured at 17.5 against rc7's 16.9.
    - BUG-185 to BUG-192.
    - FEAT-61: Synopsis Length removed.
    - FEAT-82: square Detail buttons.
  - **Batch N:** Corner position; N2 row heading; N3 Up replay.
  - **Batch O:** Corner redone as the Centre pill.
- **Settings changes:**
  - Settings › Home Screen › Synopsis Length is removed. Classic shows up to 4 lines where they fit, fewer at Large.
  - Settings › Appearance › Rail Position is now Centre / Corner (Corner replaces Top, and a saved Top becomes Corner). Default Centre.
  - No other new settings.
- **Not confirmed on hardware:** BUG-191 (the UI leg passed; Test 2 has no collection row above its last rows); BUG-186 is code hardening, not his exact case. The DM asks him about both.
- **Still open from his rc9 report**, not in rc10, so the DM doesn't promise them:
  - BUG-181: Animals thumbnails.
  - BUG-180, menu half: the menu-opening animation.
  - BUG-178: the shadow moving up.
  - FEAT-81: the Detail redesign.
  - FEAT-73: one general catalog in Discover, and the Browse tab's smoothness.
  - UX-16 / UX-17: Home's responsiveness, and the poster tips from the row below.
- **Checked against the rc9 DM's fixed list:** none of the still-open lines repeats a shipped fix.

---

Hi Steven, rc10 is ready: https://filebin.net/nuviotv-beta19-rc10-46655ff4/NuvioTV-beta19-rc10.ipa (build 142). Backup link: https://gofile.io/d/2X9Rp5yW

Thanks for the long rc9 report and the video, they helped a lot. Good to hear the loading screen titles are in your language now.

From your rc9 notes:
- Big Detail pages scroll like rc7 again with the focus ring on. The ring on episodes, seasons and trailers was the slow part.
- Classic collections in Rows now show the focused title's poster, logo and synopsis under the collection header, and each row's heading shows.
- Synopsis Length is gone. Classic shows up to 4 lines where they fit, fewer at the Large poster size.
- The "more" on the synopsis is gone too.
- Back from an actor or a More Like This title lands on that card, not on Play.
- Leaving the built-in or an external player takes you straight back to where you started, with no logo or loading screen in between.
- Discover's menus and the standard genre names follow your language.
- After Back from a collection, the card you land on no longer flickers, and an Up pressed right after still moves.
- I fixed a cause of the collection posters showing in the bottom rows with No Zoom on, but I couldn't make it happen on my TV. Tell me if you still see it.
- With Corners set to Square, Detail's buttons are square too.
- The player's top panel can't get stuck anymore, as far as I can tell. If it happens again, which player were you in, and what did you press?

The top-left rail, from your mock-up: Settings › Appearance › Rail Position › Corner (Centre is still the default; a saved Top becomes Corner). At rest it's just the Home icon in the corner, with no box. Menu opens the same rail as Centre, growing down from the Home icon, with icons only or icons and labels. I kept the glass around the icons, like the Centre rail, rather than filling the corner. Photos attached. Does that work for you?

Also new: auto-play of the next episode finds the right file in a season pack from the same torrent, and Simkl's lists and the MDBList Watchlist in the Library show their names in your language.

Still on my list: Animals thumbnails, the menu-opening animation, the shadow that moves up, the Detail redesign you described, one general catalog in Discover, the Browse tab's smoothness, and Home's responsiveness and the poster tips from the row below.
