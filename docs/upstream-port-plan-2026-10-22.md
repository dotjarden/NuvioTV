# Upstream port plan — 2026-10-22

Upstream `NuvioMedia/NuvioMobile` (cmp-rewrite): `c78756d0c` (0.6.3-beta, last plan 2026-10-21) -> `e6c399e01`. 5 non-merge commits (plus 4 merges). 0 changes under `shared/`; all in `composeApp/commonMain`/`androidMain`, `iosApp/Player/MPVPlayerBridge.swift`, string resources. Fork tip checked: submodule `6baddab46`, outer `b7f4259`.
**New baseline: `e6c399e01`.**

## Recommended ports

1. **LOW (fold into the 10-21 badges item) — choose a badge pack for the player** (83e528f00). Extends 344117e73 (player badges, still unported in the fork: no `showInPlayer` anywhere in `shared/` or `iosApp/NuvioTV`). Adds `playerBadgeSource: String` (default `""` = same pack as streams) to `StreamBadgeSettingsUiState`/`Repository`/`Storage` (+ `setPlayerBadgeSource`, `loadPlayerBadgeSource`/`savePlayerBadgeSource`), `StreamBadgeRules.forPlayer(sourceUrl)` (blank -> `normalized()`, else `setActiveSource`), and a Streams settings row + dialog shown only when `showInPlayer` is on and a pack is imported. Port as one unit with the 10-21 item 1: shared storage/rules in `shared/`, a Settings row on tvOS (name the new setting and its default, "Same as streams", in the release notes). Source: `git -C NuvioMobile diff c78756d0c upstream/cmp-rewrite -- composeApp/src/commonMain/kotlin/com/nuvio/app/features/streams composeApp/src/commonMain/kotlin/com/nuvio/app/features/player/PlayerBadges.kt composeApp/src/commonMain/kotlin/com/nuvio/app/features/settings/StreamsSettingsPage.kt`. Test: `PlaybackMatchTextTest.kt` (+20 lines upstream). Added effort on top of the badges port: ~1 h.

2. **LOW — mpv `hwdec-software-fallback=300`** (476998d56, PR #2306: iOS PiP interrupted by Notification Center froze video). Upstream adds the option so a dropped VideoToolbox session recreates instead of falling to software. The fork sets `hwdec=videotoolbox` at `iosApp/NuvioTV/Screens/MPVPlayerView.swift:941`. tvOS has no PiP or Notification Center, but the option is a harmless one-liner that also covers a VideoToolbox session invalidation on a long pause. Verify on the Test profile with a Dolby Vision file that nothing changes in the diagnostics card's `hwdec-current`. Effort: ~15 min.

## Not applicable / skip
- **mpv subtitle AutoSync for add-on subtitles** (cb581ea78, PR #2275: `AutoSyncSubtitleTextRetimer`, `AutoSyncTimelineTimeMapper`, `AutoSyncLibmpvCoordinator.android.kt`, `PlayerEngine.android.kt`). Android libmpv only; the standing call from 10-13 is not to port subtitle AutoSync. The two commonMain helpers are pure Kotlin and would port cleanly to `shared/` (SRT/WebVTT/ASS timestamp rewriting) if that call changes.
- Android PiP subtitle scaling (f8dda1c82), player side panels clear of the Android navigation bar (b9fbc09c8): Android-only.

## Open items carried
- 10-21: player badges for what is playing (LOW-MED, ~3-4 h, new `showInPlayer` setting), custom posters in Library/Collections (LOW, verify first); Watch Party chat stays deferred.
- 10-16: MDBList external/dynamic/liked lists (MEDIUM, PR #2172/#2268); Android also changed list visibility (see the Android plan).
- 10-10 TorBox mylist pagination (MEDIUM, be81802c8); 10-08 MDBList sort by release date (MEDIUM, d8ce7258); ytId-only addon streams (LOW-MED, 94976222).
- 10-19 localized Simkl status titles (LOW, ~30 min). 10-14 optional LOW: poster-resolver perf, Episode N i18n. 10-13 subtitle AutoSync: do not port.

## NuvioTV Android
Moved: `5483ec462` -> `a9cbb02c6` (30 non-merge commits). Plan: `docs/nuviotv-android-upstream-port-plan-2026-10-22.md`.
