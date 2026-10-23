# UI legs: blind routes guarded, TMDB seam, one full FA87 run (2026-10-22)

Branch `claude/ui-legs` in the side clone `~/Claude/Projects/NuvioMobile-uilegs`, base
`fccfabb3b` (tvos-shared-extraction), tip `672a54051`, 9 commits, not pushed, not landed.
Fixture: FA87E9B6 (Apple TV 4K 3rd gen, tvOS 26.5), Xcode 27.1, Debug build.

The app binary was identical for every run (NuvioTV `2F97B3F7…`, NuvioTV.debug.dylib
`74002352…`). Only the UI test bundle was rebuilt between re-runs; the base predates the
BUG-221 fix `7239c706c`.

Result after the run and its re-runs: **360 UI tests, 247 passed, 15 failed, 98 skipped**.
NuvioTVTests: **2294 tests, 2289 passed, 0 failed, 5 skipped**.

## 1. App crash in the folder legs: BUG-221 (b), fixed on the tip

test106 / test107 FolderBandReachableFromRow0 / test107 FolderRowsSeeAll / test108
(NuvioTVUITests, Stage folder legs) crashed 8 times out of 8, in two windows.

**Crash reports.** All eight are identical, in
`~/Library/Logs/DiagnosticReports/Retired/NuvioTV-2026-10-22-{143055,143125,143220,143314,153113,153201,153258,153354}.ips`.

- Exception: `EXC_BREAKPOINT` (SIGTRAP) on the main thread.
- Top of the stack: `_assertionFailure ← DynamicContainerInfo.tryRemovingItem(at:disableTransitions:) ← DynamicContainerInfo.updateItems ← updateValue`.
- It sits inside a SwiftUI layout pass: a `LazyHStack` (LazyHVStack, ForEachList, LazyLayoutComputer) in a `ScrollView`, under an `_AspectRatioLayout` child.
- No app frames except `NuvioTVApp.$main`.

**Symptom.** The crash comes about 1.5 s after the verified Select on "Chris" (launch 14:30:19.9,
crash 14:30:27.6). That is Stage Home's first publish, with the DEBUG folder seed. No remote input
was sent in that window. The recording shows Stage Home with its Continue Watching row, then the
springboard. The xcresults are kept as evidence: `ui-legs-results/Big02.xcresult` and
`Big02r.xcresult` (see Evidence).

**Not the harness.** The folder legs' launch arguments did not change on this branch. The
guarded picker step only replaced a blind Left×3 + Select with a focus-verified Select on the
same tile.

**Reproduction.**

- 14:30 and 15:30 (two windows): 8 crashes out of 8.
- 17:07, right after a fresh reboot, same binary: 4 out of 4 passed, no crash report.
- 17:23, temporary bisect class (5 launches, deleted afterwards and never committed): 0 crashes out of 5.

Card Depth state matches all of this. The state is inferred from which appearance legs actually pressed the toggle; it was not read off the probe at each moment:

| Time | Card Depth | How it got there | Folder legs |
|---|---|---|---|
| ~14:05 | OFF | — | test104/105 passed |
| 14:30 | ON | test09 had toggled it on at 14:27 | crashed |
| 15:30 | ON | test27 had turned it on; test30's restore had failed | crashed |
| 17:07 | OFF | test30 restored the baseline | passed |

That fits the coordinator's identification: BUG-221, the W3-13 raster-cache Card Depth overlay.
It is fixed on tvos-shared-extraction by `7239c706c`, and it does not reproduce on the Release
build.

## 2. Blind-route audit (task 1)

**What counts as blind.** A Select or Play/Pause with no focus read of the intended element in
the same route right before the press. An XCTAssert under `continueAfterFailure = true` does not
count as a read. The close-out note said 8 blind routes; the real count in NuvioTVUITests.swift
was 54 of 85 sites.

