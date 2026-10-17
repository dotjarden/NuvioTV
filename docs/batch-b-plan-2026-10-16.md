# Batch B: the mechanical half (B1–B10), 2026-10-16

**Status: MERGED 2026-10-17 00:1xZ on Christian's go ("merge, no cut yet"): `tvos-shared-extraction` fast-forwarded `8e8090806` → `d5dd6aec1` (5 commits), pushed, `claude/batch-b` deleted on `origin`; outer pointer bumped; NOT cut (rc5 is the next go).** Was: BUILT + REVIEWED + DEVICE-PASSED 2026-10-16, READY TO MERGE. Master plan `docs/master-plan-2026-10-14.md` §4.4 (re-sequenced 2026-10-16 from
Steven's rc4 verdict, `docs/steven-beta19-rc4-verdict-2026-10-16.md`), decisions D11–D15 accepted as written.
Clone `~/Claude/Projects/NuvioMobile-batch-b`, branch `claude/batch-b` off `tvos-shared-extraction`
`8e8090806` (Batch D + P4 merged, uncut). Not merged, not cut: rc5 (build 137) is cut on Christian's go
after the merge; its notes must say the heading details are OFF by default and that rc4's hero-ON folder
line is the toggle's ON state.

## Scope (his order)

| # | Item | Tracker | Agent |
|---|---|---|---|
| B1 | "Show Catalog Details in Headings" toggle, default OFF: Stage/Discover heading add-on suffix + the folder line on both Homes | BUG-145, BUG-159 revert, FEAT-67 | α |
| B2 | Exit from the mpv player suspends the app (repro on the device first, then fix) | BUG-165 P1 | main |
| B3 | Far-left card clipped with No Zoom on Focus ON | BUG-164 P2 | β |
| B4 | Per-row landscape cards: size from Poster Size, row height, trailer reveal | BUG-162, BUG-163 P2 | γ |
| B5 | Folder ← Detail restore on the Stage; Home ← folder re-grab regardless of age | BUG-156 P2 | δ |
| B6 | Stage heading→shelf second trim | BUG-146 P3 | β |
| B7 | Layout picker out of the folder page's band into Settings › Home Screen › Collections Layout | FEAT-71 | β |
| B8 | Best Result card: title, year, type only | FEAT-72 | α |
| B9 | Stage folder page seeds from the first item once row 0 lands, folder logo docked | FEAT-70 | β |
| B10 | DV profile 5 on mpv forces gpu-next + the routing note | BUG-166 quick half | α |

## Method

Wave 1: α (B1, B8, B10) ∥ β (B3, B6, B7, B9), main session on B2's probes, shield and simulator leg →
build + commit → Wave 2: γ (B4) ∥ δ (B5), B2 device repro + fix → gates (NuvioTVTests, Debug + Release
simulator, the relevant UI legs with `-collect-test-diagnostics never`) → two Opus read-only review
rounds (Codex on its limit until 10-29) → device pass in the Test 2 profile with the rig
(`docs/device-rig-2026-10-15.md`, `scripts/device/`, `preflight.sh` before every walk, rig lock
`~/.config/nuviotv-device/rig.lock`) → OUTCOME.

## OUTCOME

### Commits on `claude/batch-b` (off `8e8090806`)

| Commit | What |
|---|---|
| `029c6f847` | Wave 1: α (B1, B8, B10) + β (B3, B6, B7, B9) + the main session's B2 hardening and simulator leg |
| `378e29b19` | B2: `-debug.menuExitShieldOff` knob + the opt-in control leg |
| `d472c8411` | Wave 2: γ (B4) + δ (B5) |
| `07b482c1e` | Review r1 fixes (2 P1, 1 P2, P3-1..4) + legs for the new defaults (test105 rewritten, S16, S13) |
| `d5dd6aec1` | Review r2 fixes (P2-1 recognizer gating, P3-1/4/5/6) + the band's rest opacity (device finding) + leg test107 |

