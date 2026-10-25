# D-3: the compact logo steps aside for rows in its band (2026-10-23)

Design review item D-3 (P3, `docs/design-review-2026-10-22.md`): on a scrolled Cinematic Detail page, FEAT-60's compact title logo sat over rows resting under it (the Parental Guide chips under Animals and under The Simpsons).

Branch `claude/d3-compact-logo` in the clone `~/Claude/Projects/NuvioMobile-d3`, tip `c42317365`, eleven commits on `tvos-shared-extraction` `1b2fc99f3`: three for the first build, one per first-round review finding plus two follow-ups, and one for the second round's three P3s. Not merged, not cut.

## The rule

1. The band is the logo's slot: 36 to 108 pt from the scroll view's top (36 pt padding + the 72 pt slot). Its bottom is `DetailRowAnchor.screenRest`.
2. A row's lead runs from its top through `min(height, 112 pt)`: the heading, and for a chip row (Parental Guide, studio logos) the chips too.
3. The band is blocked while any row's lead overlaps it. A lead that only touches its top edge does not count, and neither does a top within 16 pt of its bottom (an anchored row resting at about 108 never hides the logo with its own heading).
4. The band is decided only at the page's true rest and held until then. Crossing the hero clearance holds it blocked until the next rest, even on a still page; back in the hero the logo hides at once. `heroClearance` = 120 is unchanged, and the probe reads `logoBand=hero` before it.
5. The fade is the existing 0.25 s ease on `visible`. Under Reduce Motion there is no animation (unchanged).

## How it is built

- `DetailRowAnchored` already reported each row's content-space top. It now also reports the height from the same `onGeometryChange` read, Cinematic only (Classic passes `heights: nil`), so both change on layout only.
- A row that leaves the hierarchy drops its height. It is re-measured when it reappears, for example after a push or a cover is dismissed, through a generation counter in the geometry reading. The tops (`detailRowOffsets`) keep their entries for the anchor and the pop restore.
- The hero-exit `onScrollGeometryChange` keeps its Bool and only hands the hero edge over (`bandOnHeroEdge`).
- `settleCompactLogoBand` decides the band from `bandAtRest(rows, lastContentOffset)`. It runs:
  - on the `ScrollDimModel.isScrolling` false edge, unless a Down settle is pending (see below);
  - when a Down focus change resolves: its `.free` branch settles at the engine's rest; a down-straddle anchor settles on its glide's own latch edge, or after the task's probe sleep if it did not move the page; an early guard exit that was not superseded settles if the page is still;
  - on a row-layout change, only while the page is still, focus is in the rows (a push or cover drops the row heights, which would read clear) and no Down settle is pending.
  - A Down focus change marks `downSettlePending` (a token, so a cancelled task never clears a newer mark) until its 0.35 s settle task resolves. Without this, the engine's reveal could rest more than 150 ms before the straddle check and the band would be decided before the anchor moved the row to 108 (hide, then show).
  - The hero edge never decides: its action can run a frame before the offset and the latch catch up (instant jumps under Reduce Motion or a pop restore).
  - Nothing runs per frame, so no flips happen mid-glide. There is no second scroll observer, no PreferenceKey and no offscreen pass.
- The pure rule and its gates (`bandAtRest`, `bandOnHeroEdge`, `settlesOnRest`, `settlesOnLayout`, `shows`) are in `DetailCompactLogoBand` (`iosApp/NuvioTV/Screens/DetailCompactLogoBand.swift`).
- DEBUG probe: `debug_ux6` now ends with `compactLogo=shown|hidden logoBand=hero|clear|blocked`.
- The logo carries its `detail_compact_logo` AX id only while it shows.
  - Before this, the page's own `.accessibilityHidden(bridgePhase != .idle)`, false while idle, overrode the logo's `accessibilityHidden(true)`. The hidden logo stayed in the AX tree.

## Gates (clone, FA87 sim, on `c42317365`)

- NuvioTVTests: 2340 tests, 5 skipped, 0 failures. That includes `DetailCompactLogoBandTests` (16 tests), which cover:
  - the 107.5 and 92 rests (clear) and a 91.5 rest (blocked);
  - a row exactly `leadDepth` tall;
  - the hero edge holding the band blocked;
  - a glide between two clear rests that never asks midway;
  - the rest edge waiting for a pending Down settle;
  - a layout change needing focus in the rows and no pending settle.
- Release sim build by the FA87 id: BUILD SUCCEEDED.
- `DetailScrollProbeTests`: 5/5 passed.
- `DetailActionSquareUITests`: 4/4 passed on `029ec7722`. Later changes touch only the compact logo's band timing and AX id.
- `testCompactLogoStepsAsideForRowsInItsBand` (TMDB on, trailer autoplay off):
  - It opens the first fixture title with a Parental Guide row; **The Simpsons** has one, while Les Condés, the file's usual title, has none.
  - It walks Down one rest at a time. The real check is the heading-geometry oracle: with the "Parental Guide" heading's top in [−40, 92), the band must read `blocked` (or `hero`) and the logo must be out of the AX tree. At least one such rest must read `blocked`, and a later one `clear` with the logo back.
  - The per-rest AX-versus-probe assertion is near-tautological: the AX id is keyed on the same `visible` the probe reports. It only catches a probe/render wiring break.
  - Final run: presses 1–3 `hero`; press 4 heading at 37 pt, `blocked`, logo hidden (the review's `a17` rest); press 5 `clear`, logo shown.
  - With no fixture title carrying the row it skips (`XCTSkip`) with the reason. **A skip is not gate-green**: the fade was not exercised, and the run needs a title with the row.

## Known limit (a design call, not fixed here)

Only a row's lead counts, not its tail. With rows 36 pt apart and a 72 pt band, a whole-row test would find a row in the band at nearly every rest and the logo would almost never show. So a shelf's last lines can still sit under the logo:

- At an Up-anchored rest, the row above always ends at 72 pt, inside the band.
- At the bottom of Les Condés in the sim, the logo sits over the cast names and roles.
- On The Simpsons it sits over the season labels.

A sub-heading inside a composite row also does not count: the Episodes row's own "Episodes" heading is part of the `.episodes` row, whose top is the season strip.

If tails have to go too, the fix is the review's other option: inset the scroll so no row rests in the band, for example by lowering `screenRest`. That is a layout change, so it is Christian's call.

## Device check (coordinator; Test profile, "Test 2" on the Living Room box)

1. Run `scripts/device/ready.sh` and install the build in the Test profile.
2. Detail layout on Cinematic (the default). Open **The Simpsons** (series) and then **Animals** (film).
3. Press Down until the Parental Guide row reaches the top: on The Simpsons the Episodes shelf (`a17`, press 3 or 4 in the sim), on Animals Trailers & Extras (`a14b`).
   - Expect: no logo while the Parental Guide heading or chips are in the logo band.
   - Expect: the logo fades in after the next press, once that glide has come to rest.
4. Keep pressing Down to the last row, then Up back to the top.
   - Expect: no blink mid-glide; the logo only changes after each glide settles.
   - Expect: it shows at rests where only a shelf's tail sits in the band.
   - Expect: it hides at rests where a heading or chip line sits in the band.
   - Expect: it hides at once when focus returns to the hero.
5. Open a cast member, then come back: the logo should follow the same rule as before the push.
6. Turn on Accessibility › Reduce Motion and repeat step 3. Expect: the logo switches on and off with no fade.
