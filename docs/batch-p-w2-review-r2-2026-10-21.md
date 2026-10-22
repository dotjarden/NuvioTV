# Batch P Wave 2: review r2 (Opus, read-only), 2026-10-21

Scope: `git diff 3cf873994 HEAD` in `~/Claude/Projects/NuvioMobile-batch-p2` (`claude/batch-p-w2`), with the focus on `33bcaaf4d` ("review r1 fixes"). `MPVKit` was ignored. Paths are relative to `iosApp/NuvioTV/` unless they start with `iosApp/`. Line numbers are at `33bcaaf4d`. No code was changed and nothing was built or run.

**Verdict: no P1.** Every r1 P2 is fixed at the code level. The geometry rewrite (r1 #4) is correct for the leading inset, but its top value is not measured. One new P2 is unverified: a retain cycle through the cached ownership value. It dates from `c7c49686c`, not from the fix commit. Four P3s.

## r1 findings
- r1 #1 (P2, expansion rule): **FIXED.** The choice is stored as `[String: Bool]` and the rule is `stored ?? (count == 1)` (`PluginsViewModel.swift:102`, `nonisolated static`). The toggle writes `!isExpanded` (`SourcesSettingsPane.swift:404`) and Remove clears the entry (`:457`). Three tests cover lone-open, stays-collapsed when a second repository is installed, and stays-expanded when B is removed. A repository that sync removes and later restores keeps its old choice. That is remembered state, not an inversion.
- r1 #2 (P2, shuffle hand-off): **FIXED.** `DetailView.swift:1450`. `pendingShuffleRoute` is `@State`. It is set in the sheet action before `showShuffleSheet = false` and cleared in the same `onDismiss` that sets `seriesPlay` (`:1166-1170`), so the gate never sees a false gap. The action's `guard meta` path sets no pending route, so it cannot latch the gate shut. The suggested gate test row was not added (P3 4).
- r1 #3 (P2, placeholder over a live field): **FIXED.** `SearchView.swift:156-162`. The `already` path does one hierarchy check plus the query-box text, hides inside a `disablesAnimations` transaction (which suppresses the `.animation(_:value:)` at `:147`), and returns before the timeout or the poll is scheduled. On a revisit where the last visit already hid it, `hide` is a no-op and the overlay stays at 0. Residual risk, not a defect: whether `UISearchBarTextField` is back in the key window by the time a pop's `onAppear` runs is unproven. If it is not, the old poll path runs, which is no worse than r1.
- r1 #4 (P2, geometry): **FIXED for leading; top unmeasured (P3 2).** The leading claim holds. The Always Visible inset is UIKit `additionalSafeAreaInsets.left` on the tab controller (`HiddenTabBarFocusBlocker.swift:68-86`), which propagates to the hosted root and to the search container alike, so the placeholder and the field move together. Corner adds 0. The top claim is unverified: see P3 2.
- r1 #5 (P3, poll cost): **FIXED.** `SearchView.swift:197-203` walks the key window only, `contains(where:)` stops at the first match, and the app has one window.
- r1 #6 (P3, app-wide observer): **FIXED.** `active` gates the editing-began observer (`:174-177`). The `$searchKeyboardFocused` receiver (`:178`) is not gated, but it only hides, which is harmless.
- r1 #7 (P2, alert placement): **FIXED.** The alert sits on the Remove row (`SourcesSettingsPane.swift:449-463`). `get` compares by `manifestUrl`, which is unique per `ForEach` id, so only one row can present at a time. Cancel and Remove both dismiss through `set(false)`, which clears the pending state. See P3 3 for the one path that bypasses `set`.
- r1 #8 (P3, focus after Remove): **NOT FIXED** (not claimed). BUG-47 still holds.
- r1 #9 (P3, plural / orphaned keys): **NOT FIXED** (not claimed; main-session strings pass). `33bcaaf4d` touches no `.xcstrings`.
- r1 #10 (P3, stale callbacks): **FIXED.** `StripPager.swift:389-391` mirrors the three callbacks on every body. `ownership` is read unconditionally in `body` (`:473`), and all four call sites (`:606`, `:665`, `:700`, `:756`) call through the box. The `DispatchQueue.main.async` hops capture `pagerBox` and read the callback at fire time, so they get the latest closure. See P2 1 for the cycle.
- r1 #11 (P3, ladder marks): **FIXED.** `NavigationRail.swift:1159-1171`. Each line is built only under `SearchOpenProbe.enabled` (a `nonisolated` launch-latched `static let`, readable in Release) and tagged `[SearchOpen]` or `[NavRail]` by `RailVisibilityRule.searchTab`. Nit: `tab=%d` takes a Swift `Int`, so `%ld` is the correct format. It prints correctly on arm64 anyway.
- r1 #12 (P3, evidence leg): **FIXED.** `iosApp/NuvioTVUITests/StageBodyCountUITests.swift:17` uses `XCTSkipUnless(NUVIO_BODY_COUNT == "1")`, the same pattern as `PLAYER_PANEL_PROBE` and the other probes. The `CLAUDE.md` gate line does not mention it. That is optional.
- r1 #13 (P3, coverage): **PARTLY FIXED.** The expansion-rule tests landed. There is no `already` policy case and no source-scan pin for `DetailView`'s covers.

## New findings

1. **P2 (unverified, from `c7c49686c`, not the fix commit): retain cycle through the cached ownership value.** `Screens/Home/StripPager.swift:392-397`
   - `box.ownership` holds the closure. The closure captures `pager = self`. `pager` holds `@State box` (its `_value` and `_location` both reference the same `StripPagerBox`), so box → ownership → closure → pager → box.
   - The pager copy also carries `controller` and the host closures. On the folder page those closures capture the `FolderRowsPage` value: `model` (`FolderDetailViewModel`), `stage` (`StageController`) and its box (`FolderRowsPage.swift:209-224`).
   - If SwiftUI does not break this cycle, each folder push/pop leaks one pager box, one StageController and one folder view model. Home's strip is app-lifetime, so the cycle costs nothing there.
   - The r1 mirroring adds closures to the box but no new owner. The cycle predates it.
   - **Fix:** check with Xcode's Memory Graph after three folder push/pops. If the cycle is confirmed, make it `weak var ownership` on the box. The environment holds the value while the pager lives; if it is ever dropped, the next body makes a new one. Alternatively, have the closure capture only `box` and `controller` and route `handleOwnership`'s view state through the box.

2. **P3: the top offset assumes a 60 pt safe area that nobody measured after the rewrite.** `Screens/SearchView.swift:141-145`
   - `98 = 158 − 60` holds only if the hosted root's top safe area is 60 before the field mounts.
   - In Tabs mode the visible tab bar adds top safe area. The field may move with it or may not; the commit records no sim shot.
   - The S1 notes put the ZStack inside `.searchable`'s UIKit container. If mounting the container changes that root's safe area, the placeholder now jumps with it, during its 0.25 s fade. With `.ignoresSafeArea()` it could not jump, so the fade could show a displaced ghost over Recent Searches.
   - **Fix:** take sim screenshots at about +0.3 s and at hide +0.1 s in Rail Corner, Rail Centre/Always Visible and Tabs, and record them in the plan. If the top moves, branch on `NavigationChrome.isRail()` for the top value, or make the `.signal` hide unanimated as well.

3. **P3: a Remove row that leaves while its alert is up strands `pendingPluginRepoRemoval`.** `Screens/Settings/SourcesSettingsPane.swift:449-463`
   - If sync from another device removes the repository, or the row is otherwise torn down while the alert is up, SwiftUI dismisses without calling `set(false)`.
   - The stale value then matches that URL again if the repository is reinstalled and expanded, and the alert pops up unprompted.
   - **Fix:** set `pendingPluginRepoRemoval = nil` in the Remove action, and in `.onChange(of: plugins.repositories.map(\.manifestUrl))` when its URL is gone.

4. **P3: small leftovers.**
   - `SourcesSettingsPane.swift:14-17` still carries the old "membership here inverts that default" doc comment above the new one. Delete it.
   - `rearm()` (`SearchView.swift:163`) runs outside the no-animation transaction, so on a second or later visit with the field unmounted, the placeholder fades in over 0.25 s instead of being there on the first frame. Wrap it in the same transaction.
   - No `DetailTrailerGateTests` row and no `SearchPlaceholderPolicy` `already` case. Both are cheap to add.

## Rules re-check
- **No agent `.xcstrings` edits:** `33bcaaf4d` touches none. Every string it uses already existed or moved verbatim.
- **`nonisolated` where called off-main:** `isRepositoryExpanded` is `nonisolated static`, called from the nonisolated XCTest. `SearchOpenProbe.enabled` is `nonisolated`. `SearchPlaceholderPolicy` stays `nonisolated`.
- **Knobs readable in Release:** the ladder marks and the placeholder marks gate on `SearchOpenProbe.enabled` (`UserDefaults`, not `#if DEBUG`). No new knob was added.
- **Test class rename:** `PluginsSortOrderTests` is now `PluginsSettingsRulesTests`, but the file is still `PluginsSortOrderTests.swift`. No script or `-only-testing` list references the old name.

P1 0 / P2 1 / P3 3 (P2 1 is unverified and predates the fix commit; P3 4 bundles small leftovers)

**What is good.** Every fix is the smallest one that removes the cause, and the commit says which r1 item each one answers. The expansion rule is pure, static and tested on the exact cases r1 named. Moving the Remove alert onto its row with a URL-matched binding makes double presentation impossible by construction. The `already` path is a clean early return: no timer and no poll, and the policy logs only once.
