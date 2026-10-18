# DM draft: reply to Steven's beta.19-rc6 verdict (2026-10-18)

**Status: SENT 2026-10-18 19:39:59.706Z** as one bubble on Christian's go, as drafted. The pre-send fetch found nothing newer than his 17:30:57Z message. Verified in the room (the bubble starts and ends as drafted, 1,779 chars) and by `fetch-dms.sh` (one copy). DM watermark now `2026-10-18T19:39:59.706Z`. Was: DRAFT, NOT SENT. SlopMonster lint 5/5. Codex cleanse skipped: Codex is out of quota until 10-29. Answers his 14:16Z verdict, its five photos and his 17:30Z request (record `docs/steven-beta19-rc6-verdict-2026-10-18.md`). Before sending, fetch the room against the watermark `2026-10-18T17:30:57.957Z` and amend the draft if he wrote again.

Facts behind it:
- Merged since rc6, so in the next build, none of it cut yet:
  - BUG-170 HDR start on mpv;
  - Batch E (Top Shelf progress bar, the speed-ups, the BUG-156 one-move return, device-passed in Test 2);
  - the mpv queue stall fix: 112 add-on subtitles loaded one at a time held the player's work queue for 2+ minutes, so there were no thumbnails and HDR came late or never on Dune, a DV profile 5 file like Animals; 4 of 4 runs pass on the TV;
  - BUG-171 "No subtitles" on mpv.
- Collections Layout (Rows / Grid) only shows with the new Home today; Classic always opens collections as a grid (B7 note).
- The Native Player grey screen is that app's own loading screen after the hand-off. Nuvio can't draw over it.

---

Hi Steven, thanks, glad rc6 feels better! Your photos made the wide-poster issues easy to see.

Fixed since rc6, coming in the next build:
- HDR on mpv: the TV now switches to HDR before the film starts, not partway in.
- Animals: I think I found why mpv showed no thumbnails and HDR came late. On Dune, which is the same kind of Dolby Vision file, mpv was loading every add-on subtitle one at a time (112 of them), and that blocked the player's other work for over two minutes. That's fixed, and on Dune thumbnails and HDR now arrive in the first seconds. Tell me if Animals behaves the same.
- "No subtitles" on mpv now really turns subtitles off.
- Going back from a collection to Home lands in one move, without the jump.
- The Top Shelf shows a progress bar for things you're partway through.

From your list:
- The wide poster going behind its neighbour: I can see it in your photos, the focused card should sit on top. I'll fix that.
- The gap under rows of wide posters: the row reserves room for the bigger trailer card even when nothing is playing. I'm looking at your first option, headings that stay up and only move down while the trailer plays.
- Native Player's grey screen: that one belongs to Native Player itself. Once Nuvio hands the film over, Native Player draws everything, so I can't put our loading animation on top of it. I'll check whether the hand-off can happen a little later, so less of that grey shows.
- Home smoothness: noted. The new Home still has a speed and smoothness pass coming, and I'll compare it against Classic.
- Collections as rows or a grid on Classic: right now that setting only appears with the new Home, and Classic always opens collections as a grid. Adding it to Classic is on my list.

Thanks again for testing so thoroughly!
