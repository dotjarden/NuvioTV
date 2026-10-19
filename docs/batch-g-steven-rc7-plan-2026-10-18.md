# Batch G: Steven's rc7 verdict → rc8 (plan, 2026-10-18)

Source: `docs/steven-beta19-rc7-verdict-2026-10-18.md` (BUG-174…183, FEAT-79/80). Three read-only code surveys (navigation/player, Detail, player performance + rail) ran 2026-10-18 evening; their findings are folded in below with file references (paths under `NuvioMobile/iosApp/NuvioTV/`). Nothing built yet.

rc8 also carries what merged after rc7: wide-poster trailers at the resting size (`457a38d34`), BUG-130 + BUG-128 (`843f84738`), Batch C part 2 (`38bd6b932`).

## Decisions for Christian (recommendation first)

- **D1 Back from a player.** Today a *manual* stream pick returns to the stream list on purpose (`dismissAfterPlayer = false`, `StreamPickerView.swift:793/823/855/1100`); only auto-play closes the picker. **Recommend: always close the picker when the player closes** (built-in and external), except when a failure alert or the failover list is queued. Alternative: keep the list for manual picks.
- **D2 Loading screen text.** Steven: "keep only the title". **Recommend: remove the status line ("Loading…/Checking…"), keep the episode line for series** (S01E03 · title is useful). Alternative: remove both.
- **D3 FEAT-79 (Classic look inside collections).** A plain Classic rows page reusing `CatalogRowView` is M; matching Classic Home's pinned hero/row anchoring is L. **Recommend: next batch (H), plain version**, so rc8 stays a fix build.
- **D4 FEAT-80 rail.** **Recommend: a "Rail Position" setting (Centre / Top), default Centre, plus "Rail Labels" (Shown / Icons Only), default Shown.** Alternative: move the rail to the top for everyone.
- **D5 External players.** No player gets language preferences today; only the stream's own subtitles are passed (`StreamPickerView.swift:1066-1083`). **Recommend: also pass the fetched add-on subtitles, ordered by the preferred subtitle language**, in this batch. Audio language can't be passed: none of Infuse, SenPlayer or Native Player documents a parameter for it.

## Items

### Wave 1: picker and loading (StreamPickerView, FirstPlayAutoPlay, PlayerScreen, PlayerLoadingOverlay)

- **G1 BUG-174 back lands on the stream list (P2, S–M).** The player is a second `.fullScreenCover` on top of the picker's cover; on close the picker stays unless `dismissAfterPlayer`. Per D1: close the picker on every player close and after an external hand-off opens; keep it only when a failure alert/failover list is queued. Up Next (`onPlayNext`, `:481`) inherits the rule. Close both covers in one non-animated transaction so the list never flashes on the way out (cause (c) in the survey).
- **G2 BUG-183 list flashes ~1 s with auto-select (P3, S).** Gap 1: the overlay waits for `arm()` in `.onAppear` (`:446-450`), so the cover presents over the bare list. Gap 2: `succeed()` sets `.done`, hiding the overlay before the player cover is up. Fix: decide auto-armed in `init` (sync read like `PlayerLoadingOverlaySetting`) and show the overlay from frame one; keep it up through `.done` while a player is being presented. Render the same `PlayerLoadingOverlay` look in the picker so picker → player reads as one screen.
- **G3 BUG-182 pulse restarts each step (P4, S).** Up to three overlay instances swap (picker's `FirstPlayAutoPlayOverlay`, `PlayerScreen` `.deciding`, then the engine's own), each with its own `@State pulse`. Fix: drive the scale from a shared clock (`TimelineView(.animation)`, phase from a start time per playback context) so swaps are invisible; drop the per-instance opacity transition on swaps. Remove the status `Text` per D2 (keep `accessibilityValue` for the UI tests).
- **G4 external subtitles (S–M, D5).** Add `SubtitleRepository`'s add-on subtitles to the external request, preferred language first. Infuse/SenPlayer/Native Player builders already accept several `sub=` (`ExternalPlayerPlatform.apple.kt`).

### Wave 2: mpv player (MPVPlayerView, Player/*)