Every UI file's profile-picker Select now goes through `DetailEntryRoute.selectChrisTile`. That
step reads `hasFocus` on the "Chris" tile before Select, logs the tile list, and stops the test
if focus can't be verified. 334 verified entries were made. The tile list never changed:
"Chris PRIMARY, Profile, Profile, Add Profile" (localized in the de/fr legs). No picker Select
went unverified.

| File | Sites | Blind before | Blind after | Change |
|---|---|---|---|---|
| NuvioTVUITests.swift | 85 | 54 | 0 | `pressVerified`/`pressIfVerified` everywhere; "get to Detail" Home walks go through `DetailEntryRoute.openDetail` |
| DetailScrollProbeTests.swift | 5 | 5 | 0 | hero entry and search result through DetailEntryRoute; tab and rail Selects verified |
| RevampEvidenceTests.swift | 7 | 7 | 0 | teaser, tab and root-row Selects verified; Account & Profiles no longer opened |
| DetailSynopsisSheetUITests.swift | 2 | 2 | 0 | picker verified; teaser must read focused |
| 39 other files (subagent audit, read-only) | 168 | 140 (P33 S15 A17 D5) | 109 | picker sites (29) and NavigationRail test04/test09 root Selects (A-risk) fixed |

P = profile picker, S = Settings rows, A = Account & Profiles, D = opens playback.

**Blind sites still left in other files (109).** 61 are in env-gated classes that skip by
default: Player*, SyncLine, SubtitleDelay, Scratch*, GuestReveal, StageBodyCount, NativePlayerParity,
FixtureSetup.

The ones that ran and matter:

- NavigationRailUITests.testRail10: Select on Stage row 0, which is Continue Watching on FA87. It
  resumed the player instead of opening Detail (see §4).
- StageStripUITests.testS11 (hold on a strip poster).
- BatchAHomeReturn L180, DetailRowAnchor L97, RailGateEvidence L192: blind card Selects that can
  open playback.
- DiscoverGenreLocalization: Select inside the genre menu.

**Opt-in gates added.** Each gated class skips unless its environment variable is set to 1:

| Test | Variable | Why |
|---|---|---|
| test35 | `NUVIO_ACCOUNT_ROWS` | walks Account & Profiles rows |
| test72 | `NUVIO_SYNCED_LAUNCH_ARGS` | uses `-stream_auto_play_mode_2`, which PlayerSettingsStorage exports |
| StageGate1.testOledBarEvidence | `NUVIO_SYNCED_LAUNCH_ARGS` | uses `-amoled_enabled_1`, a synced theme key |
| FixtureSetupTests | `NUVIO_FIXTURE_SETUP` | writes synced Poster Size and Hide Titles; a whole-class run ends on Medium+ with Hide Titles ON |

## 3. TMDB seam (task 2)

`-debug.tmdbEnabledOverride YES|NO`, DEBUG only.

- `TmdbDebugOverride` (iosApp/NuvioTV/Screens/TmdbDebugOverride.swift) reads it under `#if DEBUG`,
  using the same convention as `ProfileAutoEnter.debugEnabledOverride`.
- `NuvioTVApp.init` hands it to `TmdbSettingsRepository.setDebugEnabledOverride` before any
  repository loads.
- `loadFromDisk` consults the override before `TmdbSettingsStorage.loadEnabled()`. It lives in
  memory only, and it survives profile reloads.
- Storage and `exportToSyncPayload()` are untouched.

The unit test `TmdbDebugOverrideTests.testOverrideReadsTrueWhileThePersistedSettingAndPayloadStayUnchanged`
checks three things: `snapshot().enabled` reads true; `tmdb_enabled`, every `tmdb_*` defaults key
and the payload are unchanged; a profile reload writes nothing. It passed.

DetailFocusReturnUITests now launches with the override, and all 3 Back legs pass. Before this
change they skipped because there was no cast row.

## 4. Full run (task 3)

