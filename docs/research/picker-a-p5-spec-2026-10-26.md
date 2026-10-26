# Stream picker A — Wave P5 spec (tests), 2026-10-26

Plan: `docs/stream-picker-addons-plan-2026-10-25.md` §2 "Wave P5" and §8 (P5 rows). Branch `picker-a` in the clone `~/Claude/Projects/NuvioMobile-picker-hub` (tip `865ba971a`). Everything below lives under `iosApp/`. Write only; do NOT build, test, commit, or run `git add`. Report what you wrote, every judgment call, anything left undone.

## 0. Ground rules
- Both test targets use file-system-synchronized groups: a new file under `NuvioTVTests/` or `NuvioTVUITests/` joins its target with no pbxproj edit.
- The UI harness convention is one self-contained class per file: copy the small helpers (`element`, `pause`, a `launch`) into the new file rather than reaching into `NuvioTVUITests.swift` (its helpers are `private`). `DetailEntryRoute.selectChrisTile(_:_:timeout:)` and `DiscoveryStubServer` are shared and may be used.
- Identifiers the leg may query (all exist on `picker-a`): `stream_picker_source_panel`, `stream_picker_chip_row`, `stream_picker_chip_all`, `stream_picker_chip_refresh`, `stream_picker_chip_<index>` (0-based, in group order), `stream_picker_row` (every row carries this same identifier), `stream_picker_section_label`, `stream_picker_progress`, `stream_picker_resume_pill`, `stream_picker_empty_reason`; Detail: `detail_hero`, `detail_action_play`; player: `player.native`, `player.mpv`, `player.loadingOverlay`.
- Chips are `Button`s with the `.isSelected` trait when selected (so `XCUIElement.isSelected`) and accessibility labels of the form "ZZ Picker A, 3 sources" / "…, 1 source" / "…, loading" / "…, failed" (`SourceChipRow.accessibilityLabel(for:)`).
- The FA87 fixture (tvOS 26.5) reports `hasFocus`. Never press Select on anything whose focus you have not read first, except the one Play press and the one row press this spec names.
- Doc comments in the house style (see `PostPlayUITests.swift`, `BatchAFolderUITests.swift`): what the leg proves, which knobs it uses and why, what makes it skip rather than fail.

## 1. NuvioTVTests additions

### 1.1 `StreamsViewModelFilterTests.swift` — add two tests (keep the existing helpers)
- `testChipLabelsFollowTheFanOut`: apply `state(fanOut(loading: true), filter: nil, loading: true)`; assert `vm.sourceChips.map(SourceChipRow.label(for:))` == `["Comet \u{00B7} 2", "Torrentio", "AIO"]` (the loading chip omits its count, the failed empty one has count 0 → label "AIO" per `SourceChipRow.label`, check the implementation and match it exactly). Then apply `state(fanOut(), filter: nil, loading: false)`; assert the labels are `["Comet \u{00B7} 2", "Torrentio \u{00B7} 1", "AIO"]` and `SourceChipRow.chipsToDrop(vm.sourceChips)` == `["addon:aio"]` (failed with nothing listable → dropped once the fan-out settles; Comet/Torrentio are kept).
- `testChipOrderIsGroupOrder`: apply a state whose groups come in the order AIO, Comet, Torrentio (reuse `group(...)`), assert `vm.sourceChips.map(\.id)` == `["addon:aio", "addon:comet", "addon:torrentio"]` and that `vm.groups.map(\.id)` under "All" lists only the listable ones in that same order (`["addon:comet", "addon:torrentio"]`).

### 1.2 New `NuvioTVTests/StreamsRepositoryFilterRoundTripTests.swift`
`import XCTest`, `import SharedCore`, `@testable import NuvioTV`, `@MainActor final class`. The shared singleton `StreamsRepository.shared` exposes `uiState` (a Kotlin `StateFlow<StreamsUiState>`, read in Swift as `StreamsRepository.shared.uiState.value as? StreamsUiState`) and `selectFilter(addonId: String?)`.
- `testSelectFilterRoundTripsThroughTheSharedRepository`: `StreamsRepository.shared.selectFilter(addonId: "addon:test")`; read the state and assert `selectedFilter == "addon:test"`; then `selectFilter(addonId: nil)` and assert `selectedFilter == nil`. Restore nil in a `defer`/`tearDown` so no other test sees a filter. If the Swift bridge exposes `value` under a different name (check `SharedCore.h` under `iosApp/build/DerivedData/Build/Products/Debug-appletvsimulator/SharedCore.framework/Headers/` if present, else the Kotlin source), use that name and say so in the report.

