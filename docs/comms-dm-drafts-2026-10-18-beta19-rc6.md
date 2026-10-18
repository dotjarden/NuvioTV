# DM draft: beta.19-rc6 to Steven (2026-10-18)

**Status: DRAFT, NOT SENT.** SlopMonster lint 5/5 on the body. Codex cleanse skipped: Codex is out of quota until 10-29. IPA link: litterbox, 72 h (until about 2026-10-21 12:15Z), size-checked at 29,513,577 B. Before sending, fetch the room against the watermark `2026-10-17T11:33:35.807Z` and amend the draft if he wrote again. It answers his rc5 verdict follow-ups (the 06:08Z reply's promises) and his 11:33Z message (HDR is on mpv; add Native Player).

Facts behind it:
- rc6 = build 138, tag `tvos-v0.3.0-beta.19-rc6`, from `tvos-shared-extraction` `f2718d7bc`.
- Over rc5 it adds:
  - the rc5 promises batch (`523ad97db`);
  - the SwiftUI Pro review fixes (`9ee8597d4`);
  - the focus + performance pass (`2353a5e9b`);
  - the follow-up batch and FEAT-78 (`f2718d7bc`).
- Heading gap: ≈64 pt → ≈30 pt, measured on the rig in his config. The cards are top-aligned; they used to be centred, so they sank when the trailer card grew.
- Native Player is untested on our box (not installed).
- HDR on mpv: the display mode is requested only after the first frame decodes, which is the BUG-170 candidate. It is not in this build.

---

Hi Steven, rc6 is ready: https://litter.catbox.moe/83imiz.ipa (build 138).

From your rc5 list:
- Headings sit closer to the posters. The gap is about half what you had. The real cause was the posters being centred in the row, so they dropped every time the trailer card grew. I checked it on my TV with your settings.
- The wide posters from your add-on rest at the size of your collection tiles and grow to the big size when the trailer starts.
- A collection's name shows once.
- On the Apple TV player, a paused scrub shows only the time, no empty box.
- Watched titles get a checkmark on Home rows and inside collections.
- Not in this build: the double move when you go back (still on it) and the Animals thumbnails on mpv.

Native Player is in. If you have version 1.1.3 or newer, pick it under Settings › Player › Default Player, or hold a stream and choose "Open in Native Player". When you close it, your position comes back to Nuvio and Continue Watching updates. Two limits on their side: subtitles only go across as SRT, and DASH streams aren't supported, so those play in Nuvio instead. I don't have it on my TV, so you're the first to try it. Tell me if it opens and if the position comes back.

HDR on mpv: thanks, that narrows it down. mpv only asks the TV for HDR once the first frame is decoded, which explains the late switch. The fix is to ask for HDR from the stream info before playback starts and wait for the TV to switch. That's next, not in rc6.

Also in rc6, a pass on remote navigation and smoothness:
- Every button on the profile editor is now reachable with up and down.
- The colour swatches show focus.
- Search, collection pages and Settings no longer strand focus.
- Episodes open on your next unwatched episode.
- The source list keeps focus on the same source while more add-ons load.
- Home, the Detail page and the player redraw less, so they should feel a bit lighter.
