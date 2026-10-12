# Upstream port plan, 2026-10-10

Upstream NuvioMedia/NuvioMobile `cmp-rewrite`: `78e6373a` (0.5.8-beta) -> `612bdaef5` (6 non-merge commits). **Zero files changed under `shared/`**; one real code change in `composeApp/commonMain`, rest are Vietnamese string updates (N/A for tvOS).
Run `git -C NuvioMobile fetch upstream` first.

## Action items

### 1. [RECOMMENDED, MEDIUM, mechanical, shared/ Kotlin only] TorBox cloud library: paginate mylist for large libraries (upstream be81802c8, PR #2215)
Problem: fork's `TorboxApiClient.listCloudTorrents/Usenet/WebDownloads` fetch `/v1/api/{torrents,usenet,webdl}/mylist` in one unpaged request capped at 16 MB (`cloudListResponseMaxBytes`). Big libraries / season packs with large `files` arrays get truncated and the Cloud Library fails to load (used by `TorboxCloudLibraryProviderApi.kt` -> tvOS `CloudLibraryUI.swift`).
Fork file: `NuvioMobile/shared/src/commonMain/kotlin/com/nuvio/app/features/debrid/DebridApiClients.kt` (lines ~123-146). Upstream diff applies by hand (same code, different path `composeApp/...`):
- Replace the three `request(...)` bodies with `listCloudItems(apiKey, "torrents" | "usenet" | "webdl")`.
- Add `private suspend fun listCloudItems(apiKey, kind) = fetchTorboxCloudPages { offset, limit -> request(GET "$BASE_URL/v1/api/$kind/mylist?offset=$offset&limit=$limit", apiKey, maxResponseBodyBytes = cloudListResponseMaxBytes) }`.
- Add top-level `internal suspend fun fetchTorboxCloudPages(fetchPage)`: start offset 0, limit 100; if response is successful and `rawBody.endsWith("\n...[truncated]")` halve limit (min 1, `check(limit > 1)`) and retry; return response on error/`success == false`; accumulate pages; stop when `page.size < limit`, returning `response.copy(body = envelope.copy(data = items), rawBody = "")`; else `offset += page.size`.
- Update the stale comment above `cloudListResponseMaxBytes` ("Keep each page bounded; season packs can contain large file arrays.").
- Do NOT touch `getTorrent` (single id lookup).
Tests: extend fork's `shared/src/commonTest/.../features/cloud/TorboxCloudLibraryProviderApiTest.kt` (and `TorboxCloudLibraryFixtures.kt`) with: multi-page merge, final short page terminates, truncated-body halves limit and retries, API error not retried. Then run the shared Kotlin tests, then a tvOS build; no Swift changes expected.
Verify on device: Cloud Library with a TorBox account having >100 items loads fully.

## Not applicable
- Vietnamese string updates (bbda7e85f, 2aac7e1b4, e584679d6, d491bff32, ea972a466) and merge commits: tvOS uses its own localization; skip.

## Carry-over (still open from 2026-10-08, see docs/upstream-port-plan-2026-10-08.md)
- MEDIUM: MDBList library sort by release date (upstream d8ce7258).
- LOW-MED: ytId-only addon streams (upstream 94976222) via tvOS trailer extractor.
- Product call: Jellyfin/Emby media servers (upstream PR #2081).
