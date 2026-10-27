# NuvioMobile upstream port plan — 2026-10-27

Upstream `NuvioMedia/NuvioMobile` (`cmp-rewrite`): `7de46ead` (last plan, 2026-10-26 addendum) -> `61658f366`. 5 non-merge commits, **0 under `shared/`**. Fork tip checked: submodule `410e21e22`, outer `340b1d2`.
**New baseline: `61658f366`.**

The debrid language fixes (`6eb35df0`, `4b79c43c`), regex/badge caches and Trakt tests recommended on 10-26 already landed in the fork (410e21e22); they are closed.

## Candidates for the tvOS fork

1. **LOW-MED, optional UI batch — player chapters** (`9b95ce843`, kernexshadow): progress-bar chapter marks, current chapter name above the bar, a Chapters side panel, prev/next chapter. All in `composeApp` (`PlayerChapters.kt` model + `normalize/indexAt/nextStartMs/previousStartMs` helpers, `MatroskaChapterParser.kt`, `PlayerChaptersPanel.kt`); upstream iOS shows none ("mpv bridge does not expose them"). The fork's `iosApp/NuvioTV` player already references chapters (`MPVPlayerView.swift`, `NativePlayerScreen.swift`, `NativePlaybackCoordinator.swift`, `RemuxSession.swift`), so check what exists before porting. Worth taking: the pure helpers (`PlayerChapters.kt` 44 lines + `PlayerChaptersTest.kt`) as a `shared/` model if the Swift side lacks equivalents (the 3 s previous-chapter restart threshold matches mpv). The Matroska range-request parser is for ExoPlayer; tvOS uses mpv's `chapter-list`, N/A. Needs a Swift panel and focus work; if added, any new setting must be named with its default in release notes. ~0.5 day, only if the fork's chapter UI is thinner than this.
2. **N/A — servers title lookup between episodes** (`2c69902b1`, `ServerMatcher.kt`, `Emby/Jellyfin/MediaBrowserProvider`): the fork has no `ServerMatcher` (confirmed 10-26).

## Not applicable
`5b60b7780` (Portuguese strings), `894afaecc` (Vietnamese), `af58a32b0` / `61658f366` (version bump 0.6.5-beta, `store.json`, `Version.xcconfig`).

## Open items carried (see 2026-10-24 and 2026-10-26 plans)
Player badges + pack choice, mpv `hwdec-software-fallback=300`, optional Home-hero ratings `showOnHero` (default Off), MDBList lists/sort, TorBox pagination.
