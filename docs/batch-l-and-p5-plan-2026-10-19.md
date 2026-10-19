# Batch L (upstream ports) and Player P5: plan, 2026-10-19

**Status: APPROVED 2026-10-19 as recommended (D1–D9).** Batch L started the same day; P5 waits for Steven's rc8/rc9 verdict to be triaged. Written from three read-only code surveys of `tvos-shared-extraction` at `2baa390f1` (rc9) and upstream `cmp-rewrite` at `324afcffb`, plus `docs/player-revamp-plan-2026-10-06.md` (P5 section), `docs/master-plan-2026-10-14.md` §4.5 / D3, `docs/upstream-port-plan-2026-10-19.md` and `docs/nuviotv-android-upstream-port-plan-2026-10-19.md`.

Scope as decided 2026-10-19:
- **Batch L** = the two small NuvioMobile ports from the 10-19 check. It is its own batch, built now while Steven tests rc9.
- **P5** = the four original features, with B19 reduced to Sync Line (no automatic sync), plus Steven's DV / start-time items (BUG-166 real fix, BUG-167), plus the per-stream audio delay port (NuvioTV Android N1).
- Out of scope:
  - FEAT-74 (engine per source).
  - FEAT-75 (Atmos on mpv).
  - The optional Android items: 4K Trailers toggle, proxyHeaders check, episode rating colour.

Correction to the 10-19 morning summary: TorBox pagination, MDBList release-date sort and ytId streams are not open. They shipped in Batch D (`14f5991ce`, 10-16).

---

## Decisions for Christian (recommendation first)

| # | Question | Recommendation | Alternative |
|---|---|---|---|
| D1 | Sync Line: which subtitles? | **Add-on (external) subtitles only in v1**, both engines. That matches the native Timing row's gate. Embedded tracks have no cue list on either engine. | Also embedded on mpv. This needs a demux of the embedded track: M, risky. |
| D2 | Sync Line: reaction time | **Subtract the existing 300 ms `SUBTITLE_AUTO_SYNC_REACTION_COMPENSATION_MS`** from the press. | Raw press time. |
| D3 | Boost / Dialogue / Night: engines | **mpv only; rows hidden on native.** `AVPlayer.volume` caps at 1.0, and an audio tap over our loopback HLS is unverified. | Native via `MTAudioProcessingTap`: spike first, M–L. |
| D4 | Post-play More Like This: source | **Follow Detail's More Like This source setting** (Trakt / TMDB / Simkl). Shown when an item ends with no up-next (movies, last episodes), on both engines. | Always TMDB. |
| D5 | Per-show speed: storage | **Profile-scoped and synced** like the other track prefs (`playback_speed|<parentMetaId>`, registered in `AccountDataStores`). The toggle "Remember Speed for This Show" defaults to **off**. Turning it off deletes that show's saved speed. | Device-local `UserDefaults`. |
| D6 | BUG-166 (DV P5 in MP4 never plays natively, so no Atmos) | **Half-day spike first** on the MP4-input remux failure (`CoreMediaErrorDomain -12927`, ffmpeg "timescale not set" / "codec frame size is not set"; finding P3-F7). If the spike fixes it, P5-MP4 routes native and E-AC-3 Atmos passes through. If not, keep mpv and record why. | Skip the spike; BUG-166 stays parked. |
| D7 | BUG-167 (12–14 s to first frame on his P5 MP4s) | **Measure first.** On the rig, pull the `[PlayerRouter]` line and stage timings for a P5 MP4 sample (his Animals report showed the native-only "Préparation de Dolby Vision…" text, which the current router should skip). Then cut whichever stage the log names. | Pre-commit to a fix (e.g. probe in parallel with the mpv open). |
| D8 | Per-stream audio delay (N1): precedence | **Follow upstream.** A stream's `behaviorHints.audioDelayMs` becomes the base. The user's tweak while a hint is active is session-only. The saved per-episode delay applies only when the stream has no hint. Clamp ±60 s. mpv only (AVPlayer has no audio offset). | The saved delay always wins. |
| D9 | Batch L, Simkl titles: route | **Shared route, as upstream and Trakt do:** `StringKey.library_status_*` + `resourceString` resolved at projection time. Also localize MDBList's hard-coded "Watchlist" with the existing `trakt_watchlist` key. | Swift-side `String(localized:)` mapping. |

