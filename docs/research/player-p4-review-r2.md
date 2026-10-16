# Player P4 review, round 2 (Opus, Codex stand-in)

**Verdict: 0 P1 / 1 P2 / 5 P3**

Range: `~/Claude/Projects/NuvioMobile-player-p4`, branch `claude/player-p4`, tip `e9223d0bc`. The r1 fix commits are `9ed72bc18..e9223d0bc` (7 commits, 9 files), read in full. The second pass covered `975a70109..e9223d0bc` (30 commits): the coordinator, screen, panel host, NextEpisodeEngine, classifier, the mpv failure, log and startup paths, FirstPlayAutoPlay, StreamPickerView, and the remux stage strings. Line numbers are at the tip. This was read-only: no build was run.

## r1 verification

- **P2 #1, rebuild ownership: VERIFIED.** `rebuildStillOwns` (`NativePlaybackCoordinator.swift:833-835`) checks cancellation, `self.player === player`, `playerItem === item` and `phase == .playing`. It runs after the corrective seek, before `play()`, after the audible load and after the legible load (`:792-801`). Every early return goes through `abandonRebuild` (`:838-842`), which clears `isRebuildingItem` and `rebuildUserSeekSec`. `stop()` (player nil) and `fallbackMidPlay` (`.failed` plus a cancel, `:1761-1766`) both fail the check. The observe loop's own guard after `finishRebuild` (`:1081`) still ends the task. There is no unit test for the guards (it would need a player); acceptable.
- **P2 #2, watchdog classification: VERIFIED.** The watchdog branch is gone (`PlaybackFailureClassifier.swift:24-30`). A quiet fire is `.unknown` (remembered), a network line keeps `.network`, an HTTP line wins, and `applyingPath` still gives `.offline`. `testWatchdogWithoutNetworkEvidenceIsRemembered` calls the real `fromMpvLog` with the same `watchdogFired: true` argument as the producer (`MPVPlayerView.swift:3466`). Release-note impact is under "Release-note deltas" below.
- **P3 a, generation test: VERIFIED.** `endForcedSearchWithoutGenerationBumpForTesting` (`NextEpisodeAutoPlay.swift:700-704`) nils the watcher, hides the phase and calls `searchEnded()`. With the column not visible, that does not reach `loadSources`, so nothing bumps the generation. `testGenerationSeamDoesNotBump` proves the seam leaves it alone. Deleting `searchGeneration += 1` at `:322` would now fail `testSearchEmissionAfterSourceListIsDropped`.
- **P3 b, BUG-129 busy line: NOT VERIFIED.** The reverse race is fixed for the threshold search (`takeFlowFromSourceList`, `:662-669`). The self-reload does not work on any live exit path, and the jump path skips the busy line. See findings 2 and 3.
- **P3 c, log ring: PARTLY VERIFIED.** `clear()` at `MPV_EVENT_START_FILE` runs inside the `eventQueue` event loop, in event order with the END_FILE snapshot (`MPVPlayerView.swift:3673-3676`). The append-time filter drops more than subtitle lines and lets some subtitle noise through. See finding 4.
- **P3 d, `.local` vs `.noMedia`: VERIFIED, with a residue.** A mid-play loopback error is `.local` (`PlaybackFailureClassifier.swift:130`, call site `NativePlaybackCoordinator.swift:1146`). Engine-internal stages win over any FFmpeg code (`:148-161`). A loopback error before start stays `.noMedia`, which matches spec decision 17 ("never produced media with the host reachable" is remembered). The stage set misses a few of our own stages: finding 5.
- **P3 e, user seek during a rebuild: VERIFIED.** `noteUserSeek` is called from `seek(toChapter:)` (`:862`) and `skipSeek` (`NativePlayerScreen.swift:401`). It records only while `isRebuildingItem` is true. The value is cleared at rebuild start (`:749`), when it is consumed (`:790`) and on abandon. `lateRebuildsUsed` caps rebuilds at one, nothing else reads the value, and the resume path never sees it. A value set after it was consumed (during the group loads) is never read. The new skip-seek path has a separate problem: finding 1.
- **P3 f, `.ts` recipe and HEAD skip: VERIFIED.** The recipe is checked in (`NativePlayerParityUITests.swift:346-351`). ffmpeg picks MPEG-TS from the `.ts` extension. `XCTSkipUnless(fixtureAnswers(url))` (`:362`) uses a 5 s HEAD request, and the semaphore orders the write to `ok` before the read.
- **P3 g, off-leg teardown: VERIFIED.** The teardown is registered before the first launch (`:466`) and keys on `found.before`, which `onRead` sets before any press (`:544`). It restores the value it found, and it does nothing if the row was never read. The guest-only rule is a comment, not a skip: acceptable as long as FA87 stays a guest fixture.
- **P3 #10, device-only items:** unchanged. Carry the pause card, the any-press recogniser, the AVTextStyleRule override and the 3 s gate `took=` checks into the device pass.

