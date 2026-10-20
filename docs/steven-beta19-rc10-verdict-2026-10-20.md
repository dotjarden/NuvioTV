# Steven's beta.19-rc10 verdict, 2026-10-20

Source: Reddit chat with u/mrStevenx3, read 2026-10-20 19:18Z in the interactive session (`fetch-dms.sh --since 2026-10-20T12:52:46.001Z`).
- 16:09:19Z: the verdict, one long message, followed by 5 photos (16:09:22–25Z).
- 16:53:05Z: a remark on the built-in mpv player (no Dolby Vision, no Atmos).
- 17:40:25Z: the collection-logo placement ask again (FEAT-66), with 1 photo.
New DM watermark: `2026-10-20T17:40:28.256Z`. Photos saved in `docs/research/steven-beta19-rc10-photos-2026-10-20/` (1280 × 960, straight from `i.redd.it`).

Build: beta.19-rc10 (build 142, `1bf7866aa`: Batches L + M + N + O over rc9). His overall line: smoothness is "even worse in this version than before", everything "sluggish and unresponsive", the Stage Home and the side menu animations "feel like they're running at 20 fps".

## Photos
- **Photo 1** (`photo-1-hycqr5b5cnwh1.jpeg`): the official Nuvio app's rail for comparison: a vertical pill column (Accueil, Découvrir, Rechercher, Bibliothèque, Paramètres) flush against the left edge of the panel, vertically centred, the Nuvio logo top-left. His reference for "flush against the edge".
- **Photo 2** (`photo-2-vtryvbd5cnwh1.jpeg`): the full-synopsis screen (Camp Rock 3): the backdrop behind the text is a heavy, blocky blur he calls low quality; the open animation goes with it.
- **Photo 3** (`photo-3-4nnm23e5cnwh1.jpeg`): Home (Stage) with the Centre rail in Icons Only: the pill reads as a flat light grey slab, no glass; his "I lose the transparency effect when the side bar is set to show icons only".
- **Photo 4** (`photo-4-4oqd94d5cnwh1.jpeg`): Detail (Carrie, series) with Corners = Square: "Lire S1E1" is a wide rectangle, the trailer / watched / add buttons are squares of a different width; "not all the same width".
- **Photo 5** (`photo-5-1yjpm2e5cnwh1.jpeg`): the Corner rail open with labels (Accueil … Paramètres, Steven), 16 pt in from the edge; his "still isn't against the edge of the TV".
- **Photo 6** (`photo-6-wicegpcesnwh1.jpeg`, 17:40Z): a Classic-look collection page (Prime Video folder, Rows): the add-on logo sits top-left above the title and synopsis, the rows below. Sent with the FEAT-66 message: he wants that logo on the right. The photo for "the logo sits in the centre" on Classic collections is NOT among the six; ask which screen he meant.

## Confirmed working
- **BUG-185:** no logo on the way out of a film ("that's fine").
- **BUG-189:** Discover in his language ("that's fine").
- **BUG-191:** posters staying visible at the top with No Zoom on: "fixed!".
- **BUG-192:** the "more" is gone.
- Corner rail animation now goes downwards (the one difference he sees in FEAT-80).

## Partly fixed
- **BUG-188:** card flicker after Back from a collection "partly fixed": still now and then on Home in Stage and Classic, "much less than before, so there's a real improvement".
- **BUG-187:** Back from an actor now lands on the card, but in two steps: "the animation goes up and then comes back down onto the card, like it used to on Home" (the engine's first move, BUG-156 / BUG-176 class). Tracked as **BUG-194**.

## Not fixed, not right, or regressed
- **BUG-153, NOT FIXED on his box:** "I still have the focus ring on trailers, episodes and season posters, so the lag on the Detail page is still there." He reads the ring itself as the cause; Batch M measured the cost at 17.5 vs rc7's 16.9 with the ring on. Either the measurement missed his case (his config: accent ring ON, Medium+, Hide Titles) or the remaining lag is elsewhere.
- **BUG-190, NOT RIGHT:** "Collections in Classic mode: the logo sits in the centre instead of the top left (see photo)". No matching photo arrived; ask.
- **FEAT-61, NOT FIXED:** "In Classic mode, I've never had 4 lines of synopsis, always 3 at most. Maybe that's because I'm on the Medium+ size." Batch M's fit logic gives fewer lines at Large; Medium+ should fit 4. Measure on the rig at Medium+ with his font.
- **FEAT-82, NOT RIGHT:** square buttons are not all the same width (photo 4).
- **FEAT-80, NOT WHAT HE WANTS, twice:** (a) the Corner rail is "no different from the previous version apart from the animation now going downwards"; still not flush with the TV edge, which he finds "more natural … whether in the centre or at the top, the way Nuvio does it" (photo 1 vs photo 5). This is the open design conflict: Christian's rule that chrome glass hugs its content and never fills a corner (Batch O) vs Steven's flush rail. (b) Icons Only still loses the glass and goes flat (photo 3; Batch M D2 said screenshot it first).
- **UX-16, REGRESSED again (his headline):** "the app's smoothness is even worse in this version than before … all the animations feel like they're running at 20 fps" (Stage Home, the side menu bar). Raised to P2.
- **The bounce** (Classic, FEAT-61 (a)): still there, "but you already know about that".

## New
- **BUG-193 (P3):** the full-synopsis screen's blurred backdrop looks low quality, and so does its open animation (photo 2).
- **BUG-194 (P3):** Back from a biography lands on the cast card in two visible moves (up, then down onto the card).

## Remarks and asks
- **mpv (16:53Z):** "the built-in MPV player honestly isn't very good. It doesn't play Dolby Vision and switches every film to HDR instead. No Dolby Atmos either." mpv has no Dolby Vision output path (it tone-maps DV to HDR through gpu-next, BUG-166's rc5 fix) and decodes audio to PCM (FEAT-75). The P5 spike (2026-10-20, `claude/player-p5`, not merged) moves his DV profile 5 MP4s to the Apple TV player with real Dolby Vision and E-AC-3 passthrough; the reply can say so, with the Animals test ask.
- **FEAT-66 (17:40Z):** "the logo that goes on the left … put it on the right to avoid overcrowding the left side. For collections in classic mode, leave it on the right since there's a black image on the left and the movie titles are placed lower down." Photo 6.

## Next
- Reply DM owed (through SlopMonster, NOT SENT until the go): thank him; BUG-153 and UX-16 need a profile on his box, so ask for a short video of a Stage Home walk and a Detail scroll with the ring on, and his Appearance settings; ask which screen the "logo in the centre" photo was; say what the P5 branch does for DV MP4s; FEAT-80 is Christian's call to answer.
- Triage into the next batch (Christian's call): FEAT-82 equal widths (S), BUG-194 two-step return (S–M, the BUG-156 pattern on Detail), FEAT-61 Medium+ measurement (S), BUG-190 once the photo is in, BUG-193 blur quality (S), FEAT-80 (a)/(b) design decision, BUG-153 + UX-16 performance work (the real item: a profile on his hardware, not another sim measurement).
