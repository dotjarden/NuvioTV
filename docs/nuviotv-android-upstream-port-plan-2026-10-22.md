# NuvioTV Android upstream port plan — 2026-10-22

Upstream `NuvioMedia/NuvioTV` (`dev`): `5483ec462` (last plan 2026-10-21) -> `a9cbb02c6`. 30 non-merge commits. Read at commit-subject level only (blobless bare clone, no diffs read); effort figures are estimates, open the named commits before building.
**New baseline: `a9cbb02c6`.**

## Candidates for the tvOS fork

1. **LOW — player badge pack choice** (656835e31): same feature as NuvioMobile 83e528f00; do one port with the 10-21 badges item. See `docs/upstream-port-plan-2026-10-22.md` item 1.
2. **LOW-MED — Continue Watching cache: prefer fresh episode metadata, persist rating visibility** (a9cbb02c6) and **refresh movie resume state on the detail screen** (f81a93426). Check that the tvOS CW row does not show stale episode titles/thumbnails after a sync, and that the Detail resume button reflects progress made since the screen was last loaded. Effort: ~1 h to verify, more if stale.
3. **LOW — profile-switch hygiene** (b39ce87d4 clear the previous profile's screens; 8176029aa remove local data of profiles deleted on another device; 198acd375 poster-menu watched toggles stay with the profile that made them). Worth a device check on the Test/Chris profile switch: no row or watched state from the previous profile visible after a switch. `AccountDataStores` is the wipe registry for the delete case. Effort: ~1 h verify.
4. **LOW — ExoPlayer chapters when tunneled** (6527c7e93): Android engine detail; the 10-21 chapters item stands unchanged.
5. **LOW — HDR detection from the HEVC SPS when the container has no colour info** (cd2368624): the fork's HDR subtitle style is not ported, so skip unless the 10-21 HDR subtitle style item is picked up.
6. **LOW — streams screen: resume progress and plugin source names, resume pill styling** (56f6a278b .. 840ad0639, 5dc609dd0 align with NuvioMobile): UI polish; compare with the tvOS stream picker's resume affordance only if wanted.
7. **LOW — episode status indicators moved to top right** (1b022ea06), **loading text overlapping tall logos** (79e6bc125): cosmetic; check the tvOS loading screen with a tall clearlogo.

## Not applicable
- Library release-date sorting options removed (bf31d778a): Android UI; fork has its own Library sort.
- Strings: YouTube loading/resolution failure strings (270dcda27, 9654e36e2), "latest missing strings" (1a48ac7d3, 2b23cff42, 968afbd18), hu/pl/es/sk translations, upload commit 6464a43ec.