## New findings

### 1. P2 (unconfirmed on tvOS 27): a skip seek during a B17 rebuild uses a completion-handler seek on an item that is not ready

**Defect.** `skipSeek` (`NativePlayerScreen.swift:397-418`) always issues `await player.seek(to:toleranceBefore:toleranceAfter:)`, the completion-handler variant. During a B17 rebuild, `player.currentItem` is the new item from `replaceCurrentItem` (`NativePlaybackCoordinator.swift:766`), and it stays not-`readyToPlay` until `finishRebuild` (typically about 0.8 s, up to the 12 s fallback). Nothing gates the skip chip or auto-skip on `isRebuildingItem`. `autoRebuildDeferral` covers pauses, the last 5 minutes and recent seeks, but not "inside a skip segment", and a late-row pick rebuilds anywhere. Before P4, no mid-play item swap existed, so this window is new.

**Consequence.** AVFoundation has historically raised `NSInternalInconsistencyException` ("AVPlayerItem cannot service a seek request with a completion handler until its status is AVPlayerItemStatusReadyToPlay") for a completion-handler seek on an item that is not ready. If tvOS 27 still does this, pressing the skip chip, or an auto-skip firing, in the rebuild window crashes the app. If it does not, the seek either completes with `finished=false` (the planner calls it a scrub) or is overwritten by the corrective seek, which `noteUserSeek` now aims at the same target. I could not confirm the current behaviour from the code. The chapter seek uses the non-completion variant (`:863`) and is safe.

**Fix.** In `skipSeek`, when `coordinator.isRebuildingItem && player.currentItem?.status != .readyToPlay`, call only `noteUserSeek(to:)`. Skip the AVPlayer call and let `finishRebuild`'s corrective seek land on the target, then report completion to the planner from there (or call `seekInterrupted()` so the next tick reads it as a scrub). Alternatively, hide the chip and suppress auto-skip while `isRebuildingItem`. Add a rig check: a late pick inside an intro segment, then press the chip at once.

### 2. P3: the Sources column's self-reload fails on every live search exit (r1 P3 b)

**Defect, select and no-stream exits.** `didSelect` (`NextEpisodeAutoPlay.swift:844`) and `finishWithoutStream` (`:878`, before `phase = .noStream` at `:879`) call `searchEnded()` while `phase` is still `.searching`. `searchEnded` calls `loadSources()`, whose guard `phase != .searching` (`:302`) fails, so the list is deferred again and `sourcesBlockedBySearch` goes back to true. Nothing calls `searchEnded` after that. The log prints "loading the list" followed by "deferred".

**Defect, cancel exit.** `cancel()` and `dismissIfVisible()` go through `tearDownSearch()`. There `searchEnded()` (`:426`) does reload the list, and then `hooks.clearStreams()` (`:433`) runs right after it. `clearEpisodeStreams()` cancels the job the list just started and resets the flow (`PlayerStreamsRepository.kt:121-125`). The list's watcher sees an empty, not-loading state. Depending on conflation, the column shows "No alternate sources found yet." or a spinner that never stops.

