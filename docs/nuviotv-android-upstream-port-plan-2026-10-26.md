# NuvioTV Android upstream port plan — 2026-10-26

Upstream `NuvioMedia/NuvioTV` (`dev`): `b36db8083` (last plan 2026-10-24) -> `ef1b8cb19`. 114 commits per the GitHub compare API; ~75 non-merge, mostly a batch of contributor PRs (a11y from thebetterfarhan, Simkl/MDBList playback perf from halibiram, player fixes from several authors) that merged into `dev`. Read at message and file-stat level; open the named commits before building.
**New baseline: `ef1b8cb19`.**

## Candidates for the tvOS fork

1. **LOW-MED — Simkl/MDBList playback tracking perf + persistence** (63719770f, aed9f9478, a181df9a2, 9258da5ab, 719cc70b1, 82886dac9, 602bd21f5 and ~15 follow-ups by halibiram, 10-17 to 10-23). Playback sessions persisted separately from the library/watched snapshot, entry index for constant-time scrobble/projection lookups, no regex timestamp parsing, scoped per account, bounded-backoff retry for watch-progress metadata hydration. Fork analogues: `shared/.../simkl/` and `shared/.../mdblist/MdbListProgressProjection.kt`, `MdbListMediaIndex.kt`, `MdbListMutationTarget.kt`. Large and interdependent, so do not cherry-pick: first diff the fork's `MdbListProgressProjection.kt` against upstream Mobile to see whether the Mobile app took these; if not, treat as one ~1 day port with the tests (`TrackingProgressOverheadTest`, `SimklSyncRepositoryStorageTest`, `WatchProgressMetadataRetryTest`). Only worth it if tvOS shows scrobble CPU or memory spikes. No new setting.
2. **LOW — Trakt refresh propagates cancellation** (f28832202, `TraktProgressService.kt` +3). One-line guard against turning `CancellationException` into `IOException`. Check the fork's Trakt progress refresh in `shared/.../trakt/`. ~15 min.
3. **LOW — Jellyfin title lookup after show details expire** (ed7135058, `ServerMatcher.kt` +32, test +80). Only if the fork has a media-server matcher; grep `ServerMatcher` first, likely N/A. ~20 min to verify.
4. **LOW — libmpv: skip auto-retry on permanent HTTP errors** (830e8e83c, `PlayerRuntimeControllerErrorRecovery.kt`, `MpvPlaybackErrorPolicyTest`). Fork analogue: the tvOS mpv failure/retry path in `iosApp/NuvioTV` player (and the failover logic from the Orivio batch). Check that a 403/404 stream fails over instead of retrying. ~45 min.
5. **LOW — MKV Tracks element placed after Clusters** (9099b47ba, `MatroskaExtractor.java`). Android Media3 extractor; tvOS uses mpv/AVPlayer remux. N/A unless the remux path (`tvos-remux-verification`) has its own EBML parser; verify only.
6. **LOW — percent-encoded `{shape}` in custom poster patterns** (a7e6ca3a0, `CustomPosterUrlResolver.kt` +6). Fork analogue only if custom poster patterns exist in `shared/`; grep `{shape}`. ~15 min.
7. **Carried:** debrid language words + title-word strip, SDH colon-line fix (10-24 plan), per-language audio delay scope, badge pack choice.

## Not applicable
- Accessibility semantics (thebetterfarhan, ~25 commits): Compose/TalkBack. The tvOS equivalent is VoiceOver labels; not an upstream port, but a reasonable independent audit if wanted.
- Decoder release on background (0b9269276), tunneled playback to USB audio (2a32c1532), QR sign-in jank (7d302cc33), logo PNG decode (1ef08231a), trailer black screen (faf170eda, Compose `TrailerPlayer`), updater banner (03305b0fc), settings focus restore (e4b852e57), overlay fixes (aabc56bbb; QR overlay 3984e04b2 reverted by 825a4cc4a), torrent stream keep-alive (faf630577): Android-only.
- Forced-subtitle MPV fix (77f914c19) was reverted by efd7df263 the same day: ignore.
- i18n / RTL (French, Hebrew, `keepLtr`): Android resources.
- CI, Dependabot, Gradle tuning, worktree config: fork-local upstream housekeeping.