**How it ran.** One `test-without-building` call per class, or per chunk of 8 tests for the big
class. Every call went through both locks with the sandbox off. The simulator was rebooted after
every 5 calls.

**Time.** UI runs went from 12:29 to 19:05, 6 h 36 min wall in total. That includes rebuilds,
re-runs, reboots and about 24 min of waiting on locks held by another session. The summed test
time of the latest runs is 4.7 h. The big class's first pass took 1 h 55 min of test time
(2 h 14 min wall).

| Class | Run | Pass | Fail | Skip | Test time |
|---|---|---|---|---|---|
| NuvioTVUITests (12 chunks + re-runs) | 94 | 67 | 3 | 24 | 1h55m first pass |
| RowsOrderRuleTests | 7 | 7 | 0 | 0 | 5s |
| AccentFocusRingTests | 11 | 11 | 0 | 0 | 1m09s wall |
| ArtworkLetterboxTests | 10 | 10 | 0 | 0 | 5s |
| GifDecodePlanTests | 16 | 16 | 0 | 0 | 6s |
| StreamBadgeColorTests + TabChipContrastTests | 19 | 19 | 0 | 0 | 6s |
| BatchAFolderUITests | 5 | 3 | 2 | 0 | 5m27s |
| BatchAHomeReturnUITests | 9 | 9 | 0 | 0 | 7m57s |
| BatchARailProfileUITests | 3 | 3 | 0 | 0 | 38s |
| BatchASearchPerfUITests | 2 | 1 | 1 | 0 | 1m21s |
| DetailActionSquareUITests | 4 | 4 | 0 | 0 | 3m42s wall |
| DetailFocusReturnUITests | 3 | 3 | 0 | 0 | 3m31s wall |
| DetailRowAnchorTests | 1 | 0 | 0 | 1 | 58s |
| DetailScrollProbeTests | 4 | 4 | 0 | 0 | 7m25s |
| DetailSynopsisSheetUITests | 1 | 1 | 0 | 0 | 37s |
| DiscoverGenreLocalizationUITests | 1 | 0 | 1 | 0 | 3m59s |
| FocusRowUITests | 1 | 1 | 0 | 0 | 21s |
| FolderClassicHeroUITests | 1 | 1 | 0 | 0 | 63s |
| FolderClassicRowHeadingUITests | 1 | 1 | 0 | 0 | 64s |
| HeroFolderSwapTests | 2 | 1 | 0 | 1 | 3m00s |
| HeroLogoFocusTests | 1 | 0 | 1 | 0 | 20s |
| HeroOffLaunchTests | 1 | 0 | 1 | 0 | 70s |
| HomeBodyCountUITests | 2 | 2 | 0 | 0 | 80s |
| HomeUpIntoHeroUITests | 1 | 1 | 0 | 0 | 22s |
| InlineTrailerTileProbeTests | 2 | 2 | 0 | 0 | 57s |
| NavigationRailUITests | 16 | 15 | 1 | 0 | 12m57s |
| PinnedRowSettleRegimeTests | 2 | 0 | 0 | 2 | 70s |
| RailGateEvidenceTests | 5 | 5 | 0 | 0 | 5m38s |
| RevampEvidenceTests | 10 | 10 | 0 | 0 | 7m54s |
| RowLeadingEdgeTests | 2 | 0 | 2 | 0 | 55s |
| StageDiscoverUITests | 10 | 10 | 0 | 0 | 7m40s |
| StageGate1EvidenceTests | 16 | 15 | 0 | 1 (gated) | 10m41s |
| StageStripUITests | 17 | 16 | 0 | 1 | 10m43s |
| StripFitNoZoomUITests | 1 | 1 | 0 | 0 | 1m58s |
| TabBarScrollLinkTests | 2 | 2 | 0 | 0 | 2m41s |
| TrailerMotionUITests | 11 | 2 | 1 | 8 | 11m25s |
| TrailerSoakTests | 4 | 4 | 0 | 0 | 9m52s |
| NativePlayerParityUITests (env-gated) | 10 | 0 | 2 | 8 | 1s |
| FixtureSetupTests (gated) | 5 | 0 | 0 | 5 | 4s |
| PlayerTransportUITests (gated) | 27 | 0 | 0 | 27 | 2s |
| PlayerAudioSpeed / PlayerPanelClose / PlayerTopPanelProbe / PostPlay / SyncLine / SubtitleDelayProbe / InfoPanelProbe / ScratchServerSwitch / GuestTrailerRevealScratch / StageBodyCount (gated) | 20 | 0 | 0 | 20 | ~1s each |

