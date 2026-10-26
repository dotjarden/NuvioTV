# Stream picker A + Add-ons hub C: implementation plan (2026-10-25)

Source: `docs/stream-picker-addons-redesign-options-2026-10-25.md`. Christian's decisions (2026-10-25): stream picker **Direction A (cinematic two-pane)** built so **Direction B (best source + quality tiers)** can sit on top later; Add-ons page **Direction C (Sources hub)**. Nothing built yet. All paths are under `NuvioMobile/` unless stated; Swift paths are under `NuvioMobile/iosApp/NuvioTV/`.

This plan is written to be run in a **local session on the Mac** (Xcode, the FA87 fixture simulator, the device rig). The cloud session only wrote the docs.

## 0. How to run it locally

1. Open a Claude Code session in `~/Claude/Projects/NuvioTV` (the outer repo). Read `CLAUDE.md` first: clone-not-worktree, gates, Test profile, review loop, copy rule.
2. Clone the submodule for the work, never a worktree:
   ```
   git clone ~/Claude/Projects/NuvioTV/NuvioMobile ~/Claude/Projects/NuvioMobile-picker-hub
   cd ~/Claude/Projects/NuvioMobile-picker-hub && git checkout -b picker-a tvos-shared-extraction
   ```
   Two feature branches, landed separately so a picker regression never holds the hub: `picker-a` (sections 2–3) first, then `addons-hub-c` (section 4) rebased on it. In the clone MPVKit is a symlink over the gitlink: stage by explicit paths, never `git add -A`.
3. Record the base SHA before touching code: `git rev-parse HEAD` → `--base` for the review loop.
4. Build and test commands are the ones in `CLAUDE.md` (Kotlin: `./gradlew :shared:jvmTest :shared:tvosSimulatorArm64Test :composeApp:iosSimulatorArm64Test`; Debug + Release sim builds on `FA87E9B6-…`; `NuvioTVTests`; the UI legs named per wave, sandbox OFF). Device build via `generic/platform=tvOS` + `devicectl`, device passes in the **Test** profile only.
5. Review loop: `.claude/skills/codex-review/tools/review.sh --repo NuvioMobile --base <sha>` unsandboxed, review → fix → re-review until CLEAN. Codex quota resets 2026-10-29; before that the Opus read-only review agent stands in. Record delegation rounds and findings in this doc under "Run log" (section 7).
6. Landing: fast-forward into `tvos-shared-extraction`, push, delete the branch (local + origin) and the clone, bump the outer pointer. Cut only on Christian's go (`scripts/cut-rc.sh beta.20-rc1`). Release notes and tester DMs must name every new setting and its default (section 6).

## 1. Decisions for Christian (recommendation first)

