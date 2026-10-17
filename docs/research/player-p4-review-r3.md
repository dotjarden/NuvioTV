# Player P4 review, round 3 (Opus, Codex stand-in, narrow verification)

**Verdict: 0 P1 / 1 P2 / 2 P3**

Range: `~/Claude/Projects/NuvioMobile-player-p4`, branch `claude/player-p4`, tip `497aa405a`. The r2 fixes `e9223d0bc..497aa405a` (5 commits) were read in full, with the surrounding code at the tip. The pre-fix engine was read at `e9223d0bc:iosApp/NuvioTV/Screens/NextEpisodeAutoPlay.swift`. The lifecycle sweep covered `975a70109..497aa405a` in `NativePlaybackCoordinator.swift`, `NextEpisodeAutoPlay.swift` and `MPVPlayerView.swift`. This was read-only: no build was run.

## r2 verification

1. **P2 #1, skip seek during a rebuild (`c61b713c2`): VERIFIED.**
   - `skipSeek` records the target with `noteUserSeek` (`NativePlayerScreen.swift:408`) and hides the chip (`:410`). When `isRebuildingItem && currentItem?.status != .readyToPlay`, it logs, calls `skipPlanner.seekInterrupted()` and returns without an AVPlayer call (`:417-421`).
   - `beginSeek(.chip)` puts the interval in `consumed` and sets `chipSuppressedIndex` (`SkipSegmentPlanner.swift:139-143`). `seekInterrupted` leaves both alone (`:207-210`), so the chip cannot re-fire.
   - `updateSkipPrompt` returns before `evaluate` while rebuilding, and clears a visible chip on that tick (`NativePlayerScreen.swift:388-391`).
   - **The single read is sound.** `finishRebuild` reads `rebuildUserSeekSec`, clears it and issues the corrective seek in the same synchronous stretch (`NativePlaybackCoordinator.swift:786-792`). No skip can land between the read and the seek being issued. `finishRebuild` runs only once the item is `readyToPlay` (`:1081`), so a skip pressed after the read fails the ready-check and goes through the normal seek.
   - That skip seek supersedes the corrective seek inside AVPlayer. The corrective await returns, `rebuildStillOwns` still passes, and play continues from the skip target. The planner gets the skip's own completion. The ready-check is the right guard to keep.
   - **The test is not real:** see finding 3.

2. **P3 #2/#3, BUG-129 (`95b39de01`): VERIFIED.**
   - `searchOwnsFlow` is set in `installSearchWatcher` (`NextEpisodeAutoPlay.swift:669`). It is cleared before `searchEnded()` on every exit:
     - select (`:884`)
     - no stream (`:919`, now after `phase = .noStream`, `:920-921`)
     - `tearDownSearch`, which covers cancel, dismiss, stop and jump (`:446`, `searchEnded` last at `:463`)
     - the test seam (`:731`)
   - Every `streamsWatcher = nil` site pairs with it. `loadSources` defers on `streamsWatcher != nil || searchOwnsFlow` only (`:322`).
   - `tearDownSearch` now clears, drops a list that owned the flow, then calls `searchEnded(listWiped:)` (`:457-463`).
   - `performJump` captures `listUp` before the teardown and sets both busy flags before `beginSearch()` (`:288`, `:304-308`). `takeFlowFromSourceList` only clears `sources`, not the flags.
   - **No loops.** `searchEnded` → `loadSources` makes one clear → watch → load, and nothing calls back into an exit.
   - **No clear during an owned search.** `loadSources`' clear sits behind the `searchOwnsFlow` guard. `tearDownSearch` clears only after it has dropped ownership. `stop()` hides the column and drops `sourceListOwnsFlow` first (`:263-270`), so it never reloads.
   - **The preload is untouched.** Its `!sourceListOwnsFlow` gate is only reached before `triggered`, and every reload path runs after a search.
   - **`noteSourceListClosed` still works** (`:214-221`). The column's `onDisappear` sets `sourceColumnVisible = false`, so `searchEnded` never reloads a closed list. `onAppear` reloads the list itself (`PlayerPlaybackColumns.swift:170`).
   - **The tests drive the production code.** `selectForTesting`, `finishWithoutStreamForTesting` and `jumpForTesting` are one-line wrappers over the real `didSelect`, `finishWithoutStream` and `performJump`. Only the `settings` guard is bypassed.
   - **Every test fails on `e9223d0bc`:**
     - `testSearchEndReloadsVisibleSourceList`: the old teardown's tail is `clear, watch, load, clear`, which `assertListReloadIsLast` rejects.
     - `testSelectExitReloadsVisibleSourceList`: the old phase guard defers the list, so `sourcesBlockedBySearch` stays true.
     - `testNoStreamExitReloadsVisibleSourceList`: the old code calls `searchEnded` before `.noStream`, so the list is deferred.
     - `testEpisodeJumpShowsBusyLineThenReloads`: the old jump never sets the busy flags.
     - `testCancelAfterReloadKeepsListAlive`: it fails on the old select. With the select fix alone, it still fails on the trailing `clear`.
   - **One limit.** In the jump test, `beginSearch` returns before `installSearchWatcher` (nil settings), so its no-stream half never has `searchOwnsFlow` set. The no-stream test covers that ordering.