### Per item

- **B1 (BUG-145 + BUG-159 revert + FEAT-67).** Appearance › "Show Catalog Details in Headings" (`HeadingDetailsSetting`, key `show_catalog_details_in_headings`, default OFF). OFF: Stage and Discover headings print the bare catalog title (`\.rowHeadingShowsAddon` now carries the setting; Discover rows read the heading at draw time through `DiscoverRowsViewModel.heading(forRow:showsAddon:)` so the toggle is live), and the folder line ("name · N sources", `folderHeroDescription`) is dropped from the Classic hero-ON box (A5's line), the hero-OFF panel, the Stage folder copy and the folder page's intro (`HomeRowPreviews.folder(showsDetails:)`, `FolderRowsPlan.plainFolderPreview(showsDetails:)`); the collection title (`releaseInfo`) stays. ON = rc4. Strings ×5 in de/es/fr/it/vi, explainer `.appearanceHeadingDetails`. Tests `HeadingDetailsSettingTests`, `DiscoverRowsPlanTests`. **Release notes: OFF by default; rc4's hero-ON line is the toggle's ON state.**
- **B3 (BUG-164).** What the first card draws past its leading edge in No Zoom: the still ring nothing (a `strokeBorder` inside the frame); the still focus shadow (radius 22, measured reach ≈44 pt: 29 % darkness at the edge, 7 % at the old 26 pt cut, ~0 by 46); and the playing tile, which took ring mode's manual scale in No Zoom (35.6 pt leftward on a 16:9 tile). `RowLeadingEdgeClip.rowAllowance(noZoomOnFocus:accentFocusRing:restingWidth:artworkHeight:liftRise:)` opens 44 pt in No Zoom (was 26) and is byte-identical zoom-on (58 / 62 with the ring, pinned across six shapes); `CardSystemLiftStyle.resolve` never returns `.lift` in No Zoom. `RowLeadingEdgeClipTests` (new).
- **B6 (BUG-146).** `StripGeometry.headingGap` = `sm` (12) on the strip through `headingGap(inStrip:)` (keyed on `\.stripFocusMemory`, Classic keeps `md`), used by `CatalogRowView`, `CollectionRowView`, the loading / message / Discover retry rows, Continue Watching, Upcoming, `catalogRowHeight`, `collectionRowHeightMax`: heading → shelf 24 pt (was 28). The 20 pt zoom lift clears by 4; the accent ring is inside the artwork and rises with it, so it adds nothing. `StripGeometryTests` re-derived (every row −4, every stage +4; 154 dp titles-off zoom-on crosses the 480 compact-logo line: logo 110 → 150, synopsis 5 → 4 lines; fit boundary 168/169 → 170/171 dp).
- **B7 (FEAT-71).** Settings › Home Screen › Collections Layout (Rows / Grid, `folder_layout_default`, device-local, shown on Stage only); `FolderPageLayout.resolve(homeLayout:defaultGrid:)`. The pre-FEAT-71 per-folder Grid store is no longer read (r1 P2-1: nothing could undo a stored choice). The folder page's band keeps Edit Filters only, is invisible at rest (opacity 0.011: at 0 the focus engine skipped it on hardware, `moveFail heading=up`) and shows while its pill holds focus; with no filter-editable source the pill is "Go Back" (r1 P1-2: the loading folder keeps its BUG-47 anchor). Legs test105 (the setting through its launch argument) and test107 (Up from row 0 reaches the pill).
- **B8 (FEAT-72).** `SearchTopResultCard`: type always + year ("Movie · 2009"), no rating, no "Found in" (the row footnote keeps it). `SearchTopResultCardTests` (new).
- **B9 (FEAT-70).** `FolderStageInput.step` forwards the initial landing; the stage shows row 0's first item at once while the folder logo stays docked (`StageView(hidesLogo:)`); probe `folder initial-item card=… forward=1`. Legs test104/106 updated.
- **B10 (BUG-166 quick half).** `EngineDecision.prefersGpuNext` for any DV profile 5 the router sends to mpv (P5-in-MP4, or P5 with incompatible audio) and for the native → mpv fallback (`PlayerEngineRouter.mpvNeedsGpuNext(probe:)`); `MPVPlayerScreen(forcesGpuNext:)` → `vo=gpu-next` on hardware, `[MPV] vo=gpu-next reason=dv-p5`, note "· gpu-next"; the Enhanced Video Renderer explainer says so. Only when the native probe ran (native ON; with it OFF a P5 stays on `gpu` unless the renderer is on). `PlayerEngineRouterTests` (new). **Device check owed** (a P5 MP4 with the renderer OFF).
- **B4 (BUG-162 + BUG-163).** A shape-landscape row's card is `posterStyle.height` tall × `height × 16/9` wide (`PosterStyle.cardWidth/cardHeight`, `landscapeFromShape`; 624×351 at Medium+ against 234×351 portrait), so the row is planned at the portrait height and the heading sits where portrait headings do (the sim baseline gap was 112 pt, his ~120); the global Landscape Posters toggle keeps 360×203, Continue Watching / Upcoming / Search / Saga keep theirs. The audio-only trailer: the opaque base `LandscapeCard` never faded under the tile (`fadesBaseCard = !landscapeCatalogRows`); measured by A/B on the sim leg (card-region diff 0.00 → 16.7 once the fade applies to shape rows). Shape rows now fade the base card and take the portrait lift rule. DEBUG `-debug.addonManifestUrls` / `-debug.addonManifestRemoveMatching` seed add-ons for the legs (signed-in refusal as the collections seed); `testLandscapeShapeCatalogDrawsLandscapeCards` rebuilt (Steven's config, card height == the portrait card one row up, heading gap 38, tile == card, pixel diff once playing). `PosterStyleLandscapeRowTests` +6. Note: the bigger cards apply wherever a shape-landscape catalog renders (Classic, Search, Library too). The global toggle's path very likely carries the same audio-only defect (untouched, follow-up).
- **B5 (BUG-156).** (b) `FolderRowsPage` captures its push origin (`FolderPushOrigin`: the row + card at the focus loss, accepted within 2 s of a Select, or the current row) and restores it after a Detail pops through its own `StageController` (`source=folder` lines); the pager's `onRowChange` feeds `noteStripRowChanged`. (a) `UncoverRestorePolicy` (pure): the re-grab window runs 1.5 s from the LANDING on the target row (1.2 s from the request if it never lands), up to 3 re-grabs with the viewer-input clock live (the Classic walk saw the engine steal twice; today's device pass saw two on the folder page), retired by any viewer input at or after the pop (`ViewerInputClock`: a passive window recognizer stamping presses at `pressesBegan` and swipes past 40 pt; r2 P2-1: it fails itself only once no press and no touch is down, so a resting thumb keeps it listening). The strip memory is frozen under a push or the picker (`StripFocusMemory.setFrozen`), the card is snapshotted at the push edge. `-debug.uncoverStealMs` stands in for the hardware engine's late restoration. Probe lines for Steven's log: `folder push origin=… via=current|loss|none`, `restore pop row= item= clock=`, `restore landed … via=request|engine`, `restore regrab … age= since=landing|request n=`, `restore retired … why=viewer|expired|limit`. Legs: `testBatchB_StagePopRegrabsAfterALateSteal`, `testBatchB_StageViewerDownAfterPopIsNotPulledBack`, `testBatchB_FolderPopRestoresRowAndCard`, `testBatchB_FolderPopRegrabsAfterALateSteal`, test106. Residual: a push from a hold menu whose Select came > 2 s before the loss gets no origin.