---

## Batch L: upstream ports (now)

Branch `claude/batch-l` in a clone `~/Claude/Projects/NuvioMobile-batch-l` (never a worktree), off `2baa390f1`. One Sonnet build agent (both items are exact specs), one Opus review round to CLEAN, then the main session runs the gates. Codex is over quota until 10-29.

### L1. Binge-group infoHash fallback (upstream `d2cc0fb8a`), S

How upstream picks the next episode's stream when a binge group is persisted:
1. Same group + filename match.
2. Same group + the same torrent infoHash (case-insensitive).
3. The plain binge-group pick.

Step 2 covers season packs: one torrent serves every episode, and the add-on gives no usable filename.

Fork facts:
- The tvOS next-episode engine keeps the playing `PlaybackContext` (`NextEpisodeAutoPlay.swift:967-973`).
- `listedStream.p2pInfoHash` (`StreamModels.kt:110`) already normalises the top-level hash, the `clientResolve` hash, magnets and `torrent://`.
- The next context is rebuilt with the same `listedStream` (~`:512`), so nothing needs persisting.

Change:
- `shared/.../streams/FilenameEpisodeMatcher.kt`: `findInfoHashMatch(streams, infoHash, bingeGroup)`. It returns the first stream with the same non-blank group and the same `p2pInfoHash`.
- `NextEpisodeAutoPlay.swift`:
  - Add `playingInfoHash` and `bingeGroupInfoHashMatch(groups:settings:)`, with the same guards and `selectableStreams` as `bingeGroupFilenameMatch` (`:1013`).
  - Call it right after each filename match: `attemptBingeGroupOnlySelection` `:923` and `attemptSelection` `:946`.
  - Log line `[UpNext] binge group + infoHash match`.

Tests: `FilenameEpisodeMatcherTest.kt` (beside `:187/:202`) covers:
- same group + hash, ignoring case;
- wrong group → nil;
- blank group → nil;
- null hash → nil;
- `clientResolve` / magnet via `p2pInfoHash`;
- list order wins.

No commas in test names (K/N).

Risk: a season-pack hash also matches the current episode's listing. The debrid resolve picks the file from the episode context, so the device pass checks the episode number.

### L2. Localized Simkl status titles in the Library (upstream `LibrarySectionTitles.kt`), S

Fork facts:
- `SimklLibraryProjection.kt:27-61` hard-codes "Watching"… as top-level vals, used as `displayTitle` (`:74-77`).
- tvOS shows `displayTitle` verbatim in two places:
  - the `LibraryView.swift:259` picker label;
  - `LibraryViewModel.swift:68-71`, which feeds the pill and the hold-menu Remove label through `LibraryGridPolicy.removeLabel`.

Change:
- Add five `StringKey`s (`library_status_watching / _plan_to_watch / _on_hold / _completed / _dropped`) and the same keys in composeApp `values/strings.xml`, with fr/es/de/it from upstream and vi through the overrides.
- Resolve the title **at projection time**, not in the top-level vals. Those initialise before the provider is installed and would freeze English.
- `MdbListLibraryModels.kt:163` "Watchlist" → `resourceString("Watchlist", StringKey.trakt_watchlist)`.
- Regenerate `Shared.xcstrings` (`scripts/generate-shared-xcstrings.py`).
- The `simkl:status:*` keys stay as they are; only `displayTitle` changes.

Tests: a jvm commonTest with a fake `StringProvider` checks that the section titles come out localized, and that they fall back to English with no provider.

### Gates and device pass

