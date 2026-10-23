# NuvioTV Android upstream port plan — 2026-10-23

Upstream `NuvioMedia/NuvioTV` (`dev`): `a9cbb02c6` (last plan 2026-10-22) -> `b700cf98e`. 63 commits ahead per the GitHub compare API (a handful repeat the 10-22 list, which was read before the merge order settled). Read at commit-subject level only; effort figures are estimates, open the named commits before building.
**New baseline: `b700cf98e`.**

## Candidates for the tvOS fork

1. **LOW-MED — stream audio delay scoped to the audio source language** (a396f490f, PR #4027 "stream-delay-language"): per-language audio delay for streams. The fork's player has audio-delay controls; check whether the delay is global and whether a per-language scope is wanted. Effort: ~1-2 h if wanted, new setting needs a default named in release notes.
2. **LOW — perf: stop re-decoding badge rules for every batch of streams** (3f5d39627): applies when the player-badges port (10-21/10-22 items) lands; build the badge rules decode once in `shared/` from the start. No separate work.
3. **LOW — verify items carried from 10-22**: CW cache freshness + movie resume refresh (a9cbb02c6, f81a93426), profile-switch hygiene (b39ce87d4, 8176029aa, 198acd375), badge pack choice (656835e31). Unchanged, see `docs/nuviotv-android-upstream-port-plan-2026-10-22.md`.

## Not applicable
- libass work (4f2fd58e2 atlas pipeline, 85768bccf/99a41515f default-on, 64d00c6c9/01d953f66/d7d4b2c45 nuvio-libass AAR bumps, 9d791d335 + d5d40b82d render scale setting, 7ae2cbf81 tunneled subtitles): Android subtitle renderer; tvOS uses mpv/native subtitles.
- Tunneled playback fixes (f48eefbba, dbd70abb8, eebe3e373, 2fa602872, d7e146062): Android ExoPlayer tunneling.
- Supporter avatar URI/path fixes (7c37a1eb9, 763e4683d): Android Coil.
- Strings and version bump: es/sk/hu/pl translations (0749eb757, bdc521e99, ec2c0a46a), "latest missing strings" (c4e0032d1), ce6ca448b.
