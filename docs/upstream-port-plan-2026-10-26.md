# NuvioMobile upstream port plan — 2026-10-26

Upstream `NuvioMedia/NuvioMobile` (`cmp-rewrite`): `c114d6fb6` (last plan 2026-10-25) -> `56ae37081`. 10 non-merge commits (plus the merge), all one feature branch (`duo-half-open`), 12 files, +839/-83. `git diff --stat` shows **nothing under `shared/`**.
**New baseline: `56ae37081`.**

## Candidates for the tvOS fork

None. Every commit is the dual-screen "half-open duo" player layout (foldable devices):

- 88c9b4ce9 split video and controls at the duo fold (`core/ui/Fold.kt`, `iosMain/Hinge.kt`, `MainViewController.kt`, `iosApp/ContentView.swift`)
- bd243af9a / 7f4bd9616 / aefe6ce91 / e5c9c9609 / 43838dd07 / f1a2d1d9e tile controls, panel placement, stream badges, brightness + volume, idle dimming (`FoldControls.kt` +552, `PlayerControls.kt`, `PlayerScreenRuntimeUi.kt`, `PlayerControlActions.kt`)
- f32dce5f3 read the real system volume in the iOS player (`PlayerPlatformEffects.ios.kt`): iOS-only, no tvOS volume UI.
- d995e6834 refit paused video when the player resizes (`iosApp/iosApp/Player/MPVPlayerBridge.swift`): upstream iOS app only; the fork's tvOS player is a separate SwiftUI/mpv stack, and a tvOS window never resizes.

Only possible overlap: `aefe6ce91` shows stream badges on the duo panel. The fork already has its own badge UI; revisit only when the open badge-pack-choice item below is scheduled.

## Not applicable
All of the above (foldable-hinge layout, iOS volume/brightness, upstream iOS player bridge).

## Open items carried (see 2026-10-24 plan)
Trakt paging-test compare, badge-rule + debrid regex caches, optional Home-hero ratings `showOnHero` (default Off), player badges + pack choice, mpv `hwdec-software-fallback=300`, MDBList lists/sort, TorBox pagination.

## Addendum (same day, review session)

Upstream moved again after the morning check: `56ae37081` -> `7de46ead` (9 non-merge commits, still **0 under `shared/`**). Fork tip checked: submodule `773e48732`, outer `745b84a`. **New baseline: `7de46ead`.**

New in range: Bulgarian / Croatian / Italian strings (N/A), `2c69902b` servers title lookup between episodes (N/A, no `ServerMatcher` in the fork), and two debrid fixes that the fork needs:

1. **LOW-MED, recommended — debrid language words in release names** (`6eb35df0`, `DebridStreamPresentation.kt` +32, test +60) **+ ignore title words when reading stream languages** (`4b79c43c`, +44, test +71). Fork has the exact bug: `shared/.../debrid/DebridStreamPresentation.kt:323-324` falls back to two-letter codes only (`searchText.hasToken(it.code)`), and `languageFor` (line 448) accepts only code or label. So `ITA`/`ENG`/`FRENCH`/`GER` streams fail a required-language filter, survive an excluded one, and sort last; "The French Dispatch" reads as French. On tvOS this is wider than upstream because `allStreams = true` runs the language filter over every passthrough add-on stream, not only debrid ones. The hunks target code the fork has verbatim (alias map + per-language regexes, title strip before matching); the surrounding file has ~90 lines of fork-only passthrough code, so port by hand and add both test files' cases to a new `DebridStreamPresentationLanguageTest.kt`. No new setting. Effort: ~1.5 h incl. tests.

Verification of the carried items against `773e48732`:
- Player badges + pack choice: still unported (no `showInPlayer` / `playerBadgeSource` / `PlaybackMatchText` in `shared/` or `iosApp/NuvioTV`).
- mpv `hwdec-software-fallback`: still absent (`MPVPlayerView.swift:941` sets only `hwdec=videotoolbox`).
- Badge-rule cache (`a0735005d`): fork `StreamBadgePresentation.kt` is byte-identical to upstream's pre-commit file and compiles the rules on every call (line 5), so the commit applies as a straight cherry-pick with the path rewritten. ~20 min.
- Debrid regex cache (`def203a96`): fork file drifted (passthrough `allStreams` logic), manual port; fold into item 1 above since both touch the same functions (`hasToken` lines 471-474 still compile a `Regex` per call).
- Home-hero ratings `showOnHero`: unported, still optional.
- Trakt paging test: fork `TraktProgressFetchFailureTest.kt` covers page failure and empty list; upstream `TraktProgressPagingTest.kt` adds "undecodable page drops the list", "newest episode per show", and "error status on first/later history page". ~20 min to add.
- Custom posters per screen (10-21 item 2): **already in the fork** (`LibraryRepository.kt:713`, `FolderDetailRepository.kt:452` use `LIBRARY` / `COLLECTIONS`). Closed.
- `engine_version`: not in fork scripts; nuvio engine bump N/A.

Recommendation: one small `shared/`-only batch = item 1 (both language fixes) + debrid regex cache + badge-rule cache + the Trakt test cases (~3 h, no new setting, no UI). Leave player badges, hwdec fallback and hero ratings for a scheduled UI batch; MDBList lists/sort and TorBox pagination stay MEDIUM carries.
