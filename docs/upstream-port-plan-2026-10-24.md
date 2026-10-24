# Upstream port plan — 2026-10-24

Upstream `NuvioMedia/NuvioMobile` (cmp-rewrite): `e6c399e01` (last plan 2026-10-23) -> `c114d6fb6` (0.6.4-beta, build 147). 59 commits in range, ~46 non-merge. **0 changes under `shared/`**; the rest is `composeApp/commonMain`, `iosApp/iosApp` (Duo/foldable layout), string resources, deps. Fork tip checked: submodule `888961236`, outer `b23992a`.
**New baseline: `c114d6fb6`.**

## Recommended ports

1. **LOW — Trakt "failed request keeps Continue Watching" (2e79b3df9): ALREADY IN THE FORK.** `shared/.../trakt/TraktProgressRepository.kt` already fails the whole history fetch on a failed page (line ~759), keeps the hidden set on a failed dropped-shows fetch (~394), and clears the activity fingerprint on a failed playback request (~359), the same three behaviours upstream describes. Only gap: upstream's new `TraktProgressPagingTest.kt` (137 lines); the fork has `TraktProgressFetchFailureTest.kt`. Diff the two test files and add any missing case. Effort: ~20 min.

2. **LOW — compile badge rules once per change** (a0735005d, `StreamBadgePresentation.kt` +20, test +36). Fork has `shared/.../streams/StreamBadgePresentation.kt`; apply the cached-compiled-filters pattern (`SynchronizedObject` + `cachedRules`/`cachedFilters`) and the test. Pure `shared/`. Effort: ~30 min. Ride with the badges port if that is scheduled.

3. **LOW — debrid stream filter regex cache and single facts pass** (def203a96: `DebridStreamFormatter.kt`, `DebridStreamPresentation.kt`, test +43). Fork has both files with per-call `Regex(...)` at `DebridStreamPresentation.kt:387-389, 471-474`. Port the cache and the "compute facts once, reuse for filter then format" change. Pure `shared/`. Effort: ~45 min. Perf only, no new setting.

4. **LOW-MED — ratings and age rating on the Home hero** (d90467754, 90ab7f95d IMDb logo + grey label). New `HomeHeroMetaRepository` (162 lines) + `HomeHeroMetaRows` (Compose UI) + `showOnHero` flag in `MdbListSettings` (default **false**, "Use Ratings on Hero", setting row on the MDBList page) + `HomeCatalogParser` hunk + 3 tests. The repository/parser/setting are Compose-free and port to `shared/`; the rows are Compose and need a SwiftUI version on the Stage hero (`iosApp/NuvioTV/Screens/Home/`). Overlaps the Stage hero compression rules: check hero height budget first. New setting `showOnHero`, default Off: name it in release notes. Effort: ~3 h. Optional; only if wanted.

5. **LOW — mpv/libass/Duo/iOS layout work: N/A** (see below). **Optional: `nuvio engine 0.1.6` (c114d6fb6, `scripts/prepare-ios-dependencies.sh`)**: torrent/P2P engine bump. The fork does not bundle the Nuvio torrent engine (verify with `grep -rn engine_version NuvioMobile/scripts`); skip unless it does. Effort: 0 or ~15 min.

## Not applicable / skip
- Duo/foldable side-bar layout (36f3de689, faf51671d, 9599faff1, 668556068, 350cd4373, d1369a5e3, f9d3b3a57, 3797b9832, 8683505d2 tablet ratings anim, `VerticalBar.kt`, `ContentView.swift`): iPhone/iPad Duo only.
- libass atlas pipeline, default-on, AAR v0.0.5-0.0.7, render-scale setting, render-type string removal (da1e876ee, f439f1825, 684edefba, 7652cec7f, 126dc3e3c, 417b06705, ab5eeb2fd): Android renderer; tvOS uses mpv.
- Compose Multiplatform 1.13 beta, haze 1.7.3, Xcode 27.1 CI, version bumps, store.json publish: composeApp/CI only.
- "Remove source name from paused player" (c85dc7214, 1 string + `PlayerControls.kt`/`PlayerTimeline.kt`): check whether the tvOS paused overlay shows the source name; if it does and Christian wants parity, ~15 min, otherwise skip.
- Translation commits (el, es, hu, pt, vi, party/player badges strings): fork localisation is the xcstrings pipeline; revisit only when player badges port.

## Open items carried
- 10-21/22: player badges for what is playing + badge-pack choice (LOW-MED, ~3-4 h, new `showInPlayer` setting; items 2 and the Android badge-decode perf fold in); mpv `hwdec-software-fallback=300` (LOW, ~15 min, `iosApp/NuvioTV/Screens/MPVPlayerView.swift:941`); custom posters in Library/Collections (LOW, verify first); Watch Party chat deferred.
- 10-16 MDBList external/dynamic/liked lists (MEDIUM); 10-10 TorBox mylist pagination (MEDIUM); 10-08 MDBList sort by release date (MEDIUM); ytId-only addon streams (LOW-MED); 10-19 localized Simkl status titles (LOW). Subtitle AutoSync: do not port.
- Goal still paused until the beta.19 watch ends 10-25.

## NuvioTV Android
Moved: `b700cf98e` -> `b36db8083` (17 non-merge commits). Plan: `docs/nuviotv-android-upstream-port-plan-2026-10-24.md`.
