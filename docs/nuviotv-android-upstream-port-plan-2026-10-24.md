# NuvioTV Android upstream port plan — 2026-10-24

Upstream `NuvioMedia/NuvioTV` (`dev`): `b700cf98e` (last plan 2026-10-23) -> `b36db8083`. 28 commits per the GitHub compare API, 17 non-merge. Read at message and file-stat level; open the named commits before building.
**New baseline: `b36db8083`.**

## Candidates for the tvOS fork

1. **LOW — debrid stream language words** (138feb869 + 3d39a7cc8, `DirectDebridStreamFilter.kt` +67, tests +95). Streams without parsed languages only matched two-letter codes and "multi"; now ITA/ENG/FRENCH/GER match, and title words ("The French Dispatch", "The Italian Job") are stripped first so they are not read as the stream language. Fork analogue: `shared/.../debrid/DebridStreamPresentation.kt` / `DebridStreamFormatter.kt` (`"multi"` handled at `DebridStreamFormatter.kt:166`). Port both as one unit into `shared/`; affects required/excluded language filters and language sort. No new setting. Effort: ~1.5 h.
2. **LOW — SDH stripping keeps lines ending in a colon** (7bb59699a, `SubtitleSdhFilter.kt` +20/-2, test +70). Fork has `shared/.../player/SubtitleSdhFilter.kt` (24 lines, `speakerLabel` regex with `(?=\s|$)`). Apply the same guard, copy the test. Effort: ~20 min.
3. **LOW — keep playing when progress cannot be saved** (020710d8c, `PlayerRuntimeControllerPlaybackEvents.kt`, `ExternalPlaybackTracker.kt`). Android player-event path; verify the tvOS save path (WatchProgress write in `iosApp/NuvioTV` player) swallows a failed save rather than stopping playback. Likely a no-op. Effort: ~20 min to verify.
4. **LOW — carried from 10-23:** per-language audio delay scope (a396f490f), badge-rules decode perf (rides item 2 of the Mobile plan), CW cache freshness, profile-switch hygiene, badge pack choice.

## Not applicable
- Greek locale commits (363e3397a, 187d73737, 6364e55e5), RTL formatting fixes (2e1d7ab36, 020a4c15c, 729a9d9f0): Android resources.
- Focus fixes (dd398dd8e add-on manager after QR close, a65264ca2, 9d6cef90f): Compose focus; tvOS has its own focus model.
- Updater volume fix (cbde1403a), torrent engine 0.1.6 + error reporting (fce733d72, d1071fc99): Android-only.
- "Remove source name from paused player" (9f7b2cc64): same as Mobile c85dc7214, see that plan.
