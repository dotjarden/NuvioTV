# BUG-220: write-ahead queue for Trakt scrobble stops (2026-10-23)

Branch `claude/bug220-pending-stop` in the clone `~/Claude/Projects/NuvioMobile-bug220`, cut from `tvos-shared-extraction` `1b2fc99f3`. Not pushed, not merged. Background: `docs/research/bug219-220-code-read-2026-10-22.md` §BUG-220.

## Design in ten lines

1. Every Trakt `/scrobble/stop` is written to a per-profile queue (`TraktPendingScrobbleStopStorage`, NSUserDefaults `trakt_pending_scrobble_stops_<profileId>`) before the request leaves (`TraktScrobbleRepository.sendScrobble` → `TraktScrobbleStopOutbox.sendStop`).
2. An entry holds the item (ids, title, year, season/episode), the progress, the profile id, a timestamp and an HTTP-failure count.
3. `deliver()` now reports what happened: SENT (2xx/409) and SKIPPED (the 8 s dedupe) delete the entry; REJECTED (400/404/422, any other 4xx) deletes it; NOT_READY (no auth, profile changed) and OFFLINE (transport failure) keep it; RETRYABLE (5xx, 401/403/408/420/423/429) keeps it and counts an attempt (dropped at 5).
4. Replay (`TraktScrobbleRepository.replayPendingStops`) runs at profile selection (a new tvOS fan-out step `traktPendingScrobbleStops` right after `traktAuth`; every launch enters through it) and again whenever `TraktAuthRepository.isAuthenticated` turns true later (device-flow connect, credential sync).
5. A replay sends each entry once, oldest first, only while that profile is active; it stops at the first OFFLINE/RETRYABLE/NOT_READY, and when anything was sent it runs `TraktProgressRepository.invalidateAndRefresh()` so Continue Watching picks up the replayed position.
6. Only stops are ever replayed, never starts. A newer stop for the same item supersedes the older entry; the drain skips an entry superseded while it runs and leaves alone the item of a session that is open now.
7. Bounds: 10 entries per profile, nothing older than 7 days. Stops below 1 % (Trakt answers 422) and stops from a profile with no Trakt account connected are sent but never queued.
8. Every queue write is a fresh read-modify-write under one mutex that touches only entries still present, so a sign-out wipe landing mid-drain is never written back.
9. The store is in `AccountDataStores` (ProfileScoped `trakt_pending_scrobble_stops`, Android `nuvio_trakt_pending_scrobbles`), so sign-out wipes every profile's queue; Trakt disconnect and profile removal clear that profile's queue.
10. The read side is not touched: `WatchProgressSourceProjection` still hides representable local rows, so a removal made on Trakt is never resurrected from the local copy.

## Commits

- `e2e0364ba` storage (Apple/Android/JVM), registry entry, queue + outbox, 24 unit tests.
- `f4d5c0be9` `TraktScrobbleRepository` routes stops through the outbox and replays; tvOS fan-out step, composeApp adapter, disconnect/profile-removal clear, Android init.
- `7cb27dcc9` the queue, replay, stop-status and stop-failure lines also go to stdout (Kermit writes to os_log, which `devicectl --console` cannot see).

## Gates (on the tip `7cb27dcc9`)

- Kotlin (rerun on the tip): `:shared:jvmTest` 1668/0, `:shared:tvosSimulatorArm64Test` 1688/0, `:composeApp:iosSimulatorArm64Test` 438/0. New `TraktPendingScrobbleStopsTest` 24/0 on both shared targets; `AccountDataStoresTest` 13/0.
- NuvioTVTests (FA87, `DerivedDataUITests`): 2324 tests, 0 failures, 5 skipped, TEST SUCCEEDED.
- Release sim build (FA87 id, `DerivedData`): BUILD SUCCEEDED.
- Not run: UI legs (no Swift change), device pass (coordinator's).

## Device script (coordinator; Test 2 on the Living Room box, Trakt connected, Watch Progress Source = Trakt)

Run `scripts/device/ready.sh` first. Build and install the branch tip. Launch with the console stream: `scripts/device/console.sh start`. Every line below is printed to stdout with the prefix `[TraktScrobble]`: `console.sh grep "TraktScrobble"`.

**Pass A, live path.** Pick a film with no Trakt progress, play about 2 min on mpv, press Menu to leave the player, wait 10 s.
- Expect `Trakt pending stop queued id=<id> profile=<n> item=movie:tt…:<year> progress=<p>%`, then `Trakt scrobble stop status=201` and `Trakt pending stop live ok id=<id> result=SENT (removed)`.
- Kill the app (`console.sh stop`), relaunch (`console.sh start`), pick Test 2. No `replay:` line should appear (nothing pending). Continue Watching and the Detail page must show the position.
- If the position is missing here although the stop was `SENT`, the stop is not the problem: Trakt's `/sync/playback` read or its mapping is, and this branch does not fix it (open question 1).

**Pass B, replay path.** Second film, play about 2 min, press Menu and run `console.sh stop` at once (under a second), so the app dies before Trakt answers.
- Expect `Trakt pending stop queued …` and no `live ok` line before the kill.
- Relaunch with `console.sh start`, pick Test 2. Expect `Trakt pending stop replay: 1 pending for profile <n>`, `Trakt scrobble stop status=201 (replay)`, `Trakt pending stop replayed ok id=<id> result=SENT (removed)`, `Trakt pending stop replay done profile=<n> sent=1 kept=0 dropped=0`.
- Continue Watching and Detail must show the position after the refresh (a few seconds after Home loads).
- If the kill landed after Trakt answered, Pass B turns into Pass A (a `live ok` line before the kill); repeat it.

Afterwards, remove the two films' progress from Test 2 on Trakt.

## Simkl and MDBList

Neither queues. Simkl (`SimklMutationRepository.scrobble`) sends once with `SimklRetryPolicy.NEVER` and commits the result into its sync snapshot only after the server answers. MDBList (`MdbListScrobbleService.scrobble`) posts inside `sync.write` and applies the receipt only on success. Mirroring is not trivial: both take `TrackingMediaReference` events (Simkl enriches them from its snapshot at send time, MDBList needs an `MdbListAuthScope` and a resolved mutation target), and both commit receipts into their own snapshots. Recommended follow-up, not done here: one outbox at `TrackingScrobbleCoordinator` level that persists STOP `TrackingScrobbleEvent`s per provider and profile, built on the same queue class. The same read-side hiding applies when Simkl or MDBList is the Watch Progress Source.

## Open questions

1. If Pass A loses the position with a `SENT` stop, the cause is on the read side (`TraktProgressRepository` `/sync/playback`, held in memory), not the stop; the queue would not help.
2. Killing the app from inside the player (app switcher while playing) sends no stop at all: neither player has a background hook, and `stopTrakt` runs only from `viewDidDisappear`/deinit. A provisional stop written at the 5 s progress save, or on `willResignActive`, would cover it; not in scope.
3. A replayed stop at 80 % or more adds a Trakt play at replay time. A duplicate is only possible if Trakt received the live stop but the app died before deleting the entry; Trakt's 409 window covers a replay within the item's runtime, a later one would add a second play. Acceptable, or should replays at 80 % or more be limited to, say, 24 h?
4. After a token invalidation the entry stays (NOT_READY) and replays once Trakt is reconnected. A different Trakt account connected within 7 days would receive it; disconnect clears the queue, invalidation does not.
5. The 10-entry and 7-day bounds and the 5-failure limit are judgement calls.
