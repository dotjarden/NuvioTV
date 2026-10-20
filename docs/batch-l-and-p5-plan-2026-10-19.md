# Batch L (upstream ports) and Player P5: plan, 2026-10-19

**Status: APPROVED 2026-10-19 as recommended (D1–D9).** Batch L started the same day and merged; **P5 Wave 0 spikes S1 + S2 DONE 2026-10-20** (see OUTCOME: D6 resolved — DV P5 in MP4 plays natively; D7 measured). The P5 build waits for Steven's rc10 verdict to be triaged. Written from three read-only code surveys of `tvos-shared-extraction` at `2baa390f1` (rc9) and upstream `cmp-rewrite` at `324afcffb`, plus `docs/player-revamp-plan-2026-10-06.md` (P5 section), `docs/master-plan-2026-10-14.md` §4.5 / D3, `docs/upstream-port-plan-2026-10-19.md` and `docs/nuviotv-android-upstream-port-plan-2026-10-19.md`.

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
- **Rig recovery (2026-10-19 ~15:00 ET)**, after Christian restarted the Apple TV:
  - devicectl sat at "available (paired)": its tunnel opens on demand, and `ready.sh` only polled `list devices`.
  - mDNS kept advertising the pre-restart Companion port (61193 refused; the box listened on 49153).
  - The Companion pairing had been invalidated; re-paired with `pair.py` (PIN read off a screenshot, then deleted).
  - Fixed in `c1d13e4`: `ready.sh` opens an idle tunnel, and `atv.sh` uses the mDNS port only if it accepts a connection. `atv.env` port set to 49153.
  - `ready.sh`: **DEVICE READY** (tvOS 27.2, signing profile until 2026-10-22T04:23Z).
- **Device pass (partial)**: build 141 from `c9e54872d` installed over devicectl and launched with `-AppleLanguages (fr)`. Auto-entered profile 3 = **Test 2** (confirmed in the sidebar). Console: `docs/research/batch-l-device-2026-10-19/console-fr.log` (redacted).
  - Launch, Home, Library and the French UI: fine, no crash.
  - **L2 step skipped:** Test 2 has no Simkl connected (no Simkl activity in the log; the Library shows the local list with no section pill). The jvm `SimklLibraryTitlesLocalizationTest` is the record.
  - **L1 infoHash branch not exercisable here:** Test 2's torrent source is Comet via TorBox, and every listing carries the full release filename, so Up Next matches by filename before the new step runs.
  - Up Next regression check **not reached**: Companion arrow presses and holds did not commit seeks in the mpv player (a single hold moved about 27 s), so the rig could not drive to the end of a 51-min episode.
  - The final return to the tvOS Home screen was `console.sh stop`'s SIGTERM (`App terminated due to signal 15`), not an eject.
- **MERGED 2026-10-19** on Christian's go ("merge, no cut yet"), on the CLEAN review, the gates and the partial device pass: `tvos-shared-extraction` `2baa390f1` → `c9e54872d` (3 commits), pushed. Branch deleted (it was never on GitHub `origin`), clone `NuvioMobile-batch-l` deleted, outer pointer bumped. Not cut; it ships in the next rc.
- Release-notes line: next-episode auto-play now also matches a season pack by its torrent (same release, no filename needed); Simkl's Library lists and MDBList's Watchlist show in the app language. No new settings.

### Player P5 Wave 0: S1 + S2 spikes (2026-10-20, main session on the rig)

Clone `~/Claude/Projects/NuvioMobile-player-p5`, branch `claude/player-p5` off `1bf7866aa` (rc10 tip), MPVKit symlinked. One commit, `8e0892386`, not merged. Device: Living Room, **Test 2** (`ready.sh` READY 12:1xZ, profile 3 confirmed by the rail), Debug build with the `com.youngchris29.NuvioTV` override and `-player.nativeDolbyVision YES`; six device rounds. Logs (redacted) and 960 px shots: `docs/research/p5-spike-2026-10-20/`. Sample: Dune: Part One, Torrentio "[2021 WEB-DL 2160p Dolby Vision TV]" 29.41 GB Rutracker (the P3-F7 file; 5th Torrentio stream in the picker, TorBox instant), plus the 3.15 GB Licdom P8.1 MKV for the baseline.

**S1 (D6) — RESOLVED: the DV P5 MP4 plays natively.** The plan's hypothesis (the ffmpeg "timescale not set" / "codec frame size is not set" warnings) was wrong: both lines also appear on the P8.1 run that plays. Three stacked defects, each a different CoreMedia code, found one per round from the kept init segment:

