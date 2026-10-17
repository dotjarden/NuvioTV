# Batch B review, round 1 (read-only, 2026-10-16)

Range: `8e8090806..d472c8411` on `claude/batch-b` (clone `~/Claude/Projects/NuvioMobile-batch-b`), 3 commits, 54 files,
+2718/−416. Reviewer: Opus read-only round (Codex on its limit until 10-29). Nothing in the clone was edited.
Paths below are relative to `NuvioMobile-batch-b/iosApp/`.

**Counts: P1 2 · P2 1 · P3 9.**

## P1

### P1-1 · The cover's Menu recogniser is left OFF after an in-place player swap (next episode, failover) → a Menu during the next probe, or anywhere in a native next episode, can leave the app (BUG-165's class, moved)

`NuvioTV/Screens/MPVPlayerView.swift:741-750`. `viewWillDisappear` now re-enables the hosting cover's Menu tap
(`gateCoverMenuTap(enabled: true)`) only when `!isLeavingPlayer`. `isLeavingPlayer` (`:3593`) is true for
`isBeingDismissed` **or `isMovingFromParent`** anywhere up the chain. The player cover in
`StreamPickerView.swift:474-487` swaps its content IN PLACE: `onPlayNext: { next in selected = next }` and the failover
path change `ctx`, and `.id(ctx.id)` rebuilds `PlayerScreen` inside the same presentation (its own comment: "Failover
swaps in place the same way"). The old mpv controller is then removed from its parent, so `isMovingFromParent` reads
true, the recogniser it disabled in `viewDidAppear` stays disabled, and the cover keeps it disabled for the rest of its
life.

What then has no Menu handler:
- the new `PlayerScreen`'s `.deciding` phase (`PlayerScreen.swift:73-85`, the probe; `PlayerLoadingOverlay` has no
  Menu handling) — every swap with Native Dolby Vision on (the default);
- the native engine. `PlayerPanelHost.swift:36-39`/`:127-135`: an unconsumed Menu "continues up to SwiftUI, whose
  `fullScreenCover` pops the player". The native host never re-enables the recogniser (only `MPVPlayerView` touches
  `coverMenuTap`).

Failure scenario: episode 1 is an MKV with TrueHD (routed mpv), Up Next auto-plays episode 2, a DV P8 MKV (routed
native). Menu with the transport bar hidden → nothing claims it → unhandled Menu at the end of the chain → tvOS sends
the app to the home screen. Same for a Menu pressed during the "Checking…" loading screen after any auto-advance or a
silent failover. Before this batch the old controller re-enabled the recogniser on the way out and the cover
dismissed.

Verify first (one log line): print `isMovingFromParent` in `viewWillDisappear` on an Up Next swap in the simulator
smoke host. If it reads true, this is live.

Smallest fix: re-enable unless the COVER itself is going away, not merely this controller:
```swift
let coverDismissing = sequence(first: self as UIViewController, next: \.parent).contains { $0.isBeingDismissed }
if !coverDismissing { gateCoverMenuTap(enabled: true) }
```
(keep `closeFailover()` on `isLeavingPlayer` as it is). Add a UI leg: mpv episode → `onPlayNext` swap → Menu during
`.deciding` → app stays foreground and the cover dismisses.

### P1-2 · FEAT-71 removed the Stage folder page's only focus anchor while it loads → Menu during a folder load is an app exit (BUG-47 eject class)

`NuvioTV/Screens/CollectionsUI.swift:1797` (`if filterEntries.isEmpty { EmptyView() }`) with
`FolderRowsPage.swift:191-195` / `:271-279`. Before FEAT-71 the Edit band always held the Layout picker, so it was
mounted and focusable (`isActive` is true "before any row had focus") and was the page's documented BUG-47 anchor.
Now the band mounts nothing when `filterEntries` is empty, and `editableSources` is empty for EVERY folder until the
first repository emission (`CollectionsUI.swift:1094-1100`), and stays empty for any folder without a TMDB source
(most add-on collections, Steven's included). During that window the page shows `loadingPanel` (a `ProgressView` +
text) or a strip of `StripLoadingRow`s, none focusable. The comment at `CollectionsUI.swift:1776-1780` acknowledges
dropping the anchor and relies on "the Rows page pulls focus to the first card as soon as a row is focusable": that
does not cover the seconds before it is.

Failure scenario (memory `tvos-focus-contrast-gotchas`, BUG-47): open a collection folder whose add-ons are slow (UX-16:
Steven calls the Stage slow), press Menu before the first row loads → focus sits on the tab bar or nowhere → Menu is
the system exit → the app goes to the tvOS home screen.

