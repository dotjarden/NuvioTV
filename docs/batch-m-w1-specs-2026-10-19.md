# Batch M Wave 1: build specs (Opus critique, 2026-10-19)

These are the exact specs the Wave 1 agents build from. They come from a read-only Opus critique of `docs/batch-m-steven-rc9-plan-2026-10-19.md` against the code in `NuvioMobile-batch-m` at `782b31be6`, with the Wave 0 rig data. Paths are relative to `iosApp/NuvioTV/`. The project uses synchronized folders, so a new Swift file needs no `project.pbxproj` edit. FEAT-80 is out of Wave 1 until Steven answers the 21:02Z question; Agent C must not touch `NavigationRail.swift`, `NavigationChrome.swift` or `AppearanceSettingsPane.swift`.

## Agent A: Detail
Owns:
- `Screens/DetailView.swift`
- `Screens/Detail/*`
- `Screens/DetailCinematicHero.swift`
- `Screens/EpisodesSection.swift`
- `Screens/DetailViewModel.swift`
- `Screens/PersonDetailView.swift`
- `DesignSystem/PosterCard.swift` (only the `CardArtworkFocusLift` parameter)
- new test files

### BUG-153: cheaper tile ring, with A/B knobs
1. **`trailersRow` (`DetailView.swift:2686-2731`)** becomes `private struct DetailTrailersRow: View` with `trailers`, `resolvingTrailerId: String?` and `onPlay: (MetaTrailer) -> Void`.
   - It owns `@FocusState focusedIndex` plus the `.focused` and `.zIndex` lines; delete the `@FocusState focusedTrailerIndex` at `:546`.
   - `.detailRowAnchored(.trailers, …)` stays on the call site (`:718`).
   - In `EpisodesSection`, move the season poster row's `focusedSeason` into a child view the same way.
   - Gate all three rows' `zIndex` on `CardFocusMode.resolve(...).raisesFocusedCard`, the way `liftedCastZIndex` does.
2. **`DetailTileFocusLift` (`Detail/DetailTileFocus.swift`):** attach `.onChange(of: isFocused, initial: true)` only when `samplesRingColor` is on (Focus Ring Takes Poster Color).
3. **New knob `debug.detailTileRingNoShadow`** in `DetailBug153Knobs`:
   - Add `var focusShadow: Bool = true` to `CardArtworkFocusLift` (`DesignSystem/PosterCard.swift:~831`); the default keeps every call site identical.
   - The ring branch passes `!DetailBug153Knobs.ringNoShadow`.
   - Main suspect: the focused tile inserts a black fill with `.shadow(radius: 22)` under a SwiftUI-driven scale animation.
4. **New knob `debug.detailTileRingNoAnim`:** the ring branch's lift and the tile's `.animation(value: isFocused)` become nil.
5. Keep `debug.detailNoTileRing`.
6. **Don't** build a shared per-row ring overlay. Only the focused tile builds a ring, and an overlay outside the lift is the FEAT-14 / BUG-108 failure mode.
7. The main session re-measures on the rig: ring-on deep walks, 5 or more per cell (rc7, the tip, each knob). It ships the first change whose mean is at or under rc7's mean + 1, and promotes the winning knob to a Developer toggle.

### BUG-187: back from a cast member resets to Play
**Cause:**
- On push, `onDisappear → model.stop()` (`DetailView.swift:~1122`) calls `MetaDetailsRepository.clear()`, which wipes the cache (`MetaDetailsRepository.kt:262`).
- On pop, `start()` → `load()` emits `isLoading` with `meta = nil`, and `self.meta = state.meta` (`DetailViewModel.swift:~190`) drops every row, so focus falls to `.defaultFocus(.play)`.