### 1.3 Nothing else
`StreamPickerResumeTests` (7 cases) already covers the pill; `StreamFactsParserTest` is Kotlin. Do not add Swift twins.

## 2. New `NuvioTVUITests/StreamPickerUITests.swift`

One leg, `final class StreamPickerUITests: XCTestCase`, `let remote = XCUIRemote.shared`.

### 2.1 The fixture add-ons (served by `DiscoveryStubServer(routes:)`)
Two stream add-ons on one stub, path prefixes `/picker-zz-a/` and `/picker-zz-b/`. The removal knob matches `"/picker-zz-"` (both). `stub.origin` is `http://127.0.0.1:<port>`.
- Manifest A (`prefix: "/picker-zz-a/manifest.json"`):
  `{"id":"zz.picker.a","version":"1.0.0","name":"ZZ Picker A","description":"Stream picker P5 leg","resources":[{"name":"stream","types":["movie"],"idPrefixes":["tt"]}],"types":["movie"],"catalogs":[]}`
- Streams A (`prefix: "/picker-zz-a/stream/movie/"`), three direct links:
  `{"streams":[{"name":"ZZ A\n1080p","title":"Dune 2021 1080p WEB-DL","url":"<origin>/picker-zz-a/media/a1.mp4"},{"name":"ZZ A\n720p","title":"Dune 2021 720p WEB","url":"<origin>/picker-zz-a/media/a2.mp4"},{"name":"ZZ A\n480p","title":"Dune 2021 480p","url":"<origin>/picker-zz-a/media/a3.mp4"}]}`
- Manifest B: as A with id `zz.picker.b`, name `ZZ Picker B`, prefix `/picker-zz-b/`.
- Streams B: two direct links (`b1.mp4`, `b2.mp4`), titles "Dune 2021 2160p" and "Dune 2021 1080p".
The stub answers 404 JSON for the `.mp4` paths; the leg never needs them to play, only to be chosen.
Build the bodies with string interpolation of `stub.origin` AFTER `stub.start()` (the port is ephemeral), so the `routes` array must be built after `start()` — `DiscoveryStubServer.init(document:routes:)` takes the routes up front, so start one stub to learn the port? No: the route bodies can use RELATIVE stream URLs only if the parser resolves them (unknown). Instead: pick the port first by starting the stub, then build a SECOND `DiscoveryStubServer` with the interpolated bodies and use that one; stop the first. Say in the report if you find a cleaner way (e.g. the stub exposes `origin` before routes are needed).