Smallest fix: give the loading states their own anchor, the pattern the empty/failed panels already use: a focusable
"Go Back" button in `loadingPanel`, and, while the strip has rows but none is focusable, keep the band mounted as an
invisible anchor (or mount the band whenever `filterEntries.isEmpty && !anyRowFocusable`, passed down from
`FolderRowsPage`). A UI leg: open a folder through a slow stub add-on, Menu at once, assert `runningForeground` and the
folder popped.

## P2

### P2-1 · FEAT-71: a per-folder Grid choice stored before this batch can never be undone

`NuvioTV/Screens/CollectionsUI.swift:1336-1343` + `FolderRowsPlan.swift:442-444` (`homeLayout == .classic ||
gridOverride || defaultGrid`). The Edit band's Layout picker was the only writer of `FolderLayoutStore`; it is gone
and the new Settings default can only turn folders INTO the grid. Anyone who picked Grid on a folder in rc4 (Steven's
video shows him in that band) keeps that folder as a grid forever, with no control on the TV that clears it, and the
"Collections Layout: Rows" row in Settings looks broken for that folder.

Smallest fix: when the Settings picker writes (either value), clear `FolderLayoutStore`'s key (`folderLayoutRaw = ""`),
or drop `gridOverride` from the resolve and delete the store (one release later). Update
`testStageFollowsTheSettingsDefault` (it currently pins "a stored per-folder Grid choice still wins over a Rows
default", the trap).

## P3

1. **Teardown comment states as fact what the device pass disproved.** `MPVPlayerView.swift:3656-3662`: "on the main
   thread … that was seconds of a frozen black screen … (Steven's video: ~6 s)". The plan's OUTCOME measured
   `terminate_destroy` at 76–132 ms and concluded the 6 s black is not the teardown. Rewrite the comment to say why it
   moved (keep main free; the Vulkan teardown can block) without the 6 s claim.
2. **The Metal layer's last reference is now released on `eventQueue`.** `MPVPlayerView.swift:3664-3669`: `layer` is
   captured and dropped inside the async block, so the `CAMetalLayer` (already removed from its superlayer on main)
   deallocates on a background queue with no run loop. Usually harmless, but it can produce "uncommitted CATransaction"
   warnings. Smallest fix: after `mpv_terminate_destroy`, `DispatchQueue.main.async { _ = layer }`.
3. **`MenuExitShieldRule` is dead code with a test.** `Player/MenuExitShield.swift:99-106` is never called by
   `MenuExitShield` (which gates on `isEnabled` + a `DispatchWorkItem`), so `MenuExitShieldTests` pins a rule the
   shield does not run. Either call it in `handleMenu` or drop both.
4. **UI leg comment claims what its control disproved.** `NuvioTVUITests/PlayerTransportUITests.swift:194-196`
   ("Without `MenuExitShield` the second press reaches the root and the app backgrounds"); the plan records that the
   opt-in control passes with the shield off too. Say the leg guards the exit-then-double-Menu path, not the shield.
5. **B10 misses DV P5 when Native Dolby Vision is off.** `PlayerScreen.swift:46` routes straight to mpv with no probe,
   so `decision` is nil and `mpvForcesGpuNext` is false: a P5 stream on a box with the native engine off still renders
   green/magenta on `gpu`. Edge case (the default is on, Steven's is on); either note it in the Settings copy or probe
   P5 cheaply. Also device-owed: that `gpu-next` + `hwdec=videotoolbox` actually applies the P5 RPU on the box (no
   hardware run of the B10 path is recorded).
6. **The folder page freezes its strip memory only at `onDisappear`** (`FolderRowsPage.swift:145-147`), which runs at
   the END of the push; a trailer-card collapse reported at the start of the push can overwrite the remembered card
   first. The push origin is snapshotted at the strip's focus loss (`onStripFocusLost`), so the restore mostly
   survives, but the brief's item (3) "freeze while covered" is not in force on the folder page during the
   transition. Worth one device look with In Row trailers on.
7. **`ViewerInputClock` swipe threshold is unproven on hardware.** `Home/ViewerInputClock.swift:69` (40 pt of indirect
   travel). If a clickpad swipe moves focus with less travel, a viewer's move after a pop reads as the engine's and is
   re-grabbed up to three times in 1.5 s (`maxRegrabs(clockLive: true)`), i.e. the restore fights the viewer. Add a
   device-pass step: pop, then a short swipe Down within 1 s, expect `restore retired … why=viewer input=swipe`.
8. **B4 applies beyond the Stage.** `PosterStyle.cardWidth` feeds every `CatalogRowView`, so shape-landscape rows in
   Classic Home, Search and Library also grow to `height × 16/9` (≈624 × 351 pt at Medium+, three cards per screen).
   Consistent with the decision, but the release notes should say so, and the Classic device pass should look at one.
9. **BUG-163's root cause is left live under the global Landscape Posters toggle.** `InlineTrailerCard.swift:2650`
   (`fadesBaseCard`) still keeps the opaque base card under the tile when the GLOBAL toggle is on; the agent's own
   comment says the same layering was "not reproduced: out of B4's scope". If the sim diff (0.00 vs 27.45) is right,
   global-toggle users get audio-only trailers too. Log a tracker row, or apply the same fade.

## Checked and clean

- **mpv teardown on `eventQueue`:** the block captures `ctx`, `layer`, `started`, never `self`; `mpv` is nil'd and the
  wakeup callback cleared before the hop, the queue is serial so queued `[weak self]` work drains first and no-ops;
  a deinit that happens to run on `eventQueue` just enqueues (no deadlock); MoltenVK main-thread syncs cannot deadlock
  because main is no longer blocked.
- **`MenuExitShield`:** window-level, press-only (`allowedTouchTypes = []`), disabled outside arm→disarm, idempotent
  install per window, 2.5 s ceiling, disarm from `MPVPlayerScreen.onDisappear`; DEBUG knob gated. `swallowsRelease(.exit)`
  → true is harmless (tvOS cancels the press ~20 ms into the dismissal) and the test was updated.
- **`[MenuProbe]` lines** only log; no behaviour change.
- **B10 routing:** `prefersGpuNext` only on `.mpv` decisions with DV profile 5; P5-in-MKV stays native; the fallback
  path reads the same probe; `forcesGpuNext` is set before `viewDidLoad`; simulator stays on `gpu`; the Stream Info
  note gains "· gpu-next"; tests cover P5 MP4, P5 for another reason, P5 MKV, P8, P7 two-track, nil probe.
- **B1:** one device-local key `show_catalog_details_in_headings`, default false; gates the Stage heading suffix
  (`rowHeadingShowsAddon`), Discover loaded and non-loaded headings (computed at draw time from the spec), the folder
  line on Classic hero-ON box, Classic hero-OFF panel, Stage folder previews and the folder page's plain preview. No
  other `folderHeroDescription` caller remains ungated. Strings and the explainer present in de/es/fr/it/vi.
- **B3 (BUG-164):** zoom-on allowance byte-identical to the old inline formula (ring only for the accent ring, as before
  with No Zoom off); No Zoom opens 44 pt for the shadow; `CardSystemLiftStyle.resolve` never puts `.lift` on a No Zoom
  card, so the tile's manual lift is gone there. Tests pin both branches.
- **B4 (BUG-162/163):** `landscapeFromShape` set only by `resolved(forSectionItems:)`; global toggle keeps 360×203
  everywhere (`cardWidth`/`cardHeight`, `landscapeRowGeometry`); `StripGeometry` and Classic's `pinnedLastRowHeight`
  plan shape rows at the poster height; the BUG-122 floor removal for shape rows is consistent; `styleKey` separates
  the two landscape kinds; tile art size, base card size and SeeAll match; CW and Upcoming keep 360.
- **B5:** freeze/unfreeze tied to `setCovered(covered && restoresFocus)`; Home snapshots the card at the push edge
  before the freeze; folder page captures via `FolderPushOrigin` (rail arm excluded, directional press excluded);
  `UncoverRestorePolicy` is pure, re-grabs are deferred 0.15 s and re-checked, viewer input retires with a pager
  cancel; observer removed in `deinit`; probe lines carry `source=`. 14 policy tests.
- **B6:** `headingGap(inStrip:)` keyed on `\.stripFocusMemory`, Classic keeps `md` 16; `catalogRowHeight` and
  `collectionRowHeightMax` updated; every strip row kind (catalog, collection, CW, Upcoming, loading, message, Discover
  failed) uses it.
- **B7:** picker in Settings › Home Screen, shown only on Stage, default Rows, device-local; band hidden at rest by
  opacity only (stays a focus section, so Up still finds it) — apart from P1-2 / P2-1.
- **B8:** `foundIn` and the rating dropped, type always printed, localized "Movie"; rows keep "Found in".
- **B9 (FEAT-70):** the initial card is forwarded without starting to follow; logo slot hidden while docked;
  `seedStage()` on a pop cannot overwrite a committed stage (`hasCommitted` guard); UI legs updated.
- **DEBUG add-on seed** (`HomeViewModel.applyAddonSeedIfRequested`): DEBUG only, refuses signed-in accounts.
- **Tests:** the new unit classes pin the rules they name (policy, freeze, clip, card sizes, heading setting, layout
  default, search meta line, router); the BUG-156 UI legs assert `row` and `foc` after the pop and the steal knob
  stands in for the hardware's late restoration.
