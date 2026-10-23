# FEAT-85: Up Next in Continue Watching (GitHub #11, erdist)

2026-10-23. Christian adopted the reporter's request: Home's Continue Watching row offers the next episode once one is finished, as the phone app does. This reverses the earlier "tvOS deliberately has no Up Next row" decision.

- Branch: `claude/feat85-up-next` in the clone `~/Claude/Projects/NuvioMobile-feat85`, cut from `tvos-shared-extraction` `769e2c55e`.
- Tip: `096a000a2`. Not pushed, not merged, not device-checked.

| Commit | What |
|---|---|
| `a67ec60b0` | erdist's patch as submitted (`git apply --3way`, applied cleanly) |
| `e35ee350e` | shared review fixes |
| `eaca92d30` | Home wiring review fixes and NuvioTVTests |
| `096a000a2` | `ContinueWatchingRow.kt` comment updated (it still said tvOS has no Up Next) |

## What the patch did

- Added `shared/.../watchprogress/ContinueWatchingNextUp.kt`:
  - `buildContinueWatchingNextUpSeeds` picks the latest finished episode per series from watch progress (the provider's seed rule) plus watched history (left out under Trakt, as on mobile). It skips a series when an in-progress episode is at least as recent, when the provider hides it, when it falls outside the provider's recency window, or when its next-up was dismissed (`dismissedNextUpKeys`).
  - `ContinueWatchingNextUp.resolveEntries` fetches metadata and runs the shared `seriesPrimaryAction` to find the next episode. Each result is a synthetic `WatchProgressEntry` at position 0 with source `nuvio_next_up`.
  - `mergeContinueWatchingWithNextUp` merges those entries into the row.
  - `removeFromContinueWatching` handles Remove: an Up Next card is dismissed, a progress card is cleared.
- Added two `WatchProgressRepository` helpers: `nextUpSourceEntries()` and `isTraktProgressActive()`.
- Swift side: `HomeViewModel` keeps the in-progress list and the next-up list apart, merges them, and refreshes Up Next 1.5 s after a trigger. Triggers are progress, watched history and CW preference changes.
- The Classic and Stage Remove actions route through `removeFromContinueWatching`. The episode badge reads "Up Next · S01E04".
- 7 jvm tests.

## What I changed and why

1. **Off the main thread.** Swift called `resolveEntries` from the main actor, and Kotlin never left it. The seed scan over every progress row and watched item, plus up to 20 `seriesPrimaryAction` runs, ran on main after every playback save. The work now runs inside `withContext(Dispatchers.Default)`.
2. **No new work on every publish.** Results are memoized per seed, keyed by `nextUpResolveKey`: source, type, series id, seed season and episode, the two synced Up Next preferences, and today's date (an episode that airs overnight is picked up the next day).
   - A refresh with no new seed fetches nothing. Only the current seeds' keys are kept, so at most 20 entries.
   - A failed fetch is not memoized; the next refresh retries it.
   - Fetches use `cacheResult = false`, the fork's bulk-caller rule (as in the Upcoming sweep), so Detail's metadata cache is not filled with 20 series.
   - Four fetches run at a time (mobile's `NEXT_UP_RESOLUTION_CONCURRENCY`; the patch fired all 20 at once).
   - A `Mutex` keeps it to one refresh at a time. A Swift task cancel does not stop a Kotlin call that is already running, so overlapping refreshes would otherwise fetch the same series twice.
3. **Seed's content id, not the meta's.** The patch called `meta.seriesPrimaryAction(...)` and built the card from `meta.id`/`meta.type`. An add-on can answer with an aliased id (for example a `tmdb:` id for a `tt` one). The progress match, the dismiss key, the in-progress dedup, Go to Details and the progress saved when the card plays would then split across two ids. The fix passes `WatchingContentRef(seed.contentType, seed.contentId)`, as mobile passes `completedEntry.content`, and keys the card by the seed's id.
4. **Merge rule matches mobile.** The patch dropped a series' Up Next whenever that series had any in-progress card. Mobile (`buildHomeContinueWatchingItems`) keeps one card per series: the more recent one wins, and the in-progress card wins a tie. Example: an episode abandoned half way, then a later episode finished. Mobile shows the Up Next; the patch kept the stale in-progress card. The fork now follows mobile. Playing an Up Next card also turns it into that episode's progress card straight away, because the new progress is newer than the completion the card was dated from.
5. **Instant dismissal.** With the patch, Remove on an Up Next card left the card on screen until the 1.5 s debounce ran. Now the preferences emission (a local Remove, or a dismissal synced from the phone) drops the card at once (`withoutDismissedNextUp`), and the re-resolve then confirms it.
6. **Hold menu.** An Up Next card has no Start Over, since it already plays from 0 (`TitleHoldMenuPolicy.continueWatchingActions(isEpisode:isNextUp:)`). Mark Episode Watched on an Up Next card skips `clearProgress`: there is no progress row to clear, and under a tracker that clear is a remote delete.
7. **No repository hook.** `WatchProgressRepository` is unchanged from the base. `uiState.value.entries` (the list mobile's Home reads) and `activeSourceState` are already public. History is left out under Trakt only, exactly as mobile's `isTraktProgressActive`.
8. **Account wipe and probe line.**
   - `ContinueWatchingNextUp.clearLocalState()` joins `TvOsAccountDataCleaner`, next to the Upcoming row's in-memory clear. The memo holds the outgoing account's show titles and art.
   - Probe line: Kermit tag `CWNextUp`, `upnext seeds=N cards=N fetched=N failed=N source=… ids=…`, logged once per change.
   - Swift logs `NSLog("[UpNext] resolution failed: …")` on a thrown error; the patch used `print`.

Kept from the patch: the seed rules, the dismiss key (`nextUpDismissKey(seriesId, seedSeason, seedEpisode)`, the same key mobile writes), the synthetic-entry approach, the 20-series cap, the 1.5 s debounce, the triggers, the badge text and the Remove routing.

## Design as landed (ten lines)

1. Triggers: progress, active-source, Trakt days-cap, watched-history and CW-preference emissions. Each calls `HomeViewModel.scheduleNextUpRefresh()` (1.5 s debounce).
2. `ContinueWatchingNextUp.resolveEntries` moves to `Dispatchers.Default` and runs one refresh at a time.
3. Seeds: the latest finished episode per series (furthest or latest, from the synced preference), from progress plus history (not under Trakt).
4. Skipped: an in-progress episode at least as recent, a provider-hidden show, outside the Trakt window, a dismissed key. At most 20 seeds, newest first.
5. Each seed resolves through the memo, or else through `MetaDetailsRepository.fetch(cacheResult = false)` (four at a time) followed by the shared `seriesPrimaryAction` with the seed's content ref.
6. A resume action, no next episode, or the seed episode itself gives no card. Otherwise the card is a position-0 `WatchProgressEntry` with source `nuvio_next_up`, dated from the seed.
7. Home merges the cards into the provider-aware row: one card per series, the newer one wins, in-progress wins a tie.
8. A card plays through the existing `ResumeTarget` / stream picker path from 0. Its progress then replaces the card.
9. Remove on a card adds the profile-synced dismiss key; playing any episode of the series clears its keys (existing `WatchProgressRepository.upsert` rule).
10. Nothing persisted. The memo and keys are in memory, wiped with the account.

## Gates (clone tip `096a000a2`)

| Gate | Result |
|---|---|
| `:shared:jvmTest` | 1617 tests, 0 failures (16 in `ContinueWatchingNextUpTest`) |
| `:shared:tvosSimulatorArm64Test` | 1637 tests, 0 failures |
| `:composeApp:iosSimulatorArm64Test` | 438 tests, 0 failures |
| Release sim build (FA87 id) | BUILD SUCCEEDED |
| NuvioTVTests | 2320 executed, 5 skipped, 0 failures (TitleHoldMenuPolicyTests gains 2 Up Next cases plus asserts) |
| UI: `BatchAHomeReturnUITests` | 9/9 passed |
| UI: `HomeBodyCountUITests` | 2/2 passed |

Caveat: the FA87 fixture is a guest with no watch history, so the UI legs show Home is unchanged when there is no Up Next. No UI leg renders an Up Next card. The DEBUG Continue Watching seed could build one (a completed episode entry), but the card needs a live metadata fetch, so I did not add a leg.

## Settings decision

- Mobile has no Up Next on/off toggle; it always builds next-up items. So: no new setting.
- Mobile's two behaviour toggles, "Up next from furthest episode" (default on) and "Show unaired next up" (default on), live in the synced `continue_watching_settings_payload` and are honoured here.
- tvOS has no Settings rows for either toggle (neither did it before this change). A tvOS user changes them on the phone.
- The new user-facing string is `String(localized: "Up Next \u{00B7} \(code)")` (catalog key `Up Next · %@`), in the patch and kept. It is not in `Localizable.xcstrings`; it needs adding to the catalog in the next localization pass. It shows in English until then.

## Device check (coordinator, Test profile)

Fixture: in the Test profile, a series with one finished episode and no in-progress episode, with Nuvio Sync as the progress source. Make one by marking S1E1 watched from Detail's episode hold menu (or play S1E1 past 90 %). Make sure no other episode of that series is part way through.

1. Name the profile (Test) and run `scripts/device/ready.sh` first.
2. Home shows a card for the series reading "Up Next · S01E02" within about 2 s, with no progress bar. The console stream shows `upnext seeds=… cards=1 … ids=<id>:1:2`.
3. Press the card. The stream picker opens for S01E02 and playback starts at 0:00.
4. Play about a minute and back out. The card is now an S01E02 progress card with a bar, and there is one card for the series, not two.
5. Hold the card while it is Up Next again (repeat steps 1-2 with another episode). The menu reads Play Manually, Go to Details, Mark Episode Watched, Remove from Continue Watching, with no Start Over.
6. Mark Episode Watched. Within about 2 s the card moves to the next episode.
7. Remove from Continue Watching. The card leaves at once. On the phone in the same profile, after a sync, the same series shows no Up Next. Reverse it: dismiss one on the phone, and after the sync pull it is gone here.
8. Go to Details from an Up Next card. It opens the right series.
9. Mark the last released episode watched. No card appears for that series.
10. Optional, if the Test profile has Trakt connected: switch the source to Trakt and confirm the same series still gets its card.
11. Clean up: unmark the watched episodes and remove the progress rows. Remove any dismissals by playing an episode of the series.

## Open questions for Christian

1. **Unaired next-ups.** "Show unaired next up" defaults on (synced), so a series whose next episode has not aired gets a card that opens an empty stream picker. Mobile dates such cards from the release date and offers a Split Upcoming sort mode; tvOS already has an Upcoming row. Options:
   - keep as is (parity with the setting);
   - force aired-only on tvOS Home;
   - honour the synced sort mode (`ContinueWatchingSortMode`), which tvOS ignores today.
2. **Retry on failed fetches.** A failed metadata fetch (for example add-ons not ready at cold start) is retried only on the next trigger. Mobile retries three times with backoff. Should a retry be added if the device check shows missing cards after launch?
3. **Settings rows.** Should tvOS show the two synced Up Next toggles in Settings? That would need two new catalog strings.
4. **Localization.** The `Up Next · %@` key needs adding to the catalog.

## GitHub #11 reply (NOT SENT)

Copy rule: `deslop.py` 5/5 CLEAN, 115 words. The rival-model cleanse (`cleanse.sh`) exited 1 with no output (Codex quota is out until 10-29), so it was not cleansed.

> Thanks for the request and for the patch, erdist. We're adding it: the next build puts an Up Next card in Home's Continue Watching row once you finish an episode, as the phone app does.
>
> Your design is kept, with a few review changes: the work runs off the main thread, a series' result is reused until you finish another episode, and each series shows one card, the newer one winning, as on the phone. Remove on an Up Next card hides it on the phone too, and its hold menu drops Start Over.
>
> There is no new setting. The phone's "Up next from furthest episode" and "Show unaired next up" choices apply here too.
