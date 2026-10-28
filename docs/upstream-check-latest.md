# Upstream check — latest (rolling)

Overwritten by the `nuvio-upstream-check` scheduled task on every run. The dated reports it also writes (`docs/upstream-port-plan-YYYY-MM-DD.md`, `docs/nuviotv-android-upstream-port-plan-YYYY-MM-DD.md`) stay local and are gitignored; this file is the only tracked record and carries the baselines the next run starts from.

- **Run:** 2026-10-28
- **NuvioMobile baseline** (`NuvioMedia/NuvioMobile` `cmp-rewrite`): `86e0d5bb4` — dated report `docs/upstream-port-plan-2026-10-28.md`
- **NuvioTV Android baseline** (`NuvioMedia/NuvioTV` `dev`): `d14832e1c` — dated report `docs/nuviotv-android-upstream-port-plan-2026-10-28.md`

## NuvioMobile — 2026-10-28

Upstream `NuvioMedia/NuvioMobile` (`cmp-rewrite`): `61658f366` (last plan, 2026-10-27) -> `86e0d5bb4`. 1 non-merge commit, **0 under `shared/`**. Fork tip checked: submodule `410e21e22`, outer `89dfbe1`.
**New baseline: `86e0d5bb4`.**

## Candidates for the tvOS fork

1. **N/A — skip drag handling while controls are locked** (`45af99c41`, tapframe, fixes upstream #2410): removes 6 lines from `composeApp` `PlayerSurfaceGestures.kt` and extends `PlayerSurfaceGesturesTest.kt`. Compose touch-gesture logic for the mobile player; the tvOS player is remote-driven with no drag surface. No action.

## Not applicable
Nothing else moved.

## Open items carried (see 2026-10-24, 2026-10-26 and 2026-10-27 plans)
Player badges + pack choice, mpv `hwdec-software-fallback=300`, optional Home-hero ratings `showOnHero` (default Off), MDBList lists/sort, TorBox pagination, optional player chapters batch (check the fork's chapter UI first).

## NuvioTV Android — 2026-10-28

Upstream `NuvioMedia/NuvioTV` (`dev`): `c3f68d84a` (last plan 2026-10-27) -> `d14832e1c`. 30 commits (GitHub compare API).
**New baseline: `d14832e1c`.**

## Candidates for the tvOS fork

1. **MED, port the idea — no resume progress for live streams** (`b4e47d6d6`, `583eae818`; PR #4227): mpv can seek inside its HLS cache so a live stream reports seekable, its duration keeps growing past the short-clip guard, and the saved position later seeks beyond the live window. Fix: a pure `LivePlaybackUiPolicy.nextDurationGrowth()` sampled once per tick (skipping readings before mpv reports the requested media) plus a "don't save resume" guard (`LivePlaybackUiPolicy.kt` 28 lines + `LivePlaybackUiPolicyTest.kt`). The fork uses mpv for some streams, so the same hazard can apply; check how `iosApp/NuvioTV` playback progress saving decides a stream is live (graphify `explain` on the progress writer) and port the duration-growth heuristic if it only relies on `seekable`. Swift, ~0.5 day, unit-testable.
2. **LOW-MED, optional — player badge codec detection + filename matching** (`13683564d`; `PlayerMediaInfo.kt` +46, `PlayerBadges.kt`, `PlaybackMatchText.kt`): improves codec badges and falls back to the file name. Folds into the carried "player badges + pack choice" item; read the diff when that is scheduled.
3. **LOW — Montenegrin subtitle language** (`7eb388a83`): OpenSubtitles returns `mne`/`me`, ISO 639-3 is `cnr`; all map to `sr-ME`. The fork has no `mne`/`cnr` handling (grep of `shared/` and `iosApp/NuvioTV`). Three-line map entry in the subtitle language normaliser if one exists; ~15 min.
4. **N/A:** libass video-effect work (`cc9bdb19e`, `d5da6bcaa`, `a8813ffb1`, `f60dab973`, `7070a646a`, `2bc54ec8f`, `6e2e5f961`, `205c314ef`, `3315ef13b`, `8d771aa2c`, `7dc661731`: ASS render mode, overlay alignment, audio-delay propagation to libass; Android AAR), `11b3c9d9c` (updater dex), Hebrew/Turkish strings (`6da2237ef`, `b032356f2`, `5e7a3fd6a`, `173da9d00`) and merges. The tvOS subtitle stack is the fork's own.

## Open items carried (see 2026-10-26 plan)
Simkl/MDBList playback-tracking perf (diff `MdbListProgressProjection.kt` first), Trakt refresh cancellation guard, libmpv no-retry on permanent HTTP errors.