**Why the tests pass.** `testSearchEndReloadsVisibleSourceList` ends the search with `cancel()`, which sets `.hidden` first, and the test `clearStreams` hook only counts calls (`NextEpisodeEngineTests.swift:68`). So the one path the test covers is the one the trailing clear breaks on device, and the select and no-stream paths have no test.

**Consequence.** When the search ends by selecting a stream (the common case), the busy line "Finding the next episode's source…" stays up through the countdown and after the card hides, until the viewer re-opens the tab. The cancel path shows the same empty or stuck list that r1 flagged. This is copy and UI only: playback is not affected.

**Fix.** Do the reload once the search really no longer owns the flow. Have `loadSources` key on the search watcher plus an explicit `searchOwnsFlow` flag instead of the phase, or set the phase before `searchEnded()` in both exits. In `tearDownSearch`, call `searchEnded()` after `hooks.clearStreams()`. Tests: make the test `clearStreams` hook push an empty state to the live list watcher, and end the search through `didSelect` and `finishWithoutStream` with the phase still `.searching`.

### 3. P3: an episode jump skips the reverse-race busy line

**Defect.** `jumpToEpisode` (`:273-292`) calls `tearDownSearch()` (which clears the busy flags through `searchEnded`) and then `cancelSourceLoad()` (`:278`, which sets `sourceListOwnsFlow = false` and blanks `sources`) before `beginSearch()`. `takeFlowFromSourceList` therefore never sees the list as owner, so `sourcesBlockedByJump` is never set by the jump.

**Consequence.** The viewer picks an episode in the Episodes column while the Sources column is on screen beside it (both are on the Playback tab). The Sources column drops to "No alternate sources found yet." instead of "Finding the episode's source…". When the jump finds no stream, the busy flag was never set, so `searchEnded` does not reload and the column stays empty.

**Fix.** Capture `let listUp = sourceListOwnsFlow || sourcesBlockedBySearch` before the teardown, and set both busy flags after `beginSearch()` when `listUp && sourceColumnVisible`. Or have `takeFlowFromSourceList` also trigger on `sourceColumnVisible`.

### 4. P3: the log-ring filter drops main-stream lines and keeps some subtitle noise

**Defect.** `isMainStreamEvidence` (`PlaybackFailureClassifier.swift:185-192`) drops any line whose text contains "subtitle", or that matches `\.(…|sub|…)(\?|\b)` anywhere. Release-style file names in a main-stream URL trip both: `Movie.2024.MULTi.SUB.1080p.mkv` (`.sub` followed by a dot is a word boundary) and `…Subtitles…`. A host label like `x.sub.example` trips it too. The reverse gap: in-core `sub-add <http url>` (`MPVPlayerView.swift:1554`) runs FFmpeg's network stack under the `ffmpeg` prefix. Its `tcp:` and `tls:` lines usually carry no URL, so they survive and still read as `.network`.

**Consequence.** For a main-stream line such as `stream: Failed to open https://…/Movie.SUB.mkv`, the URL-bearing evidence is dropped. The HTTP status line usually carries no URL, so the impact is small. A timed-out subtitle fetch can still make a later early end of a dead link `.network` (not remembered), which is r1's concern in a narrower form.

**Fix.** Match only extensions at the end of a URL path (`\.(srt|vtt|…)(\?|$|\s)`). Drop the bare "subtitle" substring test, and keep "external file" and the prefix set. For the in-core fetch noise, either keep the subtitle fetch out of the core (the local-file path at `:1547` already does this when it can) or record the uptime of the last `sub-add` and ignore `ffmpeg` network lines within a few seconds of it.

### 5. P3: a few of our own remux stages still read as link evidence

**Defect.** `engineInternalStages` (`PlaybackFailureClassifier.swift:148-151`) does not include `"extract extradata"` (`RemuxSession.swift:428`), `"video stream"` (`:587`) or `"no video stream"` (`:419`). Without an FFmpeg code these fall to `.unknown`, which is remembered.

**Consequence.** Only on the forced-native path or a native attempt after mpv (`onFallback == nil`): a file mpv plays, or an audio-only item the remux refuses, goes into the 8 h memory. The impact is small.

