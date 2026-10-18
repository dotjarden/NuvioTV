# Upstream port plan — 2026-10-16

Upstream `NuvioMedia/NuvioMobile` (cmp-rewrite): `779c145a5` -> `63afb73c0` (**0.6.0-beta**, ~70 commits incl. merges, 114 files). 0 changes under `shared/` (all in `composeApp/commonMain`, `iosApp`, `androidApp`), but the MDBList code lives in `shared/` in the fork, so it ports there.

## Recommended ports

1. **MEDIUM — MDBList external, dynamic and liked lists in the library** (upstream 3913a140b/78be01c11 PR #2172 external; 2cc2e6a61/17d3c6308 PR #2268 dynamic+liked). Confirmed NOT in fork (`grep MdbListDynamicList|MdbListLikedList|MDBLIST_EXTERNAL_LIST_KEY_PREFIX shared/` = none).
   Source: `git -C NuvioMobile diff 779c145a5 upstream/cmp-rewrite -- composeApp/src/commonMain/kotlin/com/nuvio/app/features/mdblist composeApp/src/commonTest/kotlin/com/nuvio/app/features/mdblist`
   Apply to fork `shared/src/commonMain/kotlin/com/nuvio/app/features/mdblist/` (same filenames):
   - `MdbListLibraryModels.kt`: key prefixes `mdblist:external:/dynamic:/liked:`, `MdbListReadOnlyList` interface, data classes `MdbListDynamicList`/`MdbListExternalList`/`MdbListLikedList` (tab() = `TrackingLibraryTabKind.EXTERNAL`, `isMembershipDestination=false`), snapshot fields `externalLists`/`dynamicLists`/`likedLists`, `tabs()` appends them, `mdbListSupportedContentTypes()` helper. Check the fork's `TrackingLibraryTabKind.EXTERNAL` / `isMembershipDestination` exist; add if not.
   - `MdbListLibraryDecoder.kt`: `mdbListUserListId`, `decodeMdbListDynamicLists`, `decodeMdbListLikedLists`, `decodeMdbListExternalLists`, `mdbListListedAt` date-only fallback (needs `kotlin.time.Instant`).
   - `MdbListLibraryRemote.kt`: sync dynamic lists from the `/lists/user` response, `synchronizeOptional()` for `/external/lists/user` and paged `/lists/liked` (keeps cached copy on failure, rethrows rate-limit `retryAtEpochMs`), `cachedOrFetched()`, new `mdbListLibraryItemsPath` branches, `isMdbListReadOnlyListKey`.
   - `MdbListLibraryWriter.kt`: skip read-only keys in `applyMembershipChanges`.
   - Tests: copy upstream changes to `MdbListLibraryDecoderTest`, `MdbListLibraryServiceTest`, `MdbListLibrarySorterTest` (request count 4 -> 6; `MDBLIST_EMPTY_LIKED_LISTS` fixture in `MdbListLibraryTestFixtures`). Fork tests are in `shared/src/commonTest/.../mdblist/`; adapt paths.
   - tvOS UI: tabs flow automatically from `visibleTabs()`. Check `iosApp/NuvioTV/Screens/Settings/MdbListLibraryListsView.swift` (+ `NuvioTVTests/MdbListLibraryListsPolicyTests.swift`) so the hide/show list UI includes the new list kinds and never offers add/remove-to-list for them (membership picker must exclude `isMembershipDestination == false`).
   - Gate: shared Kotlin tests + SharedCore framework rebuild + tvOS build. Same sort/hide code as the open 10-08 MDBList sort item, so do them together.

## Product decision (Christian)
2. **Watch Party (experimental)** — new upstream feature, ~20 commits, ~5k lines in `composeApp/.../features/party/*` (Supabase Realtime channel, host-controlled sync, `nuvio.tv/party/<code>` links, server `watch_party` capability, Settings entry, PlayerScreenRuntimeParty, stream-source sharing). Nothing in fork. Needs a Realtime client in `shared/` (supabase-kt `Realtime`, `RealtimeSocketFactory` heartbeat fix, `SupabaseEndpointConfig.realtimeUrl`), party models/repository/sync moved from composeApp to `shared/`, then a SwiftUI party screen, deep-link handling and AVPlayer/MPV sync hooks. HIGH effort; upstream labels it experimental. Recommend: do NOT port yet; revisit when it leaves beta.

## Not applicable
- iOS PiP placeholder + handoff (#2259), CallKit-aware audio session (#2246; no CallKit on tvOS), Android audio focus / LinkActivity, nuvio engine 0.1.5 AAR (Android), 0.6.0-beta bump + store.json, Italian/pt-BR/Greek/PiP i18n strings.

## Open items carried
- 10-10 TorBox mylist pagination (MEDIUM, be81802c8) — `shared/.../debrid/DebridApiClients.kt` still unpaged.
- 10-08 MDBList sort by release date (MEDIUM, d8ce7258); ytId-only addon streams (LOW-MED, 94976222).
- 10-14 optional LOW: next-episode preload/heuristic post-credits, poster-resolver perf, Episode N i18n. Restore-dismissed-CW: fork already calls `removeDismissedNextUpKeysForContent` in `WatchProgressRepository`; verify the `WatchedRepository.markWatched` path before closing.
- 10-13 subtitle AutoSync: do not port. Jellyfin/Emby servers: only if adopted.
