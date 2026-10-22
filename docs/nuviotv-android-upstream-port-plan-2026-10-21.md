# NuvioTV Android upstream port plan — 2026-10-21

Upstream `NuvioMedia/NuvioTV` (`dev`): `ffe1625` (last plan 2026-10-20) -> `5483ec462`. 33 non-merge commits. Read at commit-subject level only (bare blobless clone, no diffs read); effort figures are estimates, open the named commits before building.
**New baseline: `5483ec462`.**

## Candidates for the tvOS fork

1. **MEDIUM — player chapters** (PR #3839, c96841068 .. 17650ae7c): chapter marks on the progress bar, skip between chapters, a chapters panel, exact mpv chapter seeks, ExoPlayer chapters off by default. The fork has chapter handling in `RemuxSession.swift` / `PlaybackModels.swift` / `MPVPlayerView.swift`; check whether it exposes chapter marks and a panel in the tvOS player. Effort: ~half a day if the panel is missing.
2. **LOW-MED — player badges for what is playing** (1b8af0adc): same feature as NuvioMobile 344117e73; see `docs/upstream-port-plan-2026-10-21.md` item 1. Do one port for both.
3. **LOW-MED — MDBList dynamic/liked lists** (PR #4136, 4809e5653, bcd3efe60, 0262b51cb): new dynamic and liked lists start hidden, read-only lists read whole, "hide only when a big batch turns up". Pairs with the carried MDBList external/dynamic/liked-lists item; port together.
4. **LOW — separate HDR / Dolby Vision subtitle style** (73fa9620d, PR #4073) and **subtitle lift steady on pause / letterbox** (fbe872baa, 651fa7dd5, d993c6eab, PR #4139). The tvOS app draws its own subtitles over native and mpv; check the lift when the title clears the progress bar. HDR style toggle is optional.
5. **LOW — detail ratings load before remote watch progress** (c04318ed6, PR #4151): check the tvOS Detail load order; ratings should not wait on Trakt/Simkl progress.
6. **LOW — server title lookup, one lookup per title** (723242ab5, PR #4161): applies if the fork's self-hosted server discovery resolves addon titles per request.

## Not applicable
- Background downloads, silent installs, updater banner (6f8a415a2, a04eef8e8, c272af068, 181564cca): Android only.
- Watch party chat/pairing/keypad (0f84b75e9, 89d77c375, 0945e720f), engine switch placement (810543e35).
- Lighter detail episode card recomposition (58ad4973f), mpv track-list read per file (c96841068; the fork's mpv path is its own).
- pt-BR / missing-string commits.
