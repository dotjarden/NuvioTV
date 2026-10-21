# Batch P Wave 2: review r1 (Opus, read-only), 2026-10-21

Scope: `git diff 3cf873994 c7c49686c` in `~/Claude/Projects/NuvioMobile-batch-p2` (`claude/batch-p-w2`), `MPVKit` ignored. Paths are relative to `iosApp/NuvioTV/` unless they start with `iosApp/`. Context: the Wave 2 section and "Critique applied" in `docs/batch-p-steven-rc10-plan-2026-10-20.md`, plus `docs/batch-p-w2-critique-2026-10-21.md`. No code was changed and nothing was built or run. Line numbers are at `c7c49686c`.

**Verdict: no P1.** Four confirmed P2s: the Plugins expansion rule inverts when the repository count changes, the shuffle → series hand-off re-mounts the hero trailer for one sheet dismissal, the Search placeholder flashes over a live field on every return, and its geometry ignores the rail inset and Tabs mode. A fifth P2, the Remove alert's placement, is unverified. The fan-out cut is correct for every scroll-position writer.

## Findings

1. **P2: the expansion rule inverts when the repository count crosses 1.** `Screens/Settings/SourcesSettingsPane.swift:413`
   - `isExpanded = (count == 1) != toggled.contains(url)` stores a flip relative to a default that itself moves.
   - Case 1: a lone repository the user collapsed is in `toggledPluginRepos`. Install a second one and the first re-expands, because `false != true`.
   - Case 2: with two repositories, the user expands A (A is in the set) and removes B. A collapses, because `true != true`.
   - A repository removed by sync from another device leaves its URL in the set. If it comes back, it starts inverted.
   - The Remove handler (`:245`) clears only the removed repository's URL, so neither case is fixed.
   - The critique also asked for an expansion-rule unit test, and none landed: `PluginsSortOrderTests` covers only the sort.
   - **Fix:** store the user's choice, not a flip. Use `@State var pluginRepoExpanded: [String: Bool]` and `isExpanded = pluginRepoExpanded[url] ?? (count == 1)`; the toggle writes `!isExpanded`. Move the rule into a `nonisolated static func` on `PluginsViewModel` and test it: lone open, toggle closes, a second install keeps both choices, removing B keeps A's choice.

2. **P2: the shuffle → series hand-off re-mounts the hero trailer between the two covers.** `Screens/DetailView.swift:1448`, with the sheet at `:1166-1178`
   - The shuffle action sets `pendingShuffleRoute` and `showShuffleSheet = false`. `seriesPlay` is set only in the sheet's `onDismiss`, after the dismissal animation.
   - For that animation every gate input is false. `trailerMountCandidate` turns true, and `updateTrailerMount` (`:1466`) mounts the `AVPlayerLayer` unless the page is scrolling. The trailer starts, possibly with sound, which is the #8 complaint.
   - A few hundred ms later `seriesPlay` lands and the layer is torn down again.
   - That is one extra layer build-and-teardown (BUG-153 measured the build at ~50 ms on the main thread) right as the series cover presents.
   - **Fix:** `shuffleSheetShown: showShuffleSheet || pendingShuffleRoute != nil`, or add a `seriesPlayPending` input. Add a gate test row for "sheet closing with a pending route".

3. **P2: the Search placeholder shows again over a live field on every return.** `Screens/SearchView.swift:143-152`, `:165-170`
   - `onAppear` always calls `rearm()` and draws the look-alike at opacity 1, above `SearchFieldLayer`.
   - `onAppear` also fires on a pop back from a pushed `TitleRoute` (the `navigationDestination` at `:49`) and on a revisit of the kept-alive tab. In both cases the real field may already exist, and it may already hold a query.
   - The poll's first check is at +50 ms, and then the hide runs a 0.25 s fade. So for about 300 ms a 0.3-white "Search movies & shows" is drawn over the real prompt or over the typed query. It is about 1 pt off, so it reads as ghosting.
   - If the private class-name match ever misses, which it will on an OS rename, the overlay sits there for the full 1.6 s.
   - **Fix:** in `onAppear`, call `if Self.searchFieldIsMounted() || !owner.queryBox.text.isEmpty { policy.hide(.signal) }` before anything draws, with no animation (`var t = Transaction(); t.disablesAnimations = true`). Better still, arm the placeholder only on a tab select, not on a NavigationStack pop. Add a policy case for "already mounted at appear → never visible".

4. **P2: the placeholder's geometry is absolute and ignores the rail inset and Tabs mode.** `Screens/SearchView.swift:131-139`
   - `.padding(.leading, 98).padding(.top, 158).ignoresSafeArea()` pins one spot.
   - With the rail Edge + Always Visible, `.railTabRoot` adds 36 pt to the tab root's leading safe area (`NavigationChrome.contentSafeAreaExtra`, read via `\.railLeadingInset`). The real field moves by that amount and the placeholder does not.
   - In Corner the extra is 0, which is Steven's setup and probably the setup behind the "1 pt match on the sim".
   - In Tabs mode the visible tab bar sits above the content, so the real field's y very likely differs.
   - The plan records the match as measured on the sim, in a mode it does not name.
   - **Fix:** drop `.ignoresSafeArea()` and pad from the safe area (98 − side safe area, 158 − top safe area), adding `@Environment(\.railLeadingInset)`. Or measure per mode and branch on `NavigationChrome.isRail()`. Either way, put the sim shots for Rail Edge/Always, Rail Corner and Tabs in the device check.