### Reviews (Opus read-only, the Codex stand-in)

- **r1** over `8e8090806..d472c8411` (`docs/research/batch-b-review-r1-2026-10-16.md`): **2 P1 / 1 P2 / 9 P3.** P1-1 the cover's Menu recogniser stayed off after an in-place Up Next / failover swap (`isLeavingPlayer` is also true for `isMovingFromParent`) → re-enabled unless an ancestor `isBeingDismissed` (`coverIsBeingDismissed`). P1-2 FEAT-71 removed the loading folder's only focus anchor (the BUG-47 eject class) → the band always mounts while active, "Go Back" when nothing is editable. P2-1 a pre-FEAT-71 per-folder Grid choice could never be undone → the store is no longer read. P3-1/2/3/4 fixed (teardown comment, layer release on main, the shield's rule wired, the leg's comment); P3-5 (B10 needs the probe) and P3-8 (B4 sizes apply beyond the Stage) recorded above; P3-6 (freeze at `onDisappear` comes late) covered by the push-edge snapshot; P3-7 (40 pt swipe threshold) and P3-9 (global-toggle trailer path) are follow-ups.
- **r2** over the range with `07b482c1e` (`docs/research/batch-b-review-r2-2026-10-16.md`): **0 P1 / 1 P2 / 7 P3.** All three r1 P1/P2 fixes verified. P2-1 `ViewerInputRecognizer` failed itself at a press end while a clickpad touch was still tracked → `pressesDown` + `touchStart` gating. P3-1 `cover=` on the `[Failover] viewWillDisappear` line; P3-2 leg test107 for the band's reachability; P3-4 the rule now runs in `gestureRecognizerShouldBegin`; P3-5 the layer's last reference through `Unmanaged`, released on main; P3-6 the band's doc comment. P3-3 (the Go Back pill may flash before focus moves to row 0) and P3-7 (re-run the folder legs) covered by the final gates / device check.