Gates on the tip:
- `./gradlew :shared:jvmTest :shared:tvosSimulatorArm64Test :composeApp:iosSimulatorArm64Test`
- NuvioTVTests
- Debug + Release simulator builds
- Debug device build

Device pass (dev build, **Test profile**, `scripts/device/ready.sh` first):
1. A season-pack series from a torrent add-on with no filenames: Up Next picks the same release and the right episode, and the console shows the infoHash line.
2. App language French, Simkl connected: the Library pill and the picker show the French status names, and Remove reads in French. If the Test profile has no Simkl, this step is skipped and the unit test is the record.

Merge on go ("merge, no cut yet"): fast-forward, push, delete the branch and clone, bump the outer pointer. It ships in the next rc.

---

## Player P5 (after Steven's rc8/rc9 verdict is triaged)

Branch `claude/player-p5` in clone `~/Claude/Projects/NuvioMobile-player-p5`, off the tip after Batch L merges.

### Wave 0 (main session): spikes, then the spec critique

- **S1, DV P5-in-MP4 remux (D6), half day.** On the rig:
  - Reproduce `-12927` with a P5 MP4 sample. The only one tested so far is Dune, 29 GB, moov at the end.
  - Fix the MP4-input path: set the output timescale from the input stream and pass the codec frame size.
  - If AVPlayer plays it, route P5 MP4 native, remove the `PlayerEngineRouter.swift:67-74` rule, and check that E-AC-3 Atmos reaches the receiver. If not, record the failure in the plan and leave the rule.
- **S2, start-time measurement (D7).** On the rig, log `[PlayerRouter]`, the `MediaProbe` duration (the 4 s cap at `MediaProbe.swift:79-117`; a timeout gives a nil probe, which routes to mpv and loses `prefersGpuNext`), and the mpv stages (`MPVStartupStageReducer`) for a P5 MP4 and a P8 MKV. The fix follows the log. Candidates:
  - cache the probe per `playbackStreamKey`;
  - run the probe in parallel with the mpv open when the picker tags say DV;
  - a shorter probe cap for MP4s with a late moov.
- One Opus critique of the W1–W3 specs.

### Wave 1: two agents, disjoint files

**Agent A, Sync Line (B19).**
- `Player/PlayerTopPanelModel.swift`: a `cueSource: (() async -> [SubtitleSyncCue])?`.
- `Player/PlayerSubtitlesTab.swift`: a "Sync Line" row under Timing (after `:47`) that opens a cue list starting 20 s before the current position. Select computes `delay = position − cue.start − 300 ms` and calls the existing `onSubtitleDelayChange`. That reuses mpv `sub-delay` (`MPVPlayerView.swift:1923`) and the native VTT re-time (`NativePlaybackCoordinator.swift:1400`).
- Cue sources:
  - Native add-on subtitles parse `LocalHLSServer.vttBase[index]` through shared `PlayerSubtitleCueParser.parse` (`PlayerSubtitleCueParser.kt:5-20`; SRT/VTT/ASS/TTML).
  - mpv add-on subtitles re-fetch the selected track's URL from `context.externalSubtitles` and parse it.
- Wiring: `MPVPlayerPanelAdapter.swift:35-42` and `NativePlayerPanelAdapter.swift:29-35`. The row is hidden for embedded tracks (D1).
- Tests:
  - the delay maths (cue, position, compensation, clamp);
  - parser coverage already exists in `PlayerSubtitleUtilsTest.kt`;
  - a UI leg beside `SubtitleDelayProbeTests.testSubtitleDelayTimingRow`.

**Agent B, audio and speed (B20 + B23 + N1).**
- **B20 (mpv only).**
  - Add `volume-max=200` to the init options array (`MPVPlayerView.swift` ~910-940).
  - New device-local keys `player.boostDb` (0–10 dB, default 0) and `player.audioMode` (Off / Dialogue / Night, default Off) in `PlayerTuning` (`PlaybackModels.swift:12-33`), registered in `NuvioTVApp.swift:79`.
  - Runtime apply through `state.setAudioBoost` / `state.setAudioMode`: `volume` 100–316 %. Dialogue = a centre-gain `lavfi` pan on sources with 3+ channels; Night = `dynaudnorm`.
  - Rows in `Player/PlayerAudioTab.swift` after `:55`, hidden on native (D3).
  - Check `audio-channels=auto` against the pan layout on hardware.
