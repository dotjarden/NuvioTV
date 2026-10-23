# UI-legs follow-ups, Wave 4 harness work (2026-10-23): ON HOLD, code done, legs not run

Branch `claude/harness-w4` in the side clone `~/Claude/Projects/NuvioMobile-harness`, base
`78b83c261` (tvos-shared-extraction), tip `d57126d43`, 7 commits. Not pushed, not rebased, not landed.
The clone stays in place (MPVKit is a symlink over the gitlink there; stage by explicit paths).

**Status.** Christian put Wave 4 on hold until the 72-hour watch ends. The stop came after every
code change was written and compiled, and before the first UI run. So:

- **Done and verified:** the two DEBUG seams (task 3). Their unit tests pass on FA87.
- **Done, compiled, not run:** every UI-leg change (tasks 1–7). Both test bundles build
  (`build-for-testing`, schemes NuvioTVUITests and NuvioTVTests, Debug, FA87 id, through the build
  lock). No UI leg was run, so no leg result below is "after".
- **Not started:** nothing on the list. HeroOffLaunchTests.test31D was left alone as asked.

## Results

NuvioTVTests (FA87, both locks, sandbox off), one run:

| Class | Before | After |
|---|---|---|
| StreamAutoPlayModeDebugOverrideTests (new) | — | 3 / 0 / 0 |
| AmoledDebugOverrideTests (new) | — | 3 / 0 / 0 |
| TmdbDebugOverrideTests (control) | 3 / 0 / 0 | 3 / 0 / 0 |

The first run of the two new classes crashed in the payload read: the sync export's values include
nested JSON objects, which the bridged `[String: JsonElement]` view cannot cast. The tests now
read the payload through `NSDictionary`; the re-run was 9 / 0 / 0. The TMDB test reads only
primitives and is unaffected.

UI legs: before = the 2026-10-22 full run (`ui-legs-full-run-2026-10-22/README.md`); after = not run.

| Task | Leg | Before (pass/fail/skip) | After |
|---|---|---|---|
| 1 | test27CardDepthCoverageAB | 0/1/0 (a, stale: chips are pickers) | not run |
| 2 | test46StillModeRiseIsZero | 0/1/0 (c, ring edge read) | not run |
| 2 | test70RowEdgeFadeSpike | 0/1/0 (c, backdrop column) | not run |
| 2 | RowLeadingEdgeTests ×2 | 0/2/0 (c, backdrop changes with title) | not run |
| 3 | test72AutoPlayFirstPlayAndHoldPlay | 0/0/1 (gated) | not run |
| 3 | StageGate1 testOledBarEvidence | 0/0/1 (gated) | not run |
| 4 | NavigationRail testRail10 | 0/1/0 (blind Select resumed CW) | not run |
| 4 | StageStrip testS11 | 1/0/0 (blind hold) | not run |
| 4 | BatchAHomeReturn (Classic leg + 4 others guarded) | 9/0/0 class | not run |
| 4 | DetailRowAnchorTests | 0/0/1 (Playback unavailable) | not run |
| 4 | RailGateEvidence testAlwaysVisibleInsetSweep | 1/0/0 (blind Select) | not run |
| 5 | NativePlayerParityUITests | 0/2/8 | not run (expected 0/0/10 without the env vars) |
| 6 | test33SeasonPosterRow | 0/0/1 (TMDB off) | not run |
| 7 | BatchASearchPerf testBatchA_SearchTypingFix | 0/1/0 (6388 ms vs 4000) | not run |

## Per task: what changed

1. **test27** (`d7fcff3b6`). The leg now drives the Card Depth picker rows (Edge › Subtle, Sheen › Soft,
   Edge Coverage › Top) instead of the old chips.
   - Focus moves onto a row by frame and is read exactly: "Edge" never matches "Edge Coverage".
   - The menu opens through `pressVerified` only on that read. `chooseMenuOption` gained an
     optional `rowFocused` predicate; test101's call is unchanged.
   - An option is selected only once it reads focused.
   - The leg reads the rows' values first. A `defer` puts the pickers back to those values, then
     runs test30's baseline (Card Depth OFF, both focus toggles OFF, Ocean), whatever the outcome.

2. **Measurements** (`a9917e9ff`). Each method is documented in a comment at its call site.
   - **test46:** the `poster_artwork` box comes from `-debug.cardGeometryProbe YES`. The same card
     is captured focused and then unfocused (one Left). Only pixels inside its artwork are read:
     the middle 60 % of the width, starting 8 pt under the box top, over 45 % of its height. The
     best vertical alignment of the two luma profiles (correlation, ±24 pt) is the rise, asserted
     0 ± 2 pt. The boxes must not move either. `-accent_focus_ring NO` is pinned (a local key).
   - **test70:** the bezel check now estimates the fade alpha from the card artwork within 24 pt
     of the bezel. It takes the slope of Soft luma against Off luma, since
     Soft = a·Art + (1 − a)·backdrop, and asserts ≤ 0.35. The alphas at d140 and d280 are reported
     as calibration. When there is no artwork with structure at the bezel, the check skips at the
     end of the leg.
   - **RowLeadingEdge:** card #1 at rest (two captures, which must agree) is compared with its
     expanded tile, with the same title focused, so the hero backdrop cannot change. Trailer Start
     Delay is 3 s and the hero trailer is off. This does not judge bleed from focus alone (the
     still-mode shadow, the system lift): that is present in both states.

