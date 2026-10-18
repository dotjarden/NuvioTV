# NuvioTV (Android TV) upstream → tvOS port plan — 2026-10-17

Upstream: `NuvioMedia/NuvioTV` (Kotlin/Compose TV), HEAD `f7e2a78ad` (2026-10-16, PR #4071).
Baseline: `d0ecc1dd` (2026-07-03), the date of `docs/nuviotv-android-feature-gap.md`.
Window: 2,213 commits (1,478 non-merge) since the baseline. I read the full non-merge subject list and ~25 diffs.
Coverage of the tvOS side was checked with greps over `NuvioMobile/iosApp/NuvioTV`, `NuvioMobile/shared/src`, `docs/` and `CLAUDE.md`. It is NOT an exhaustive audit. Every item below starts with a "verify first" step for that reason.

This is separate from the daily NuvioMobile check (`docs/upstream-port-plan-*.md`). The open items there (MDBList lists/sort, TorBox pagination, ytId streams) are not repeated here.

## Headline
The tvOS fork already has most of what Android TV shipped since July: Simkl, MDBList ratings/lists/accounts, episode shuffle, global landscape posters, IntroDB, binge-group reuse, post-credits/next-episode preload, stream info overlay, pause overlay, subtitle delay/sidebar, Top Shelf, custom posters, cast bios, sign-out confirm, library watched filter. Only the small items in A and decisions in B are left.

## A. Recommended ports (execute with Claude Code)

### A1. LOW (S): subtitle language aliases — upstream `2a54e8cbe`, `d34a5025d`
- Fork file: `NuvioMobile/shared/src/commonMain/kotlin/com/nuvio/app/features/player/PlayerSubtitleMatching.kt` (language override map near line 45 already has `"spa"`, `"spl"`).
- Add `"spn" -> es`, `"sp" -> es`, `"esp" -> es` (OpenSubtitles Spanish-EU codes).
- Add HBS handling: if the label contains `hbs`, strip it and resolve the remainder via the override map, so Serbian/Croatian/Bosnian are not lumped into one group.
- Tests: extend `PlayerSubtitleMatching*Test` (see `PlayerSubtitleMatchingIndonesianTest.kt`). Upstream tests are in `PlayerSubtitleUtilsMimeTest.kt`.
- Gate: shared Kotlin tests, then SharedCore framework rebuild.

### A2. MEDIUM (M): binge-group selection by filename — upstream `953938c72`, `ac8d5275c`, `b0ca75514`, `d293973bd`, `2c5554ecf`
- Upstream added `core/player/FilenameEpisodeMatcher.kt` (155 lines). It stores `behaviorHints.filename` on the binge-group cache entry, including after manual stream selection. It also does an early binge-group match with reuseBingeGroup that ignores source filters, and it skips that match if autoplay was already handled.
- Verify first: the fork has `reuseBingeGroup` (CLAUDE.md, 2026-09-12 note) but `grep FilenameEpisodeMatcher` finds nothing. Check what happens when the next episode's stream list has no identical bingeGroup but has a filename with the right SxxExx.
- Port `FilenameEpisodeMatcher` into `shared/.../streams` or `.../player`, with tests. Wire it where the fork picks the next-episode stream (`iosApp/NuvioTV/Screens/NextEpisodeAutoPlay.swift`, `StreamPickerView.swift`, and the shared auto-play selector). Persist the filename on manual selection.
- Source: `git -C <NuvioTV clone> show 953938c72 ac8d5275c b0ca75514 d293973bd 2c5554ecf`.

### A3. MEDIUM (S–M): Trakt progress resilience — upstream `befc72857`, `8905c1c0c`, `3a871400d`
- `befc72857`: a failed Trakt progress request must not wipe Continue Watching (keep the last good list). Has a 140-line failure test to copy.
- `8905c1c0c` and `3a871400d` are performance only: skip redundant refreshes after watch actions, and recheck playback once after the force window. Optional.
- Verify first: read the fork's Trakt progress path (`shared/.../trakt/TraktLibraryRepository.kt`, `watching/sync/TraktWatchedSyncAdapter.kt`, `WatchProgressRepository`). Check whether a failed fetch clears or replaces the cached CW list. Port only if it does.

### A4. MEDIUM (S): do not push profile settings on profile switch — upstream `82661599a`
- Data-loss class bug: after a profile switch, the first emitted settings signature was pushed to the cloud and could overwrite newer cloud settings. Fix: tag the signature with the profile id, `distinctUntilChanged().drop(1)`, and push for the profile the change was made on.
- Verify first: find the fork's equivalent of Android's `ProfileSettingsSyncService` (grep `shared/src` for profile settings blob / push-on-change). If tvOS has no debounced auto-push of profile settings, close this item as N/A.

### A5. LOW (S): JS plugin declared series type — upstream `8b60bdfe1`
- `PluginMediaType.kt` plus a 33-line test: episodic JS plugins lost their declared `series` type. The fork has JS plugins (QuickJS).
- Verify first: check how the fork maps the plugin's declared type for series requests, then port the 1-line fix and test if affected.

### A6. LOW (S): shuffled-series reload after profile switch — upstream `7c525627d`/`61dbbf888`
- `EpisodeShuffle.kt`: only reset the selection on a newer visit, and keep the previous selection on the HOME surface when the picker can't find it, so shuffle doesn't reroll repeatedly while CW loads.
- Verify first: compare with the fork's `shared/.../shuffle/` session logic.

### A7. LOW (S): Top Shelf should use custom posters — upstream `228820681`
- Android applies custom poster overrides to TV recommendations. The fork has `CustomPostersSettingsView` and a `NuvioTopShelf` extension, but nothing links them.
- Verify first: read `NuvioTopShelf` and how it picks artwork. If custom posters aren't applied, resolve the override in the shared snapshot written for the extension (App Group).

### A8. LOW (S): confirm before removing an add-on — upstream `f010e2a13`
- No confirm dialog found in the fork's add-on settings. Add a SwiftUI confirmation (tvOS `confirmationDialog`/`alert`) with a destructive Remove. Verify first by grepping the add-on remove action in `iosApp/NuvioTV/Screens/Settings`.

### A9. LOW (S, optional): 4K Trailers toggle — upstream `e08d5616a`
- Android replaced a fixed RAM cap with a "4K Trailers" setting. Only relevant if trailer decode quality/memory is a tvOS issue (open BUG-128 trailer hang, BUG-130). Park unless trailers show memory or stutter problems on Apple TV HD.

### A10. LOW (S, optional): HLS/DASH proxyHeaders — upstream `01df9ed1f`, `19b391018`, `6cd7fcca7`, `be226bf6c`
- Android bug: custom `proxyHeaders` were dropped on child HLS/DASH requests. For tvOS, verify that headers set via `AVURLAssetHTTPHeaderFieldsKey` / mpv `http-header-fields` apply to variant playlists and segments for streams with `behaviorHints.proxyHeaders`. Device test needed.

### A11. TRIVIAL: episode rating color
- `7c4c5ea44`: episodes rated 9.7+ get `#1DA1F3` in the ratings section. Only if the fork shows an episode ratings grid.

## B. Product decisions (Christian), not recommended to build now
- **Watch Party (experimental)** — about 20 commits since 2026-10-13 (`b38c9971d` realtime, `e1faa00ed` sync, `a574b34e7` page, `4688b7e8b` player sync, `628ad8dae` catch-up, `834052420` preview, `92ec8d87d` QR). Needs a Supabase Realtime client, party models, deep links and AVPlayer/mpv sync. Large (L). Upstream still labels it experimental (`6a9d63631`). Recommend defer; same call as `upstream-port-plan-2026-10-16.md`.
- **Jellyfin / Emby media servers** (`af0107e89` through `10ab19892`, about 14 commits, settings sync, library browse, play, watched sync). XL; already parked in the master plan (U3). Revisit only if users ask.
- **Ambient Mode idle slideshow** (`17021b206`, `a86aea0ae`). tvOS has the system screen saver and Top Shelf; skip unless asked.
- **Episode options overlay redesign** (`baaf35709`, `707648dea`, `f98eef026`, `f555e468b`: still backdrop, appearance options, left/right to step episodes). The fork has its own detail design; take ideas only if you revisit the episode context menu.
- **Movie post-play recommendations** (`5a3a80edb`, `d9c47309f`, `1c7b5b4db`, `ec8efa8e3`): already planned as P5 B22 "post-play More Like This".

## C. Not applicable to tvOS (do not port)
ExoPlayer/AFR/Dolby Vision/allocator/RGB565/tunneling work; `nuvio engine` torrent AAR; APK updater and update channels; Leanback Watch Next and Android TV channels; Sentry; launcher icon/banner; sidebar and settings-rail UI refactors; Compose perf/baseline-profile work; screen-reader labels (Android a11y; tvOS uses VoiceOver separately); supporter perks and member gradients; locale-only commits (Greek, Italian, Polish, Turkish, Hebrew, Hungarian, Slovak, Spanish); `strings_servers.xml`; HTTP/2 option removal.

## D. How to run this with Claude Code
1. `git -C NuvioMobile checkout -b claude/nuviotv-android-ports tvos-shared-extraction`.
2. Clone upstream for reading: `git clone --filter=blob:none https://github.com/NuvioMedia/NuvioTV.git /tmp/nuviotv-upstream` (then `git -C ... show <sha>`).
3. Do A1 and A4 first (shared Kotlin only, quick tests), then A2 and A3. Group A5–A8 into one small SwiftUI/Kotlin batch.
4. Gate per `CLAUDE.md`: shared Kotlin tests, SharedCore framework rebuild, tvOS build, then a device pass for A2, A7 and A10.
5. After merging, record the new baseline here (`f7e2a78ad`, 2026-10-16) so the next NuvioTV check only reviews newer commits.
