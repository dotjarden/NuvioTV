# Upstream port plan, 2026-10-08

Upstream NuvioMedia/NuvioMobile `cmp-rewrite`: `b8801eb4` (0.5.7-beta) -> `78e6373a` (0.5.8-beta, build bump).
~40 commits incl. merges. **Zero files changed under `shared/`** (upstream keeps these features in `composeApp/commonMain`; the fork's equivalents live in `NuvioMobile/shared/`, so every port below is a hand-port into shared/ + Swift wiring, not a cherry-pick).
Run `git -C NuvioMobile fetch upstream` first (already fetched by this run; tags 0.5.7-beta, 0.5.8-beta present).

## Action items

### 1. [MEDIUM, mechanical shared + small UI] MDBList: sort library lists by release date (upstream d8ce7258, port of NuvioTV#3881)
Fork has none of it (no `RELEASED_*`, no `releaseDate` in shared/). Files (upstream composeApp paths -> fork shared/ equivalents):
- `library/LibraryDisplaySettings.kt`: add `LibrarySortOption.RELEASED_DESC/RELEASED_ASC`; `availableLibrarySortOptions` offers them only for `LibrarySourceMode.MDBLIST`; `effectiveLibrarySortOption` falls back (remote tracking -> DEFAULT, else ADDED_DESC) when the selected option is unavailable; new `libraryReleaseYear()` regex fallback; MDBLIST DEFAULT sort now uses the generic listRanks comparator (provider order).
- `library/LibraryProviderOrders.kt`: `observeLibraryProviderOrders` dispatches RELEASED_* to new `sorter.observeReleaseOrder(key, descending)`. Add that method to the `TrackingLibrarySorter` interface (check the fork's other implementers: Trakt/Simkl).
- `library/LibrarySavedContent.kt` (+4 lines).
- `mdblist/MdbListLibraryDecoder.kt`: parse `releaseDate = row.text("release_date","released")`; `MdbListLibraryModels.kt`: `releaseDate` field + snapshot `itemsOrder`/`MDBLIST_ITEMS_ORDER`; `MdbListLibraryProjection.kt`, `MdbListLibraryService.kt` small edits.
- `mdblist/MdbListLibraryRemote.kt`: `items(key, sort, order)` now requests list items WITHOUT a sort (MDBList returns owner's saved order) and `synchronize(..., reloadItems)` re-downloads cached lists once when `itemsOrder` changed, and on manual refresh.
- `mdblist/MdbListLibrarySorter.kt`: `RELEASED_ORDER_KEY`, `observeReleaseOrder`, shared `observeOrder`, `oldestFirst()` direction check.
- Upstream also refactored MDBList HTTP into `core/network/ApiHttpClient.kt` (`createApiHttpClient`, `readBoundedResponseBody`). Do NOT port that refactor; keep the fork's `MdbListNetworkEngine`.
- tvOS: add "Recently released / Oldest released" to the Library sort picker only when source = MDBList (`LibraryView.swift` / `LibraryViewModel.swift`); EN strings only. Port upstream tests if present in `composeApp/src/commonTest` (`git show d8ce7258 --stat`).
Gate: jvm + K/N tests, NuvioTVTests, device check: MDBList list, sort Recently released, then Oldest released, pull-to-refresh picks up an owner-side sort change.

### 2. [LOW-MED, mechanical, shared + a Swift decision] Streams that only carry `ytId` (upstream 94976222, PR #2115)
Addons may return `{ "ytId": "..." }` only. Upstream now parses and plays them; fork's `shared/.../streams` does not know `ytId` (only trailer code touches YouTube), so such streams are silently dropped by the parser (`url == null && infoHash == null ...`).
- `StreamModels.kt`: `ytId: String?`, computed `youTubeIdToResolve` (only when url/externalUrl/infoHash/clientResolve all empty), include `ytId != null` in the "playable" getter.
- `StreamParser.kt`: read `ytId`, keep stream when only ytId present. Port `StreamParserTest` + `StreamYouTubeTest` additions.
- Resolution: upstream's `YouTubeStreamResolver` calls `TrailerPlaybackResolver.resolveSingleUrlFromYouTubeUrl` (new, returns the HLS **master playlist** URL instead of best variant). tvOS already has its own trailer extraction (`TrailerLocalHLS.swift`, `DetailViewModel.swift`). Decision for Claude Code: reuse the tvOS trailer extractor to turn `ytId` into a playable URL in the stream-pick path (preferred), or fall back to opening the watch URL externally if extraction fails. Show "Could not load this YouTube video." on failure.
Priority is low unless a real addon in use emits ytId-only streams.

### 3. [LOW, opportunistic] `AddonManifest.supportsResource(name, type, id)` helper (AddonModels.kt, +7 lines)
Pure helper added for the servers feature; port only if item 1/2 or later work needs it. Nothing live depends on it.

## Not applicable / backlog

- **Media servers (Jellyfin + Emby)**: PR #2081 `feat/servers`, ~25 commits, ~3,500 new lines in `composeApp/.../features/servers/*` (`MediaBrowserClient/Provider/Mapper`, `ServerRepository`, `ServerMatcher`, `ServerPlayback`, `ServerWatched`, `ServerSync`, `core/sync/MediaServerSync.kt`), library browse of server libraries, server streams in the picker, watch-progress import toggle, transcoding rules (avoid transcode for high-bitrate/HEVC, burn-in image subtitles), stream info "play method", home/search integration. **None of it is in shared/**, so tvOS gets nothing for free. This is a product call for Christian, not scheduled work: it overlaps `docs/orivio-feature-comparison-2026-10-01.md` item 2 (Plex/Jellyfin, marked Missing). If wanted, the clean route is: extract `features/servers/mediabrowser/*` + models + sync into `shared/` (they look platform-neutral Ktor + kotlinx), then build tvOS Settings > Servers, Library tab, and a stream-picker section in SwiftUI. Treat as a multi-batch epic; start with a plan doc. Note the one hook already needed if servers are ever ported: `CustomPosterUrlResolver.resolve()` returns null for server item ids (`ServerItemRef.isServerId`).
- ExoPlayer native memory / VOD cache / buffer settings (PR #2178, 36228818 and 6 follow-ups), settings kept on-device (394cd0bf): Android only. N/A (AVPlayer). Optional idea from 10-07 still stands.
- `278886e1` reset `nextEpisodePreloadTriggered` flag: composeApp player state. N/A (tvOS has its own `NextEpisodeAutoPlay.swift`; worth a glance only if preload-on-next-episode was ever ported).
- Hero fixes (500a8a81 tablet/phone alignment, 796e715c hero content shift): Compose only. N/A.
- Croatian language (d8607e40, daade43b, 1993c211), store publish, version bump 0.5.8 / store.json: tvOS English-only, versions independently. N/A.

## Claude Code next steps
1. `git -C NuvioMobile fetch upstream && git -C NuvioMobile show d8ce7258` and implement item 1 on a branch off `tvos-shared-extraction`.
2. Optionally item 2.
3. Servers epic: only on Christian's go.
