# Batch D: upstream ports + SenPlayer (2026-10-15)

**Status: MERGED 2026-10-16 ~01:20 ET on Christian's go ("merge it"): `tvos-shared-extraction` fast-forwarded `975a70109` → `14f5991ce`, pushed; feature branch deleted (local + origin); outer pointer bumped on `main`; clone deleted. NOT cut (rides into rc5), nothing posted.** Branch `claude/batch-d` tip `14f5991ce` (11 commits on `975a70109`), pushed to `origin` as a backup. Master plan `docs/master-plan-2026-10-14.md` §4.3 / §2e. Branch NuvioMobile
`claude/batch-d` off `tvos-shared-extraction` `975a7010` (beta.19-rc4, build 136), built in the clone
`~/Claude/Projects/NuvioMobile-batch-d` (MPVKit symlinked over the gitlink; stage by explicit paths).
Runs beside the player P4 session (its own clone); the two touch disjoint files (this batch: `shared/`
Kotlin, the external-player Swift/plist spots, the stream picker's ytId branch, Library sort labels).

## Scope

| # | Upstream | Item | Spec |
|---|---|---|---|
| U6 | `6fefbcdab` (#2244) | Restore dismissed Continue Watching shows when episodes are marked watched | `WatchedRepository.markWatched(items)` clears the series' dismissed next-up keys; `removeDismissedNextUpKeysForContent` matches the bare id as well as the `id|` prefix. Tests. |
| U7 | `be81802c8` (#2215) | TorBox cloud `mylist` pagination | `listCloudItems` + `fetchTorboxCloudPages` (offset/limit 100, halve the limit on a locally truncated body, stop on a short page). Tests in `shared/commonTest` (the function is `internal` to `shared`; composeApp's `TorboxCloudLibraryProviderApiTest` cannot reach it). |
| U1 | `d8ce7258` | MDBList Recently / Oldest released sorts; owner's saved order as DEFAULT | `LibrarySortOption.RELEASED_DESC/ASC` offered for MDBLIST only; `effectiveLibrarySortOption` falls back when a source does not offer the selected option; items requested without a sort so MDBList returns the saved order; one cached oldest-first release order per list; cached lists re-downloaded once (`itemsOrder`) and on manual refresh. Reconciled with batch 11's newest-first port (`docs/upstream-port-plan-2026-10-01.md`): the newest-first DEFAULT comparator is replaced by the owner's order, as upstream did. tvOS: the Library L1 Sort pill picks the two options up from `availableLibrarySortOptions`; labels "Recently Released" / "Oldest Released". |
| U2 | `94976222` | ytId-only add-on streams | Parser keeps them; `youTubeIdToResolve` only when ytId is the sole source; on select, tvOS resolves the video through the trailer extractor's single-URL mode (HLS master playlist, else progressive) via the new shared `YouTubeStreamResolver`; URL is session-only (no reuse cache, failover memory keyed on the ytId); auto-play excluded by construction (its candidate filters never see a ytId-only stream). |
| FEAT-56 | GitHub youngchris29-art/NuvioTV#5 | SenPlayer as an external player (public promise 2026-10-06) | New `IosExternalPlayerSpec` on the Outplayer/VidHub/Infuse shape (`url`, `position` s, `filename` + `name`, `sub`, `x-success`/`x-error`), `senplayer` in `LSApplicationQueriesSchemes` + the ContentView probe list, a return session like Infuse's so a returned `position` is recorded, `debug.senplayerMethod` bisect knob (`minimal` / `noname`). Decision D8: build + device-verify rather than a binary read; parameter names unverified until then. |

Not in this batch (master plan §2e): U8 next-episode preload timing (nothing to port), U9 poster resolver rewrite (declined), U10 "Episode N" i18n (tvOS English-only), U11 subtitle AutoSync (not portable), U3 Jellyfin/Emby (parked).

## Method

Two execution agents by file ownership (K: `shared/` + `composeApp/src/commonTest`; S: `iosApp/`), no concurrent builds (S held its xcodebuild until K's gradle gates finished), two internal Opus read-only review rounds (Codex is on its usage limit until 10-29), gates jvm + K/N shared tests, composeApp `iosSimulatorArm64Test`, NuvioTVTests, Debug + Release simulator; device pass in the Test 2 profile through the rig (`docs/device-rig-2026-10-15.md`, rig lock `~/.config/nuviotv-device/rig.lock` shared with the P4 session).

## OUTCOME

### Build (2026-10-15 evening, two execution agents)

Kotlin half (agent K), five commits on `975a70109`: `4b3368bfe` U6, `645d6f1e0` U7, `2d8ffff78` U1, `7cab8f4cb` U2 (shared), `62aa87eb8` FEAT-56 (shared). Swift half (agent S), three commits: `09b0da72f` U2 (tvOS), `5f73cb8c6` U1 labels, `fcb62abb4` FEAT-56 (tvOS). Gates on `fcb62abb4`: jvm 1482 / K/N 1500 / composeApp 438 (baselines 1444 / 1462 / 435), NuvioTVTests 1701 / 0 (baseline 1688), Debug + Release simulator green. One K/N-only compile break fixed on the way: Kotlin/Native rejects commas inside backticked test names (upstream's new `MdbListLibrarySorterTest` name carried one; upstream only runs that suite on the JVM).

### Review round 1 (two Opus read-only agents, one per half)

Kotlin half: **1 P1 / 1 P2 / 6 P3.** Swift half: **0 P1 / 6 P2 / 6 P3.** Every P1/P2 fixed; declines below.

| # | Sev | Finding | Fix |
|---|---|---|---|
| K1 | P1 | The fork's `LibraryRepository.pullFromServer` hard-codes `USER_INITIATED`, and U1 maps that intent to `reloadItems = true`: every SyncManager pull (foreground, 15-min timer, profile entry) would re-download every MDBList list (quota exhaustion → 429 blocks ratings/scrobble/library). Upstream had already moved the intent to AUTOMATIC in `c1022e2eb`, never taken by the fork. | Ported `c1022e2eb`: `pullFromServer(profileId, refreshIntent = AUTOMATIC)`, `retryLoadAsync` passes USER_INITIATED, SyncManager on the default; composeApp `LibraryScreen.kt` Retry passes USER_INITIATED. Test: automatic refresh reuses cached lists, manual re-downloads. `ff1f05987` |
| K2 | P2 | tvOS passed `providerOrders: [:]` into the Library projection (the Swift comment claimed mobile did the same; it does not), so Recently/Oldest Released would sort by the 4-digit year only. | Public `LibraryRepository.observeProviderOrder(listKey:sortOption:)` → `Flow<LibraryProviderOrderResult(ranks, failed)>`; the tvOS `LibraryViewModel` watches it per (list, sort) and feeds the ranks in, falling back to DEFAULT on failure as mobile does. |
| K3 | P3 | `YouTubeStreamResolver.resolve` swallowed `CancellationException` as "could not resolve". | Rethrown (K/N delivers it to Swift as an NSError, not an abort); tests. |
| K4 | P3 | `ContinueWatchingPreferencesRepository` mutated `_uiState.value` read-then-write off-main (`togglePosterWatchedAsync` runs on Default). | `update {}` / `getAndUpdate {}` on every mutator, `SynchronizedObject` around `hasLoaded`. |
| K5 | P3 | TorBox pager had no loop bound (an offset-ignoring server = infinite loop). | Fork hardening: 1000-page cap, stop when a page adds no new id; tests incl. the `limit == 1` still-truncated throw. |
| K6 | P3 | SenPlayer `minimal` bisect leg drops the callbacks silently. | Comment (by design: url-only leg returns no position). |
| K8 | P3 | Stream-mode extractions logged as trailer extractions. | `[stream]` prefix on the single-URL path only. |
| K9 (from the Swift review) | P2 | `claimCallback` required `lastPlayedUrl` to match for any positioned success; `lastPlayedUrl` is Infuse's own name, so a SenPlayer return with `position` alone would be ignored. | Present `lastPlayedUrl` must still match (Infuse unchanged); absent is accepted for any non-Infuse player (session id + player id tie the callback); tests. |
| S1 | P2 | Manual "Try Next Source" could land on a ytId stream. | Rejected set widened with the ytId keys (the list itself stays intact for the index lookup); test. |
| S2 | P2 | A late YouTube resolve replaced a playback the viewer started since (picker and in-player). | `resolvingKey == rowKey` + `selected == nil` guards; engine generation counter. |
| S3 | P2 | A failed in-player resolve closed the panel with no feedback. | One-shot `sourceSwitchFailure` on `NextEpisodeEngine`, shown by the players' toast. |
| S4 | P2 | `[ExtPlayerProbe] return url=` redacted only `lastPlayedUrl`; an unknown echo parameter could put a debrid link into a committed console log. | Allowlist (`position`, `duration`, `error*`, `x-source`); every other value `<redacted>`; tests. |
| S5 | P2 | SenPlayer position likely dropped as built. | = K9. |
| S6 | P2 | Test gaps (manual failover exclusion, `playbackSession(for:)` nil `lastSourceUrl`, engine list vs auto-play filter). | Added with pure static filters. |
| S7 | P3 | `@Sendable` capture warnings from the completion-handler + Task hop. | `try? await` form. |
| S8 | P3 | In-player Sources tab never marked a ytId (or debrid) source as current. | `playbackStreamKey` comparison; YouTube caption on the in-player row too. |
| S9 | P3 | `PlaybackStreamKey` keyed on raw `ytId`. | `youTubeIdToResolve`. |
| S10 | P3 | New xcstrings keys English-only. | Translation pass before a public cut (standing). |

Declined, documented: K7a (a `WatchedRepository.markWatched` unit harness needs tracking-registry + profile seams; the restore helper is covered and the call is one line). Reviewer-confirmed clean: old `MdbListLibrarySnapshot` payloads decode (defaults + `ignoreUnknownKeys`), the sort option is local-only, Trakt/Simkl/local sorting unchanged, `check(limit > 1)` cannot escape to Swift (`TorboxCloudLibraryProviderApi` wraps in `runCatching`), auto-play never sees a ytId stream (`isAutoPlayable` keys on `playableDirectUrl`), Infuse's return path byte-identical, the resolved googlevideo URL never reaches `lastSourceUrl` / failover memory / the return session's `playbackSession`.

### Review round 2 (one Opus read-only agent over the whole range `975a70109..f4db9b0ea`)

**0 P1 / 1 P2 / 6 P3.** Every round-1 fix confirmed complete. P2: after the pull-intent fix the only USER_INITIATED library pull on tvOS was the failed-state Retry, so a list re-sorted on mdblist.com (which does not bump its `updatedAt`) would never refresh on the TV → a **Refresh** control for provider libraries (Trakt/Simkl/MDBList) next to the List/Sort pills, calling the same USER_INITIATED pull. P3s fixed: skip-intro chip keeps precedence over the source-switch failure caption in mpv (D-pad Down otherwise performed a hidden skip); picker late-resolve guard made real with a per-request token invalidated on any `selected` write and on disappear, plus `pickerOnScreen` on the internal path; `InAppYouTubeExtractor.extract` rethrows cancellation so the resolver's rethrow is reachable end to end and the Swift resolve Tasks are stored and cancelled; a failed provider order re-subscribes on retry/refresh; `ContinueWatchingPreferencesRepository.persist()` reads one snapshot; the TorBox page cap logs when it returns a partial list. Fix commit `14f5991ce`; gates on it: jvm 1490 / K/N 1508 / NuvioTVTests 1707 / 0 (1 pre-existing skip), Debug + Release simulator, Debug device build.

### Device pass (2026-10-16 00:38–00:55 ET, Living Room Apple TV, Test 2 profile, rig, dev build 136 from `f4db9b0ea` = before the round-2 fixes; evidence `docs/research/batch-d-device-pass-2026-10-16/`, console redacted)

| Step | Result |
|---|---|
| 1 U6 | **Not walkable on the TV, by design of the feature:** nothing on tvOS reads or writes `dismissedNextUpKeys` (the only writer is mobile's `App.kt`, the only readers mobile's `HomeScreen.kt`; the shared CW row builder tvOS uses ignores the field; grep over `iosApp/NuvioTV` + `shared/commonMain` 2026-10-16). "Remove from Continue Watching" on the TV is a plain `clearProgress`. The port's effect is cross-device: a dismissal made on the phone (profile-synced preferences) is cleared when an episode is marked watched on the TV, so the phone's Home restores the show. Verified by the unit tests and the call-path trace (hold-menu Mark Episode Watched → `markWatched(item:)` → the Collection overload → `dismissedNextUpContentIdsToRestore`). A phone + TV check is Christian's if wanted. |
| 2 U2 | **PASS.** `scripts/device/fixtures/ytid-addon.py` served from the Mac, installed in Test 2 through Add-ons › Install from manifest URL (typed over the rig), Lizzie Borden › Sources: the "ytId fixture" group lists "YouTube (ytId fixture)" with the YouTube caption; Select → row spinner → `[TrailerExtract] [stream] selection: manifest=2160 progressive=360`, `[PlayerRouter] mpv — probe unavailable`, mpv plays the googlevideo HLS master (`[MPVStats] +48s cache=74.7s … underruns=0`, frames on screen; the `HTTP error 400` lines are mpv's HLS keepalive probes). Two Menu presses exited cleanly (`isLeavingPlayer=true`), fixture add-on removed afterwards. Not checked on device: the `lastSourceUrl` omission (unit-tested), the in-player Sources tab mark (round-2 build). |
| 3 FEAT-56 | **Plist + probe half PASS, hand-off OWED:** `[ExtPlayerProbe] canOpenURL(senplayer://) = false` with no "not allowed to query" error, so the `LSApplicationQueriesSchemes` entry works; SenPlayer is not installed on this box (app list: NuvioTV, VidHub, Infuse). **Christian:** install SenPlayer from the App Store on the Living Room Apple TV, then in Test 2 hold a source row → SenPlayer (or set it as the default player under Settings › Player): does it start at the resume position, does the add-on subtitle show, and on exit does the console (`-debug.extPlayerProbe YES`) print `[ExtPlayerProbe] return url=` with a `position`? If it opens but ignores the parameters, relaunch with `-debug.senplayerMethod minimal` / `noname` to bisect. |
| 4 U1 | **OWED (D7):** Settings › Services in Test 2 shows Connect Trakt / Connect Simkl / Connect MDBList, none connected. **Christian:** Services › MDBList → Connect (device code on mdblist.com), Library › List pill → an MDBList list → Sort pill shows Recently Released / Oldest Released and List Order; List Order must match the order saved on mdblist.com; re-sort the list on mdblist.com, press the new **Refresh** button beside the pills, the new order shows. |
| 5 U7 | Unit tests only (Test 2's TorBox account is small). Optional: Debrid Cloud on a > 100-item account loads fully. |

Rig notes: with Rail = Hidden, a Menu press on a root tab (Settings root) sends the app to the tvOS home screen; three blind Menus in a row did that and the following presses opened Prime Video's profile picker (nothing selected, backed out with Menu, NuvioTV relaunched). Screenshot one Menu at a time near a root.

### Final state (2026-10-16 01:05 ET)

- **Branch:** NuvioMobile `claude/batch-d`, 11 commits `4b3368bfe`…`14f5991ce` on `975a70109` (beta.19-rc4), pushed to `origin` (branch only; no tags). Working tree clean. Clone `~/Claude/Projects/NuvioMobile-batch-d` (MPVKit symlink, `local.properties` copied, `DerivedDataDevice` cloned from the player clone) can be deleted after the merge.
- **Gates on the tip:** `:shared:jvmTest` 1490 / 0 (baseline 1444), `:shared:tvosSimulatorArm64Test` 1508 / 0 (1462), `:composeApp:iosSimulatorArm64Test` 438 / 0 (435), NuvioTVTests 1707 / 0 / 1 skipped (1688), Debug + Release simulator, Debug device build (`iosApp/build/logs/batch-d-*.log`).
- **Device smoke of the tip** (Test 2, 01:00 ET): installed as build 136 under `com.youngchris29.NuvioTV`, launched into Test 2, Home and the Library grid render, no crash lines; the Library Refresh pill is absent for the local library as designed (Test 2 has no provider library). The U2 playback pass above ran on `f4db9b0ea`, two commits earlier (the round-2 fixes do not touch the resolve path).
- **Device left:** Test 2, Home, dev build `14f5991ce`, console stream stopped, rig lock released.

### Port table

| Item | Upstream | Fork files | Deviations from upstream (all deliberate) |
|---|---|---|---|
| U6 | `6fefbcdab` | `watched/WatchedRepository.kt`, `watchprogress/ContinueWatchingPreferencesRepository.kt`, test `ContinueWatchingDismissedRestoreTest` | The id rule lives in `dismissedNextUpContentIdsToRestore()` (testable without a `WatchedRepository` harness); the repository's mutators use `update {}` + a `SynchronizedObject` (upstream read-then-writes). |
| U7 | `be81802c8` | `debrid/DebridApiClients.kt`, test `TorboxCloudPagingTest` (7 + 2 cases, in `shared/commonTest` because the pager is `internal` to `shared`) | Fork hardening: 1000-page cap, stop when a page adds no new id, `log.w` on a partial return. |
| U1 | `d8ce7258` (+ `c1022e2eb` / `32449a7a1` for the pull intent) | `library/LibraryDisplaySettings.kt`, `LibraryProviderOrders.kt`, `LibraryRepository.kt`, `tracking/TrackingLibrarySorter.kt`, `mdblist/MdbListLibrary{Decoder,Models,Projection,Remote,Service,Sorter}.kt`, composeApp `LibrarySavedContent.kt` + `strings.xml` + `LibraryScreen.kt`; tvOS `LibraryGridPolicy.swift`, `LibraryViewModel.swift`, `LibraryView.swift`; tests across both modules | Batch 11's newest-first MDBLIST DEFAULT is replaced by the owner's saved order (= upstream). The fork keeps `MdbListNetworkEngine` (no `ApiHttpClient` refactor). New public `LibraryRepository.observeProviderOrder(listKey, sortOption)` (+ `LibraryProviderOrderResult`) so tvOS feeds MDBList's per-list orders into the grid (mobile does this through `rememberLibraryProviderOrders`). New tvOS Refresh pill for provider libraries (tvOS has no pull-to-refresh). "List Order" label unchanged. |
| U2 | `94976222` | `streams/StreamModels.kt`, `StreamParser.kt`, new `YouTubeStreamResolver.kt`, `trailer/InAppYouTubeExtractor.kt`; tvOS `StreamsViewModel.swift`, `StreamPickerView.swift`, `NextEpisodeAutoPlay.swift`, `PlaybackModels.swift`, `PlaybackProgressRecorder.swift`, `MPVPlayerView.swift`, `NativePlayerScreen.swift`, `MPVPlaybackTab.swift`, `Localizable.xcstrings`; tests in both modules | No App Store watch-page branch (tvOS is a full build). Failover memory keyed `<addon tag>|yt:<id>`, never the googlevideo URL; `lastSourceUrl` withheld (the fork's only persisted link; tvOS has no reuse-last-link cache). Manual "Try Next Source" skips ytId streams (upstream lets its manual flows resolve them). Cancellation propagates (upstream's `runCatching` swallows it). |
| FEAT-56 | GitHub NuvioTV#5 | `player/ExternalPlayerPlatform.apple.kt`, `player/external/ExternalPlaybackReturn.kt`; tvOS `Info.plist`, `ContentView.swift`, `StreamPickerView.swift`, `ExternalPlaybackReturn.swift`; tests | Parameter names unverified until the device test; a positioned `x-success` without `lastPlayedUrl` is accepted for non-Infuse players. |

### Upstream-report candidates (not filed)

1. `d8ce7258`: `MdbListLibrarySorterTest`'s new test name contains a comma, which Kotlin/Native rejects (`Name contains illegal characters`); upstream only runs that suite on the JVM.
2. `be81802c8`: a page failure after the first discards every page already fetched (a 1000-item library with one flaky page shows nothing); no loop bound if the server ignores `offset`; `check(limit > 1)` throws out of a suspend function.
3. `d8ce7258`: `MdbListLibrarySorter.oldestFirst()` compares `releaseDate ?: year.toString()` as strings, so a list mixing full dates and bare years can mis-orient; `libraryReleaseYear` takes the first 4-digit run (`"2008-2013"` → 2008).
4. `94976222`: `InAppYouTubeExtractor.extract` / `YouTubeStreamResolver` swallow `CancellationException` (a cancelled resolve reads as "could not resolve").
5. Upstream mobile's `pullFromServer` intent moved to AUTOMATIC in `c1022e2eb`; a fork that took `d8ce7258` without it would re-download every MDBList list on every sync (this fork's round-1 P1).
6. `ExternalPlaybackReturn.claimCallback` requires Infuse's `lastPlayedUrl` for any positioned success, so any other player's return is ignored unless it mimics Infuse.

### Follow-ups (not in this batch)

- Christian's device items: FEAT-56 SenPlayer hand-off (install SenPlayer first), U1 with MDBList connected in Test 2, optional U7 on a > 100-item TorBox cloud, optional U6 phone + TV cross-check.
- Translation pass for the new English-only strings (`Could not load this YouTube video.`, `Recently Released`, `Oldest Released`) before a public cut.
- Release notes for rc5 must say: MDBList "List Order" now follows the order saved on mdblist.com (was newest added first); cached MDBList lists download once more after the update; two new MDBList sorts; a Refresh pill on provider libraries; add-on streams that only carry a YouTube id now play (resolved on the device, never auto-played); SenPlayer as an external player (untested hand-off).
- Native player: its chip order was not changed for the source-switch failure caption (its skip is a contextual action, never hidden).
- `WatchedRepository.markWatched` has no unit harness (tracking registry + profile seams); the restore helper is covered.
- GitHub #5 second reply drafted (`docs/comms-github-issue5-reply-2026-10-15.md`, 5/5), waits for the go and ideally for the SenPlayer device result.

### Merge recipe (on the go)

```
cd "~/Claude/Projects/Nuvio tvOS/NuvioMobile" && git fetch origin claude/batch-d && git checkout tvos-shared-extraction && git merge --ff-only 14f5991ce && git push origin tvos-shared-extraction && git push origin --delete claude/batch-d
cd .. && git add NuvioMobile && git commit -m "NuvioMobile → 14f5991ce (Batch D merged)" && git push
```
Then delete the clone `~/Claude/Projects/NuvioMobile-batch-d`.

## Device pass plan (Test 2 profile, rig, lock held)

| Step | Item | Walk | Pass = |
|---|---|---|---|
| 1 | U6 | Home › Continue Watching: hold a series card → Remove (dismiss its next-up). Open the show's Detail → Episodes → hold the next episode → Mark Episode Watched (or the CW hold menu's Mark Episode Watched on another episode of the same show). Back to Home. | The show is back in Continue Watching (next-up re-armed); console shows the dismissed key dropped. |
| 2 | U2 | Mac serves `scripts/device/fixtures/ytid-addon.py` (LAN `192.168.1.127:8765`). Settings › Add-ons › Install from manifest URL → `http://192.168.1.127:8765/manifest.json`. Open any title → Sources → "YouTube (ytId fixture)" row → Select. | Row listed; spinner; playback starts (native or mpv) on the resolved HLS master; `[YouTube]`/extractor lines in the console; no reuse-cache write; auto-play never picks it. Remove the add-on afterwards. |
| 3 | FEAT-56 | SenPlayer is NOT installed on the Living Room box (app list 2026-10-15: NuvioTV, VidHub, Infuse). **Christian:** install SenPlayer (free, tvOS 17+) in the Test 2 profile, Settings › Player › default external player → SenPlayer (or hold a source row → SenPlayer), play, seek, exit. Report: did it start at the resume position, did the subtitle show, and did NuvioTV record the position on return (`[ExtPlayerProbe] return url=` line under `debug.extPlayerProbe`). If it opens but ignores parameters, try `-debug.senplayerMethod minimal` / `noname`. | Hand-off opens SenPlayer; the three halves answered for the GitHub #5 reply. |
| 4 | U1 | Needs MDBList connected in Test 2 (decision D7). **Christian:** Settings › Services › MDBList → connect (device code on mdblist.com), Library › List pill → an MDBList list, Sort pill → Recently Released, then Oldest Released; List Order should match the order saved on mdblist.com; change the saved sort on mdblist.com and pull-to-refresh (manual refresh) → the new order shows. | Both sorts order by release date; List Order = owner's order. |
| 5 | U7 | Needs a TorBox account with > 100 cloud items; the Test 2 TorBox account is small. Covered by unit tests; **optional** for Christian: Library › Debrid Cloud on a > 100-item account loads fully. | Full list. |