### B2 · BUG-165 exit eject (device repro 2026-10-16 18:00–18:45 ET, Test 2, Living Room ATV, rig)

**What reproduces and what does not.** Baseline build `8e809080` and the Wave 1 build `029c6f847` (with
the hardening below) were walked from the Continue Watching hold menu → Play Manually → a source, with
Home underneath and native forced off through `-player.nativeDolbyVision NO` so the route is mpv:

| Exit press | Baseline | Fixed build |
|---|---|---|
| 100 ms Menu (1080p MKV) | clean, picker in ~1 s | clean (`menu began action=exit` → `shield armed` → `menu cancelled sinceExit=23ms` → `viewWillDisappear sinceExit=25ms` → `shield disarmed held=557ms swallowed=0` → `terminate_destroy took=76ms`) |
| 0 ms Menu (the 10-15 rig eject) | clean | clean (`took=111ms`) |
| Menu, then Menu 0.25 s later | — | clean, picker still up; the second press reached neither the controller nor the shield |
| 100 ms Menu from a 4K DV · HDR10+ MKV on gpu-next, second Menu 2.5 s later | — | clean; the second Menu dismissed the picker to Home, as it should |
| **Menu held 0.8 s** | **tvOS home screen, app suspended** | **tvOS home screen, app suspended, with NO `menu began` line**: mpv kept decoding in the background. The baseline run shows no third Vulkan teardown either. |

So the only eject either build produced is tvOS's own press-and-hold-Back-to-Home gesture, which the
system handles before the app sees the press. The native engine exited cleanly on the same walk. The
teardown that the 10-16 triage suspected (`mpv_terminate_destroy` on the main thread) takes 76–132 ms
once moved off it; the "6 s of black" in Steven's video is not the player's teardown on this box. In
Test 2 no display-mode re-sync happened (screenshots worked during the 4K play), so the TV-side
re-sync his Match Content setting adds could not be timed here.

