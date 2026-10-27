# NuvioTV Android upstream port plan — 2026-10-27

Upstream `NuvioMedia/NuvioTV` (`dev`): `ef1b8cb19` (last plan 2026-10-26) -> `c3f68d84a`. 13 commits, 6 files changed per the GitHub compare API.
**New baseline: `c3f68d84a`.**

## Candidates for the tvOS fork

None. Contents: French / other string updates and merges (`4a9678d29`, `d9fb4ae16`, `80d084627`, `51f0ce7c5`, `a5402a777`, `abf8b1a27`), a README-style message edit (`bb171ab8d`), and `7837fb1c2` "Fix subtitle lift after player controls hide" (PR #4266, Compose subtitle offset on Android). The tvOS subtitle layout is the fork's own SwiftUI/mpv stack; no action.

## Open items carried (see 2026-10-26 plan)
Simkl/MDBList playback-tracking perf (diff `MdbListProgressProjection.kt` first), Trakt refresh cancellation guard, libmpv no-retry on permanent HTTP errors.
