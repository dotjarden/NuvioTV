# Batch P Wave 2: spec critique (Opus, read-only), 2026-10-21

Scope: the Wave 2 table in `docs/batch-p-steven-rc10-plan-2026-10-20.md` (W2-1 to W2-5), read against the clone `~/Claude/Projects/NuvioMobile-batch-p2` at `3cf873994`. Paths are relative to `iosApp/NuvioTV/` unless they start with `iosApp/`. No code was changed.

**Verdict.** W2-1, W2-2 and W2-4 can go to their owners after the small fixes below. W2-3's three candidate fixes rest on a reading the code does not support: the 1.13 s matches the rail's focus hand-off ladder, not a keyboard mount. Re-scope the spike before agent B starts. W2-5's knobs (c) can be built in one pass once the "fade mask" knob is re-targeted. The fan-out cut (a) is judgment work and should come back as a findings report, not a shipped fix.

---

## 1. Drift found

| Spec line | What the code says | Correct anchor |
|---|---|---|
| W2-1: "applies cleanly; `SourcesSettingsPane.swift` only" | The patch applies cleanly. Tweak (b) needs a new `SettingsDescriptionID` case and its copy, which live in a second file. | `Screens/Settings/SettingsDescriptions.swift:172-174` (cases) and `:375-377` (copy) |
| W2-1: `.sourcesPluginRepo` "if its text fits the header" | It does not fit. The copy says "Removes this plugin repository and its providers from this Apple TV." The patch already moves that ID onto the Remove row. The header needs its own case. | `SettingsDescriptions.swift:376` |
| W2-1: "Seven new strings" | The patch adds 6 new keys, and the tweak (b) copy makes 7. One key is `"%lld of %d providers on"`, not `%lld of %lld`, because `scraperCount` is a Kotlin `Int` (Int32). "Remove" and "Cancel" already exist. The patch also orphans `"1 provider"` and `"%d providers"`. | `Localizable.xcstrings:655`, `:2254` |
| W2-1: "the MDBList disconnect alert" as precedent for an `.alert` on a section | That alert is not in this pane. It sits on a `SettingsSection` in the Services pane, and SettingsView owns the others. | `Screens/Settings/ServicesSettingsPane.swift:51`; `SettingsDestructiveRow` doc at `SettingsRowViews.swift:740` |
| W2-1: sort moves to `PluginsViewModel.sortedScrapers(in:)` "with a unit test" | As an instance method this can't be unit-tested. `scrapers` is `private(set)` and only the `FlowWatcher` on `PluginRepository.shared` fills it. | `Screens/PluginsViewModel.swift:13`, `:17-25`, `:77-79` |
| W2-2: "`DetailView.isTrailerActive` gains `seriesPlay == nil`" | Correct. The gate is at `Screens/DetailView.swift:1436-1441`. The shuffle sheet is a second presentation that is also missing from the gate (see §2). | `DetailView.swift:432`, `:1166` |
| W2-3: "the black is the `.searchable` container holding its content until the keyboard is laid out" | This is an inference, and the code points elsewhere. A rail select runs `fallbackHandOff`, which calls `resetFocus` at +0.35 s and again at **+1.0 s** on the Search tab (`SidebarHandOffLadder.search = [0.35, 1.0, 1.75, 2.5]`). The comment there says the keyboard "arrives 1-2 s after the tab opens". Both visits measured exactly 1.13 s, which looks like a timer, not a layout cost. | `DesignSystem/NavigationRail.swift:1100-1108`, `:1153-1182`; `DesignSystem/HiddenTabBarRedirect.swift:57-66` |
| W2-3: candidate (1), "draw the wash/background in a layer the container does not own" | The background and the wash already sit in a `ZStack` *below* `SearchFieldLayer`. On an empty query the wash is empty by design: `clear()` runs on an empty field, and the wash only follows the Top result after keyboard focus. `Theme.Palette.background` is `0x0D0D0D`, or `0x000000` with OLED True Black, which Steven runs. Black is the page's own look when the idle page shows nothing. | `Screens/SearchView.swift:39-45`, `:184-192`, `:244-249`; `Screens/Search/SearchWashDriver.swift:53-58`, `:81-86`; `DesignSystem/Theme.swift:17`, `:64` |
| W2-3: fade out "on `searchKeyboardFocused`" | That flag is written only in Rail mode, by `HiddenTabBarFocusBlocker` mounted inside `NavigationRail`. In Tabs mode it never turns true, so a cover gated on it would never fade. | `DesignSystem/NavigationRail.swift:59-62`, `:538-543`; `ContentView.swift:556` (`if NavigationChrome.isRail()`) |
| W2-3: candidate (2), "keep the Search tab's view alive across tab switches (`MainTabView`)" | The `TabView` already keeps tab subtrees alive (see the "kept-alive tab subtree" comment). `SearchOpenProbe.appear` is an `onAppear`, which fires on every visit even when the view is not rebuilt. A per-visit 1.13 s with a live subtree rules this candidate out. | `ContentView.swift:453-466`, `:534-537`; `SearchView.swift:82-89` |
| W2-3: `navigationChrome.searchKeyboardFocused` "in `ContentView.swift`" | The model is `NavigationChromeModel`, in `NavigationRail.swift`, not `ContentView` or `NavigationChrome.swift`. | `NavigationRail.swift:62`, `:100-103` |
| W2-4: "Delete `RailGlassVariant` … its tests/UI references" | Unit test: `NavigationChromeTests.swift:341-352`. **There are no UI references to the flag.** `railGlass(_:)` in `NavigationRailUITests.swift:741` (used at 763/793/862/966/974/993/1007) is the glass-*bounds oracle* helper and must stay. No outer `scripts/` reference `-debug.railGlass`. | `NavigationChrome.swift:398-419`; `NavigationRail.swift:631-649` (`pillGlass`, used at `:685` and `:744`) |
| W2-5 (a): "the existing body counters (`HomeRowsList.top`, …)" | No counter is named `HomeRowsList.top`. The counter is `HomeBodyCounter` (DEBUG only). It ticks `HomeRowsList` at `Screens/Home/HomeRowsList.swift:109` and is read through the `debug_bodycounts` AX label (`HomeView.swift:892`). It has no tick for `StripPager`, `StageStripHome` or a strip page. | `Screens/HomeBodyCounter.swift:14-43` |
| W2-5 (a): fan-out files | The strip's host, row closure and `HomeViewModel` observation are in `Screens/Home/StageStripHome.swift`, which the spec does not name. The rows are built there, not in HomeView. | `StageStripHome.swift:48` (`@ObservedObject model`), `:235-265`, `:268-283` |
| W2-5 (a): anchors | `CatalogRowView` is at `BrowseComponents.swift:4947` (its body at `:5194`) and `InlineTrailerCardModel` at `InlineTrailerCard.swift:365`. Both are correct. The Stage hero's model is `StageController.bgTrailer` (`StageController.swift:44`), observed by `StageBackgroundTrailer` (`StageView.swift:147`) and `HomeHeroLeaves.swift:308`. Each card also owns its own model (`InlineTrailerCard.swift:2229`). | — |
| W2-5 (b): trace symbolication | `rc10-home-timeprofile.trace` and `rc10-tp.xml` exist in `~/Library/Logs/nuviotv-traces/`. The Wave 0 build was a bundle-overridden Release from the P5 clone, which is now gone. The only Release dSYMs on disk are `NuvioMobile/iosApp/build/{tvos-ipa,DerivedDataDeviceRelease}/…/NuvioTV.app.dSYM`, and they may not match that build. Check UUIDs (`dwarfdump --uuid` against the trace's image list) before relying on `--dsym`. | — |
| W2-5 (c): `-debug.homeNoFadeMask`, "the row edge fade drawn as a mask per card" | The Row Edge Fade is a per-**row** mask, active only when the setting is Soft. Steven runs Off, and the default is Off. It can already be A/B'd from the launch line with `-row_edge_fade off`, and Wave 0 run 3 did exactly that. The mask that is on in every configuration on the Stage walk is the strip's `StripEdgeMask`. | Row fade: `DesignSystem/RowEdgeEffectStyle.swift:121-149` (`RowSoftEdgeMaskModifier`), `:211`, `:218`. Strip mask: `Screens/Home/StripPager.swift:387-389`, view at `Screens/Home/StageView.swift:314` |
| W2-5 (c): "launch-latched like `RailGlassVariant` was" | W2-4 deletes that type in the same wave, and it belongs to agent B. Point agent C at the pattern instead (`nonisolated enum`, `static let current = UserDefaults…`, readable in Release), e.g. `RailSearchInsetHold`, `NavigationChrome.swift:393-396`. The knobs go in a new C-owned file. | — |
| W2-5 (c): "Card Depth … a knob is the only A/B" | Debug overrides already exist (`-debug.cardDepthOn/Edge/Coverage/Sheen`), but they are `#if DEBUG`. The rig walks **Release**, so the new knob must not live there. | `DesignSystem/CardDepthStyle.swift:240-276`, `:306`, `:313` |

## 2. Per item

### W2-1, BUG-197 Plugins rows (agent A)
**Implementable in one pass?** Yes, once the sort rule's testability is fixed and the seeding rule is pinned down.

**The patch itself**
- **Compile.** `SettingsRowChrome { … } trailing: { … }` matches the two-builder init at `SettingsRowViews.swift:231-240`. The leading-only extension is at `:251-255`. `SettingsRowLabel(title:subtitle:systemImage:)` matches `:290-298`. The `let` bindings inside the `ForEach` builder closure are legal. `String(localized: "\(enabledCount) of \(repo.scraperCount) providers on")` compiles, since Int32 interpolation already does at old line 391. `Text("\(repo.name) and its providers …")` is a `LocalizedStringKey` and is extracted. No compile risk found.
- **Button style.** None is needed. The kit's list buttons (`SettingsActionRow`, `SettingsDestructiveRow`, `SettingsSwitchToggleStyle`) are plain `Button`s whose label is `SettingsRowChrome`, at `SettingsRowViews.swift:731-737`, `:765-776`, `:454-470`. The header matches them, and dropping the old `.chip` style is correct.
- **Explainer.** The header passes no `descriptionID`, so the explainer pane keeps the last described row. Tweak (b) fixes this: pass `descriptionID:` to the header's `SettingsRowLabel`. `SettingsDescriptionsTests.testEveryIDIsUsedAndOnlyKnownIDsAreUsed` (`NuvioTVTests/SettingsDescriptionsTests.swift:40-45`) scans `Screens/Settings/` for literal `descriptionID: .x`, so the new case must appear in that form.
- **`.alert` on `SettingsSection`.** `SettingsSection` is a `Section` inside the scaffold's `List` (`SettingsPaneScaffold.swift:53-56`). The only precedent is MDBList (`ServicesSettingsPane.swift:51`). No test shows whether a modifier on a `Section` is distributed to each row, which could present once per row or warn "already presenting". Verify on the sim that it presents exactly once with three or more repos expanded. If it doesn't, attach the alert to the Remove row, which is focused and on screen when pressed.
- **Focus after collapse.** Low risk: the focused header row survives the toggle.
- **Focus after Remove.** Medium risk. After confirming, the presenting row and its whole block disappear. Alert dismissal tries to return focus to a deleted row, so the List falls back, often to the pane's first row. BUG-47 holds, because "Enable Plugins" and the entry row stay focusable. The visible jump to the top needs a UI check.
- **List identity.** A `ForEach` keyed by `manifestUrl` whose content yields several rows, with the inner `ForEach(id: \.id)` composed under it, is fine. A `scraper.id` shared across two repos no longer collides. Expanding and collapsing inserts and removes rows without animation. Acceptable, but name it in the pass.
- **Data mismatch.** "N of M": N counts `scrapers(in: repo)`, while M is `repo.scraperCount` from the manifest (`PluginModels.kt:53`). During a refresh, or with providers not yet downloaded, you get "3 of 5" with three rows listed. Use `repoScrapers.count` for M, or state why not. There is also no singular form, so "1 of 1 providers on".

**The two tweaks**
- (a) **"Seed on appear and when the count becomes 1" is the likeliest bug.** In a lazy `List`, `onAppear` on a section or row fires every time a row scrolls back in. That re-inserts the URL and re-expands a lone repo the user had collapsed. A `.onChange` attached to the `Group` or `Section` is distributed per child. Recommended instead: derive it. Keep `toggledPluginRepos` and compute `isExpanded = (repositories.count == 1) != toggled.contains(url)` as a pure, unit-testable function. This needs no lifecycle hook, and the lone repo is open by default and stays closed once closed. Note: `plugins.start()` runs in SettingsView's `onAppear` (`Screens/SettingsView.swift:97`), so `repositories` is often empty on the pane's first frame.
- (b) is placed correctly on the header `SettingsRowLabel`. It needs a new case. Suggested copy: "Shows or hides this repository's providers."

**Sort rule.** Make it a `nonisolated static func` over `[PluginScraper]`, or over any name-bearing value, so the test does not drive `PluginRepository`. Building a `PluginScraper` in Swift means calling the full Kotlin init: 14 parameters, because defaults are not exported (`PluginModels.kt:98-112`). A generic `sortedByName(_:name:)` tested with strings is simpler. Test "b" before "C", and "Provider 2" before "Provider 10".

**Most likely way to get it wrong:** the `onAppear` seeding that re-expands a collapsed lone repo, followed by putting the sort test on the instance method.

### W2-2, BUG-198 series Play (main session)
**Implementable?** Yes. The gate (`DetailView.swift:1436-1441`) lacks `seriesPlay`, while the auto-play guards already check it (`:3002`, `:3017`) and `.onChange(of: seriesPlay?.id)` (`:1142-1147`) cancels only auto-play and the bridge.

**Missing.**
- The **shuffle sheet** (`showShuffleSheet`, `:432`, `.sheet` at `:1166`) is also not in the gate. Decide explicitly whether it pauses the trailer. The sheet's `onDismiss` then sets `seriesPlay`, which the fix covers.
- "So the next cover cannot be forgotten" only holds if the pure function takes one named parameter **per presentation** and the test lists every `.fullScreenCover` / `.sheet` in DetailView. Those are `showStreams`, `seriesPlay`, `trailerPlayback` / bridge, `showSynopsisSheet` and `showShuffleSheet` (`:1166`, `:1179`, `:1193`, `:1215`). A test that counts the presentations in the source (as `SettingsDescriptionsTests` scans files) would make forgetting one a test failure.
- Side effects to accept: `chipGlassFlat` (`:1592`) and the poster backdrop (`:1622`) also key on `isTrailerActive`. Under the cover the backdrop swaps in, invisible, and the trailer re-mounts on dismiss, the same as the movie `showStreams` path does today.

**Tests:** `TrailerStartGateTests`, `TrailerBridgeTests`, `DetailScrimTests`, plus a new `NuvioTVTests/DetailTrailerGateTests.swift`. The project uses synchronized groups, so a new `Screens/Detail/DetailTrailerGate.swift` needs no pbxproj edit.

### W2-3, BUG-195 Search black (agent B)
**Implementable as written?** No. The spike's question is wrong.

The code makes a fourth explanation the most plausible, and the spike has to rule it in or out first. The keyboard's focus at +1.13 s is the rail's hand-off ladder landing on its **1.0 s check**: `exitRail` → `fallbackHandOff` → `resetFocus` at `asyncAfter` 0.35 and then 1.0 (`NavigationRail.swift:1167-1180`; `HiddenTabBarRedirect.swift:57-66`). Search usually has no return route (`chrome.topReturnRoute(tab:)`, `:1127`). The spike must log, on the sim with `-debug.searchOpenProbe YES`:
- `[NavRail] select tab=`, `exit via=… result=`, each ladder reset (add a log line in `fallbackHandOff`), `[KBFocus] keyboard=1` (`HiddenTabBarFocusBlocker.swift:264`) and `[SearchOpen]`;
- the same open in **Tabs mode**, where there is no rail and no ladder;
- 100 ms screenshots to see what is actually drawn: idle page rows (Recent Searches, the Discover entry row), the keyboard band, or nothing.

If the keyboard is ready at 0.35 s, or Tabs mode is fast, the fix is a Search-specific ladder (an earlier check, or resetting focus on keyboard readiness). That lives in `HiddenTabBarRedirect.swift` / `NavigationRail.swift`, not in the page.

**Of the spec's three candidates:**
- (2) is ruled out by the code (§1).
- (1) changes nothing on an idle open, because background plus empty wash is black (§1). It only helps if the spike shows the idle rows are drawn but hidden by the container. In that case, the views to look at are `SearchFieldLayer` (`SearchView.swift:162-193`, where `.searchable` sits on `SearchContent`'s `ScrollView`), the `NavigationStack` root `ZStack` (`:37-46`), and whether tvOS hoists the search controller to the stack root, which would put the `ZStack` inside it too. A cover drawn outside must be non-focusable (`.allowsHitTesting(false)`, never a focusable copy of Recent Searches).
- (3), the crossfade, stays the fallback.

**Missing.**
- A mode-independent "painted"/"ready" signal. `searchKeyboardFocused` is Rail-only, so any cover needs a timeout or its own observer.
- What "the page's own look" is at an empty query, given the wash is empty by design.

**Most likely way to get it wrong:** build candidate (1), see no change on Steven's OLED-black config, and leave a Tabs-mode cover that never fades.

**Tests to keep green:** `NuvioTVUITests.swift` `test93RailMenuFromSearchKeyboard` / `test93b…` (`:9711`, `:9717`; these exist because of the 2.5 s ladder), `test92/94/95` (`:9443`-`:9588`), `NavigationRailUITests.testRail05b_FocusStaysInsideTheRailOverSearch` (`:481`), `BatchASearchPerfUITests`, `SearchWashPolicyTests`, `SearchPoliciesTests`, and `RailFocusPolicyTests` if the ladder changes.

### W2-4, Icons Only light tint (agent B)
**Implementable?** Yes, in one pass. `pillGlass` (`NavigationRail.swift:631-649`) collapses to `!showsLabels ? .regular.tint(white 0.12) : .regular`. `showsLabels` is at `:486-488`.

Delete `RailGlassVariant` (`NavigationChrome.swift:398-419`) and `testRailGlassVariantResolution` (`NavigationChromeTests.swift:341-352`).

**Most likely way to get it wrong:** grepping for `railGlass` and deleting the `railGlass(_:)` bounds-oracle helper in `NavigationRailUITests.swift:741` along with Rail08/Rail12/Corner glass assertions that use it. Keep the `#if DEBUG railBoundsOracle` (`:658`) too. Keep the "background, never `glassEffect` around the buttons" rule (`:627-629`). Update the comment that describes the variants.

**Tests:** `NavigationChromeTests` and `NavigationRailUITests` (Rail08, Rail12, the Edge/Corner frame legs at `:966-1007`).

### W2-5, the rest of P1 (agent C)
**Implementable in one pass?** (c) yes, after the re-target below. (b) depends on a dSYM that may not exist. (a) is not one-pass Sonnet work: the cut is design work and should come back as a measured report.

**Where the fan-out most likely is, from the code.** `StripPager` writes `@State positionId` on **every page**, inside `withAnimation` (`StripPager.swift:635`, `:642`). That re-runs `StripPager.body`. `pages()` (`:442-467`) then re-invokes `row(key)` for every mounted page, which gives each row a fresh `CatalogRowView` value. `StripPagerBox`'s own comment says "their closures never compare equal" (`:121-124`). Those closures are `onSelect` / `onItemFocusChange` / `cardFootnote` (`BrowseComponents.swift:4957-4968`).

The same body also installs `.environment(\.pinnedRowFocusOwnership, PinnedRowFocusOwnership(report: {…}))` (`StripPager.swift:394-396`). That is a fresh non-`Equatable` closure struct (`Screens/PinnedRowUpFallback.swift:75-85`), read by `PinnedRowUpFallbackTarget` in every row (`:111`). So every mounted row and its modifier re-evaluates per press, inside an animation transaction.

Secondary sources:
- `StageStripHome` observes all of `HomeViewModel` (`StageStripHome.swift:48`), so any publish rebuilds the pager.
- `atTop` flips (`StripPager.swift:589-735`, rows 0 and 1 only).
- `focusRequest` writes on restores.

`StageController` publishes nothing (`StageController.swift:10`). The per-card `InlineTrailerCardModel` publishes `phase`, `morphStage` and `tileArt` (`InlineTrailerCard.swift:382-391`) only to its own card.

**The string scanning (b) is probably the same root.** Kotlin/Native strings bridge as NSString subclasses, so hashing and `==` on `MetaPreview.id`, `section.key` and the `ForEach` ids in each re-evaluated row go through `characterAtIndex:`. Each extra row body costs a diff over its Kotlin-backed ids. Have (b) test this hypothesis before hunting for "a per-press sort".

**Instrument first.**
- Add `StripPager`, `StageStripHome` and `StripPageSlot` ticks to `HomeBodyCounter.names` (`Screens/HomeBodyCounter.swift:18-19`).
- Add a Stage Down-walk variant of `HomeBodyCountUITests` (that test walks Classic Right) as a **new** file, not in `NuvioTVUITests.swift`.

**Fix shapes.**
- Isolate the `ScrollView` + `.scrollPosition` into a child view, so `positionId` stops re-running the page list.
- Or make `StripPageSlot` compare on `(key, mount, a row-data revision)`.
- `.equatable()` on `CatalogRowView` that ignores its closures is the **most likely way to get it wrong**: stale `onSelect` captures, and rows that miss data updates. The spec's "value snapshots / `.equatable()`" needs a revision token rule. Those choices are Opus-level.

**Knobs (c): can each remove exactly one layer? Yes, with these seams.** All three are launch-latched constants readable in Release, so a conditional modifier's identity change does not matter.
1. `-debug.homeNoFadeMask` should drop the strip mask: `.mask(alignment: .top) { StripEdgeMask(…) }` at `StripPager.swift:387-389`. It is on in every configuration and repaints during every glide. The per-row fade already has an A/B (`-row_edge_fade off`). Optional 4th knob: `StageArtMask` on the art layer (`StageView.swift:103`, `:113-126`). Keep it separate; do not fold it into knob 1.
2. `-debug.homeNoPageOpacity`: the `.visualEffect { content.opacity(StripGeometry.pageOpacity(…)) }` at `StripPager.swift:462-466`. At opacity below 1 a page is composited offscreen. The stage text's own opacity animation (`StageView.swift:293`) is a different layer: leave it alone.
3. `-debug.homeNoCardDepth`: `CardDepthModifier.body` returns `content` (`CardDepthStyle.swift:391-397`). This removes the overlay and its per-card `rail.mask` (`:502`) everywhere, Detail included. It does **not** remove "Depth Takes Poster Color" sampling (`samplesDepthColor` in `PosterCard.swift:1053-1055`, `:1337`, `SagaCard.swift:113`, `CollectionsUI.swift:562`, `InlineTrailerCard.swift:2317`). That is CPU work rather than a layer, so leave it in place and note it. Do not inject at `ContentView.swift:177`, which is agent B's file.

**Tests:** `StripPagerTests`, `StripGeometryTests`, `StripFocusMemoryTests`, `StripMotionSignalTests`, `StripRowsPlanTests`, `StripFitPageTests`, `CardDepthRailStyleTests`, `RowSoftEdgeMaskTests`, `EdgeFadeCurveTests`, `RowEdgeFadeSettingTests`, the `InlineTrailer*Tests`, and UI `StageStripUITests` S01-S17 (above all S07 focus memory, S08 Menu glide, S10 background trailer, S17 fit rows), `StripFitNoZoomUITests`, `HomeBodyCountUITests`, `TrailerMotionUITests`. Add a unit test per knob's resolver (default off, `YES` on).

## 3. Test coverage summary

| Item | Keep green | Add |
|---|---|---|
| W2-1 | `SettingsDescriptionsTests` (all 5), `SettingsCategoryTests` | Sort test (case, natural numbers); expansion-rule test (lone repo open, toggle closes, second repo collapsed). No UI leg exists for Plugins: the fixture has no plugin repo, so the device pass needs one installed in **Test** and removed afterwards. |
| W2-2 | `TrailerStartGateTests`, `TrailerBridgeTests`, `DetailScrimTests`, `DetailFocusReturnUITests` | `DetailTrailerGateTests`: one case per presentation, the series cover named. |
| W2-3 | `test92/93/93b/94/95` (NuvioTVUITests), `testRail05b`, `BatchASearchPerfUITests`, `SearchWashPolicyTests`, `RailFocusPolicyTests` | A UI leg on `[SearchOpen] painted` vs tab select in both modes, if the fix is ladder-side. |
| W2-4 | `NavigationChromeTests`, `NavigationRailUITests` | None. Delete `testRailGlassVariantResolution`. |
| W2-5 | the strip, depth, fade and trailer tests listed above | Knob resolver tests; Stage body-count UI leg (new file). |

## 4. File ownership

The three sets are disjoint as listed, and agent C's list does not collide with A or B. The following files are needed **outside** each agent's set:
- **A:** `Screens/Settings/SettingsDescriptions.swift` (new case and copy); `Localizable.xcstrings` (closed; main session).
- **B (W2-3):** probably `DesignSystem/HiddenTabBarRedirect.swift` (`SidebarHandOffLadder`). Possibly `DesignSystem/HiddenTabBarFocusBlocker.swift` (a mode-independent keyboard signal) and `Screens/Search/SearchWashDriver.swift` (if "the look" means a wash at an empty query). Its UI legs are in the shared `NuvioTVUITests.swift`.
- **C:** `Screens/Home/StageStripHome.swift` and `Screens/Home/StageView.swift`, if "Home strip" does not already cover them (say so explicitly); `Screens/HomeBodyCounter.swift`; `Screens/PinnedRowUpFallback.swift` (the ownership env value); `HomeView.swift` (closed, but likely untouched: rows are built in `StageStripHome`).
- **Main session:** `Screens/DetailView.swift`, new `Screens/Detail/DetailTrailerGate.swift`, new `NuvioTVTests/DetailTrailerGateTests.swift`.
- **Overlap watch:** `NuvioTVUITests.swift` is shared. B's Search legs live there, so C must add its Stage leg in a new file. `ContentView.swift:177` (the Card Depth injection) belongs to B, so C must not knob there.
