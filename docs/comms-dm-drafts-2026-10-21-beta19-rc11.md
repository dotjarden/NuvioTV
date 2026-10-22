# DM draft: beta.19-rc11 to Steven (2026-10-21) — SENT

**Status: SENT 2026-10-21T07:48:19.967Z** as one bubble on Christian's go (pre-send fetch 07:47Z quiet; `~/Library/Logs/NuvioDM/rc11-send.js`, gated on our rc10 reply being the newest bubble), verified in the room by the script's walk and by `fetch-dms.sh` (`youngchris2989 (me)`). DM watermark now `2026-10-21T07:48:19.967Z`. Christian's addition before the send: the corner-rail line (he knows it is not yet what Steven asked for and is working on it for the next build). Was: DRAFT, NOT SENT. Links filled from the cut log (`docs/research/cut-rc11-2026-10-21.log`). Pre-draft fetch 2026-10-21T07:29Z: no new message since the watermark `2026-10-20T21:44:28.479Z`.

Facts behind it:
- **rc11:** build 143 `6baddab4`, tag `tvos-v0.3.0-beta.19-rc11`, from `tvos-shared-extraction` `b97c7385e` (Player P5 `44200c23a`, Batch P Wave 1 `3cf873994`, Wave 2 `d2c99e30c`, the translation pass) plus the build bump. Outer pointer `b31a30f`.
- **IPA:** 30,132,873 B, sha256 prefix `0121632b697aaa1c`. Filebin until 2026-10-28 (size checked against the bin's JSON); gofile backup. Build 6 m 16 s.
- **Over rc10 (build 142) it adds:**
  - **Player P5:** Dolby Vision profile 5 in MP4 plays in the Apple TV player (BUG-166); Sync Line (pick the spoken line to set the subtitle delay); Audio Mode Off / Dialogue and a Boost (0–10 dB); per-show speed memory; an add-on's audio-delay hint as the Reset value; a More Like This row on the end screen.
  - **Batch P Wave 1:** Rail Style Floating / Edge; square Detail buttons that are really square and equal (Square corners + Icons Only); four synopsis lines at Medium+ (five with Open Sans); the synopsis screen on the page's own backdrop; the folder page's title block; Back from an actor lands on that card in one move (BUG-194).
  - **Batch P Wave 2:** Plugins: one row per provider, collapsible repositories, Remove behind a confirmation, A–Z (GitHub #7); the background trailer stops when Play is pressed on a series (GitHub #8); Search shows its field from the first frame (BUG-195); the Icons Only rail pill is a lighter glass (BUG-196); the Home strip rebuilds far less per press — on the rig the walk's hitch time is down about a fifth and the long stalls are halved (UX-16, partial; never quote a hitch count).
- **New settings and defaults:**
  - Settings › Appearance › Rail Style: Floating (default) / Edge. Shown in Rail mode.
  - Player panel › Audio › Audio Mode: Off (default) / Dialogue. Player panel › Audio › Boost: Off (default), up to +10 dB.
  - Player panel › Playback › Remember Speed for This Show: Off (default), series only.
  - Player panel › Subtitles › Sync Line: a button next to the delay, no setting.
  - No other new settings. Settings › Sources › Plugins is laid out differently (rows per provider), no new keys.
- **Not confirmed on hardware:** the Search placeholder's look on a TV (the timing is proven; the frame was never captured on the rig); his Open Sans + Medium+ synopsis (five lines on the rig).
- **Still open from his rc10 report**, not in rc11, so the DM doesn't promise them: BUG-153 / UX-16's remaining Home cost (Card Depth is the next target), FEAT-66 (collection logo on the right), BUG-181 Animals thumbnails, BUG-180's menu animation, BUG-178 the shadow, FEAT-81 the Detail redesign, FEAT-73 one general catalog in Discover.
- **Checked against the rc10 DM's fixed list:** none of the still-open lines repeats a shipped fix.

SlopMonster: the body below lints 5/5 CLEAN (376 words, 5/5 again after the rail line). Cleanse skipped (Codex quota out until 10-29).

---

Hi Steven, rc11 is ready: https://filebin.net/nuviotv-beta19-rc11-5c9698e0/NuvioTV-beta19-rc11.ipa (build 143). Backup link: https://gofile.io/d/QC76sKRB

Thanks for the rc10 report and the second video. This one is bigger than usual, so here is what to look for.

From your notes:
- Settings › Appearance › Rail Style: Floating keeps the pill a little in from the edge (that stays the default), Edge sets it flat against the left of the screen. Works in Centre and Corner.
- With Icons Only the collapsed pill no longer goes near-black over a dark hero. It is a lighter glass now.
- I know the corner rail still isn't quite what you asked for. I'm working on getting it right for you in the next build.
- Detail's buttons with Square corners are square and all the same size.
- Four synopsis lines at Medium+, five with your font. Tell me if that is too many.
- The synopsis screen sits on the page's own backdrop instead of the blur.
- Back from an actor lands on that card in one move.
- Search no longer opens on a black screen. The field is drawn from the first frame and the keyboard arrives over it.
- Home: the strip does much less work per press now. On my rig the Down walk's stall time is down about a fifth and the long stalls are halved. Not fixed, better. The next cost is Card Depth, which is where I go next.

Player:
- Dolby Vision profile 5 MP4 files play in the Apple TV player now, no more mpv for those.
- Subtitles › Sync Line: press it while a line is spoken, pick that line from the list, and the delay is set.
- Audio › Audio Mode Off / Dialogue (Dialogue raises voices), and Boost up to +10 dB. Both off by default.
- Playback › Remember Speed for This Show, off by default, series only.
- If an add-on sends an audio delay for a stream, Reset goes back to that value.
- The end screen shows a More Like This row.

From GitHub: plugin providers can be switched one at a time, and the background trailer stops when you press Play on a series.

Still on my list: the collection logo on the right, Animals thumbnails, the menu-opening animation, the shadow that moves up, the Detail redesign, one general catalog in Discover, and the rest of Home's responsiveness.