- **B23 per-show speed.**
  - `PlayerTrackPreferenceStorage` gains `loadSpeed/saveSpeed(parentMetaId)` in the expect object and the apple/jvm/android actuals.
  - Register `DynamicPrefix("playback_speed|")` in `AccountDataStores.kt:467-480`.
  - Apply the speed in mpv `onFileLoaded` (`:1337`, beside the delay restore) and after the native player is ready (`NativeSpeedModel`, `NativePlaybackTab.swift:14-37`).
  - A "Remember Speed for This Show" toggle under the speed row in `MPVPlaybackTab.swift:53` and `NativePlaybackTab.swift:51-58`.
- **N1 per-stream audio delay.**
  - Add `audioDelayMs: Int?` (clamp ±60000) to `StreamBehaviorHints` (`StreamModels.kt:235-242`), parsed in `StreamParser.kt:38-66`, and carried in `CachedStreamLink`.
  - Copy it into `PlaybackContext` at `StreamPickerView.swift:223-231`.
  - mpv `setAudioDelay` (`:1931`) splits into stream base + session tweak + saved per-episode, per D8. Only the no-hint case persists.
  - Port upstream's `StreamAudioDelayTest` maths as a shared test.
  - JS plugin results carry no hints today (`StreamFetchSupport.kt:205-212`); leave them out unless the upstream plugin shape has the field.

File overlap: A owns `PlayerSubtitlesTab`, `PlayerTopPanelModel`, both panel adapters, `LocalHLSServer`. B owns `PlayerAudioTab`, both Playback tabs, `PlaybackModels`, the `StreamModels` / `StreamParser` shared files and `PlayerTrackPreferenceStorage`. **Both touch `MPVPlayerView.swift`** (A: the cue fetch closure; B: the init options, `onFileLoaded`, `setAudioDelay`), so B goes first on that file and A rebases its hunk. Builds are serialised under `iosApp/build/with-lock.sh`.

### Wave 2: one agent, post-play (B22)

- Shared: `MetaDetailsRepository.moreLikeThis(type, id)`, reusing `applyMoreLikeThisSource` (`MetaDetailsRepository.kt:499-535`) without touching the Detail singleton's `uiState`.
- mpv: `PostPlayView` (`MPVPlayerView.swift:4698`) gains a focusable More Like This row under Play Again / Back to Details.
- Native: an `AVPlayerItemDidPlayToEndTime` observer in `NativePlaybackCoordinator` presents the same post-play view when there is no up-next (today native just sits at the end).
- A poster closes the player and pushes `TitleRoute(preview:)` (`DetailView.swift:2404`). This needs a new dismiss-then-navigate hook on the player presenter.
- UI leg: the end of a short fixture → the row shows → Select lands on Detail.

### Wave 3: DV and start-time changes (main session), from S1 / S2

Whatever the spikes justify: the router rule change and remux fix (BUG-166), and the stage cut (BUG-167). Each comes with router unit tests in the existing `PlayerEngineRouter` test file.

### Reviews, gates, device pass

- Two Opus review rounds to CLEAN; if the work runs past 10-29, the last round goes through `codex-review/tools/review.sh --base <branch point>`.
- Gates as in Batch L, plus the UI legs: Sync Line, post-play, speed memory, and the existing `NativePlayerParityUITests` and `PlayerTransportUITests`.
- Device pass (dev build, **Test profile**, `ready.sh` first):
  1. An add-on subtitle 2 s off: Sync Line lands it on mpv and on native.
  2. Boost +6 dB audibly louder with no clipping on a loud trailer; Dialogue raises speech on a 5.1 film; Night evens out a loud/quiet scene (mpv).
  3. End a movie on each engine: the More Like This row shows, and a poster opens Detail.
  4. Set 1.25× with Remember on, then play the next episode: 1.25×. Toggle off: the next episode plays at 1×.
  5. A stream with `audioDelayMs` (stub add-on fixture): the delay applies, a tweak is lost on the next stream, and the saved per-episode delay is untouched.
  6. P5 MP4 sample: the engine the spike chose, the time to first frame against the S2 baseline, and Atmos on the receiver if native.
  7. Regression: a P8 MKV still plays natively; a P5 MKV is unchanged; failover to mpv at the same position still works.

