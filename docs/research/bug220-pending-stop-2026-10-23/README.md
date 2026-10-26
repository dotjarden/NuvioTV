# BUG-220: write-ahead queue for Trakt scrobble stops (2026-10-23)

Branch `claude/bug220-pending-stop` in the clone `~/Claude/Projects/NuvioMobile-bug220`, cut from `tvos-shared-extraction` `1b2fc99f3`. Not pushed, not merged. Background: `docs/research/bug219-220-code-read-2026-10-22.md` §BUG-220.

## Design in ten lines

1. Every Trakt `/scrobble/stop` is written to a per-profile queue (`TraktPendingScrobbleStopStorage`, NSUserDefaults `trakt_pending_scrobble_stops_<profileId>`) before the request leaves (`TraktScrobbleEngine.send` → `TraktScrobbleStopOutbox.sendStop`), stamped with the item, progress, profile id, time and the Trakt user slug.
2. The send reports what happened: SENT (2xx/409), SKIPPED (the 8 s dedupe) and REJECTED (other 4xx) delete the entry; NOT_READY (no auth, profile changed) and OFFLINE (transport failure) keep it; RETRYABLE (5xx, 401/403/408/420/423/429) keeps it and counts an attempt (dropped at 5).
3. Replay runs at profile selection (tvOS fan-out step `traktPendingScrobbleStops` after `traktAuth`; every launch enters through it) and whenever `TraktAuthRepository.isAuthenticated` turns true; requests go to one worker (one pending request is kept while it is busy; a failed drain does not end it).
4. Before replaying, the drain reads Trakt: `/sync/playback` (paused rows with their progress) and `/sync/history/{movies|episodes}?start_at=<oldest entry − 10 min>`. Reads are lazy (playback once, history at most once per kind, each when the first entry needs it): an entry that cannot be checked is never sent and the drain stops there, but entries before the failed read may already have been sent. Kept lazy rather than prefetched, so a drain of movies only never reads episode history.
5. A stop at 80 % or more is replayed only when Trakt has no matching play since it was queued, so a live stop whose response was lost never becomes a second play.
6. A stop below 80 % is dropped when Trakt's paused row for the item is within 1 point of it (our own stop landed, answer lost; any timestamp), when the row was paused after the entry was queued (no slack) at another position (another device), or when a play exists since then (finished elsewhere; checked even when a stale paused row exists).
7. An entry queued for another Trakt account (slug differs) is dropped; with the account not known, the drain fetches the user settings once and then waits.
8. Each entry is sent once per drain, oldest first, while its profile is active; a RETRYABLE failure moves on to the next entry, OFFLINE/NOT_READY stop the drain; a live send's entry is in flight and skipped; when anything was sent, Trakt progress is refreshed once.
9. Bounds: 10 entries per profile; 24 h for stops at 80 % or more, 48 h below; stops under 1 % and stops from a profile with no Trakt account are sent but never queued. Only stops are ever replayed, never starts.
10. Queue writes carry a wipe generation (per profile, plus a global one for sign-out) and are never written back after a wipe: sign-out (AccountDataStores entry + `TraktScrobbleRepository.clearLocalState` in both cleaners), Trakt disconnect (under the queue lock) and profile removal. The read side (`WatchProgressSourceProjection`) is untouched.

## Commits

- `e2e0364ba` storage (Apple/Android/JVM), registry entry, queue + outbox, first tests.
- `f4d5c0be9` `TraktScrobbleRepository` routes stops through the outbox and replays; tvOS fan-out step, composeApp adapter, disconnect/profile-removal clear, Android init.
- `7cb27dcc9` the queue, replay, stop-status and stop-failure lines also go to stdout (Kermit writes to os_log, which `devicectl --console` cannot see).
- `d80820a9e` review round 2 (P3s): position-aware playback check, history check behind a stale paused row, per-profile wipe generation, resilient replay worker, one account fetch per drain, reworded read semantics.
- `a89835ee9` review round 1 (2 P2 + 5 P3): Trakt pre-checks, 24 h / 48 h limits, in-flight set, wipe generation, account slug, no head-of-line block, auth watcher without `drop(1)`; the request path moves into the injectable `TraktScrobbleEngine`. One commit, not seven: the fixes share `TraktPendingScrobbleStops.kt` and the engine extraction, and the intermediate states would not compile.

## Review round 1 (coordinator, on `7cb27dcc9`): what changed

| Finding | Fix |
|---|---|
| P2-1 watched replay can add a duplicate play | history check since queued − 10 min before any replay at ≥ 80 %; 24 h limit |
| P2-2 replay ignores what Trakt holds now | `/sync/playback` once per drain; newer paused row or newer play drops the entry; 48 h limit below 80 % |
| P3-3 same stop sent twice during a live retry | outbox in-flight id set; the drain skips it |
| P3-4 a wipe can be written back | wipe generation checked before every save; disconnect via `queue.clearProfile` (lock); removal and sign-out invalidate, then clear under the lock; the dead helpers now have callers |
| P3-5 token invalidation keeps entries | user slug per entry, matched on replay (survives a reconnect to the same account) |
| P3-6 head-of-line block | RETRYABLE continues; OFFLINE / NOT_READY / failed read stop |
| P3-7 auth watcher `drop(1)` | `distinctUntilChanged()` without `drop(1)`; its first emission is the first selection's drain |

## Review round 2 (coordinator, on `a89835ee9`: CLEAN at P2+, P3s)

