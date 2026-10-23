# D-3: the compact logo steps aside for rows in its band (2026-10-23)

Design review item D-3 (P3, `docs/design-review-2026-10-22.md`): on a scrolled Cinematic Detail page, FEAT-60's compact title logo sat over rows resting under it (the Parental Guide chips under Animals and under The Simpsons).

Branch `claude/d3-compact-logo` in the clone `~/Claude/Projects/NuvioMobile-d3`, tip `c0f0ab918`, three commits on `tvos-shared-extraction` `1b2fc99f3`. Not merged, not cut.

## The rule

1. The band is the logo's slot: 36 to 108 pt from the scroll view's top (36 pt padding + the 72 pt slot). Its bottom is `DetailRowAnchor.screenRest`.
2. A row's lead runs from its top through `min(height, 112 pt)`: the heading, and for a chip row (Parental Guide, studio logos) the chips too.
3. The logo fades out while any row's lead overlaps the band (edges that only touch don't count) and fades back in once every lead is clear.
4. The band is only checked after FEAT-60's hero clearance (`heroClearance` = 120, unchanged). The probe reads `logoBand=hero` before that.
5. The fade is the existing 0.25 s ease on `visible`. Under Reduce Motion there is no animation (unchanged).

## How it is built

- `DetailRowAnchored` already reported each row's content-space top. It now reports the height from the same `onGeometryChange` read, so both change on layout only.
- The existing hero-exit `onScrollGeometryChange` now returns a `Gate` (`heroGone`, `bandBlocked`) instead of a Bool. Its `of:` closure gains a loop over at most nine rows. `ScrollDimModel.logoBandBlocked` is published only when it flips.
- There is no second scroll observer, no PreferenceKey and no offscreen pass. Measuring rows in scroll space would have sent a preference update every frame; content-space frames plus the content offset give the same answer.
- The pure rule is `DetailCompactLogoBand` (`iosApp/NuvioTV/Screens/DetailCompactLogoBand.swift`).
- DEBUG probe: `debug_ux6` now ends with `compactLogo=shown|hidden logoBand=hero|clear|blocked`.

## Gates (clone, FA87 sim)

- NuvioTVTests: 2334 tests, 5 skipped, 0 failures, including the new `DetailCompactLogoBandTests` (10 tests).
- Release sim build by the FA87 id: BUILD SUCCEEDED.
- `DetailActionSquareUITests`: 4/4 passed.
- `DetailScrollProbeTests`: 5/5 passed, including the new `testCompactLogoStepsAsideForRowsInItsBand` (run with `-debug.tmdbEnabledOverride YES`).
  - On the first run, two legs failed at the Search route: focus landed on "Les Norton" instead of "Les Condés". This was fixture drift, not this change; both passed on the rerun.
- The new leg walked Les Condés down 10 presses: `hero` for presses 1–3, then `shown clear` for presses 4–10.
  - This title has no Parental Guide row, so no rest blocked the band and the fade itself was not exercised in the sim.
  - The shown/blocked pairing is asserted never to occur.

## Known limit (a design call, not fixed here)

Only a row's lead counts, not its tail. With rows 36 pt apart and a 72 pt band, a whole-row test would find a row in the band at nearly every rest and the logo would almost never show. So a shelf's last lines can still sit under the logo:

- At an Up-anchored rest, the row above always ends at 72 pt, inside the band.
- At the bottom of Les Condés in the sim, the logo sits over the cast row's names and roles (`d3_down4` in the leg's xcresult).

If that also has to go, the fix is the review's other option: inset the scroll so no row rests in the band, for example by lowering `screenRest`. That is a layout change, so it is Christian's call.

## Device check (coordinator; Test profile, "Test 2" on the Living Room box)

1. Run `scripts/device/ready.sh` and install the build in the Test profile.
2. Detail layout on Cinematic (the default). Open **Animals** (film) and then **The Simpsons** (series).
3. Press Down until the Parental Guide row reaches the top: on Animals focus Trailers & Extras (the review's `a14b` rest), on The Simpsons the Episodes shelf (`a17`).
   - Expect: no logo while the Parental Guide heading or chips are under the logo band; the logo fades in once the row has scrolled clear.
4. Keep pressing Down to the last row, then Up back to the top.
   - Expect: the logo shows at rests where only a shelf's tail sits in the band.
   - Expect: it fades out for the Parental Guide row and for each heading passing the band.
   - Expect: it hides once focus is back in the hero.
   - Watch for blinking: a quick hide-then-show while one glide carries a heading through the band.
5. Turn on Accessibility › Reduce Motion and repeat step 3. Expect: the logo switches on and off with no fade.
