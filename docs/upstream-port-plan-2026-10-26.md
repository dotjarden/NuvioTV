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