**Fix:**
- In the `detailWatcher` closure, keep the current meta while a reload has none yet:
  ```swift
  if state.meta == nil, state.errorMessage == nil, self.meta != nil { self.isLoading = state.isLoading; return }
  ```
  - Make this a pure `DetailMetaAdoption.keepsCurrent(hasMeta:incomingMeta:error:)` with unit tests.
  - Skip the assignment when `state.meta == self.meta`.
- **Fallback restore:**
  - A `@MainActor final class DetailFocusMemory` reference box, with no published state.
  - It is written from `onChange(of: focusedCastIndex)` and `onChange(of: focusedCompanyIndex)`.
  - More Like This and Collection rows become child views, each with their own `@FocusState focusedId: String?` that writes the box. Add no new FocusStates to `DetailView`.
  - On `onAppear` after a push, run FEAT-79's rungs `[(0, force), (0.35, force), (0.8), (1.1)]` (`CollectionsUI.swift:~1636`), standing down on `ViewerInputClock`.
  - `claimLatePlayFocusIfNeeded` is already safe.
- **Probe:** a DEBUG `debug_detail_focus row= idx=` label, mounted only under `-debug.detailFocusProbe`.
- **UI leg:** Detail → cast → Back, and More Like This → Back. It needs TMDB enrichment on, because cast cards are links only with a tmdbId.

### BUG-192
- `DetailCinematicHero.swift:304-312`: replace the HStack with `teaserText.background { teaserPlatter(...) }.animation(...)`.
- The "more" key isn't in `Localizable.xcstrings`.

### FEAT-82
- Add `@Environment(\.posterStyle) private var posterStyle` to `DetailView`.
- Add a pure `DetailActionShape.isSquare(cornerRadius:)` that returns `cornerRadius == 0`.
- Apply `.buttonBorderShape(isSquare ? .roundedRectangle(radius: 0) : .capsule)` inside both `prominentActionButtonStyle` and `compactActionButtonStyle` (`:~2017`, `:~2028`), in both branches; this covers Start Over.
- Grep the action row for a hand-drawn `Capsule()` or `.glassEffect(` and handle it the same way.
- Unit-test the helper; take a sim screenshot of square `.glass` / `.glassProminent`.

## Agent B: Home and collections (starts after Christian answers the D8 question)
Owns:
- `Screens/HomeView.swift`
- `DesignSystem/PinnedRowGeometry.swift`
- `Screens/Settings/HomeScreenSettingsPane.swift`
- `Screens/CollectionsUI.swift`
- `Screens/Home/*`
- the `homeSynopsisLength` case and copy in `Screens/Settings/SettingsDescriptions.swift` (it moved here from Integration so `SettingsDescriptionsTests` stays green on B)

### FEAT-61
- Delete `SynopsisLength` (`PinnedRowGeometry.swift:466-487`), the AppStorage (`HomeView.swift:6288-6289`, `HomeScreenSettingsPane.swift:57-60`) and the picker row (`:172-182`).
- `longSynopsis` (`HomeView.swift:~6296`) loses only its `.long` guard.
- In `LongSynopsisTests`, delete `testSynopsisLengthDefaultsToStandard` and turn `testPlanIgnoresTheSetting` into a plan-stability test.
- Add a table test of line counts per poster size × font × form.
- **Line target (D8, Christian 2026-10-19: "4 where it fits"):** ask `LongSynopsis.grant` for 4 lines on Classic in every case; it falls back to fewer lines when the poster size and font leave no room (Large), and **the hero frame never grows**: rows never pay (BUG-87/89). The release notes say Large may show fewer than 4.