**Working theory for his box.** His TV goes black for seconds after the exit (the HDMI re-sync back from
the title's mode: his Chihiro exit was black for ~4–6 s too, and that one landed on the picker), he
presses Back again and holds it, tvOS goes Home with the picker still up: exactly the "source list on
reopen" his video shows. His answer on the exact press (asked in the 21:06Z DM) decides. The app cannot
intercept the system hold.

**What was built anyway (hardening, all verified harmless on hardware):** `MenuExitShield` (a window
recogniser enabled only between the exit decision and the cover's end; it never claimed a press in
seven exits); `MenuPrecedence.swallowsRelease(.exit)` is now true (the exit press's release no longer
runs up the responder chain; tvOS cancels it anyway ~20 ms after the dismissal starts); the cover's
Menu recogniser is not re-enabled on the way out; `mpv_terminate_destroy` runs on `eventQueue` (the
Metal layer kept alive by the block) with `[MPV] terminate_destroy took=`; `[MenuProbe]` phase lines on
every Menu press; `-debug.menuExitShieldOff YES` A/B knob. Simulator legs
`testMenuExitOverRootKeepsTheAppForeground` (passes) and the opt-in control
`testMenuExitOverRootControlWithShieldOff` (`PLAYER_EXIT_CONTROL=1`): the control passes too, so the
simulator cannot show what the shield changes; the leg guards the exit-then-double-Menu path, not the
shield. Evidence: `docs/research/batch-b-device-2026-10-16/` (r3–r10, console-repro-b/c.log,
console-fix-a/b.log; redact `/stremio/<token>/` before committing logs).

**For the DM / release notes:** ask Steven whether he held Back; tell him a held Back is tvOS's Home
gesture and that the picker stays where it was on reopen; the mpv exit itself is now instant on the app
side. If his answer is a single short press, the next lever is his `[MenuProbe]` lines (every Menu press
now logs its phase), which need his console or a Developer pane readout (not built).

### Gates

| Tip | NuvioTVTests | Debug sim | Release sim | UI legs (FA87) |
|---|---|---|---|---|
| `029c6f847` (wave 1) | 103 in the touched classes / 0 | green | — | `testMenuExitOverRootKeepsTheAppForeground` + `testMenuHidesBarThenExits` pass |
| `d472c8411` (wave 2) | 1827 / 0 (1 skipped) | green | green | g1 folder 104–106 + StageDiscover 13/13; g2 BatchAFolder 4 + BatchAHomeReturn 6 = 10/10; g3 StageStrip 11 pass / 1 skip / S13 + S16 (expected, re-pinned) / S11 (pre-existing); g4 rail-profile 3/3, TrailerMotion 2 pass / 8 skip (YouTube) / test89 (pre-existing), RowLeadingEdge ×2 (pre-existing: fail on the untouched `8e8090806` clone too) |
| `07b482c1e` (r1 fixes) | 1819 / 0 (1 skipped; the 8 removed store tests) | green | green | S13, S16, test104 pass |
| `d5dd6aec1` (r2 fixes, final) | 1819 / 0 (1 skipped) | green | green | g6: test104/105/106/107 + the exit leg 5/5; g7: BatchAHomeReturn 6/6 + the landscape leg = 7/7 |

Device builds: `029c6f847` (BUG-165 verification), `07b482c1e` (the pass), `d5dd6aec1` (the band re-check and one exit). ⚠️ The range server for the exit legs: `iosApp/build/smoke/range_server.py 8000` serving `test-long.mkv` (cloned from the P4 clone), env `TEST_RUNNER_PLAYER_BAR_PROBE=1 TEST_RUNNER_PLAYER_SMOKE_URL=http://127.0.0.1:8000/test-long.mkv`.

### Device pass (Living Room Apple TV 4K, tvOS 27.2, Test 2, rig; console logs `console-pass-a/b/c.log`, screenshots `p1`–`p9` in `docs/research/batch-b-device-2026-10-16/`)

Build `07b482c1e` (Wave 2 + r1 fixes); the r2 build `d5dd6aec1` re-checked the band: Up from row 0 lands on the pill (`focus → frame=1597,81,184,66`), "Go Back" shows top-right for the add-on-only Test Folder (`p10-folder-up-pill`), Down returns to row 0 and the pill vanishes (`p10-folder-down`) → **B7 PASS**.

| Item | Result |
|---|---|
| B1 OFF (default) | **PASS**: bare catalog headings on the Stage; the folder's stage copy reads "Test Folder / Test Collection" with no sources line (`p1-row2`, `p1-row3`). |
| B1 ON (`-show_catalog_details_in_headings YES`) | **PASS**: "New Streaming Releases: Movies · AIO Metadata 1" (`p9-stage-heading-on`). The Classic hero-ON folder line is the same gate; not walked (Test 2's collection row sits past nine Classic rows) → Christian. |
| B6 heading gap | **PASS**: the heading sits right above the posters on Home and on the folder page (`p1-row3`, `p2-folder-open`). |
| B3 No Zoom far-left card | **PASS** with the trailer playing: full poster-colour ring, soft shadow, no cut (`p1-row3-leftcrop`); at rest the still ring is intact (`p2-folder-open`). |
| B9 folder seed | **PASS**: the page opens on Spider-Man's art + meta + synopsis with "Test Folder" docked (`p2-folder-open`, `folder initial-item … forward=1`). |
| B7 band | no pill at rest **PASS**; Up from row 0 on `07b482c1e` → `moveFail heading=up` (**FAIL**, fixed: rest opacity 0.011, leg test107) → re-check on the r2 build below. |
| B5 (b) folder ← Detail | **PASS**: `folder push origin=…_2/tt35934755 via=current`; after the pop the engine stole twice (`regrab from=outside age=44`, `from=…_1 age=74`, both `since=landing`), then `rung=1 landed=1` on row 2 card tt35934755 with Below's trailer playing (`p4-home-back`, which is the folder page). |
| B5 (a) Home ← folder | **PASS** visually (`p5-home-back`: the folder tile focused on the Test Collection row): `landed … after=593 via=request`, the engine paged to Upcoming at +53 ms, `regrab … n=1`, paged back; the probe then printed `retired why=expired` (the re-grab's own landing is not recorded: logging gap, follow-up). |
| B8 Best Result | **PASS**: "Avatar / Movie · 2009", no rating, no Found in (`p7-search-avatar`). |
| BUG-165 exit on the batch build | **PASS** ×6 (100 ms, 0 ms, double, 4K DV HDR10+, with the r1 cover rule): picker every time, `menu ended/cancelled swallow=1`, destroy 76–136 ms. |
| B4 landscape row | **PASS** (round 2, rig, stub add-on `scripts/device/fixtures/landscape-addon.py` in Test 2 at Medium+): the fixture row's focused card is 624 × 351 (focus frame `140,1098,624,395`) against 234 × 351 (`234,395`) on the portrait rows above and below, the heading "Landscape Row (fixture)" sits right above the cards (`q8-down11`, `q12-row-above` for the pair), and the in-row trailer shows its PICTURE on the card: `[TrailerZoom] reveal … surface=inline key=movie:zzland-dune`, layer 616×343, burst frames at 1.06 s and 7.37 s show the Dune trailer's frames (`q10-trailer-burst.burst/*.jpg`, `q11-trailer-playing-2`); `q9` caught the trailer's own black opening frame at the reveal. Add-on removed afterwards (`t6`, `t7`). |
| B10 DV P5 → gpu-next | **PASS** (round 2, rig, `-player.enhancedRenderer NO -player.nativeDolbyVision YES`, Dune: Part One, Torrentio "[2021 WEB-DL 2160p Dolby Vision TV]" 29.41 GB Rutracker, the P3-F7 file): `[PlayerRouter] mpv — DV P5 in MP4 (remux unsupported) — Dune`, `[MPV] vo=gpu-next reason=dv-p5`, `[MPVStats] vo=gpu-next`, 88 s of play with `underruns=0`, cache 54–67 s; the one screenshot the HDR output allowed (`s7-p5-playing`, +10 s) shows the Legendary logo in gold on dark blue, no green/magenta cast. Exit on one Menu clean (`isLeavingPlayer=true cover=1 sinceExit=27ms`, shield held 548 ms swallowed 0, `terminate_destroy took=205ms`). The periodic `vt decoder cb: output image buffer is null: -12909` / `hardware accelerator failed to decode picture` pairs (22 in 90 s, `dropped=vo:14`) are pre-existing on this file: the P3 pass of 10-15 logged 42 of them on mpv with the renderer ON (`console-rig-b.log`). |
| `-folder_layout_default grid` | sim leg test105; not walked on the box. |

Observation (pre-existing, not Batch B): the Stage's Continue Watching and Upcoming headings float ~140 pt above their 16:9 cards (the rows are planned at the portrait height; Batch A's `g4-home-rest` shows the same). Same class as BUG-162 (b); a follow-up if Steven notices.

### Device pass round 2 (2026-10-16 ~20:45–21:10 ET, rig, Test 2): B4 + B10

Dev build of the merged tip `d5dd6aec1` (device Debug, `-allowProvisioningUpdates`, profile to 2026-10-22 04:23Z, app UUID `4E3AF5FF-011D-3C0E-A36B-E79C2D4C168E`, debug dylib `8E314EBE-85C0-3854-B816-7F94067C6FAD`, 139 MB, container `D82CB8F6…`) installed over devicectl; the device cache was cloned from the P4 clone into `NuvioMobile/iosApp/build/DerivedDataDevice` (APFS clonefile, 2 s). Console logs `console-b4.log`, `console-b10.log`, `console-final.log` (redacted); screenshots `q*` (B4), `s*` (B10), `t*` (cleanup) in `docs/research/batch-b-device-2026-10-16/`.

- **B4 walk.** Launched with `-home_layout stage -inline_trailers_enabled YES -trailer_playback_location poster -debug.posterSizeOverride mediumPlus -debug.trailerProbe YES` (overrides for this process only; nothing stored changed). The stub add-on (`scripts/device/fixtures/landscape-addon.py`, port 8766: manifest + one catalog of eight `posterShape: landscape` metas with metahub 16:9 backdrops and each title's YouTube trailer, ids under the fixture's own prefix so Cinemeta never answers) was installed through Add-ons › Install from manifest URL typed over Companion (`q4`–`q6`, "Installed Landscape fixture."), because the DEBUG `-debug.addonManifestUrls` seed refuses a signed-in account. Home grew 11 → 12 rows; eleven Downs reached the fixture row (`q8`): card 624 × 351 at Medium+, heading right above, Dune's art + logo + meta on the stage. The trailer ran the normal pipeline (`dwell fired` → `expand branch=miss` → extraction 2.2 s → `attach surface=inline` → `reveal reason=cap`), and the burst shows its picture on the card (1.06 s: Paul in the Atreides uniform; 7.37 s: the box scene) — BUG-163's audio-only path is gone on hardware. Up one row: a portrait card at `234,395` (`q12`), the same 395 pt frame height.
- **B10 walk.** Relaunched with `-player.enhancedRenderer NO -player.nativeDolbyVision YES -home_layout stage` (the first attempt on Classic had the rail press vetoed and a Down + Select open Lizzie Borden's picker; harmless). Search "Dune" → top result → Play within 2 s → Sources: Comet first, Torrentio collapsed (`s4`), expanded and walked to the Rutracker "Dolby Vision TV" 29.41 GB row (`s6`). Select → the router line, the forced vo line and the stats above; a fast vertical swipe opened the Info panel (`[Scrub] stroke end intent=v`), screenshots then failed for the rest of the play (HDR output), Menu closed the panel and a second Menu exited cleanly to the picker (`s10`).
- **Cleanup.** Fixture add-on removed through the row's hold menu → Remove Add-on → "Remove Landscape fixture?" → Remove (`t4`–`t7`; BetterPosters is the last row again); fixture server stopped; the app relaunched with no arguments and auto-entered Test 2 on its stored Classic Home (`t8`); console stopped; rig lock released. Nothing stored in Test 2 was changed (every setting ran as a launch-argument override).
- **Rig fixes on the way:** `preflight.sh` greps with `-a` (a log with NULs read as "binary" and the pid check failed); `console.sh stop` now waits for the stream process to exit, because a stream killed mid-write prints its "App terminated due to signal 15" lines at its old offset and punched 90 NULs into the log a following `start` had already truncated and reused. One Companion connect timed out (`_systemInfo`) before any press and succeeded on the retry (port 58625 after a re-resolve).

### Left for Christian (feel items the rig cannot judge)

1. Classic Home, Show Hero ON, a collection folder focused: the box shows the wordmark and Open Folder only; with "Show Catalog Details in Headings" ON the "name · N sources" line returns (rc4's look).
2. ~~Steven's landscape add-on in Test 2 at Medium+~~ DONE by the rig with the stub add-on (round 2 below); only the look of his own add-on's art is left to his eye.
3. ~~A DV profile 5 MP4 with Enhanced Video Renderer OFF and native ON~~ DONE by the rig (round 2 below): the vo line is in the console and the one SDR-window screenshot has correct colours; the panel-side HDR look stays his.
4. BUG-156 with a thumb resting on the clickpad: Back out of a folder, then one Down click without lifting inside a second: the strip must follow the Down (`restore retired … why=viewer input=down`), never pull back.
5. The folder page's pill: Up from row 0 shows "Edit" (or "Go Back" for an add-on-only folder) top-right, nothing at rest.
6. BUG-165: Steven's answer on the exact press decides; a held Back is tvOS's Home gesture.

### Follow-ups (not in this batch)

- The Stage's own 16:9 rows (Continue Watching, Upcoming) show the BUG-162 (b) floating heading (pre-existing).
- The global Landscape Posters toggle's trailer path very likely has BUG-163's audio-only defect (untouched).
- B5: a re-grab's own landing should log `restore landed`; the 40 pt swipe threshold is unproven on hardware.
- B10 with native OFF: no probe runs, so a P5 stays on `gpu` unless the renderer is on.
- P1-1 (cover recogniser after an Up Next swap into native) has no UI leg; the `cover=` probe field is in for the device.
- Pre-existing failing legs on the baseline `8e8090806` too (not Batch B): `RowLeadingEdgeTests` ×2, `StageStripUITests.testS11_HoldMenuOnStripPoster`, `TrailerMotionUITests.test89HeroTextNeverDoubles`.
- Translation pass for the 7 new keys is done (de/es/fr/it/vi); "Stage" in the Collections Layout subtitle stays untranslated like the existing strings.

### Merge recipe (on Christian's go)

```
cd "~/Claude/Projects/Nuvio tvOS/NuvioMobile"
git fetch ~/Claude/Projects/NuvioMobile-batch-b claude/batch-b:claude/batch-b
git checkout tvos-shared-extraction && git merge --ff-only claude/batch-b && git push origin tvos-shared-extraction
git push origin --delete claude/batch-b && git branch -d claude/batch-b
cd .. && git add NuvioMobile && git commit -m "Batch B merged: NuvioMobile tvos-shared-extraction 8e8090806 → <tip>"
```
Then rc5 (build 137) through `scripts/cut-rc.sh`; release notes: every new setting with its default (Show Catalog Details in Headings OFF, rc4's hero-ON line is its ON state; Collections Layout Rows; the folder page's Layout pick moved to Settings), the Best Result card fields, landscape add-on rows at Poster Size, DV profile 5 on mpv uses gpu-next, the mpv exit is instant on the app side. The clone can be deleted after the merge.