3. **P3 #6, resume-seek ownership (`d02851dce`): VERIFIED, with a regression.**
   - The guard (`NativePlaybackCoordinator.swift:1119-1123`) uses the `rebuildStillOwns` predicate. `phase = .playing` is set before `observePlayback` (`:1019-1021`), and the signaling retry keeps `.playing`. `isPaused` is not read on this path, so a plain resume still plays.
   - **The regression is a B17 rebuild that fires during the resume seek:** finding 1.

4. **P3 #4, log ring (`56f77b50d`): VERIFIED, with a residue.**
   - Lines are now dropped by mpv module, by FFmpeg subtitle context (`leadingContext`, `PlaybackFailureClassifier.swift:213-219`), by "external file", and by a subtitle extension that ends the URL path (`:207-208`). `Movie.SUB.1080p.mkv` and `x.sub.example` are kept.
   - The `sub-add` block runs entirely on `eventQueue` (`MPVPlayerView.swift:1554-1562`).
   - **`drainEvents()` is safe there.** It is a separate serial-queue block, not nested in `drainEvents` (`subAdd` always hops with `async`), so `mpv_wait_event` stays single-threaded. The block holds `self` strongly, so `deinit` cannot run during it. `drainEvents` returns on a nil handle or SHUTDOWN, and `subtitleLoadDrained` still runs after it.
   - **Exposure.** `addAddonSubtitles` requires `fileLoaded` (`:1508`), so a start failure is never in the window. Only failures after the file has loaded are exposed. The window loses more than r2 meant: finding 2.

5. **P3 #5, engine stages (`497aa405a`): VERIFIED. I agree with `no video stream` as `.local`.**
   - `PlayerEngineRouter.swift:38` already sends an item with no video stream to mpv. The remux only hits `RemuxSession.swift:419` on a native attempt, and that attempt then falls back to mpv.
   - Decision 17's `.local` (with [C-3]) means "our own engine failed". That is true here, and the link's real verdict comes from mpv's run.
   - A renamed audio file listed as a video is a content judgement that neither engine makes. Only forced-native (`onFallback == nil`) leaves it unremembered: acceptable.
   - `"video stream"` (`:587`) is an `AVStream` lookup failure, so it is ours too. The tests cover all three stages, with and without an HTTP code.

6. **Sweep.** The remaining mpv hunks keep every mpv call on `eventQueue`:
   - the harvest: `applyHarvestScreenshotPath`, the synthetic frame, the `autoreleasepool` capture
   - the `[MPVStats] vo=` read
   - the cache-buffering observe

   The main hops are strong. The new finding is in the coordinator.

## New findings

### 1. P2: a B17 auto rebuild before the first `play()` leaves playback stopped for good (`d02851dce` widened it)

**Defect.**
- `checkLateSubtitles` / `applyLateSubtitles` need only `server != nil`, `phase == .playing`, no rebuild in progress and no rebuild used (`NativePlaybackCoordinator.swift:661`, `:673`). `phase` turns `.playing` before the first item is ready (`:1019`). The add-on watcher calls `checkLateSubtitles` at any time (`:337`).
- `autoRebuildDeferral` does not defer at startup (`:710-714`): `isPaused` starts false, `durationSec` is 0 and `lastUserSeekUptime` is 0.
- So a slow add-on's fetch that completes after the 8 s startup gate, plus the 1 s debounce, can rebuild while the first item is still loading or during its resume seek. That only happens when a late rendition is DEFAULT and nothing is showing.
- `rebuildItem` cancels the observe task and captures `wasPlaying: timeControlStatus != .paused` (`:742`). Before the first `play()`, that is false.
- Before `d02851dce`, the cancelled task carried on after the resume seek and called `play()` and `startTrakt` on the swapped item. That was an accident, but playback started. Now the new guard returns (`Task.isCancelled`), and before ready the loop never reached `play()` at all.
- `finishRebuild` then honours `wasPlaying == false`, and nothing ever calls `play()`. `playIssued` stays false, so the stage never reaches `.started` (`:1010`). Trakt and the trackers are never started, and the resume target is replaced by the rebuild's position.

