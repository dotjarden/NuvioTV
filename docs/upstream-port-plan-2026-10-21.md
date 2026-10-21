# Upstream port plan — 2026-10-21

Upstream `NuvioMedia/NuvioMobile` (cmp-rewrite): `324afcffb` (0.6.2-beta, last plan 2026-10-20) -> `c78756d0c` (**0.6.3-beta**). 12 non-merge commits (plus merges and i18n). 0 changes under `shared/`; all in `composeApp/commonMain`, `iosApp/Configuration`, `store.json`, string resources. Fork tip checked: submodule `6baddab46`, outer `e75a3ef`.
**New baseline: `c78756d0c`.**

## Recommended ports

1. **LOW-MED — player badges for what is playing** (upstream 344117e73 "show badges for what is playing"). New `PlaybackMatchText.kt` builds a match string from the live `PlayerMediaInfo` (resolution, codec, DV/HDR10/HLG, bit depth, audio codec/channels, language) and runs it through the existing `StreamBadgeMatcher` (new overload `matchedBadges(candidates:, filters:)`); `PlayerBadges.kt` draws the chips in the player controls; new setting `showInPlayer` in `StreamBadgeSettings*` (+ Streams settings row). The fork already has stream badges (`DesignSystem/StreamBadges.swift`, `BadgeSettingsViewModel`, `Settings/StreamBadgesSection.swift`) but nothing in the player chrome. Port: matcher overload and `showInPlayer` storage in `shared/` (the badge rules are shared), the match-text builder as a Swift function over the fork's native/mpv media info, a chip row in the tvOS player top panel, one Settings toggle (name it and its default in the release notes). Source: `git -C NuvioMobile diff 324afcffb upstream/cmp-rewrite -- composeApp/src/commonMain/kotlin/com/nuvio/app/features/player/PlaybackMatchText.kt composeApp/src/commonMain/kotlin/com/nuvio/app/features/player/PlayerBadges.kt composeApp/src/commonMain/kotlin/com/nuvio/app/features/streams`. Test: port `PlaybackMatchTextTest.kt` (70 lines) to shared jvmTest. Effort: ~3-4 h. Gate: shared tests + NuvioTVTests + device look at the player panel.

2. **LOW — custom posters in Library and Collections catalog views** (upstream 8c5e09c06). `CatalogRepository` now picks `CustomPosterScreen.LIBRARY` / `COLLECTIONS` instead of always `HOME` when applying the custom-poster pattern, and applies it to the library catalog state too. The shared `CustomPosterUrlRepository.patternForScreen` exists in the fork; check where the tvOS library grid and collection folders resolve poster URLs (`withCustomPosterUrls` equivalent in `shared/.../CustomPosterUrls.kt`) and make sure they pass the per-screen pattern. Effort: ~30-45 min. Verify first; it may already be per-screen on tvOS.

3. **DONE / skip — binge-group infoHash + filename seeding** (upstream 1b85c6458 seeds `currentStreamFilename/InfoHash` from the starting stream). The fork reads both off `context.listedStream` (`NextEpisodeAutoPlay.swift` `playingFilename`/`playingInfoHash`) and has the infoHash fallback (Batch L L1, cab68cd1d). The 10-19 item 1 is closed.

## Product decision (Christian)
4. **Watch Party (experimental)** — 0.6.3 adds phone-companion chat (ebb176787: `PartyCompanion*`), return-key send, party source label as plain text. Still nothing in the fork; the standing call is not to port until it leaves beta.

## Not applicable
- Engine switch moved to the top row with a confirm dialog (182684275) and centre controls staying put on pause (37a6656a2): the tvOS player has its own chrome.
- Version bump (014fa2e2f), `store.json` 0.6.3-beta, pt-BR / Hungarian / Vietnamese i18n (party, autosync, servers strings), debug-APK workflow edits.

## Open items carried
- 10-16: MDBList external/dynamic/liked lists (MEDIUM, upstream PR #2172/#2268); check whether it landed in the fork before the next batch. Android now also changed mdblist list visibility (see the Android plan).
- 10-10 TorBox mylist pagination (MEDIUM, be81802c8); 10-08 MDBList sort by release date (MEDIUM, d8ce7258); ytId-only addon streams (LOW-MED, 94976222).
- 10-19 localized Simkl status titles (LOW, ~30 min). 10-14 optional LOW: poster-resolver perf, Episode N i18n. 10-13 subtitle AutoSync: do not port.

## NuvioTV Android
Moved: `ffe1625` -> `5483ec462` (33 non-merge commits). Plan: `docs/nuviotv-android-upstream-port-plan-2026-10-21.md`.
