# Steven's beta.19-rc6 verdict, 2026-10-18

Source: Reddit chat with u/mrStevenx3, read 2026-10-18 19:31Z by `scripts/reddit/fetch-dms.sh --since 2026-10-18T12:40:40.401Z`.
- 14:16:53Z: the verdict text.
- 14:16:56Z–14:17:22Z: five photos, saved in `docs/research/steven-beta19-rc6-photos-2026-10-18/` (`*.small.jpg` = 1400 px copies).
- 17:30:57Z: one follow-up request.

New DM watermark: `2026-10-18T17:30:57.957Z`.

Build: beta.19-rc6 (build 138). rc6 carries the rc5 promises batch, the focus + performance pass and FEAT-78 Native Player. It does not include BUG-170, Batch E, the mpv queue-stall fix or BUG-171; those were merged after the cut.

His overall line: "this update is really good". Detail pages are where he notices the biggest improvement.

## Confirmed working

| Item | His words (paraphrased) |
|---|---|
| BUG-146 / B11 heading positions | "perfect overall"; the only small issues are on landscape rows (below) |
| BUG-162 landscape poster sizes in his add-on | all good, works as expected |
| BUG-173 collection name once | appears only once, perfect |
| FEAT-64 watched checkmarks | there and working |
| FEAT-78 Native Player | works well; on return, Continue Watching updates properly |
| Focus + performance pass | biggest gain on Detail pages: heavy pages that lagged now run smoothly. Home is slightly better, but still not as smooth as the old Home (Classic) |

## New items

1. **Landscape card z-order.** A focused landscape poster's right edge is drawn *behind* the poster to its right instead of in front of it.
   - Photo 1 (the playing trailer card in "Nouveaux films (Films)", his Prime Video add-on): the card's right edge sits under the "Live Stream from Hell" card.
   - Photo 3 (My Happy End focused): its right edge sits under L'Amour de ta vie.
   - Likely cause: the focused or expanded card lacks a raised `zIndex` over later siblings in the `LazyHStack`, so the later card wins.
   - He says it happens "both in collections and inside them".
2. **Too much space under landscape rows.** "The titles in the bottom row sit too low, probably to leave room for the trailer preview."
   - Photos 1–3: a large empty band between the landscape row and the next heading ("Top 10 des films (Films)", "Studios" in photo 4).
   - The row reserves the morphed trailer card's height at rest.
   - His two options: keep the headings up and push them down only while the trailer plays, or don't enlarge the poster when the trailer starts.
3. **Native Player loading screen.** While the movie loads in Native Player there is an unattractive grey screen. He asks for Nuvio's pulsing loading animation during that time, switching to Native Player once the movie is ready.
   - Feasibility caveat: the grey screen belongs to the external app after the hand-off.
   - What Nuvio controls is only how long its own loading overlay stays up before the hand-off. Ties into FEAT-77 (pulsing-title loading, D18).
4. **Home smoothness vs Classic.** The Stage Home is better than rc5 but still less smooth than Classic. Ties into UX-16 (1) / B16 (speed A/B) and the rest of the master plan's Stage polish.
5. **Collections layout on Classic Home** (17:30Z): "add the option to arrange collections (in rows or a grid) on the 'classic' home screen". Overlaps FEAT-61 (b) and FEAT-71 (Collections Layout moved into Settings in B7). Check what B7's setting already covers on Classic before treating this as new work.

Photo 5 (Classic Home, Continue Watching with Spider-Man: Brand New Day) and photo 4 (the "Services de Streaming" folder row under a Netflix poster wall) show the same large gap above the next heading ("Nouveaux films !", "Studios").

## Next

- Reply DM SENT 2026-10-18 19:39:59Z (`docs/comms-dm-drafts-2026-10-18-rc6-reply.md`).
- The next build (rc7) can carry Batch E, BUG-170, the mpv queue stall fix and BUG-171. Item 1 (z-order) and item 2 (row gap) are small enough to fold in first.

## Follow-up 2026-10-18 19:47Z

On the wide-poster trailer: he prefers the poster **not** enlarging when the trailer starts. The Apple TV focus lift already enlarges the focused poster (his second photo), which he finds enough: simpler, no risk of shifting or bouncing, and better looking. rc7 (built before this message) still grows the card; the rc7 DM says we'll look at keeping it at the poster's size for the next build (D16 reversal: play the trailer at the rest size on shape-landscape rows).