New settings and defaults for the release notes and the tester DM:
- Player Audio tab › Boost: 0 dB.
- Player Audio tab › Audio Mode: Off.
- Player Playback tab › Remember Speed for This Show: Off.
- Player Subtitles tab › Sync Line: an action, not a setting.

Each new Settings row also gets a `SettingsDescriptionID` and copy (`SettingsDescriptions.swift:132-151`, `:338-411`), and strings in the five locales through `scripts/populate-localizable-xcstrings.py`.

### Agents and cost

Batch L: 1 build agent + 1 review round. P5: 1 critique, 3 build agents (A ∥ B, then C), 2 review rounds. Never more than three agents at once; builds serialised.

## Risks

- **S1 may not fix the remux.** BUG-166 then stays mpv-only and Atmos stays native-only (FEAT-75). Say so to Steven plainly.
- **The P5 MP4 probe** reads over the network with a 4 s cap. Large MP4s with the moov at the end may time out, which today silently routes to mpv without `prefersGpuNext`. S2 measures it.
- **Dialogue / Night filters** assume a stereo or 5.1 layout that mpv may not output with `audio-channels=auto` on tvOS. This is hardware-only; the device pass decides whether Dialogue ships.
- **Post-play navigation** out of a full-screen cover into Detail is a new path. Dismissing the cover first is the known-safe order (the "empty-pushed-view EJECT" class).
- **The Sync Line mpv cue fetch** re-downloads the subtitle. Some add-on subtitle URLs are one-shot or slow, so the row shows "Cues unavailable" instead of hanging.
- **Free-team provisioning expires 10-22 00:23 EST**; the first device build after that re-signs.

---

## OUTCOME

### Batch L (started 2026-10-19)
- Clone `~/Claude/Projects/NuvioMobile-batch-l`, branch `claude/batch-l` off `2baa390f1`, MPVKit symlinked (stage by explicit paths).
- Build (Sonnet agent): `cab68cd1d` L1, `2930c79a5` L2, plus the gate fix `c9e54872d` (the composeApp `ComposeResourcesStringProvider` `when` needed the five new keys). The fr/es/de status names are fork overrides written in-house; upstream ships only `values-it` for these keys.
- Opus review r1: **CLEAN**, no findings. The season-pack worry is ruled out in code: `fetchStreams` resets the state on a new videoId before the watcher subscribes, so the hash match only ever sees next-episode listings. Notes only: no `torrent://` test case; a stale KDoc in `StringProvider.kt:253`.
- Gates on `c9e54872d`, all green:
  - `:shared:jvmTest` 1563/0, `:shared:tvosSimulatorArm64Test` 1585/0, `:composeApp:iosSimulatorArm64Test` 438/0.
  - NuvioTVTests 1967/0 (5 skipped).
  - Release + Debug simulator builds.
  - Debug device build with the `com.youngchris29.NuvioTV` bundle-ID override.
- Gate notes: the `generic/platform=tvOS Simulator` destination fails to link (it also builds x86_64, and SharedCore is arm64-only), so the sim builds ran on the FA87 destination. Tests use the `NuvioTVTests` scheme. The device build needs the per-target bundle-ID override.
- Device pass: **not run.** `scripts/device/ready.sh` refused at ~14:45 ET: "Apple TV 'Living Room' is unavailable after a wake and 60s". Not retried, per the standing rule. The pass waits for the box to be awake.