### Failures and classification

#### (b) Real app defects (not fixed)

**BUG-221 crash: NuvioTVUITests test106 / test107 ×2 / test108.** Covered in §1. It failed 8/8 in
two windows and passed 4/4 after the reboot, once Card Depth was OFF. Fixed on the tip by
`7239c706c`.

**BatchAFolderUITests.testLandscapeShapeCatalogDrawsLandscapeCards: the wide trailer tile does
not grow (D16).**
- The wide trailer tile (`stage=wide`) stays at the folder-tile size, outer 415.9×234.0.
- D16 says it should grow to the poster height, 350.95 pt.
- Screenshot: `landscape-2-wide` in `BatchAFolderUITests.xcresult`.
- Candidate cause: the W3-13 Card Depth raster cache on the trailer tile (`68c05a4bb`/`ff41c0e22`).
  Worth re-checking on the tip after `7239c706c`.

**BatchAFolderUITests.testStageFolderTitleLogoSitsAtTheBlockTop: the folder title block floats
again (BUG-190).**
- On the Stage folder page, `stage_info` starts at y = 200.5 instead of the block top at 120 ± 4.
- The TENZING wordmark sits about 80 pt below the top, the float BUG-190 removed.
- The folder logo itself, `folder_stage_logo` at (140, 22), has risen.
- Screenshot: `bug190-folder-after-move` in `BatchAFolderUITests.xcresult`.

**HeroOffLaunchTests.test31DHeroOffRowsWaitForSync: the focus panel presents before the rows open.**
- With hero off, the panel presented `item=movie:smoke` at 5373 ms, before the held rows opened:
  "a 'present' line before the rows opened".
- It looks like a consequence of `5a077731c`, which builds Continue Watching outside the rows
  LazyVStack.
- **Decision needed:** is that a regression, or is test31d's contract stale?

#### (a) Stale expectations

Fixed, one commit per class, and passing on FA87:

- **DetailSynopsisSheetUITests.** Breaking Bad's synopsis fits four lines, with or without TMDB
  (`trunc=0`), so the leg now opens Dune (2021) with the TMDB override.
- **test82.** Batch F put Collections Layout directly under Home Layout, in both layouts.
- **test94.** Since FEAT-72 the Top result card shows no "Found in …"; the assertion now checks
  the Movies row.

Not fixed:

- **test27CardDepthCoverageAB.** It reports "Edge Coverage chips never appeared". The Card Depth
  chip rows became picker rows (Edge › Subtle, Sheen › Soft, Edge Coverage › Top), so the leg
  needs a rewrite to drive the pickers. That is not a constant swap.

#### (c) Harness blindness or measurement

Fixed and re-run green:

| Test | What was wrong | Fix |
|---|---|---|
| test01 | the card's composed label carries a live trailer readout | match the card by title |
| test05 | the German root row's Cell carries no identifier | read the id in its subtree |
| test09 | the Down walk ran on to "Import Badge Pack" | walk by tree index, verify the row |
| test28 / test30 | the toggle walk finished one row past, on an unlabeled "Edge" Cell | frame-verified nudge |
| test51 | the route's settle outlasted the 4 s auto-play | `openDetail(settle: false)` |
| DetailScrollProbeTests | Down + Lefts landed on the "b" key | route fallback; "Drop Game" tolerated |
| RevampEvidenceTests | root rows are read by label; Home Screen is reached by a read walk | trailer auto-play off; the teaser step needs the teaser button |