### 2.2 Launch sequence (three launches, like `BatchAFolderUITests.testLandscapeShapeCatalogDrawsLandscapeCards`)
Helper `launch(_ extra: [String]) -> XCUIApplication`: `app.launchArguments = extra`, `app.launch()`, wait up to 90 s for a button whose label contains "Chris", then `DetailEntryRoute.selectChrisTile(self, app, timeout: 5)`.
Common arguments on every launch: `-home_layout classic`, `-debug.rememberLastProfile NO`, `-detail_trailer_autoplay NO`, `-debug.trailerForceNoTrailer YES`, `-hero_trailer_autoplay NO`, `-debug.streamAutoPlayModeOverride MANUAL` (the picker must show; auto-play would skip it).
1. **Seed launch:** common + `-debug.addonManifestRemoveMatching /picker-zz-` + `-debug.addonManifestUrls <origin>/picker-zz-a/manifest.json,<origin>/picker-zz-b/manifest.json`. `pause(14)` (the seed applies on Home's first add-ons emission). Terminate.
2. **Leg launch:** common + `-debug.openDeepLink nuviotv://title?id=tt1160419&type=movie&name=Dune` + `-detail_layout cinematic` + `-home_upcoming_row_enabled NO`. Wait up to 45 s for `detail_hero` or `detail_action_play`; if neither appears, `XCTSkip` ("the deep link never produced a Detail page — network or fixture, not the picker"). Then wait up to 15 s until the focused element (`app.descendants(matching: .any).element(matching: NSPredicate(format: "hasFocus == true"))`) has a label starting with "Play" / "Resume" (if focus is elsewhere, `XCTFail` naming the focused label; do NOT walk focus). Press Select once.
3. **Cleanup launch** in a `defer` registered right after the seed launch: terminate, `launch(common + ["-debug.addonManifestRemoveMatching", "/picker-zz-"])`, `pause(10)`, terminate. The fixture must never keep the stub add-ons.

### 2.3 Assertions on the picker (after the Play press)
a. `stream_picker_source_panel` exists within 20 s. Print `[PickerLeg] panel up`.
b. Rows: `app.descendants(matching: .any).matching(identifier: "stream_picker_row")`; wait up to 20 s until `count >= 5` (3 + 2 under "All"). Assert exactly 5 (`XCTAssertEqual`, message naming the count; if the fixture has other movie stream add-ons installed the count is higher — then assert `>= 5` and print the labels of the chips instead; decide at run time: `>= 5` is the assertion, `== 5` is a print).
c. Info panel: an element labelled "Dune" exists inside the picker within 10 s (the `TitleLogoHeader` image carries `accessibilityLabel(title)`, or its text fallback shows the title). Record `[PickerLeg] title shown as image|text`.
d. Chips: `stream_picker_chip_all` exists and `isSelected`; `stream_picker_chip_0` and `stream_picker_chip_1` exist; the set of their labels equals `{"ZZ Picker A, 3 sources", "ZZ Picker B, 2 sources"}` (order = install order, normally A then B; assert the set, print the order). `stream_picker_chip_2` does not exist (only when the row count was exactly 5).
e. Section labels under "All": `stream_picker_section_label` count == number of chips with sources (2 when exactly 5 rows).
f. Initial focus: the first `stream_picker_row` (`element(boundBy: 0)`) `hasFocus` within 5 s (poll every 0.25 s). This is the P4 device-pass fix (`865ba971a`): the request re-issues until focus is observed on the first row.
g. Right from the list steps the chip: press `.right`, `pause(0.6)`; the chip whose label starts with the FIRST chip's add-on name is `isSelected`, `stream_picker_chip_all` is not, the row count drops to that add-on's count (3 or 2), and the first row still `hasFocus` (the step keeps focus on the list). Press `.right` again: the other chip is selected, the row count is the other count. Press `.right` once more: wraps to "All" (selected, 5 rows). Each press 0.6 s apart (the throttle is 112 ms).
h. Up from the first row lands on the selected chip: with "All" selected, press `.up`, `pause(0.6)`, assert `stream_picker_chip_all.hasFocus`. Press `.right` on the chip row (focus moves to chip_0, NOT a selection change: assert chip_0 `hasFocus` and "All" still `isSelected`). Press `.select` on chip_0: it becomes `isSelected`, focus stays on chip_0, rows == its count. Press `.down`: the first row `hasFocus`.
i. Resume pill absent: `stream_picker_resume_pill` does not exist (no progress for this title on the fixture; if it does exist, print its label and do not fail).
j. Select plays: with the first row focused, press `.select`. Within 30 s one of `player.native`, `player.mpv`, `player.loadingOverlay` exists (the stub 404s the media, so the player may fail afterwards; existence is the assertion). Print which. Then press `.menu` up to 3 times, 1 s apart, until `stream_picker_source_panel` or `detail_hero` is back (best effort, no assert).

Collect every `[PickerLeg]` print so the run log can quote them. Timeouts generous (the sim is slow); no `sleep` longer than 1 s in a loop step.

### 2.4 Skips vs failures
Skip only when the Detail page never appears (network). Everything after Play is a failure, with messages that name identifiers and labels seen (`focusedNodes`-style dump: iterate `app.descendants(matching: .any).matching(NSPredicate(format: "hasFocus == true")).allElementsBoundByIndex` and print identifier + label).

## 3. Report
Files written, line counts, every deviation from this spec with the reason, and any identifier or API you could not find (name the file you looked in). Do not run anything.