3. **Seams** (`7d89cafb5`). test72 uses `-debug.streamAutoPlayModeOverride FIRST_STREAM` and the
   OLED leg uses `-debug.amoledEnabledOverride YES|NO`. Both `NUVIO_SYNCED_LAUNCH_ARGS` gates are
   removed.

4. **Blind Selects** (`e02621ced`). Each guarded Select reads a card-sized focus plus the layout's
   own readout naming a catalog card. The readout is `debug_strip foc=` on Stage and
   `debug_homeReturn own=/foc=` on Classic. Continue Watching, Upcoming and folder tiles are
   refused. If the read fails, the leg takes a screenshot and aborts without pressing.
   - testRail10 and S11 step Down first, never Select.
   - BatchAHomeReturn: the Classic leg at L177 plus the Stage, steal, viewer-down and batchC legs.
   - DetailRowAnchor: goes through `DetailEntryRoute.openDetail()`.
   - RailGateEvidence L192: the Detail step is logged as skipped when no catalog card is verified.

5. **NativePlayerParity** (`9bb9692ce`). `requiredEnv` throws `XCTSkip` when a variable is absent.
   The chapters and late-subtitle legs check `PLAYER_NATIVE_PROBE` first.

6. **test33** (`750ccc342`). Runs with `-debug.tmdbEnabledOverride YES`.

7. **BatchASearchPerf** (`d57126d43`). The measurement changed; the 4 s budget did not.
   - An unmeasured warm-up query ("dune") settles first, then the field is cleared.
   - The title is then typed in a fresh session.
   - The fix leg retries over-budget with a second ten-letter title ("the matrix") and keeps the
     better settle.

## Seam design

**`stream_auto_play_mode`**
1. Swift `StreamAutoPlayModeDebugOverride` reads `-debug.streamAutoPlayModeOverride <MODE>` under
   `#if DEBUG` and returns nil when the key is absent or blank.
2. `NuvioTVApp.init` hands the name to `PlayerSettingsRepository.setDebugStreamAutoPlayModeOverride`
   right after the TMDB seam, before any repository loads.
3. The name is decoded like storage's (`StreamAutoPlayMode.valueOf`); an unknown name clears it.
4. `loadFromDisk` uses `override ?: persisted ?: MANUAL`. The override is in memory only, survives
   `onProfileChanged`, and `setStreamAutoPlayMode` still writes as before.
5. `PlayerSettingsStorage` and `exportToSyncPayload()` are untouched. The unit test proves the key,
   the `stream_auto_play_mode*` defaults and the payload stay unchanged.

**`amoled_enabled`**
1. Swift `AmoledDebugOverride` reads `-debug.amoledEnabledOverride YES|NO` under `#if DEBUG`
   (`ProfileAutoEnter` convention).
2. `NuvioTVApp.init` hands it to `ThemeSettingsRepository.setDebugAmoledEnabledOverride` before any
   repository loads.
3. `loadFromDisk` uses `override ?: store.loadAmoledEnabled() ?: false`, published on `amoledEnabled`.
   `AppThemeModel`, the wash and Settings all read that flow.
4. In memory only, survives profile reloads, never written. `clearLocalState` behaves as before.
5. `TvOsThemeSettingsStore` and its export are untouched. The unit test proves the key, the
   `amoled_enabled*` defaults and the theme payload stay unchanged.

## Open items (when Wave 4 resumes)

- Run every leg in the table, one invocation per class through both locks. A helper is in the
  scratchpad, but it is session-local, so rewrite it. Then record before→after and classify any
  failure.
- **test27:** the first run will show whether the picker rows' AX shape matches the exact-title
  read. The full run saw an unlabelled focused Cell on "Edge", so the frame fallback is the path
  to watch. Also check that the menu's options are found by `chooseMenuOption`'s candidates.
- **test46:** the correlation needs structure in the top 45 % of the poster. A flat poster skips;
  the leg does not pass.
- **test70:** the alpha estimate assumes the backdrop is unrelated to the card art. Read the d280
  calibration alpha (≈ 1) on the first run before trusting the threshold.
- **RowLeadingEdge:** if the hero dims or changes when the tile expands, the leg will fail on that.
  Classify it from the `_00b_at_rest` / `_03_expanded` shots.
- **test72:** on the fixture The 100 may read "Playback unavailable"; the leg then skips by design.
- **Not on the list but seen:** `BatchASearchPerfUITests.openSearch` and the Settings/tab openers in
  StageStrip and RailGateEvidence still press Select without a verified read. These are S-risk,
  not D-risk.
- Landing: the coordinator runs the review loop and the gates, then fast-forwards
  `claude/harness-w4`. Kotlin changed (two repositories), so the gradle gate applies.