**Consequence.** On a resumed title with a slow subtitle add-on, the player can sit on "Buffering…" over a frozen frame until the viewer presses Play. No scrobble start goes out for the session. The window is narrow (the fetch must finish inside the ready + resume-seek window), but the result looks like a hang.

**Fix.** Add `playIssued` to the guards of `checkLateSubtitles` and `applyLateSubtitles`. The playback tick re-calls `checkLateSubtitles` (`:1217`), so the late files are picked up on the first tick after `play()`. Do not gate inside `rebuildItem` instead: `applyLateSubtitles` has already published the rows and recorded the URLs by then, so the auto path would be lost. Add a rig leg: `-debug.nativeLateSubtitleDelaySec 0` on a resumed title. The probe should show `late=` only after the first `stage=started`, and the item should play.

### 2. P3: the `sub-add` attribution window also swallows FFmpeg lines queued before the command

**Defect.**
- The window opens before `sub-add` and closes after a full `drainEvents()` (`MPVPlayerView.swift:1558-1561`). Wakeup blocks for events logged before `subtitleLoadBegan()` sit behind this block on the serial queue, so their LOG_MESSAGEs are drained inside the window. Every `ffmpeg*` line among them is dropped (`PlaybackFailureClassifier.swift:236-239`).
- The drop is by prefix, so main-stream `ffmpeg/demuxer` lines go as well as the URL-less `tcp:`/`tls:`/`https:` lines it targets.
- `sub-add` blocks for up to mpv's network timeout on a dead subtitle host. That is the same outage that breaks the main stream, so the stream's own protocol lines from that period are lost too.

**Consequence.** Only failures after the file has loaded. These can lose their network evidence and read `.unknown` (remembered for 8 h) instead of `.network`, unless the path monitor already says `.offline`. Subtitles are added right at file load, so warnings from the first second of playback are the ones exposed. This is low on hardware, and the outage case is the worst one.

**Fix.**
1. Call `drainEvents()` once before `subtitleLoadBegan()`, so the window holds only lines the command produced.
2. Inside the window, drop only protocol contexts (`leadingContext` ∈ `tcp`, `tls`, `http`, `https`, `crypto`), not every `ffmpeg*` prefix.

Add a ring test with an `ffmpeg/demuxer` line inside the window.

### 3. P3: `testChipSeekDeferredToRebuildDoesNotRefire` passes without the change

**Defect.** The test (`SkipSegmentPlannerTests.swift:311-319`) exercises only `beginSeek(.chip)` + `seekInterrupted()`, and the planner is unchanged in this range. It held before `c61b713c2` and would still pass if the screen's new branch were deleted. The branch that matters (no AVPlayer seek on a not-ready item, `NativePlayerScreen.swift:417`) has no test.

**Side effect worth one line in the device notes.** The deferred landing is judged as a user scrub by `observeTick`. A recap chip pressed during a rebuild therefore marks the intro it lands on as deliberate, so the intro will not auto-skip. This is acceptable for a chip press.

**Fix.** Rename or recomment the test as a planner property. Add the screen branch to the rig checklist: a late pick inside an intro, then press the chip at once. Expect `skip seek → … deferred to the late rebuild`, then `late rebuild: user seek … wins`, and no crash.

## Clean

- The skip guard, the chip hiding and the corrective-seek ownership: verified above.
- The BUG-129 flags, exits, reload order, preload and close paths, and the five tests: all fail on the pre-fix code.
- The resume-seek predicate on its own path.
- The subtitle-context and URL-anchored filters, and the threading of the `sub-add` block.
- The three `.local` stages and their tests.
- The mpv hunks of the whole range: no mpv call off `eventQueue`, no weak main hop on a path that must report.