- **D1 Backdrop default.** The shared `StreamBackgroundMode` (Normal / Cinematic, `shared/.../streams/StreamBadgeSettingsRepository.kt:27`) defaults to Normal and tvOS never reads it. **Recommend: ship the picker with Cinematic as the tvOS default** so testers see the redesign without hunting for a switch; "Source Background" in Settings › Sources flips it back to Normal (plain black, today's look). Alternative: Normal default, Cinematic opt-in.
- **D2 Tab name.** The hub holds add-ons, catalogs, debrid and plugins. **Recommend: keep the tab labelled "Add-ons" for beta.20** (testers and the Reddit guides say "Add-ons tab"); the page title inside reads "Sources". Rename the tab in a later beta if the hub sticks.
- **D3 Catalogs.** **Recommend: move** catalog enable/reorder from Settings › Home Screen into the hub's Catalogs page and leave a one-line "Managed in Add-ons › Catalogs" link row behind. Hero Sources stays on Home Screen (it is a Classic-layout concern). Alternative: duplicate in both places.
- **D4 Manage from phone.** **Recommend: stage it.** beta.20 ships the hub, inline controls, install sheet and catalogs page; the QR phone-management flow gets a half-day feasibility spike first (section 4, H6) and ships in beta.21 if the spike passes. Alternative: hold the whole hub until QR works.
- **D5 "All" view shape.** With no chip selected, **recommend: one flat list with a small section label per add-on** (upstream mobile's `StreamSectionHeader`, non-focusable, with the per-add-on "Fetching…" spinner). Picking a chip hides the labels. Alternative: fully flat, no labels.

## 2. Stream picker, Direction A

### What stays
`StreamsViewModel` row models and keys (`StreamRowModel`, `.equatable()`, BUG-207), `StreamRowView` anatomy (title, description with dwell expand, size chip, badge packs, optional add-on logo column), `FirstPlayAutoPlayController` and its cover (BUG-183), `StreamPickerExitPolicy` (BUG-174), the failover alert, `ExternalPlayMenu`, `RejectedStreamLinks`. None of the five presenters (`DetailView.swift:1291/1301`, `EpisodesSection.swift:253`, `HomeView.swift:1321`, `ContentView.swift:306`) change signature: `StreamPickerView.init` (`StreamPickerView.swift:169`) already receives `poster`, `episodeStill`, `synopsis`, `meta`, `logoUrl`, `season`, `episode`, `episodes`, which is everything the left pane needs.

### Wave P0: shared seams (Kotlin, `shared/src/commonMain/.../streams/`) — S

- **P0.1 Bind the per-add-on filter.** `StreamsUiState.selectedFilter` / `filteredGroups` (`StreamModels.kt:364-378`) and `StreamsRepository.selectFilter(addonId)` (`StreamsRepository.kt:724`) exist for mobile. Confirm `selectFilter` survives `reload()`/`clear()` the way tvOS wants (reset to null on a new title, keep on refresh) and add a jvmTest for both.
- **P0.2 Group status for chips.** `AddonStreamGroup` (`StreamModels.kt:331`) has `isLoading`; add `errorMessage: String?` (set where the fan-out catches a per-add-on failure) so a chip can show the Android TV error state. jvmTest: a failing add-on yields a group with `errorMessage` and no streams.
- **P0.3 Background mode.** Nothing to add; `StreamBadgeSettingsUiState.backgroundMode` + `setBackgroundMode` (`StreamBadgeSettingsRepository.kt:24,167`) are ready. Per D1, change the tvOS storage default to Cinematic in `StreamBadgeSettingsStorage` for the tvOS target only (expect/actual or a platform default), with a tvosSimulatorArm64Test.
- **P0.4 B-ready seam (no UI yet).** Add `StreamsUiState.bestCandidate: StreamItem?` computed from the existing `StreamQualityRank.rankBest` (`StreamAutoPlayRanking.kt:64-87`) over `filteredGroups`, plus a `StreamFacts` data class (resolution, hdr, sourceType, codec, audio, sizeBytes, cached, languages; all nullable) with a parser that today fills only what the debrid formatter and `StreamBadgeRules` already know. Direction B consumes both; nothing in A renders them. jvmTest on the parser for three real add-on descriptions (Torrentio, Comet, AIOStreams lines from `docs/research/` shots).

### Wave P1: layout — M

New files, each small, so `StreamPickerView.swift` shrinks rather than grows:

- **`Screens/StreamPicker/StreamPickerBackdrop.swift`.** `CachedAsyncImage` of `meta.background ?? poster` (episode: `episodeStill` on top, background behind) at a reduced decode size (1280 wide), `scaledToFill`, under a horizontal scrim with the Android TV stops (solid background at 0 and 1, 0.85 at 0.15/0.85, 0.40 at 0.30/0.70, 0.15 at 0.50) plus a bottom 0.6 band. Shown only when `backgroundMode == .cinematic`; Normal keeps `Theme.Palette.background`. No live `.blur` modifier (perf; see P4).
- **`Screens/StreamPicker/StreamPickerInfoPanel.swift`** (left 40 %, non-focusable). `TitleLogoHeader` in the Detail logo slot (180 high, max 600 wide), then for episodes `S1 · E3` + episode title + runtime, for movies genres · year (`meta`), then the poster at 2:3 (260 wide, corners from `PosterStyle`), then a live line "Finding streams… 3 of 4" while loading (count = groups answered / groups expected) that becomes "155 sources from 4 add-ons" when done. Hide the poster when the vertical space is under 700 pt (the loading cover and alerts are unaffected).
- **`Screens/StreamPicker/StreamPickerSourcePanel.swift`** (right 60 %). One `RoundedRectangle(Theme.Radius.hero)` panel on `Theme.Surface.panel` (`.thick`; the token's comment already names the picker), inner padding `Theme.Spacing.md`, containing in order: resume pill (P3.3), chip row (P2), list (P3). Padding top/trailing/bottom `Theme.Spacing.screen` from the screen edge.
- **`StreamPickerView.swift`.** Replace the `ScrollView { LazyVStack }` body (`:279-391`) with `HStack(spacing: 0) { InfoPanel; SourcePanel }` over the backdrop. The debrid warning banner, the test-stream section and the toast/alert overlays move into the source panel header/footer unchanged. The loading cover (`:407-411`) stays full-screen above everything.

### Wave P2: source chips — M

- **`Screens/StreamPicker/SourceChipRow.swift`.** A horizontal `ScrollView` of `FilterChip`s (`DesignSystem/FilterPills.swift:97`, `.chip(selected:)`): a refresh chip (icon only, spins via `.symbolEffect(.rotate)` while any group `isLoading`, calls `StreamsRepository.reload`), then "All", then one chip per `AddonStreamGroup` in group order (`StreamAutoPlaySelector.orderAddonStreams`, which follows installed add-on order). Chip label "Comet · 6" (count omitted while loading).
- **States.** Loading: label at 0.6 opacity with a `ProgressView().scaleEffect(0.5)` trailing. Error (`errorMessage != null`): `Theme.Palette.error`-tinted fill at 0.12, removed from the row 1.6 s after the fan-out finishes unless it has streams (Android TV `scheduleErrorChipRemoval`). Selected: accent fill from `.chip(selected:)`. The accent focus/selection colour is the only brand colour on the screen, per the HIG contract.
- **D-pad.** `.onMoveCommand` on the list: `.left`/`.right` move the selected chip one step with wrap, 112 ms repeat throttle, and scroll the list to the top (Android TV `StreamScreen.kt:1240-1261`). The chip row is its own `.focusSection()`; Up from the first row lands on the selected chip via `prefersDefaultFocus(in:)` on the selected chip. After Select on a chip, focus stays on the chip (not the list).
- Selecting a chip calls `StreamsRepository.selectFilter(group.addonId)`; "All" passes `nil`. `StreamsViewModel` reads `filteredGroups` instead of `groups`.

### Wave P3: list and rows — M

- **P3.1 Flat list.** `LazyVStack(spacing: Theme.Spacing.sm)` of `StreamRowView`s for `filteredGroups.flatMap`, keyed as today (`StreamsViewModel.swift:120-140`). Per D5, when `selectedFilter == nil` insert a non-focusable `StreamSectionLabel` (add-on name, `Theme.Font.sectionTitle`, plus "Fetching…" spinner while that group `isLoading`) before each group's rows. The collapsed `groupHeader` button (`StreamPickerView.swift:625-654`), the expanded-set state (`:449-472`) and the collapse-focus dance (`:656-669`) go away.
- **P3.2 Row surface.** Rows become 12 pt-radius cards on `Theme.Palette.surface` at rest (upstream mobile white 5 %, Android TV #1A1A1A) so they read inside the panel; focus keeps the `.settingsRow` white platter for now (the native-List pass is a separate debt; do not mix it into this batch). Row padding `md`. Everything inside the row is unchanged.
- **P3.3 Resume pill.** Above the chip row: "Resume from 1:12:04" or "Resume from 40 %" when the picker is opened with a saved position and not `startFromBeginning` (the presenters already know this: `startOverMovie`, Continue Watching). Capsule on `surfaceElevated`, `metaStrong` font, non-focusable. Source of the position: the same repository the Detail Play button uses for "Resume" (`DetailView`'s resume/`startOverMovie` logic); add an optional `resumePositionMs`/`resumeFraction` pair to `StreamPickerView.init` with defaults nil so presenters opt in one at a time (Detail movie, series episode, Continue Watching).
- **P3.4 Initial focus.** First row once the list has rows, else the "All" chip; never steal focus from a row the user has moved to (keep `:1234-1244`). Focus restore after the player uses the same keys as today.
- **P3.5 Empty and error states** move into the panel: the existing reason/hint texts (`StreamsViewModel.swift:340-374`) centred in the list area; the test-stream button only when there are no groups.

### Wave P4: settings and performance — S

- **P4.1 Setting.** Settings › Sources › "Source Background": Cinematic / Normal, default per D1, stored through `setBackgroundMode`. Explainer text in `SettingsDescriptions.swift`. String catalog entries.
- **P4.2 Perf.** Backdrop decoded once at 1280 wide, no `.blur`, scrim as a `LinearGradient` overlay; material only on the panel. Measure scroll on the device with a 150-stream Torrentio list (BUG-207's repro) before and after; if the panel material costs frames, fall back to `Theme.Palette.surface.opacity(0.72)` behind the panel (same fallback Android TV uses below API 31).
- **P4.3 Trailer hold.** The series trailer must stay stopped under the picker (BUG-198); the backdrop image must not re-trigger it.

### Wave P5: tests and gates — M

- **NuvioTVTests.** Chip order and labels from a fixture `StreamsUiState` (loading, error, counts); `selectFilter` round trip; resume pill formatting; `StreamFacts` parser (Swift side only if the Kotlin test does not cover it).
- **NuvioTVUITests.** New `StreamPickerUITests` on the fixture add-on (`DiscoveryStubServer.swift` already serves streams): opens Dune from the fixture, asserts the info panel logo, chip row with "All" + one chip per add-on, Right moves the selection, first row focused, Select plays. Keep `NativePlayerParityUITests` and `PostPlayUITests` green (both pass through the picker).
- **Gates.** All `CLAUDE.md` gates on the tip, the two legs above, then a device pass in the Test profile: a movie with 100+ streams, an episode, auto-play on, external player hand-off, Back from the player (BUG-174), White theme chip contrast (BUG-43 family).

### B-ready seams to leave in place
`StreamsUiState.bestCandidate` and `StreamFacts` (P0.4); `StreamPickerSourcePanel` takes a `content` enum (`.list` now, `.tiers` later) so B replaces the panel body, not the layout; the chip row is a separate view so B can swap it for tier chips; `FirstPlayAutoPlay` stays untouched so B's "Best source" card can call its candidate walk.

## 3. Picker scope guard
Not in this batch: the native-List focus pass, structured metadata rows (that is C's parser and B's UI), pinned sources, codec filter exposure, per-series quality memory, stream caching between opens. Note them in the tracker as follow-ups if testers ask.

## 4. Add-ons page, Direction C (Sources hub)

### What exists to build on
`AddonRepository` (`shared/.../addons/AddonRepository.kt`): `addAddon` (:280), `removeAddon` (:323), `moveAddon` (:337, unused on tvOS), `setAddonEnabled` (:361), `refreshAll` (:386), `refreshAddon` (:395); `AddonOverview` (totalAddons, activeAddons, totalCatalogs); `ManagedAddon` with `manifest.logoUrl/description/version/types/resources/catalogs/behaviorHints`, `isRefreshing`, `errorMessage`. tvOS: `AddonsView.swift` (157 lines, to be replaced), `AddonsViewModel.swift`, the Catalogs disclosure in `HomeScreenSettingsPane.swift:279-306` (`CatalogSettingRow` :682-717, move up/down via context menu), `DebridViewModel.isConnected(providerId)` (`DebridViewModel.swift:90`), `PluginsViewModel` and the Plugins section in `SourcesSettingsPane.swift:268`, the Settings row kit (`SettingsRowViews.swift`: `SettingsRowChrome`, `SettingsRowLabel`, `SettingsSwitchGlyph`).

### Wave H1: view model — S
- `AddonsViewModel` gains `move(addonAt:by:)`, `refreshAll()`, `refresh(manifestUrl:)`, `overview` (from `AddonOverview`), `lastRefreshedAt`, and a `HubSummary` struct: add-on counts, catalog counts (from the Home Screen catalogs model), debrid providers connected (from `DebridViewModel`), plugin state (from `PluginsViewModel`, only when the tvOS plugin repository reports `pluginsEnabled`).
- URL normalisation before `addAddon`, ported from Android TV (`AddonManagerViewModel.kt:189-205`): `stremio://` → `https://`, require http(s), strip a trailing `/manifest.json` and slashes. Unit tests in NuvioTVTests.

### Wave H2: hub screen — M
- **`Screens/Addons/SourcesHubView.swift`** replaces `AddonsView`'s body (tab label per D2). `ScrollView { LazyVStack(spacing: sectionGap) }`, padding `screen`, flat background (BUG-214).
- **Row 1, summary cards** (`.card` button style, 16:9-ish, three across): **Add-ons** ("4 installed · 3 on", a strip of up to five 44 pt logos) → scrolls to the installed section; **Catalogs** ("8 of 12 on Home") → `CatalogOrderView` (H4); **Debrid** ("TorBox connected" / "Not connected") → Settings › Services; **Plugins** (only when enabled on this build; "2 repositories · 7 providers") → Settings › Sources › Plugins.
- **Row 2, action cards:** **Install add-on** → install sheet (H3); **Refresh all** (subtitle "Updated 2 h ago", spinner while `refreshAll` runs); **Manage from phone** (hidden until H6 ships; behind a `DebugConfig` flag during development).
- **Installed add-ons** section title (`screenTitle`) with an inline spinner while loading, then one `AddonCardView` per add-on; "No add-ons installed. Install one to get started." when empty.
- **`Screens/Addons/AddonCardView.swift`.** Card on `surface`, 12 pt radius, padding `lg`, one `.focusSection()` so Left/Right stay inside. Left: 44 pt manifest logo (puzzle glyph fallback), name (`sectionTitle`, 1 line), "v1.4.2 · Streams · Catalogs · Subtitles" (`meta`, types from `resources`), host (`caption`, secondary, 1 line), "Catalogs: N" (`caption`). Status pill: Active / Disabled / Refreshing / Unavailable (`error` tint when `errorMessage != nil && manifest == nil`). Right: inline controls as separate focusable buttons in the Settings row kit style: **On/Off** (`SettingsSwitchGlyph`), **↑**, **↓** (disabled at the ends), **Remove** (destructive; confirm alert kept from today: "Remove <name>? Its catalogs and streams will no longer appear."). Select on the name area opens `AddonDetailSheet`: description, version, resource list, catalog list, manifest URL, Refresh, and **Configure** when `behaviorHints.configurable`: tvOS cannot open the web, so show the configure URL as a QR code (`CIQRCodeGenerator`, available on tvOS) with the URL text under it.
- Reorder calls `moveAddon` and keeps focus on the moved card (re-request focus by key after the model updates). Toasts for install/remove/refresh reuse the picker's capsule toast.

### Wave H3: install sheet — S
- `.sheet` with the current field + Install button moved out of the page (`AddonsView.swift:53-101`), the DEBUG "Quick install" chip kept DEBUG-only, status modal (Checking / Installed / Couldn't install) mirroring upstream's `NuvioStatusModal`. On success the sheet closes and focus lands on the new card.

### Wave H4: catalogs page — M
- **`Screens/Addons/CatalogOrderView.swift`**: list of catalog rows ("Top Movies · Movie", add-on name, "Disabled on Home" in `error` when off), each with On/Off, ↑, ↓ inline (same kit as H2), plus a "Follow add-ons order" switch at the top (Android TV `CatalogOrderScreen`). Backed by the same model `HomeScreenSettingsPane` uses today. Per D3 the Home Screen pane keeps a link row "Catalogs — managed in Add-ons"; Hero Sources stays.

### Wave H5: tests and gates — M
- **NuvioTVTests.** URL normalisation; hub summary from fixtures (counts, debrid connected, plugins hidden when disabled); reorder moves and bounds; configure-QR payload equals the configure URL.
- **NuvioTVUITests.** New `AddonsHubUITests`: hub cards present, install sheet opens and installs the fixture manifest, card shows logo/status, ↓ moves it below the next card and the stream picker's chip order follows (one test that opens the picker after reordering: this is the user-visible reason reorder exists), Remove confirms and removes, Catalogs page toggles a catalog and Home reflects it.
- **Gates** as in `CLAUDE.md`, then a device pass in the Test profile: install a tester add-on by URL, reorder, disable, remove, catalogs reorder, and remove the tester payload afterwards.

### Wave H6: Manage from phone (beta.21, per D4) — L
- **Spike (half day, before any build).** A `Network.framework` `NWListener` HTTP/1.1 server on tvOS bound to the Wi-Fi address, serving one static page, reachable from an iPhone on the same LAN; confirm whether tvOS prompts for local-network permission for an inbound listener (expected: no, the prompt is for outbound local traffic) and whether the app needs `NSLocalNetworkUsageDescription`. Record the result here.
- **Build.** `Services/PhoneManagementServer.swift` (listener, JSON endpoints: state, propose change), a trimmed page ported from Android TV's `core/server/AddonWebPage.kt` (3.3k lines; keep add by URL, enable/disable, reorder, catalogs order; drop collections and TMDB search), the `PendingAddonChange` model and `ConfirmAddonChangesDialog` (added/removed/reordered/catalog changes, Reject/Confirm with focus on Confirm) from `AddonConfigServerModels.kt:160`. QR of `http://<ip>:<port>/` on the TV via `CIQRCodeGenerator`, server stops when the overlay closes or the app backgrounds. Change the hub's "Manage from phone" card from hidden to shown.
- **Tests.** NuvioTVTests for the change-set diff and the confirm model; a UI leg that drives the server over loopback from the test runner.

## 5. Order of work and sizes

| Step | Branch | Items | Size |
|---|---|---|---|
| 1 | `picker-a` | P0.1–P0.4 (Kotlin, jvmTest + tvos test) | S |
| 2 | `picker-a` | P1 layout, P2 chips, P3 list/rows | M+M+M |
| 3 | `picker-a` | P4 setting + perf, P5 tests, review loop, gates, device pass, land | S+M |
| 4 | `addons-hub-c` | H1 view model, H2 hub + cards, H3 install sheet | S+M+S |
| 5 | `addons-hub-c` | H4 catalogs, H5 tests, review loop, gates, device pass, land | M+M |
| 6 | cut on go | beta.20-rc1 with 1–5 | — |
| 7 | `addons-hub-phone` | H6 spike, then build if it passes | L |

## 6. New settings and user-facing changes (for release notes and the tester DM)
- **Source Background** (Settings › Sources): Cinematic / Normal, default **Cinematic** (D1; Normal if Christian picks the alternative).
- Stream picker: two-pane layout, source chips with loading/error state, Left/Right switches source, resume pill, flat list with per-add-on labels, no more collapsed groups.
- Add-ons tab: Sources hub with summary cards, inline On/Off, Move Up/Down and Remove on each add-on card, add-on detail sheet with Configure as a QR code, Install moved to a sheet, Refresh all, Catalogs page (moved from Settings › Home Screen; a link row stays there).
- No other defaults change. Badge packs, Show Add-on Logo, Badges Above Title, Auto-Play Best Source and its Cached-only sub-toggle are untouched.
- Every DM and release-note draft goes through the copy rule (`scripts/deslop/deslop.py`, SlopMonster) before Christian sees it; nothing is sent without his go.

## 7. Run log
(Filled in by the local session: delegation rounds, review verdicts per `--base`, gate results per tip, device pass notes, declines.)