1. **-12927 at media admission: the master carried no `VIDEO-RANGE`.** `RemuxSession.videoSignaling` took the range from `color_trc` only; a P5 stream's VUI is unspecified (IPT-PQ-C2 has no VUI code), so the P5 master went out as `CODECS="dvh1.05.06"` with `RANGE=-` (rig-b log 10-15 confirms it) and tvOS 27 rejected the PQ media exactly as `SegmentMap` documents. Fix: when the VUI says nothing, the DOVI record decides — P5/P7 → PQ, P8 by `dv_bl_signal_compatibility_id` (1 PQ, 4 HLG, 2 none). The `[Remux] signaling` line now prints VIDEO-RANGE.
2. **-4 after init.mp4 + seg-00001 were fetched: the `dvh1` sample entry's hvcC had `numArrays=0`.** The source is the in-band (`dvhe`) layout: a 23-byte hvcC header with no VPS/SPS/PPS, so the 848-byte init segment (hvcC 31 b) gave AVPlayer nothing to configure a decoder from (the HDR10 and P8.1 inits are 885 b and 3382 b, parameter sets included). The existing recovery (`extractVideoExtradata`) only ran for `extradata_size == 0`; it now also runs when the hvcC's arrays hold no NAL (`hvccHasNoParameterSets`, unit-tested on bytes).
3. **The recovery itself did not work on MP4.** ffmpeg's `extract_extradata` filter splits packets on Annex B start codes, so on the length-prefixed source it read its 200 packets and failed ("failed at extract extradata", round 4). Replaced by a direct walk of the length-prefixed NALs (`extractLengthPrefixedHEVCParameterSets`, nal length from `lengthSizeMinusOne`). Round 5 then failed with **-16041** and a first fragment of 28 KB instead of 158 KB for the same 192 samples: Annex B extradata makes movenc assume the packets are Annex B too and "reformat" them, which mangled every sample. The walk now rebuilds a **complete hvcC** (the source's 23-byte header, `numOfArrays=3`, one array each for VPS/SPS/PPS) so movenc copies it verbatim and leaves the samples alone.

Round 6 (`8e0892386`): `[Remux] rebuilt hvcC 123b`, init.mp4 948 b with `numArrays=3` + `dvcC` profile 5, `[NativePlayer] item readyToPlay`, `stage=started t=+5.59s`, 17 segments served over ~70 s with no stall, fallback or error line; the devicectl screenshot during playback (`shots/52-native-playing.small.png`, the Sardaukar parade) shows natural colour, no green/magenta cast, so the hardware is doing the DV processing. Exit clean (BUG-185 path, 0 ms). The `PlayerEngineRouter` P3-F7 rule (P5 in MP4 → mpv) is removed; the DEBUG self-check and `PlayerEngineRouterTests` say P5 MP4 → native; the native → mpv fallback on gpu-next stays.