Not fixed (reported):

- **test46StillModeRiseIsZero (rise 9.0 pt, earlier 4.0).** The edge finder reads the still-mode
  focus ring's outer edge (frame minY 526.5) against a neighbour's artwork edge (535.5). The
  artwork tops are level and the ring is drawn even with `-accent_focus_ring NO`.
- **test70RowEdgeFadeSpike ("x=4 still carries artwork", 62 > 28).** The x = 4 column samples the
  Home backdrop art (blue foliage) behind the row band. The card does fade: d140 differs from Off
  (0.115).
- **RowLeadingEdgeTests ×2 (bleed 76/255 and 51/255).** The column left of the first card is the
  hero backdrop, which changes with the focused title. In the focused capture the inline trailer
  tile is also expanded. This is not a card bleed. Captures: `rowEdge_noZoom_03/04`.
- **HeroLogoFocusTests.test62 and TrailerMotionUITests.test89.** Their "first row" walks land on
  FA87's 2-card Continue Watching row ("Smoke Test", "MPV Smoke"). test62 reached only 1 distinct
  card; test89 saw 1 text swap in 8 Rights. test86/86B skip for the same reason (a 360×203 CW card).
- **NavigationRailUITests.testRail10.** The blind Select lands on Stage row 0, which is Continue
  Watching, so it resumed the player instead of opening Detail.
- **DiscoverGenreLocalizationUITests.** The blind Down + Select inside the genre menu never moved
  the pick off "Action" in 14 rounds.
- **NativePlayerParityUITests ×2.** `XCTUnwrap` on PLAYER_SMOKE_URL / PLAYER_SMOKE_CHAPTERS_URL
  fails instead of skipping when the env var is absent. Nothing is pressed.
- **BatchASearchPerfUITests.testBatchA_SearchTypingFix.** Settle took 6388 ms against a 4000 ms
  budget, on a shared, loaded machine.

### Skips (fixture state, not failures)

- **Pinned (Nuvio-style) hero mode off:** test47, 48, 58, 63–67; PinnedRowSettle ×2.
- **No folder or collection on Chris's Home:** test31, 56; HeroFolderSwap test55.
- **Trailer extraction unavailable on the sim:** TrailerMotion test85/85B/85C/88B/91.
- **"Playback unavailable" on the fixture:** test77; DetailRowAnchor.
- **Card Depth off:** test50.
- **TMDB season posters off:** test33. The override would let it run.
- **test59:** `debug_ux6 anchor=` never reports `logos`; all four titles opened.
- **test78:** Breaking Bad trunc=0.
- **Gated (§2):** test35, test72, test42 (guest-only), OLED.
- **Other:** test34, 36, 49, 54, 61, 68; StageStrip S09.

## 5. Fixture notes

- Play reads "Playback unavailable" for Dune, Dune: Part Two and Breaking Bad, so Detail's default
  focus is **Mark Watched**. The old blind teaser Selects in RevampEvidence would have marked those
  titles watched; the guard refused instead.
- The profile has a 2-item Continue Watching row ("Smoke Test", "MPV Smoke") above the catalogs.
- TMDB is off (the override covers it), pinned hero is off, and the baseline is Card Depth OFF
  (test30).

## 6. Decisions needed

1. test27 rewrite for the Card Depth picker rows.
2. Measurement approach for test46, test70 and RowLeadingEdge, which currently read ring and
   backdrop edges.
3. test31d contract versus `5a077731c`.
4. Re-check the two BatchAFolder geometry legs (D16 grow, BUG-190) on the tip.
5. test72 and the OLED leg need a DEBUG override seam like the TMDB one to run on the signed-in
   fixture.
