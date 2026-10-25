# UI-legs follow-ups, Wave 4 harness work (2026-10-23)

Branch `claude/harness-w4` in the side clone `~/Claude/Projects/NuvioMobile-harness`, base
`78b83c261` (tvos-shared-extraction), tip `e4bd3824a`, 9 commits. Not pushed, not rebased, not
landed. The clone stays in place; MPVKit is a symlink over the gitlink there, so stage by explicit
paths.

History: the work was parked mid-way on 2026-10-23 (code written and compiled, no UI leg run) and
resumed the same day when the hold lifted. Everything below is from the resumed runs.

Fixture: FA87E9B6 (tvOS 26.5), Debug, `-derivedDataPath iosApp/build/DerivedDataUITests`. Every run
went through both locks (simulator lock outside the build lock) with the sandbox off. The simulator
never wedged.

## Result

**Every touched leg is green or skips by design; nothing is red.** The only skip with a fixture
cause is test72: The 100 reads "Playback unavailable" on FA87.

Gates:

- **Kotlin:** `./gradlew :shared:jvmTest :shared:tvosSimulatorArm64Test :composeApp:iosSimulatorArm64Test`
  under the build lock: BUILD SUCCESSFUL (5 min 59 s).
- **NuvioTVTests, the seam classes:** 9 / 0 / 0. That is StreamAutoPlayModeDebugOverrideTests 3,
  AmoledDebugOverrideTests 3, and TmdbDebugOverrideTests 3 as the control.
- **Builds:** both test bundles build (`build-for-testing`, schemes NuvioTVUITests and NuvioTVTests).

### UI legs before → after (pass / fail / skip)

Before = the 2026-10-22 full run (`ui-legs-full-run-2026-10-22/README.md`).

| Task | Leg | Before | After | Notes |
|---|---|---|---|---|
| 1 | test27CardDepthCoverageAB | 0/1/0 | **1/0/0** | Edge › Bold, Edge Coverage › Top then Full through the pickers (shot `27c`: Edge Bold, Sheen Soft, Edge Coverage Full). The `defer` put both pickers back to their starting values, then ran the test30 baseline. 779 s. |
| 2 | test46StillModeRiseIsZero | 0/1/0 | **1/0/0** | Crystal Lake: the artwork box was identical focused and unfocused (640, 530.5, 212×322). Best shift 0 px, correlation 1.000. |
| 2 | test70RowEdgeFadeSpike | 0/1/0 | **1/0/0** | Bezel artwork fade alpha 0.041 over 30,912 px. Calibration: d140 0.646 (ramp ≈ 0.61), d280 1.000. The band column still reads 62: the backdrop, now reported only. |
| 2 | RowLeadingEdgeTests ×2 | 0/2/0 | **2/0/0** | After fix `434639b27`. Leading edge 140; allowances 44 (No Zoom) and 58 (zoom on). Rest drift 0, expanded vs rest 0/255 in both legs. |
| 3 | test72AutoPlayFirstPlayAndHoldPlay | 0/0/1 (gated) | 0/0/1 | The gate is gone. The leg now skips at "Play is disabled (no source can serve The 100 on this fixture)", by design. The seam itself is proven by the unit test. |
| 3 | StageGate1 testOledBarEvidence | 0/0/1 (gated) | **1/0/0** | The override takes effect: the edge strips read luma 0.0 with oled-on, 12.0 with oled-off, 0.0 with wash off, and 19.5 / 10.3 for classic-oled-on. Steps are 0.0 everywhere. |
| 4 | NavigationRail testRail10 | 0/1/0 | **1/0/0** | Down to a catalog card first, then a verified Select; Detail opened. |
| 4 | StageStrip testS11 | 1/0/0 | **1/0/0** | Held on `com.linvo.cinemeta:series:imdbRating/tt19231492` ("Dark Matter"), a verified catalog poster. |
| 4 | BatchAHomeReturnUITests (class) | 9/0/0 | **9/0/0** | All 5 guarded Selects pressed on verified catalog cards. |
| 4 | DetailRowAnchorTests | 0/0/1 | **1/0/0** | Now runs through DetailEntryRoute (Severance series). Its first run failed Up 1 (residual 109), fixed in `e4bd3824a`; Up 1 now counts as end-of-content clamped. |
| 4 | RailGate testAlwaysVisibleInsetSweep | 1/0/0 | **1/0/0** | The Detail push went from a verified catalog card (`own=…series:imdbRating`), not Continue Watching. |
| 5 | NativePlayerParityUITests | 0/2/8 | **0/0/10** | All skip cleanly without the env vars. |
| 6 | test33SeasonPosterRow | 0/0/1 | **1/0/0** | Ran with `-debug.tmdbEnabledOverride YES`: season posters present, Classic glass reads 0. |
| 7 | BatchASearchPerf (class) | 1/1/0 | **2/0/0** | fix leg: warm-up (dune) settled in 1061 ms, unmeasured; fight club settled in 134 ms (first 51, maxBody 0, cancelled 2). legacy leg: 50 ms, cancelled 0. No second attempt was needed. |

## Fixes during the run

There were two, one commit each. Both are (c), harness.

1. **`434639b27` RowLeadingEdge.** The rewrite's first run failed: No Zoom 21/255, zoom on 222/255.
   - The backdrop was provably still: the at-rest drift was 0/255.
   - A per-column profile showed what the first card draws past the row edge. With No Zoom, the
     still focus shadow fades out by x ≈ 90. With zoom on, the lifted 16:9 tile reaches x ≈ 102 and
     its shadow x ≈ 78.
   - Since BUG-164, `RowLeadingEdgeClip.rowAllowance` deliberately opens the clip for exactly that:
     44 pt (No Zoom) and 58 pt (zoom on). A column taken left of the tile's own edge therefore sat
     inside the allowed opening.
   - The leg now judges the 60 pt just past the clip: the row's leading edge (one card pitch left of
     card #2, read from unfocused cards) minus the allowance, minus 2 pt of slack.
   - The two allowances are duplicated as constants with their derivation, because the UI target
     cannot import the app. Keep them in step with `rowAllowance`.