- **Atmos (FEAT-75) not verifiable with this file:** its English track is E-AC-3 5.1 without JOC. The remux stream-copies E-AC-3 (`AUDIO=ec-3`) exactly as it already does for the HDR10 and P8.1 Dune variants, so an Atmos P5 MP4 (Steven's Animals) would reach the receiver as E-AC-3 JOC unchanged; the receiver check is Christian's, with such a file.
- **Seen on the way (mpv, the rc10 route):** on all three mpv fallback rounds the VideoToolbox decoder logged `hardware accelerator failed to decode picture` / `output image buffer is null: -12909, reconfig 1` every ~4 s on this P5 file, with `dropped=vo:22` by +40 s. With P5 routed native it no longer applies to P5 MP4s; it may be what Steven sees as BUG-181's "late" thumbnails on Animals (mpv). Not chased.
- **Seen on the way (native):** a pre-play item failure is slow to surface — the two failed attempts (first try + the "retry without SUPPLEMENTAL-CODECS") spanned ~50 s before the mpv failover (console-s1b, 12:37:03 → 12:37:53). The retry is pointless when there is no SUPPLEMENTAL-CODECS to drop (P5, HDR10, SDR). Wave 3 item: skip the retry when `supplementalCodecs == nil`, and look at capping the first failure's wait.

**S2 (D7) — measured.** `[PlayerRouter] probe took …` is now printed with the cap; stages are the existing `[Loading] engine=… stage=… t=+…s` lines. Times from the router's start (stream resolution by the debrid add-on happens before it and is not in these numbers):

| Run | Probe | Stages | First frame |
|---|---|---|---|
| P5 MP4 native (round 6) | 1.54 s | connecting +0.01 · preparing(dv) +1.59 · buffering +2.11 · readyToPlay after seg-00002 (14.4 MB) | **+5.59 s** (≈ 7.1 s incl. probe) |
| P8.1 MKV native (Licdom 3.15 GB) | 1.37 s | preparing(dv) +1.07 · buffering +2.66 · readyToPlay after seg-00002 (5.2 MB) | **+4.45 s** (≈ 5.8 s) |
| P5 MP4 on mpv (rounds 1–3, the rc10 route) | 1.68–2.27 s | connecting +0.05 · buffering +1.4–1.9 · `[DisplayMode] criteria … gamma=pq` +1.8 | **+2.3–2.9 s** (≈ 4.2–5.2 s) |

- The probe never came near the 4 s cap in six runs (1.37–2.27 s), including the 29 GB MP4 with its moov at the end; the "nil probe → mpv without gpu-next" risk in the plan did not show on this box. A shorter cap buys nothing; the per-`playbackStreamKey` probe cache would save the 1.4–2.3 s on a replay only.
- Our own stages are short (remux open + keyframe index ≈ 1.1–1.6 s, master served by ≈ 2.1–2.7 s). The rest is AVPlayer buffering: `readyToPlay` waits for the second segment, and the first segment of both films is tiny (black opening frames), so native "started" lags the master by ~3 s and lands 2–3 s after mpv would. Candidate for Wave 3: a shorter first segment pair, or `preferredForwardBufferDuration` on the item, measured again.
- Steven's 12–14 s (BUG-167) is not reproduced from the router onwards (≈ 5.8–7.1 s here); the difference has to come from stream resolution before the router, his network, or the mpv start on his box. His console with these lines would settle it; the DM can ask for a `[PlayerRouter]`/`[Loading]` excerpt on his next build.

**Decisions taken for Wave 3:** P5 MP4 routes native (the three fixes above ship as the BUG-166 real fix); add the no-supplemental retry skip; keep the probe cap; measure the first-segment buffering before touching it. The rc notes must say P5 MP4s now play on the Apple TV player with Dolby Vision, and ask Steven for Animals (Atmos) on it.

**Gates on `8e0892386` so far:** `PlayerEngineRouterTests` 9/0 on the FA87 simulator (the five routing tests incl. the new P5-MP4-native case, plus four `hvccHasNoParameterSets` byte tests); Debug device build with the bundle-ID override. Not yet run: the full NuvioTVTests, Kotlin gates and Release sim (they come with the P5 branch's review rounds, nothing in the commit touches shared/).

**Rig notes:** the Detail's hero trailer swallows the first Select (enter trailer → Menu → Select → Select opens the picker); the picker remembers which add-on groups are expanded, so screenshot before counting rows; Dune is the 5th Torrentio stream (DV TV MP4) and the Licdom P8.1 MKV is 11 rows further down; a pyatv Companion `_systemInfo` timeout on one press is transient (retry once). Six device rounds, ~2 h 10 m wall clock including five Debug device builds (the first needs the bundle-ID override in a fresh clone, ~10 min; the rest ~4 min).

### Player P5 Wave 1 (2026-10-20, in progress)

- **Critique first** (Opus, read-only): `docs/p5-w1-w3-critique-2026-10-20.md`. Line drift fixed in the specs; two findings changed the scope: this MPVKit's libavfilter has no `dynaudnorm` / `loudnorm` / `acompressor` (13 audio filters), so **Night mode is dropped and Audio Mode ships as Off / Dialogue only**; Boost needs `volume-max=320` for +10 dB. The three new rows are **player-panel rows only, no Settings › Playback rows and no description ids**. Track prefs are per profile *and per device*, not synced: the release notes must not say "synced". Two of the plan's "Decisions" were therefore taken in-session (Q1 Night off, Q2 panel-only); Christian can reverse either.
- **Agents A (Sync Line) and B (audio, speed, N1)**, Sonnet, in parallel in the one clone, B owning the four shared player files and A applying its hunks after B's marker. Both reported green on their own tests and the Debug sim build. Wave 3's retry skip (`NativePlaybackCoordinator.signalingRetryAllowed`) was added by the main session in the same tree.
- **Strings:** `scripts/populate-localizable-xcstrings.py` on the Debug build added 19 catalog entries; 2 harvested from mobile, 11 still untranslated (the translation pass before any public beta.19; `build/localizable-needs-translation.json` in the clone lists them). Two stray keys ("on", "%@  %@") came from an accessibility value and a cue-row interpolation and are being removed in the r1 fix pass.
- **Gate on the as-built tree** (`009a9cc93`, committed as a checkpoint): `:shared:jvmTest :shared:tvosSimulatorArm64Test :composeApp:iosSimulatorArm64Test` green (3 m 16 s); NuvioTVTests **2049 / 0** (5 skipped); NuvioTVUITests compile; Debug + Release simulator builds green. The first gate run died on one optional chain in the retry skip (fixed in the checkpoint).
- **Review r1** (Opus, read-only, `docs/p5-w1-review-r1-2026-10-20.md`): **P1 1 / P2 4 / P3 12.** The P1 was the same optional chain. P2s: Sync Line leaves nothing focused while cues load (focus Cancel + `.defaultFocus`); the cue loader's UTF-8/Latin-1 decode misses UTF-16 (reuse `SubtitleVTT.decode` + SDH stripping); the new UI legs skip the existing start gates; the retry gate should use the spec's empty-string form. Notable P3s: `lastAppliedAf` recorded even when mpv rejects the filter; a native panel open can save 1.0 over a remembered speed; "Audio Delay Reset" with a stream hint went to 0 s. **Product call taken:** Reset returns to the stream's base (the hint). Fix pass running (Sonnet); review r2 and the gate follow, then one commit.
- **Not done yet:** Wave 2 (post-play More Like This, agent C), the UI legs have never been run, the device pass (steps 1–7 of the plan, Test profile), the translation pass, the `[AudioFx] af=… rc=` check on hardware (the `lavfi` filter-list syntax is unverified on real mpv).