5. **P3: the hierarchy poll walks every window's full view tree every 50 ms, for up to 1.6 s.** `Screens/SearchView.swift:165-184`
   - It is bounded (it stops on hide, on the timeout via `policy.isVisible`, and on disappear via `visit`) and it runs on the main queue. It cannot leak or run forever.
   - Each tick, though, does `String(describing: type(of:))` for every view in every window: rail, chrome and the Search page. That is up to 32 walks during the tab transition the bug is about.
   - **Fix:** walk only the key window and stop descending once found. Or poll at 100 ms. Or, cheaper, look for the `UISearchController` through the hosting controller's `navigationItem.searchController?.searchBar.window != nil`.

6. **P3: the editing-began observer is app-wide for the kept-alive tab's lifetime.** `Screens/SearchView.swift:153-155`
   - Any `UITextField` beginning editing elsewhere (the Settings repository URL, a PIN) runs `hide(.signal)` on the Search placeholder.
   - It is harmless today, because the next `onAppear` re-arms.
   - Paired with 3, an editing-began that arrives *before* `onAppear` is lost, and only the poll saves the visit.
   - **Fix:** filter on `($0.object as? UIView)?.superview` being a `UISearchBar` descendant. Or ignore notifications while `visit` is odd, that is, between `onDisappear` and `onAppear`.

7. **P2 (unverified): the `.alert` is on a `SettingsSection` inside the List.** `Screens/Settings/SourcesSettingsPane.swift:236-251`
   - `SettingsSection` is a `Section` (`SettingsRowViews.swift:366`). Whether SwiftUI distributes `.alert` to each row, which would mean N presenters on one binding and "already presenting" warnings, or holds it on a recycled cell, is not shown by any test.
   - The plugin fixture has no repository, so no UI leg reached it. The critique asked for a sim check with three or more repositories expanded, and the plan does not record one.
   - **Fix:** attach the alert to the `SettingsDestructiveRow` (`:457-464`), which is on screen and focused when pressed, with `isPresented: pendingPluginRepoRemoval?.manifestUrl == repo.manifestUrl`. Or verify on the sim and record it.

8. **P3: focus after Remove is not handled.** `Screens/Settings/SourcesSettingsPane.swift:244-247`
   - Confirming removes the presenting row and its whole block.
   - The alert's focus return has no target, so the List falls back, often to the pane's first row. BUG-47 still holds.
   - **Fix:** a `@FocusState` on the headers and the Add row. After `removeRepository`, focus the next repository's header, or the "Add repository" row.

9. **P3: strings.** `Screens/Settings/SourcesSettingsPane.swift:427`
   - "%lld of %lld providers on" matches the catalog, since both values are Swift `Int`, so the `%d` concern from the critique no longer applies.
   - It has no plural, so "1 of 1 providers on" appears.
   - `"1 provider"` and `"%d providers"` (`Localizable.xcstrings:656`, `:2256`) are now orphaned.
   - The `.xcstrings` hunk is consistent with a script run: empty `{}` entries plus the trailing newline. No agent hand-edit is visible.
   - **Fix (main session, not an agent):** a plural variation for that key, and mark the two old keys stale or drop them on the next strings pass.

10. **P3: the pager's ownership closure now runs on its first-body copy on the hot path.** `Screens/Home/StripPager.swift:383-392`
    - `handleOwnership` → `page(to:)` reads `onRowChange`, `onPageStart`, `onStripFocusLost` and `controller` from the pager value captured on its first body.
    - Before, the closure was rebuilt every body, so it was always fresh. `rowKeys` (via `box.rowKeys`) and Reduce Motion (via `box.reduceMotion`) are already routed through the box.
    - Today's call sites are safe, because their closures capture only reference or binding state: `stage`, `$isScrolledDown`, the `navigationChrome` object, the folder page's `box`/`stage`/`model`.
    - A future host closure that captures a `let` or an environment value would go silently stale.
    - **Fix:** mirror the three callbacks into `StripPagerBox` on each body (`box.onRowChange = onRowChange`, and so on) and call through the box. Or state the "callbacks must capture only stable references" invariant on the `init`.

11. **P3: the probe marks in `fallbackHandOff` run for every tab.** `DesignSystem/NavigationRail.swift:1159`, `:1167`, `:1170`
    - They are correctly gated: `SearchOpenProbe.mark` checks `enabled`, which is launch-latched and off by default.
    - They are still labelled `[SearchOpen]` on Home/Library hand-offs, and the interpolated string is built before the gate.
    - **Fix:** `guard SearchOpenProbe.enabled` at the call sites, or `@autoclosure` the argument. Optionally log only when `RailItem.title(for: tab)` is Search.

