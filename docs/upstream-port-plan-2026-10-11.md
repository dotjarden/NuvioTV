# Upstream port plan — 2026-10-11

Upstream `NuvioMedia/NuvioMobile` (cmp-rewrite): `612bdaef5` -> `ee3d91506` (0.5.9-beta, 2026-10-10). 0 changes under `shared/`; all in composeApp, i18n, store.json, iosApp version.

## Recommended ports
None new and urgent. Prior open items still stand: 2026-10-10 TorBox mylist pagination (MEDIUM, upstream be81802c8), 2026-10-08 MDBList sort by release date (MEDIUM, d8ce7258) and ytId-only addon streams (LOW-MED, 94976222).

## Optional / decision-dependent
1. Jellyfin/Emby media-server fixes (upstream PR #2207, commits 5a24beb09, c2ed4c5e1, de69f9a98, e05178c89, 6f98691d6, 1bb2b10eb; composeApp `features/servers/*`, `mediabrowser/MediaBrowserProvider.kt` + tests). Fork has NO servers feature, so these only matter IF you decide to port Jellyfin/Emby (PR #2081). If you do, port from ee3d91506 (not the original PR) so these fixes come with it: search each server once per type, skip unplayable versions, mixed movie/show libraries, genre-required libraries, playback-info flagged as playback.
2. 9b5500311 "Defer custom poster URL resolution to UI layer": Library poster pattern now applied per visible row in the UI (remember-d) instead of mapping all items on every publish(). Perf nicety. LOW; apply only if the tvOS library screen re-maps all items with the poster pattern on each state publish (check where fork calls withCustomPosterUrls for Library).

## N/A
Bengali/other i18n (1ba9ddd1e, bb9b7e467), version bump/store.json, merges.

## Claude Code prompt
"Read docs/upstream-port-plan-2026-10-11.md and the open items from 10-10 and 10-08. Do the 10-10 TorBox pagination port first (shared DebridApiClients.kt + tests), then 10-08 MDBList sort."
