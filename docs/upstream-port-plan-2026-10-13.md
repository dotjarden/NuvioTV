# Upstream port plan — 2026-10-13

Upstream `NuvioMedia/NuvioMobile` (cmp-rewrite): `ee3d91506` -> `dac3f3141` (7 commits, PR #2143 "Mobile subtitle AutoSync" by DavidVamaiotu). 0 changes under `shared/`; ~9.2k added lines, all composeApp (+ docs/subtitle-autosync.md).

## What upstream added
Subtitle AutoSync: compares an add-on subtitle against subtitle timing embedded in the playing video; corrects constant delay, frame-rate drift, or per-cue-group timing. No audio analysis. Setting "Auto Sync Subtitle" (Playback > Subtitle/Audio, off by default, tolerance 100-500 ms, Thorough/Quick). Success = "Auto synced" badge on the subtitle card; failures toast; cancels on subtitle change/manual delay/leaving player.
Upstream scope: Android ExoPlayer, HTTP(S) streams only. iOS, libmpv, libass ASS/SSA, external players are explicitly NOT covered.

## Split of the code
- Pure Kotlin, portable in principle (composeApp commonMain): AutomaticSubtitleSync.kt (2140 lines, matcher), AutoSyncTimelineRetime.kt (2373), AutoSyncSubtitleCueParser.kt, AutoSyncSampledReferenceAligner.kt, AutoSyncReferenceConsistency.kt, AutoSyncNoFitTracker.kt, AutoSyncRunPolicy.kt, AutoSyncSyncedLabel.kt, AutoSyncPreferencesRepository.kt, SubtitleCharsetDetector.kt, AutoSyncDelayPreflight.kt.
- Android-only (ExoPlayer extractors/sidecar/HTTP; NOT portable): EmbeddedSubtitleTimelineLoader.kt (1764), AutoSyncExtractorsFactory, AutoSyncPlayerCoordinator/EngineController.android, AutoSyncSidecarBridge.android, AutoSyncSubtitleHttp.android, PlayerEngine.android/PlayerSidecarSubtitles/RewrappableExtractor changes.

## Recommendation: DO NOT port now (product call, HIGH effort)
The matcher needs a reference timeline of embedded subtitle cues from the video. On Android that comes from ExoPlayer extractors. tvOS plays via AVPlayer/MPV, so the embedded-cue source would have to be rebuilt (e.g. read embedded text tracks via MPV `sub-text`/demux cache, or an MKV/MP4 text-track reader), which is the hard part and is not in upstream. Also no audio fallback, so videos without embedded subtitles get nothing. Only worth doing if subtitle desync is a real pain point on tvOS.

If you decide to go ahead (phased):
1. Extract the pure matcher/retimer/cue-parser/charset files into `shared/` (nothing there depends on Compose; verify imports, port upstream's tests - note upstream kept tests out of the PR, so write your own offset/drift/grouping tests).
2. Design a tvOS reference-cue source for MPV (and AVPlayer if used) behind an interface mirroring `AutoSyncPlayerContracts.kt`.
3. Add Settings > Playback toggle + tolerance + Thorough/Quick, "Auto synced" badge on subtitle card, cancel-on-change rules from docs/subtitle-autosync.md.
4. Swift apply path: swap subtitle cues / adjust delay without reloading media.

## Open items carried (unchanged)
- 10-10 TorBox mylist pagination (MEDIUM, upstream be81802c8) - shared/.../debrid/DebridApiClients.kt + TorboxCloudLibraryProviderApiTest
- 10-08 MDBList sort by release date (MEDIUM, d8ce7258); ytId-only addon streams (LOW-MED, 94976222)
- Jellyfin/Emby servers + PR #2207 fixes: only if media servers are adopted.

## Claude Code prompt
"Read docs/upstream-port-plan-2026-10-13.md. Do not start AutoSync unless I say so. Do the 10-10 TorBox pagination port first, then the 10-08 MDBList sort."