- **G5 BUG-180 film ~10 fps behind open menus (P2, M).** Ranked cause: live `.glassEffect` + `.shadow` over the Metal video layer (top panel `PlayerTopPanel.swift:91-94`, pause card, stream info card, chips, transport pills) recomputed every video frame at 4K/HDR, with `vulkan-swap-mode=fifo` stalling mpv on the slow compositor. Fix: a player-only solid/translucent fill (`PlayerSurfaceStyle`) in those six places, shadows dropped. Plus: refresh stream info only while the Info tab is shown; narrow `MPVPlaybackTab`'s observation; gate the seek-preview harvest and thumbnail pre-warm on `!panelOpen && !controlsVisible`. Measure with `[MPVStats] frame-drop-count` on a DV file, panel open, before/after.
- **G6 BUG-181 empty thumbnail box on DV (P3, S).** Decode refuses DV P5 (`KeyframeThumbnailer.swift:395-397`), so DV only has harvested frames, and `match(near:)` returns nil past its tolerance, which hides the card body. Fix: nearest-frame fallback with no distance limit, keep the last frame during a lookup (clear only when the scrub ends), and a solid placeholder card instead of an empty slot. Prefetch around the playhead is a follow-up (M). Atmos stays FEAT-75 (separate).

### Wave 3: Detail and Home rows (DetailView, EpisodesSection, TrailerThumbnail, PersonDetailView, HomeView)

- **G7 BUG-177 no ring/depth on trailers, episodes, season posters (P3, M).** All three use `tileFocusLift` + `lift: .plain`, which never reads the ring setting (the documented BUG-104 follow-up, `PosterCard.swift:160-164`), and none passes `railTint`; the trailer's 0.2 scrim and the season stroke sit over the depth layer. Fix: port CastCard's ring architecture (`PlainLabelRing` band + overlay, `CardArtworkFocusLift`, `CardCaptionFocusDrop`), default card button style, `railTint` sampling like FolderTile, overlays moved under the depth layer, focused-card zIndex. Extend `PlainLabelRingTests`.
- **G8 BUG-178 shadow moves up with the page (P3, S, device A/B).** No app scrim scrolls with content. Likely the tvOS 26 system top scroll-edge effect on Detail's vertical ScrollView (Home already opts out, `HomeView.swift:3219`). Fix: `.scrollEdgeEffectHidden(true, for: .top)` on Detail; second suspect `DetailTopScrim` is on/off at 0.96 black, so ramp its opacity with the dim. Try both on the TV; ask Steven for the video if neither matches.
- **G9 BUG-179 actor biography cut off (P3, S).** `PersonDetailView.swift:83-92` is `lineLimit(8)` in an inert focusable block. Fix: Select opens `DetailSynopsisSheet(title: name, logoURL: nil, overview: bio)`, with the ⌄ when truncated, keeping BUG-34's focus anchoring.
- **G10 BUG-175 Continue Watching card under its neighbour (P3, S).** `ContinueWatchingRow` (`HomeView.swift:5243-5285`) has no `.zIndex`; Batch F only fixed catalog rows. One fix covers Classic and Stage. Same check for `UpcomingRow`.

### Wave 4: Stage Home and rail (StageController, StripPager, UncoverRestorePolicy, NavigationRail, AppearanceSettingsPane)

- **G11 BUG-176 collection → Home takes two moves on Stage (P3, M).** Two candidates: (1) the 1.5 s uncover gate disables other rows and the passive input clock sees the press after the engine moved, so the first press goes nowhere; (2) the page hold only starts once the pager re-installs its handle, so the strip pages away and back. Fix: arm the hold from `restoreAfterUncover` time; replace the `.disabled` gate with a redirect or open it on press-began. Confirm with the `[StageStrip] restore …` / `page held` lines on the TV before and after.
- **G12 FEAT-80 rail position + icons only (P4, M).** Per D4: Rail Position (Centre/Top; `.leading` → `.topLeading` + top inset in `NavigationRail.swift:359/376`) and Rail Labels (no `Text`, width stays `collapsedWidth`, accessibility labels kept). Two rows in Appearance › Navigation, shown in Rail mode; strings in the catalog.

### Next batch (H)
- FEAT-79 Classic rows page for folders (D3).
- Thumbnail prefetch near the playhead (G6 follow-up), FEAT-75 Atmos.

## Order and gates
Waves 1–4 touch separate files, so they can run as parallel agents (≤ 3 at a time, no concurrent builds). Gates: NuvioTVTests, Debug + Release, the Stage/Detail/player UI legs touched, one Opus review round (Codex quota until 10-29). Device pass in Test 2: G1/G2/G3 with auto-select on and off and an external player; G5 frame drops with the panel open on a DV file; G6 scrub on DV; G7 ring on/off; G8 scroll up on a long Detail page; G9 a long biography; G10 Classic CW; G11 collection → Home on Stage, five times; G12 both settings.

Release notes must name the new settings (Rail Position, Rail Labels) and their defaults, and say Back from a player now returns to the page you started from.
