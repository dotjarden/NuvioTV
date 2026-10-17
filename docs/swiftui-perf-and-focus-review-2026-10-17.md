# SwiftUI performance review + focus consistency pass (2026-10-17)

Submodule branch `claude/focus-consistency` (tip `aa66d8bab`: `a802e41f8` + `f78fe7ea8` + the Home split merged from `claude/home-split`; local only), cut from `tvos-shared-extraction` `523ad97db`. Not merged.

Method: three read-only review agents (Home/browse performance, the rest of the app's performance, focus across every screen). They used the `swiftui-performance-audit` and `swiftui-ui-patterns` skills. All performance findings come from reading the code: there is no Instruments trace yet.

## Gates

- Debug and Release builds on the FA87 simulator: green.
- New UI test `FocusRowUITests.testProfileEditorDownFromRightmostSwatchReachesSave`: PASS. With the helper made a no-op it FAILS ("Down never reached the colour swatches"), so the test reproduces the reported bug.
- NuvioTVTests: 1838 executed, 0 failures (5 skipped).

## Focus: what changed

The root cause of the Edit Profile complaint: the tvOS focus engine only moves Up/Down to a control whose frame sits in the path of the focused one. The editor stacked centred rows of different widths: the name field, the avatar strip, eight swatches, one or two PIN chips, Save, Delete. Any control that had nothing directly above or below it was a dead end.

New helper `DesignSystem/FocusRow.swift`: `.focusRow(alignment:)` = full-width frame + `.focusSection()`. Any vertical press enters the next row on the nearest control. Convention: a `.focusSection()` must never sit on a view that hugs its content.

| Screen | Fix |
|---|---|
| Edit / Add Profile | every row is a `.focusRow()` (name, avatar strip, swatches, PIN chips, Save, Delete) |
| Welcome | primary sign-in button and the "other ways" pill row are full-width sections (Up from an outer pill reached nothing) |
| PIN pad | keys are no longer `.disabled` while a PIN is checked: that left nothing focusable after the 4th digit. The actions guard `isBusy` instead |
| Email sign-in | Sign In / Cancel are no longer disabled while busy (focus was thrown into the text fields on press); guarded in the actions |
| Collection folder (Classic) | Edit Filters corner button and the tab chips are sections (unreachable unless directly above/below) |
| Search | Top result, empty-state action and the Discover tiles are full-width sections |
| Library, Debrid Cloud | Refresh row is a full-width section |
| Detail | studio/network logos row and Trakt comments are full-width sections |
| TMDB filter editor | each text field row, each chip row and the footer (Save / Cancel / Clear) are sections |
| Player panel (subtitle delay, mpv audio delay) | Reset stays mounted (no-op at 0); it used to vanish on press and drop focus |

## Focus: found, not fixed (follow-ups)

- Never disable or remove the focused control. Still broken in: Add-ons Install while installing, Settings Save Key, badge Import, Install Repository, MDBList Connect/Disconnect, Clear Pattern, the shuffle sheet's Play. Also Connect → activation-card swaps in Services, Start ↔ Stop Remote Setup, and shuffle-sheet phase changes. Each needs a `@FocusState` hand-off in `onChange(of: phase)`, the `ServerConnectionView` pattern.
- Settings List rows with more than one control: plugin repo row (trash plus every scraper toggle in one row), badge pack row, key and URL field + button rows, subtitle text-colour swatches. `CatalogSettingRow` recorded on device that a List row exposes one focus target. Check on the Apple TV, then split them into separate rows.
- Episodes shelf has no initial target: Down from the season picker lands on the nearest episode, not the next one to watch. Add `.defaultFocus`.
- Welcome, Person and Entity still use `.focusScope` + `.prefersDefaultFocus`, which `SettingsRootView` documents as unreliable. Move them to `@FocusState` + `.defaultFocus`.
- TMDB filter editor: Menu dismisses the cover and drops unsaved edits. Product call: confirm or save on exit.

Proposed convention:
- `.focusRow()` on every vertically stacked group;
- `@FocusState` + `.defaultFocus` for initial focus;
- never disable or remove the focused control;
- one focusable per Settings List row;
- tab roots use `.railMenuReveal()`, pushed pages use the system pop, and covers with unsaved state add `.onExitCommand`.

## Performance: what changed (low-risk, equality-gating)

1. `DetailView.dimModel` is now `@State`, not `@StateObject`. Holding the model subscribed the ~3,200-line Detail body to every dim step (~17 per scroll ramp) and every scroll-latch flip. Only `ScrollDimOverlay` and `DetailTopScrim` observe it now, as the BUG-41 comments always intended. Confirm with the `[BUG41] detailBodyEval` probe.
2. mpv player tick (`MPVPlayerView.refreshState`, every 0.5 s): position, duration, pause, buffering and the transport mirror are written only when they change. A paused player no longer re-renders the overlay and transport bar twice a second.
3. `HomeViewModel`: `isLoading`, `errorMessage`, `continueWatching` and `upcoming` are written only when they change. Kotlin data classes bridge `equals` as `isEqual`, so the compare is structural. The progress flow emits on every playback save while Home sits under the player.
4. Stream picker add-on logo: `AsyncImage` (no cache, full decode on every row) → `CachedAsyncImage` decoded at 44 pt.

## Batch 2 (`f78fe7ea8`, same day)

Taken from the lists below, avoiding the Home files (the HomeView split runs in its own session).

- Perf #2 (Detail flags): `refreshFlags` writes only on change, and library, add-on, continue-watching-prefs and shuffle emissions skip the per-episode watched scan.
- Perf #3 (Episodes): the grouping, season order and posters are cached per `MetaDetails` object, so a Left/Right press no longer re-sorts every episode. Moving the focus state into a child view is not done.
- Perf #8 (profiles): `ProfilesViewModel` writes only on change.
- Perf #12 (decode sizes): episode stills and profile avatars decode at 1.2× their drawn size, which covers the focus lift.
- Focus "never disable the pressed control": Add-ons Install, Save Key, Import Badge Pack, Install Repository, Clear Pattern, MDBList Connect/Disconnect and profile Save. The phase-swap hand-offs (Connect → activation card, Remote Setup Start ↔ Stop, the shuffle sheet) are still open.
- Opus review r1: 0 P1 / 1 P2 / 4 P3, all fixed except the Home hold-route note.
  - The P2: the stream-picker logo now stays clear while loading and when it fails, where it had shown a shimmer and then a grey tile.
  - The open note: Home no longer republishes `isLoading` during the hero hold; nothing found reads a stale field, but give it a device look.
- Gates: Debug + Release, NuvioTVTests 1838/0, FocusRowUITests PASS.
- Held back because they change behaviour and need a device judgement: Episodes `.defaultFocus` on the next unwatched episode, cast row keyed by person id, a lazy stack for Search results.

## Home split (`claude/home-split` `f96acfdc0`, merged as `aa66d8bab`)

Built in a separate session and clone, branched off `a802e41f8`. It shares no files with batch 2, and the merge was clean.

- Perf #1: the rows region (`Home/HomeRowsList.swift`) observes only `HomeViewModel`. The hero header, backdrop and debug labels are leaf views (`Home/HomeHeroLeaves.swift`) that observe the focus models themselves. The per-row closures are replaced by one stable actions object.
- Also done there: #4 (posterStyle / trailer gate once per row body), #10 (`rowsByKey` for the Stage strip) and #11 (`pinnedPlan` once per body).
- Measured with a new DEBUG body counter (`HomeBodyCounter`, `HomeBodyCountUITests`). Over six hero commits, HomeView body evaluations went from 12 to 0 and CatalogRowView from 30 to 6.
- Reviewed by one Opus round in that session; its findings were fixed.
- Stage UI leg S11 fails identically on the base, so the failure predates this change.
- Gates after the merge: Debug + Release (FA87), NuvioTVTests 1838/0 (5 skipped), FocusRowUITests PASS.
- Device pass owed (Test profile): walk Home rows in Classic and Stage. Check the hero swap, the pinned-row settle, Up into the hero, and Continue Watching / Upcoming actions, and confirm nothing in the tuned Home behaviour moved.

## Performance: found, not fixed (ranked)

| # | Severity | Where | Issue | Fix | Effort |
|---|---|---|---|---|---|
| 1 | High (DONE, Home split) | HomeView (5 observed objects) | Every hero focus commit (0.2 s dwell) re-runs the 600-line body and every visible row. Fresh closures mean no row can be skipped | split the rows region into a view that observes only `HomeViewModel`; hero/backdrop leaves observe the focus models; one stable `HomeRowActions` reference instead of per-row closures | L |
| 2 | High (DONE, batch 2) | `DetailViewModel.refreshFlags` | 7 watchers write every flag unconditionally; `computeWatchedEpisodeKeys` makes 2 Kotlin calls per episode (1,000+ on long shows) on main | equality-gate; recompute keys only on watched/progress emissions for this id; coalesce | M |
| 3 | High (grouping DONE, batch 2) | `EpisodesSection` body | groups and sorts every episode (Kotlin reads in the comparator) on every D-pad move | group once per `meta`; move the focus state into a child view | M |
| 4 | Medium (DONE, Home split) | `CatalogRowView` | `posterStyle`, `inlineTrailersActive` (UIAccessibility read + probe) recomputed per card | hoist to one `let` per body | S |
| 5 | Medium | `InlineTrailerCard`/`PosterCard` | ~10 `@AppStorage` observers + a `@StateObject` per realized card | one `FocusAppearance` value in the environment; build the trailer model only when enabled | M |
| 6 | Medium | `CachedAsyncImage` | memory-cache hits still draw a shimmer frame + start a repeatForever animation on mount | seed the loader from the cache in `init` | S-M |
| 7 | Medium | Stream picker | row-level `@FocusState` re-renders every row per move; `ViewThatFits` with up to 9 badge candidates; rows keyed by offset | `StreamRow` subview reading `isFocused`; a custom `Layout` for the badges; key by `playbackStreamKey` | M |
| 8 | Medium (gating DONE, batch 2) | ContentView / ProfilesViewModel | app root re-renders on every profile/auth emission | equality-gate writes; don't observe at the root | S-M |
| 9 | Medium | Search results | non-lazy `VStack`; fresh footnote closure per body | `LazyVStack`; stable footnote provider | S-M |
| 10 | Medium (DONE, Home split) | StageStripHome | linear Kotlin-bridged row lookup per mounted row | publish `rowsByKey` from the VM | S |
| 11 | Low-Med (pinnedPlan DONE, Home split) | HomeView | `pinnedPlan` (4 UserDefaults reads + math) evaluated 10+ times per body; `heroItems` reallocated per access | compute once per body | S |
| 12 | Low (DONE, batch 2) | Episodes thumbnails, profile avatars | decoded at the 1920 px default; live 28 pt blur on spoiler stills | pass `.points(...)` decode sizes | S |
| 13 | Low | Settings | ~15 watchers replay on open, each writing unconditionally | equality-gate | M |
| 14 | Low | transport bar, Detail cast, chapters | `ForEach` keyed by offset | stable ids | S |

Suggested next step: an Instruments SwiftUI trace on the Apple TV (View Body counts for `CatalogRowView`, `InlineTrailerCard`, `PosterCard`, `EpisodesSection`), resting ~0.3 s per card across a Home row and walking a long series' episodes, before and after #1-#3.

## Device pass owed (Test profile)

- Edit Profile: from every swatch, Down reaches PIN / Save; Up from Save reaches the swatches; the avatar strip (cloud account) is reachable from the name field and from the swatches.
- Welcome (signed-out): Up from Continue as Guest / Connect to a Server reaches the primary button.
- PIN prompt: after a wrong PIN, focus stays on the pad.
- Classic collection folder with a TMDB source: Up from a left chip reaches Edit Filters.
- Player panel: Reset on subtitle delay keeps focus.
- Detail on a long series: scroll feel unchanged (dim, scrim, trailer hand-off).