### BUG-190
- Give `HeroTextLayer` (`HomeView.swift:~6730`) an explicit internal `init`.
- `FolderDetailView` gets `@StateObject HomeHeroFocusModel`, `@StateObject HeroArtResolver` and `@FocusState ctaUnused`.
- `classicRowsContent`'s `onItemFocusChange` also calls `focusModel.reportFocus(item, from: section.key)`.
- `onChange(focusModel.focusedItem)` calls `resolver.present(item, isFolder: false)`.
- On push and pop, call `focusModel.setCovered(true/false, restoresFocus: true)`.
- Layout, `classicRows` only:
  ```
  VStack {
    compact logo slot (compactTop 12 + 64)
    ZStack {
      HomeHeroBackdrop for the focused title (Nuvio form)
      HeroTextLayer(compact: true, showsCTA: false, forceNuvioLayout: true, compression: 0)
    }.frame(height: heroCarouselHeightPinned 352)
    ScrollView(classicRowsContent)
  }
  ```
  No rising header and no compact ghost.
- Painting the focused title's backdrop doesn't conflict with BUG-38, which was about the folder's own backdrop.
- Check `FolderEditMenuBand` for overlap in a sim screenshot.

### BUG-191
**Cause:**
- In No Zoom, `focusLift = 0`, so a fit page equals the measured row height.
- A collection row ends with 12 pt of padding, against 24 for a catalog row, so its last 12 pt sit inside the next page's 24 pt top feather (`StripEdgeMask(gutter: stageBottomGap)`).

**Fix:**
- Add a pure `StripGeometry.fitPageHeight(measured:page:focusLift:)` returning `min(page, (measured + (focusLift > 0 ? 2*focusLift : StripGeometry.stageBottomGap)).rounded(.up))`, used at `StripPager.swift:500-503`.
- Unit tests:
  - No Zoom gives measured + 24;
  - zoom gives measured + 40;
  - both are capped at the page.

**UI leg:**
- A fixture Home order with a collection row second to last (the BUG-38 guest-sim collections seeding).
- `-no_zoom_on_focus YES`, walk to the end.
- Add a DEBUG `debug_strip_fit key= h=` label and assert h ≥ measured + 24.
- A/B with `-debug.stripFitRows NO`.

### BUG-188
**Cause:**
- After `restore landed`, focus goes for about 195 ms to `UIKitFocusableFillerItem` at y = −218: the row above's scroller stand-in, which the gate's `.disabled` doesn't cover (the BUG-176 class).
- No stage swap happens, so holding swaps would do nothing.

**Fix:**
- In `handleUncoverMove`: on `.regrab` with `key == nil`, the gate closed, and the focused item's type name containing `FocusableFillerItem` (read in release builds, as the DEBUG diagnostic does at `:~340`), regrab synchronously with no `regrabDefer`.
- A pure `UncoverRestorePolicy.regrabsImmediately(fillerFocused:gateClosed:viewerInputSinceLanding:)` with unit tests.
- Keep `scrollDisabled` while the gate is closed (BUG-176).
- Rungs 1 and 2 miss because they fire during the pop transition; leave them alone.
- Device pass only: the simulator never makes this move.

## Agent C: player, picker, Discover
Owns:
- `Screens/StreamPickerView.swift`
- `Screens/FirstPlayAutoPlay.swift`
- `Screens/Player/PlayerPanelHost.swift`
- `Screens/Discover*` and `Discover/*`
- new test files
- **Not** `MPVPlayerView.swift`, `NavigationRail.swift`, `NavigationChrome.swift` or `AppearanceSettingsPane.swift`.

### BUG-185
**Built-in player:**
- Wrap the `$selected` binding at `StreamPickerView.swift:~489`. When the setter gets nil and `afterPlayerOutcome == .closePicker`, write `selected = nil` inside a `Transaction` with `disablesAnimations = true`. That's one site, with no player edits.
- `handlePlayerDismissed → closePicker()` stays as it is; there's one close path and no double dismiss.
- Log the time from the setter to `onDismiss`: under 100 ms means instant.
- If it's still animated, fall back to `UIView.setAnimationsEnabled(false)` in the setter, re-enabled in `handlePlayerDismissed` with a 1 s watchdog.