2. **`e4bd3824a` DetailRowAnchor.** The leg now ran for the first time in weeks, and Up 1 failed
   with residual 109.
   - On Severance the page's last reachable offset is `content − vis − inset`:
     2627 − 863 − 157 = 1607. About rested there on Down 4–6.
   - Up 1 to Trailers & Extras re-issued y=1873 and stayed at 1607.
   - The clamp exemption ignored the probe's `inset=`; it adds it now.

## Per task: what changed

1. **test27** (`d7fcff3b6`). The leg drives the Card Depth picker rows (Edge, Sheen, Edge Coverage).
   - Focus moves onto a row by frame and is read exactly: "Edge" never matches "Edge Coverage".
   - The menu opens through `pressVerified` only on that read. `chooseMenuOption` gained an
     optional `rowFocused` predicate; test101's call is unchanged.
   - An option is selected only once it reads focused.
   - A `defer` restores the starting picker values and then the test30 baseline.

2. **Measurements** (`a9917e9ff`, plus fix `434639b27`). Each method is documented at its call site.
   - **test46:** `poster_artwork` boxes come from the geometry probe. The same card is captured
     focused and then unfocused. The rise is the best vertical alignment of the pixels inside its
     artwork (±24 pt), asserted 0 ± 2.
   - **test70:** the fade alpha is estimated from the card artwork at the bezel, as the slope of
     Soft luma against Off luma, and asserted ≤ 0.35. d140 and d280 are reported as calibration.
   - **RowLeadingEdge:** card #1 at rest is compared with its expanded tile, same title focused,
     in the column past the BUG-164 clip opening.

3. **Seams** (`7d89cafb5`). test72 uses `-debug.streamAutoPlayModeOverride FIRST_STREAM` and the
   OLED leg uses `-debug.amoledEnabledOverride`. Both `NUVIO_SYNCED_LAUNCH_ARGS` gates are gone.

4. **Blind Selects** (`e02621ced`, plus fix `e4bd3824a`). Each guarded Select reads a card-sized
   focus and the layout's readout naming a catalog card: `debug_strip foc=` on Stage,
   `debug_homeReturn own=/foc=` on Classic. Continue Watching, Upcoming and folder tiles are never
   selected.
   - testRail10 and S11 step Down first, never Select.
   - BatchAHomeReturn: 5 sites guarded.
   - DetailRowAnchor: goes through DetailEntryRoute.
   - RailGate L192: the Detail step is skipped if no catalog card is verified.

5. **NativePlayerParity** (`9bb9692ce`). `requiredEnv` throws `XCTSkip` when a variable is absent.

6. **test33** (`750ccc342`). Runs with `-debug.tmdbEnabledOverride YES`.

7. **BatchASearchPerf** (`d57126d43`). The 4 s budget is unchanged.
   - An unmeasured warm-up query ("dune") settles first.
   - The field is cleared and the title is typed in a fresh session.
   - The fix leg retries an over-budget settle with "the matrix" and keeps the better one.

## Seam design

**`stream_auto_play_mode`**
1. Swift `StreamAutoPlayModeDebugOverride` reads `-debug.streamAutoPlayModeOverride <MODE>` under
   `#if DEBUG`; it is nil when absent or blank, and always nil in Release.
2. `NuvioTVApp.init` hands the name to `PlayerSettingsRepository.setDebugStreamAutoPlayModeOverride`
   before any repository loads.
3. The name is decoded like storage's value (`StreamAutoPlayMode.valueOf`); an unknown name clears
   the override.
4. `loadFromDisk` uses `override ?: persisted ?: MANUAL`. The override is in memory only and survives
   `onProfileChanged`.
5. Storage and `exportToSyncPayload()` are untouched. The unit test proves the key, the
   `stream_auto_play_mode*` defaults and the payload stay unchanged.

**`amoled_enabled`**
1. Swift `AmoledDebugOverride` reads `-debug.amoledEnabledOverride YES|NO` under `#if DEBUG`.
2. `NuvioTVApp.init` hands it to `ThemeSettingsRepository.setDebugAmoledEnabledOverride` before any
   repository loads.
3. `loadFromDisk` uses `override ?: store.loadAmoledEnabled() ?: false`, published on
   `amoledEnabled`. AppThemeModel, the wash and Settings all read that.
4. In memory only, survives profile reloads, never written.
5. `TvOsThemeSettingsStore` and its export are untouched. The unit test proves the key, the
   `amoled_enabled*` defaults and the theme payload stay unchanged.

## Open items

- **test72** can only skip on FA87: The 100 has no playable source there. Exercising the
  auto-play path needs a fixture title with a source, or the smoke stream.
- **RowLeadingEdge** duplicates the 44 / 58 pt allowances. A change to `rowAllowance` must update
  the leg too.
- **test27** takes about 13 minutes, nearly all of it Settings walks. It works, but it is the
  slowest leg in the class.
- **Not on the list but seen:** these still press Select without a verified read. They are
  tab-level selects (S-risk), not D-risk:
  - `BatchASearchPerfUITests.openSearch`
  - StageStrip `openTab` and `openDeveloper`
  - RailGate `openTab` and the `railWalk` Search select
- **Landing:** review loop, then the gates, then fast-forward. Kotlin changed in two repositories;
  the Kotlin gate is already green on this tip.
