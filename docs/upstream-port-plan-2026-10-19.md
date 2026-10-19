# Upstream port plan — 2026-10-19

Upstream `NuvioMedia/NuvioMobile` (cmp-rewrite): `63afb73c0` (0.6.0-beta, last plan 2026-10-16) -> `324afcffb` (**0.6.2-beta**). 12 non-merge commits, 60 files. 0 changes under `shared/`; all in `composeApp/commonMain`, `iosApp`, `store.json`. Fork tip checked: submodule `2baa390f1`, outer `abd5bf5`.
**New baseline: `324afcffb`.**

## Recommended ports

1. **LOW-MED — binge-group infoHash fallback** (upstream d2cc0fb8a "filename and infoHash matching for binge group stream selection"). The filename half is already in the fork (`NextEpisodeAutoPlay.swift` "Filename matching", `FilenameEpisodeMatcher` in `shared/`). Not in the fork: the **infoHash fallback** — when binge group matches but the filename does not, accept a stream with the same `bingeGroup` and the same `infoHash` as the playing one. `grep -in infoHash NextEpisodeAutoPlay.swift` = none.
   Source: `git -C NuvioMobile diff 63afb73c0 upstream/cmp-rewrite -- composeApp/src/commonMain/kotlin/com/nuvio/app/features/streams/StreamsRepository.kt composeApp/src/commonMain/kotlin/com/nuvio/app/features/streams/BingeGroupCacheRepository.kt`
   Files: `iosApp/NuvioTV/Screens/NextEpisodeAutoPlay.swift` (matcher next to `expectedNextFilename()`; read the playing stream's `infoHash` off `context.listedStream`), plus `shared/.../streams/StreamsRepository.kt` if the shared auto-play flow should get the same persisted-hash step (tvOS keeps the entry in `PlaybackContext`, so no `BingeGroupCacheRepository` change). Add a NuvioTVTests case (same bingeGroup, different filename, same infoHash -> picked). Effort: ~1 h. Gate: NuvioTVTests + shared jvmTest.

2. **LOW — next-episode preload lead time floor** (upstream PlayerNextEpisodeAutoPlay.kt). Preload lead was `autoPlayTimeoutSeconds`; now `max(timeout, 10 s)` capped at 30 s, so a short or zero timeout still preloads in time. Check the fork's FEAT-49 preload trigger (`NextEpisodeAutoPlay.swift` preload lead / `shouldShowNextEpisodeCard` call) and apply the same clamp if it uses the raw timeout. Effort: ~15 min + a unit test.

3. **LOW — localized Simkl status titles in the library** (upstream `LibrarySectionTitles.kt`, 3 call sites). Maps `simkl:status:{watching,plantowatch,hold,completed,dropped}` to string resources (`library_status_*`) instead of the English `displayTitle`. Fork keys exist in `shared/.../simkl/SimklLibraryProjection.kt`; apply in the tvOS library tabs/filter chip via `StringProvider` + the xcstrings pipeline (5 new keys). Only matters for non-English locales. Effort: ~30 min.

## Product decision (Christian)
4. **Watch Party (experimental)** — 0.6.1/0.6.2 added host-only control (f352f2b2d), chat (b253a7c5d: PartyChat, PartyChatContent ~600 lines, PartyApi) and PiP party sync. Still nothing in the fork; the 10-16 recommendation stands: do NOT port until it leaves beta. Chat makes the tvOS cost higher (on-screen keyboard entry on a TV).

## Not applicable
- iOS PiP / Now Playing system-control handler (`PlayerSystemControlHandler`, `MPVPlayerBridge.swift` requestSystem*), `MetalLayer` simulator presentation shim, iOS simulator build fix (f89d569ff), `PlatformInsets`, `formatLocalTime` (party chat only).
- Version bumps, `store.json` (0.6.1/0.6.2-beta), Italian/Greek/Dutch/Polish i18n fixes (party strings, escaped apostrophes).

## Open items carried
- 10-16: MDBList external/dynamic/liked lists (MEDIUM, upstream PR #2172/#2268); check whether it landed in the fork before the next batch.
- 10-10 TorBox mylist pagination (MEDIUM, be81802c8); 10-08 MDBList sort by release date (MEDIUM, d8ce7258); ytId-only addon streams (LOW-MED, 94976222).
- 10-14 optional LOW: poster-resolver perf, Episode N i18n. 10-13 subtitle AutoSync: do not port.

## NuvioTV Android
Upstream `NuvioMedia/NuvioTV` HEAD is still `c613e9311` (same as the baseline in `docs/nuviotv-android-upstream-port-plan-2026-10-19.md`). No new commits; no new Android plan file written.