| Finding | Fix |
|---|---|
| P3-a "every remaining entry is kept" was inaccurate | reworded: an entry that cannot be checked is never sent; reads stay lazy (one per kind) |
| P3-b 10-min slack drops newer local progress | playback progress decoded; within 1 point = ours; newer = paused after `createdAtMs` (no slack) at another position |
| P3-c an older paused row skipped the history check | history checked in that branch too |
| P3-d the worker died on a thrown replay | try/catch per request (CancellationException rethrown); arm/launch races commented (drains serialise) |
| P3-e global wipe generation | per-profile generations under the lock; the global one only on sign-out |
| P3-f slug null when the settings fetch failed | one `refreshUserSettings` per drain, then re-evaluate |

## Gates (on the tip `d80820a9e`)

- Kotlin: `:shared:jvmTest` 1708/0, `:shared:tvosSimulatorArm64Test` 1728/0, `:composeApp:iosSimulatorArm64Test` 438/0. `TraktPendingScrobbleStopsTest` 49/0 and `TraktScrobbleEngineTest` 15/0 on both shared targets; `AccountDataStoresTest` 13/0.
- NuvioTVTests (FA87, `DerivedDataUITests`): 2324 tests, 0 failures, 5 skipped, TEST SUCCEEDED.
- Release sim build (FA87 id, `DerivedData`): BUILD SUCCEEDED (the first run failed on a transient "no space left on device" from another build; the rerun passed).
- Not run: UI legs (no Swift change), device pass (coordinator's).

## Device script (coordinator; Test 2 on the Living Room box, Trakt connected, Watch Progress Source = Trakt)

Run `scripts/device/ready.sh` first. Build and install the branch tip. Launch with the console stream: `scripts/device/console.sh start`. Every line below is printed to stdout with the prefix `[TraktScrobble]`: `console.sh grep "TraktScrobble"`.

**Pass A, live path.** Pick a film with no Trakt progress, play about 2 min on mpv, press Menu to leave the player, wait 10 s.
- Expect `Trakt pending stop queued id=<id> profile=<n> item=movie:tt…:<year> progress=<p>%`, then `Trakt scrobble stop status=201` and `Trakt pending stop live ok id=<id> result=SENT (removed)`.
- Kill the app (`console.sh stop`), relaunch (`console.sh start`), pick Test 2. No `replay:` line should appear (nothing pending). Continue Watching and the Detail page must show the position.
- If the position is missing here although the stop was `SENT`, the stop is not the problem: Trakt's `/sync/playback` read or its mapping is, and this branch does not fix it (open question 1).

**Pass B, replay path.** Second film, play about 2 min, press Menu and run `console.sh stop` at once (under a second), so the app dies before Trakt answers.
- Expect `Trakt pending stop queued …` and no `live ok` line before the kill.
- Relaunch with `console.sh start`, pick Test 2. Expect `Trakt pending stop replay: 1 pending for profile <n>`, `Trakt scrobble stop status=201 (replay)`, `Trakt pending stop replayed ok id=<id> result=SENT (removed)`, `Trakt pending stop replay done profile=<n> sent=1 kept=0 dropped=0 superseded=0`.
- Also a pass: `Trakt pending stop replay skipped id=<id>: Trakt already holds this position (removed)` with `superseded=1`. That means Trakt did receive the stop before the kill (response lost); the pre-check saw it and sent nothing. The position must still show.
- Continue Watching and Detail must show the position after the refresh (a few seconds after Home loads).
- `Trakt pending stop replay failed: …` means a drain threw; the entry is kept and the next trigger retries.
- A `deferred` line means the replay waited: `no Trakt auth`, `Trakt account not known yet` or `Trakt state could not be read`; relaunch once more.
- If the kill landed after Trakt answered (a `live ok` line before the kill), Pass B turned into Pass A; repeat it.

Afterwards, remove the two films' progress from Test 2 on Trakt.

## Simkl and MDBList

Neither queues. Simkl (`SimklMutationRepository.scrobble`) sends once with `SimklRetryPolicy.NEVER` and commits the result into its sync snapshot only after the server answers. MDBList (`MdbListScrobbleService.scrobble`) posts inside `sync.write` and applies the receipt only on success. Mirroring is not trivial: both take `TrackingMediaReference` events (Simkl enriches them from its snapshot at send time, MDBList needs an `MdbListAuthScope` and a resolved mutation target), and both commit receipts into their own snapshots. Recommended follow-up, not done here: one outbox at `TrackingScrobbleCoordinator` level that persists STOP `TrackingScrobbleEvent`s per provider and profile, built on the same queue class. The same read-side hiding applies when Simkl or MDBList is the Watch Progress Source.

## Known small items

- Android `TraktPendingScrobbleStopStorage` writes with `commit()` (synchronous disk IO, on the main thread when the player's stop arrives there). Kept so the entry is on disk before the request leaves; the payload is a few KB. Not fixed.
- The sign-out wipe's on-disk erase runs in the platform cleaner, outside the queue lock; the global wipe generation stops any write that read before it, and a clear of every slot under the lock follows. A write between a generation check and its save (microseconds) remains theoretically possible.

## Open questions

1. If Pass A loses the position with a `SENT` stop, the cause is on the read side (`TraktProgressRepository` `/sync/playback`, held in memory), not the stop; the queue would not help.
2. Killing the app from inside the player (app switcher while playing) sends no stop at all: neither player has a background hook, and `stopTrakt` runs only from `viewDidDisappear`/deinit. A provisional stop written at the 5 s progress save, or on `willResignActive`, would cover it; not in scope.
3. An entry queued before the user slug was known (settings not fetched yet) carries no slug and replays into whichever account is connected; disconnect still clears it.
4. A playback removed on Trakt from another device leaves no trace, so a stop below 80 % queued before that removal can bring it back within 48 h.
5. The 10-entry, 24 h / 48 h, 5-failure, 10-minute history slack and 1-point same-position values are judgement calls.