12. **P3: `StageBodyCountUITests` is an evidence leg in the default UI target.** `iosApp/NuvioTVUITests/StageBodyCountUITests.swift:136`
    - It takes about 70-140 s per run: a 16 s settle, up to 30 s polling, 10 × 1.8 s presses, and a 90 s worst-case picker wait.
    - Its one assertion (≥ 3 distinct rows) depends on the FA87 fixture's five rows.
    - It adds a launch to a suite that already wedges the sim after about 6 UI runs. The `HomeBodyCountUITests` precedent has the same shape.
    - **Fix:** `try XCTSkipUnless(ProcessInfo.processInfo.environment["NUVIO_EVIDENCE"] == "1")`, or leave it out of the gate's `-only-testing` list. Record which choice was made in `CLAUDE.md`'s gate line.

13. **P3: test coverage.**
    - `DetailTrailerGateTests` tests the pure rule but not that every presentation feeds it. A new `.sheet`/`.fullScreenCover` in `DetailView.swift` would still pass. The critique's source-scan idea (count `\.sheet(|\.fullScreenCover(` in `DetailView.swift` = 4 and pin it) would make forgetting one a failure.
    - `HomePerfKnobsTests` mostly tests `UserDefaults.bool` and not the wiring. That is acceptable for three one-line `if`s.
    - The deleted `testRailGlassVariantResolution` loses nothing, because the type is gone, and no test asserts the Icons Only tint either. That is acceptable: it is a visual, device-picked value.

## Checked and fine
- **Detail gate inputs:** they match every presentation on the page. That is the shuffle `.sheet` (`:1166`), `showStreams` (`:1179`), `seriesPlay` (`:1193`), the trailer bridge (`:1215`, via `model.trailerPlayback`) and the synopsis sheet.
- **Detail pushes:** `navigationDestination` and `NavigationLink` pushes are covered by `onDisappear` → `model.stop()`, which nils `trailerVideoURL` (`DetailViewModel.swift:301`).
- **Detail mount on `seriesPlay`:** `seriesPlay` is `@State`, so setting it re-evaluates `trailerMountCandidate`, and `onChange(…, initial: true)` (`:1025`) un-mounts.
- **Detail unmount timing:** un-mounting during the cover's rise swaps to the still instantly. That matches today's film-picker path and is not a stall.
- **Rail:** nothing references `RailGlassVariant` or `-debug.railGlass`. `railGlass(_:)` in `NavigationRailUITests.swift:741` is the bounds helper and stays. The `-all` Labels-shown path is gone with it, as intended.
- **Strip position writers:** every `positionId` writer goes through the `nonmutating set` on the shared `StripScrollPosition`, and the engine's own scroll writes through `$position.id`. The writers are `page(to:)` (programmatic, Menu-to-top, sync after a held pop restore), `rowKeysChanged`, `followRowsWhileOutside` and `onAppear`. Equal writes publish nothing, as `@State` did.
- **Strip animation:** `withAnimation(…, completionCriteria:)` carries through `objectWillChange`, and S08 (the Menu glide) passed.
- **Stored page content:** it is only as old as the pager's last update. Every input it reads is either pager state (`fitHeights`, `uncoverGateKey`, which re-run the pager body and rebuild the scroller) or read live at call time (`row(key)` → the host's `model`). Mount flips go through each slot's own `StripPageMount`. No staleness found.
- **Stable ownership across `rowKeys` changes:** it survives them, because the closure reads `box.rowKeys`, pruned in `rowKeysChanged`. A profile switch that rebuilds the pager makes a new box.
- **Knobs:** each knob is one `if` around one layer (`StripEdgeMaskModifier`, `StripPageOpacityModifier`, `CardDepthModifier.body`). They are `nonisolated` `static let`s, launch-latched and read in Release. The `HomeBodyCounter` ticks are all inside `#if DEBUG`.
- **Isolation:** `sortedByName` / `sortedScrapers` are `nonisolated static`. The generic seam avoids building Kotlin `PluginScraper`s in tests, and `scraper.enabled` / `repo.name` bridge to `Bool` / `String` correctly.
- **Placeholder:** `accessibilityHidden(true)` and `allowsHitTesting(false)` are right for a look-alike, and the placeholder reuses the field's own catalog key "Search movies & shows".

P1 0 / P2 5 / P3 8 (one of the P2s, 7, the alert placement, is unverified)

**What is good.** erdist's patch fixes a real structural bug (one VStack made the List treat a whole repository as a single focusable row). The tweaks went in as the critique asked: the derived state replaces `onAppear` seeding, the header has its own description, and the sort is a testable static with a stable tie-break. `DetailTrailerGate` turns the inline rule into one named input per cover, which is the right shape for the "forgot a cover" bug class. The fan-out cut is small and well-aimed: one leaf observes the position, the environment value is stable, and the mount flags already lived in the box. It comes with before/after body counts, not a claim. The Search spike overturned both the original theory and the critique's ladder theory with measurements in both modes, and the placeholder that came out of it is bounded, non-focusable and logs its own reason.