**No-logo hold:**
- Add `@State coverIsCloseHold`, set in `prepareForPlayerClose`'s `.closePicker` branch and in `closePicker()`.
- Add `var showsLogo = true` to `FirstPlayAutoPlayOverlay` (`FirstPlayAutoPlay.swift:~584`). When false, it draws `Color.black.ignoresSafeArea().focusable()` with the AX id `streamPicker.closeHold`. It must stay focusable (BUG-47).
- `loadingCover` passes `!coverIsCloseHold`.

**External hand-off (`:~1155`):**
- Use `ExternalPlayerPlatform.buildIntent`. On `Success(url)`, call `closePicker()`, then `UIApplication.shared.open(url)` 0.1 s later from a closure that doesn't capture the view.
- Re-add `cancelLaunchForCallbackUrl` in the completion (as `ExternalPlayerPlatform.apple.kt:~281` does).
- A failure keeps today's fallback and toast.

### BUG-186
- `PlayerPanelHostController.close` (`Player/PlayerPanelHost.swift:~200`): keep the `closing` guard.
  - If `isBeingPresented`, defer to `transitionCoordinator`'s completion.
  - Otherwise reset `closing = false` in `dismiss`'s completion.
  - Add a `Task { @MainActor }` watchdog at 0.6 s: if `closing && presentingViewController != nil && !isBeingDismissed`, reset and `close(animated: false)`.
- This covers both engines.
- Unit test: in a `UIWindow`, present, close during the present, and expect a dismissal.
- UI legs (mpv smoke fixture): Menu within 100 ms of the panel appearing, and swipe-up then an immediate Menu. In both, `player.panel` must be gone within 2 s and a second Menu must exit.
- No native "Infos" fallback.

### BUG-189
- New `Discover/DiscoverGenreNames.swift`: a `nonisolated enum` with `display(_:)`. Trim and lowercase, then switch over the Cinemeta and TMDB names:
  - Cinemeta: Action, Adventure, Animation, Biography, Comedy, Crime, Documentary, Drama, Family, Fantasy, History, Horror, Mystery, Romance, Sci-Fi, Sport, Thriller, War, Western, Reality-TV, Talk-Show, Game-Show, News, Film-Noir, Music, Musical, Short.
  - TMDB: Science Fiction, TV Movie, Action & Adventure, Sci-Fi & Fantasy, War & Politics, Kids, Soap.
  - Each case uses a literal `String(localized: "Action", comment: "Discover genre")`; unknown values pass through.
- `catalogDisplay(_:)` covers Popular, Featured, Trending, New and Top Rated.
- Display-only call sites:
  - `DiscoverGridPlan.genreLabel` (`DiscoverGridModel.swift:~60`);
  - `DiscoverRowsPlan.catalogLabel` (`:~127`): compare raw names for clashes, localize the output;
  - genre row `title`/`heading` in `DiscoverRowsPlan.specs` (`:~148-149`); `genre:` stays raw, and confirm `title` isn't used as a key;
  - the fallback spec titles.
- Add `String(localized:)` entries for "Genre" and "Browse".
- Unit tests: mapping, pass-through, case and whitespace, and the clash check on raw names.
- UI leg under `-AppleLanguages (fr)` reading the `discover.genrePicker` label (Cinemeta enabled on FA87).

## Integration (main session)
- Populate `Localizable.xcstrings` from a Release build (`scripts/populate-localizable-xcstrings.py`) and translate the needs-translation list for fr/es/de/it/vi.
- Leave `appearance.railPosition` until FEAT-80.
- Merge order A, B, C.

## Risks carried
- D8 (4 lines at every poster size) conflicts with "rows never pay" at Large.
- The BUG-153 signal needs the 5-per-cell re-measure.
- The BUG-185 `disablesAnimations` on a cover dismiss is unverified (fallback above).
- The BUG-186 watchdog must not fire during a slow dismiss (`isBeingDismissed`).
- Removing Synopsis Length turns Long on for every Classic user (release notes).
- No shared/ changes, but the Kotlin trio still runs as a gate.