6. Guard next: NavigationRail testRail10 (it resumes playback), StageStrip S11 and the other
   D-risk sites.

## Evidence

Failing-class bundles kept in `~/Claude/Projects/NuvioMobile-uilegs/iosApp/build/DerivedDataUITests/ui-legs-results/`:

- `Big02.xcresult` and `Big02r.xcresult` (BUG-221, crash logs attached)
- `Big0456r.xcresult` (test27, test46)
- `Big4651r.xcresult`
- `Big09.xcresult` (test70)
- one bundle per failing class: BatchAFolder, BatchASearchPerf, DiscoverGenreLocalization,
  HeroLogoFocus, HeroOffLaunch, NativePlayerParity, NavigationRail, RowLeadingEdge, TrailerMotion

All passing bundles were deleted.

## 7. After landing (coordinator, 2026-10-22 ~23:55Z)

- **Landed:** `claude/ui-legs` merged into `tvos-shared-extraction` as `b9dda53c6` (merge commit; the tip had moved to `0cf4a29eb` for beta.19), outer `469c176`. Gate on the merge: Kotlin tests green, NuvioTVTests 2303 / 0 (5 skipped), Release sim build, UI target compiles. The clone (9.2 GB, result bundles included) was deleted; the eight BUG-221 crash logs stay under `~/Library/Logs/DiagnosticReports/Retired/`.
- **Rules corrected (CLAUDE.md):** the Release sim build must use the FA87 id as the destination (`generic/platform=tvOS Simulator` links x86_64 against the arm64-only SharedCore and fails: Release has no `ONLY_ACTIVE_ARCH`); the `NuvioTV` scheme has no testables, so unit tests run with `-scheme NuvioTVTests` and legs with `-scheme NuvioTVUITests`.
- **BatchAFolder on the tip, before any fix:** both legs failed the same way (so neither was this branch's doing).
  - **BUG-190 = (b), real, REOPENED.** `StageView` passes `.topLeading` to the outer logo-slot frame once the folder logo has risen, but `HeroLogo`'s own inner `.frame(maxWidth:maxHeight:alignment: .bottomLeading)` kept bottom-aligning the bitmap inside the same height, so the title logo sat at `120 + 150 − logoHeight` (TENZING, 68 pt: 201). The leg was written with the rc11 fix and never ran before today; the rc11 device pass judged the folder heading, not the title logo. Fix `0c5f852c6`: `HeroLogo` takes an `alignment` (default `.bottomLeading`, so Home, Discover and Classic are unchanged) and the Stage passes `logoAlignment` through. Leg green; **device PASS in Test 2** (Debug build `78b83c26` on the Living Room box, Test Collection › Test Folder › Right: the folder name is the small heading at the top and the TENZING wordmark starts at the block top). Shots: `bug190-sim-tip-before.small.png` (sim, pre-fix tip), `bug190-device-docked.small.png`, `bug190-device-after-right.small.png`. The DEBUG collections seed refuses a signed-in account on the box (`[CollectionsSeed] imported=false refused=signedIn`), so the check used the profile's own collection.
  - **D16 = (a), stale.** Steven's rc6 follow-up (2026-10-18, `457a38d34`, shipped rc8, confirmed rc9: "wide posters without enlargement") reversed D16's grow; the leg still expected the poster-height tile. Rewritten in `78b83c261` (the wide tile's outer size = the rest size, its top on the rest card's top). Shot: `d16-sim-tip-wide-rest-size.small.png`. Both legs 2 / 2 on the fix, NuvioTVTests 2303 / 0, Release sim green; merged as `78b83c261`, NOT cut.
- **test31D** is filed as BUG-223 / plan decision D10 (classify by a code read of `5a077731c` before any code).
- **The rest of §6** is on the plan's Wave 4 list (`docs/open-items-plan-2026-10-21.md` §7).
