# Upstream port plan — 2026-10-25

Upstream `NuvioMedia/NuvioMobile` (cmp-rewrite) has not moved since the 2026-10-24 plan: tip is still `c114d6fb6` (0.6.4-beta, build 147), 0 new commits. Fork tip checked: submodule `888961236`, outer `ccfe935`.
**New baseline: `c114d6fb6`** (unchanged).

NuvioTV Android (`NuvioMedia/NuvioTV` `dev`) also unchanged at `b36db8083`, so no Android plan file today.

## Recommended ports

Nothing new. The open items in `docs/upstream-port-plan-2026-10-24.md` stand: compare `TraktProgressPagingTest.kt` against the fork's `TraktProgressFetchFailureTest.kt` (LOW, ~20 min); badge-rule regex cache (LOW, ~30 min); debrid regex cache and single facts pass (LOW, ~45 min); optional Home-hero ratings behind `showOnHero`, default Off (LOW-MED, ~3 h). Carried from earlier plans: player badges + pack choice, mpv `hwdec-software-fallback=300`, MDBList lists/sort, TorBox pagination.
