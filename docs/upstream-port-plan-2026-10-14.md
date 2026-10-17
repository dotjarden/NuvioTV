# Upstream port plan — 2026-10-14

Upstream `NuvioMedia/NuvioMobile` (cmp-rewrite): `dac3f3141` -> `779c145a5` (0.5.10-beta, ~25 commits). Changes land in `composeApp/commonMain` (not `shared/`) plus iosApp PiP/MPVKit. Several touch logic the fork already keeps in `shared/` or mirrors in Swift.

## Recommended ports (all small)

1. **LOW-MED — restore dismissed Continue Watching shows when marking episodes watched** (upstream 6fefbcdab, PR #2244). Fork's `shared/` has the same gap.
   - `shared/.../features/watched/WatchedRepository.kt` `markWatched(items: Collection<WatchedItem>)` (~line 767): before delegating, `items.filter { it.isEpisode }.map { it.id }.distinct().forEach { ContinueWatchingPreferencesRepository.removeDismissedNextUpKeysForContent(it) }` (+ import).
   - `shared/.../watchprogress/ContinueWatchingPreferencesRepository.kt` `removeDismissedNextUpKeysForContent` (~line 168): filter `it == normalizedContentId || it.startsWith(prefix)`.
   - Add tests in `shared/src/commonTest/.../WatchedRepositoryTest.kt`. Verify the tvOS "mark episode/season watched" path goes through this overload.
2. **LOW — next-episode preload/heuristic post-credits timing** (upstream c27c92fa2). Logic is in composeApp upstream; the fork mirrors it in Swift: `iosApp/NuvioTV/Screens/NextEpisodeAutoPlay.swift` (~lines 400-440, `preloadNextEpisodeStreams`) and `Player/SkipSegmentPlanner.swift`.
   - Preload also fires when `duration - position <= preloadLead` (not only via card threshold).
   - For post-credits scenes with provider `"heuristic"`: if scene duration < (duration - userThresholdMs) -> don't show card; else show at `position >= userThreshold` (ignore scene end). Non-heuristic unchanged (`max(sceneEnd, userThreshold)`). Add cases to `SkipSegmentPlannerTests.swift`.
3. **LOW — CustomPosterUrlResolver perf rewrite** (upstream bdbe5388c, PR #2239): single-pass token scanner + 32-entry prepared-pattern cache instead of per-call regex. Fork file: `shared/.../core/poster/CustomPosterUrlResolver.kt`. CAUTION: upstream now returns the pattern unchanged when it has no placeholders; the fork deliberately returns `null` (port of 6ce99ef2) — keep fork behavior and keep `CustomPosterUrlResolverTest` green. Only worth it if poster rows stutter on tvOS.
4. **LOW (optional) — localize generic "Episode N" titles** (upstream 4ff0deb02..885cb2f30). Upstream added `localizedEpisodeTitle` (composeApp i18n). Only relevant if tvOS shows non-English UI for Continue Watching subtitles; would need a tvOS Swift equivalent. Skip unless localization is in scope.

## Not applicable
- iOS Picture-in-Picture via MPV VideoToolbox frames (PR #2248, `PlayerPictureInPictureController.swift`, MPVKit pin bump, MetalLayer/ContentView): iPhone/iPad; no tvOS PiP.
- Version bump 0.5.10-beta, store.json, test-isolation fixes (androidHostTest), TL;DR poster settings page tweak.

## Open items carried (unchanged)
- 10-10 TorBox mylist pagination (MEDIUM, upstream be81802c8) — shared/.../debrid/DebridApiClients.kt + TorboxCloudLibraryProviderApiTest
- 10-08 MDBList sort by release date (MEDIUM, d8ce7258); ytId-only addon streams (LOW-MED, 94976222)
- 10-13 subtitle AutoSync: recommend NOT porting (HIGH effort).
- Jellyfin/Emby servers: only if adopted.

## Claude Code prompt
"Read docs/upstream-port-plan-2026-10-14.md. Do item 1 (dismissed Continue Watching restore) with tests, then the open 10-10 TorBox pagination and 10-08 MDBList sort. Items 2-4 are optional."