**Fix.** Add the first two to the set. For `"no video stream"`, decide whether it counts as our limit (mpv plays audio-only) and say so in the set's comment.

### 6. P3 (pre-existing, same class as r1 #1): the first item's resume seek can be overtaken by `stop()`

**Defect.** In `observePlayback`'s first-item branch, `await player.seek(to: resume)` (`NativePlaybackCoordinator.swift:1115`) is followed by `player.play()`, `playIssued`, and `recorder.startTrakt` / `startTrackers` (`:1124-1125`). There is no ownership check after the await. `stop()` has already called `stopTrakt` and `stopTrackers`. This predates P4, but it is the exact pattern r1 #1 fixed for the rebuild.

**Consequence.** If the viewer presses Menu during the resume seek of a resumed title, the paused player restarts briefly (until the loop's top guard ends the task), and a Trakt or Simkl "start" scrobble goes out after the "stop". The tracker shows the title as watching until the scrobble expires.

**Fix.** After the await, `guard !Task.isCancelled, self.player === player, self.phase == .playing else { return }` (the same predicate as `rebuildStillOwns`).

## Clean (second pass, beyond r1's list)

- **Rebuild teardown.** `abandonRebuild` after `stop()` only flips `isRebuildingItem`. The resulting `onChange` → `evaluatePauseCard` is harmless because the rule needs `.playing`. `stop()` cancels the observe task before nilling the player, so no path leaves `syncAudioSelection` or `checkLateSubtitles` gated.
- **The user-seek target** only ever reaches the corrective seek. A seek issued during the corrective seek cancels it inside AVPlayer, so the user still wins.
- **`fromNativeStage`.** It checks the engine-internal list before `lastErrorCode`, so a stale code recorded at `RemuxSession.swift:958` cannot override "no usable keyframe index". The mid-play remux path now uses the same function with `atOpen: false`.
- **NetworkPathMonitor:** lock-guarded, a singleton with a weak handler, and true until the first update. **FirstPlayAutoPlay:** the thrown error is classified with `.remote`, the timeout never rejects, and an offline reject is skipped with a log line. **StreamPickerView:** the skip log and `shouldReject` agree on `healthySeconds`.
- **Panel host.** `anyPress` uses the delegate's `shouldRecognizeSimultaneously → true` (`PlayerPanelHost.swift:97-100`) and consumes nothing. Menu is reported once from `pressesBegan`, ahead of the unchanged handling. The delegate callback only reports transitions. `openPanel(tab:column:)` keeps the Down-press guards.
- **Pause card:** the task is cancelled on resume and on disappear, "unknown = visible" holds, and the card is not focusable and not hit-tested. **The loading overlay** never covers a mid-play rebuffer, the post-play cover or the up-next chip (it is gated on `!playbackStarted` and `!loadingStage.isStarted`). The rebuild never moves the stage back.
- **mpv:** the `PLAYBACK_RESTART` stage hop is a strong `main.async`. The END_FILE snapshot is taken on `eventQueue`. `screenshot-sw` is written on change only, `autoreleasepool` wraps the capture, and the node bytes are scaled before they are freed. `PauseInfoCard` now takes values and re-renders from the observing parent.
- **The r1 fix diff** adds no new user-visible strings and no settings. The edited comment in `PlayerPlaybackColumns.swift` describes behaviour that finding 2 shows does not happen yet.

## Release-note deltas from the r1 fixes

- A start that never delivers media while the TV is online is remembered against the link again (8 h). Network, offline, cancelled and our-own-engine failures are still not remembered, and neither is a debrid resolve timeout.
- If a native-player failure is our own engine's limit (no keyframe index, no segment map, the local server, the audio transcoder, the DV P7 converter, or any loopback error after playback started), the link is not remembered.
- A chapter pick or a skip during a late-subtitle rebuild is kept: the player does not jump back. Finding 1 is open for the skip chip.
- Do not claim that the Sources column reloads by itself after the up-next search until finding 2 is fixed.
