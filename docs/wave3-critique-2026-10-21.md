# Wave 3 critique (W3-1, W3-2), 2026-10-21

Read-only Opus critique of `docs/wave3-plan-2026-10-21.md` against clone `NuvioMobile-wave3` @ `6baddab46`. Paths are relative to `iosApp/NuvioTV/` unless noted. FFmpeg citations come from upstream `release/7.1` `libavformat/movenc.c` and `mux.c`. The MPVKit build is older, so its message text differs slightly ("in stream 0"), but the logic is the same.

**Verdict:** W3-1's diagnosis is wrong. The source packets HAVE pts, so fix (a) targets a branch this file never takes. The real fault is the DTS grid in the video branch (details below). W3-2 is sound apart from one anchor: `fieldFocused` lives in another struct and cannot be reached from the alert.

## 1. Drift

| Spec says | Actually |
|---|---|
| "every video packet logs `[mp4] pts has no value` and `Packet duration: -671`" | Both lines come from the **output** muxer (`[mp4 @ 0x13919d200]`); the input is `[mov,mp4,… @ 0x1390de100]`. They appear **once per fragment**, 6 pairs for segments 2–7, at dts 92065 + k·96768 (log :97-113). Neither concerns source packets (see §2). |
| timestamp pass `RemuxSession.swift:1033-1080` | rescale + origin `:1029-1034`; pre-roll drop `:1042`; video branch `:1047-1064`; audio branch `:1065-1075`; write + error print `:1077-1082` |
| boundary math `:1012` | cut condition `:1011-1013` (`pts != noTS` is on `:1012`) |
| learned duration `:1051` | guard `:1051`, assignment `:1052`, first-pts fallback `:1053-1054`; declaration `:599` (its comment "a stream constant" is false: `:1052` overwrites it on every packet) |
| clamp `:1058`, synthesis `:1062` | correct. The line the spec misses is `:1059` (monotonic bump). `reorderSlack = 6` is at `:592`; `vAnchorOut`/`vIndex`/`vPrevDTS` are at `:864-866`. |
| audio `:1073` / `aNextDTS :1074` | correct |
| `PlayerEngineRouter.swift:37` | correct (`route(probe:nativeDVEnabled:dvP7FelToMpv:)`); `decide` `:49`; `nativeReason` `:146` |
| `NativePlaybackCoordinator ~:1830-1840` | `failIfPreplayback` `:1832`, MID-PLAY branch `:1833-1841`, `fallbackMidPlay` `:1864`. Needs no change. |
| "existing remux tests `NuvioTVTests/Remux*Tests.swift` stay green" | **No `Remux*Tests.swift` exist.** The only player-engine test is `PlayerEngineRouterTests.swift`. |
| `StripPager.swift:947/:964` | correct (the `if HomePerfKnobs…` lines). Structs `:945`/`:960`, doc comments `:941-944`/`:957-959`, uses `:474`/`:548` |
| `CardDepthStyle.swift:390-400` | correct; `:392-394` keep `noCardDepth` |
| `SettingsDestructiveRow :742` | correct (body `:763-777`) |
| `fieldFocused :534` "the pane's existing @FocusState" | `:534` is inside `private struct PluginRepoEntryRow` (`:530`), not `SourcesSettingsPane` (`:8`). The alert (`:452-470`, action `:458-465`) is in `SourcesSettingsPane.pluginsSection` (`:362`) and **cannot write it**. |
| "check `Remove API Key` in Services" | It is in **Sources** `:182` (MDBList). Sources also has "Remove Personal API Key" `:116` (TMDB). Services has five destructive rows (`:97, :154, :244, :381, :390`), Account `:37, :96`, Appearance `:653, :744`, CustomPosters `:102`. All of them share the one kit row. |
| `removeRepository :72`, `statusMessage :46` | correct (`private(set)`) |

## 2. W3-1: BUG-199

**Path of the failing packet.** The mov demuxer always fills pts (dts + ctts), so `pts == noTS` never happens on this file. Packet: video, pts 590005 after `:1033`.
1. `:1011` cut test: pts ≥ 580608 was already cut at segment 7, so nothing happens here. The packet sits ~14 frames into segment 7, mid-GOP.
2. `:1052` sets `vDur = pkt.duration` (667 or 668; see below).
3. `:1056`: the grid dts lands at or above 590005.
4. `:1058` clamps dts to pts: 590005.
5. **`:1059`: `vPrevDTS` is 590016 (the previous packet's dts), so dts becomes prev + 1 = 590017.** dts is now above pts.
6. `:1062` is skipped because pts exists.
7. `:1077` `av_write_frame`. mux.c `compute_muxer_pkt_fields` rejects pts < dts with EINVAL (-22). That is the error line at log :114; mux.c works on a copy, so the values printed at `:1079` are ours.

**What the -671 / "pts has no value" pair is.** It comes from movenc `check_pkt`. At a fragment's first sample (`trk->entry == 0`), `ref = start_dts + track_duration`, which equals the previous dts plus the previous packet's **declared duration**. -671 is `dts − ref`, not a packet duration. movenc then rewrites `dts = ref+1` and `pts = NOPTS`, and `ff_mov_write_packet` prints "pts has no value" and sets pts = dts. This is a **second, silent defect**: every segment's opening keyframe loses its composition offset, so it presents about 6 frames early. Expect a judder or ordering glitch at every 6 s boundary, even on files that never hit EINVAL.

**Root cause (hypothesis, simulation-backed).** `:1056` computes `anchor + (vIndex − 6) · vDur`, and `:1052` re-learns `vDur` on every packet. Timescale 16000 at 23.976 fps gives 667.33 ticks per frame, so stts cycles 667/667/668. Each flip moves the whole grid by about `vIndex` ticks. At vIndex ≈ 880 (segment 7) that is more than a frame, which uses up the 6-frame reorder slack. The grid then collides with B-frame pts, and the clamp + bump give pts < dts.

I simulated `:1052-1059` with that stts cycle and hierarchical-B decode order:
- The pts < dts failure reproduces at decode index ~3000–5000, depending on pyramid depth.
- The fragment-start gaps drift negative toward −666, the same shape as the log's −671.
- With a constant or rational grid: zero failures.

The real file fails sooner, so its stts/reorder is rougher than the model. Agent B should confirm by logging `(vIndex, pkt.duration, pts, dts)` for the first ~1000 video packets.

This also explains why MKV is fine. matroska gives a constant default duration (42 ms → 672 ticks), so `vDur` never flips. The earlier MP4 successes probably used a 24000/90000 timescale, which gives exact 1001-tick frames.

**Fix (replaces the spec's (a)–(c)):**
- **(1) Root:** a non-jittering grid. Either accumulate the actual durations (`gridNext += pkt.duration`, `dts = gridNext − slack·vDur0`), or rescale `vIndex` by the stream's `avg_frame_rate`, which is already read at `:474`. Make `vDur` truly learn-once, so the `:599` comment holds.
- **(2) Safety net, mirroring the audio branch `:1073`:** after `:1059`, `if pts != noTS, pts < dts { pts = dts }`. Log the first nudge. Here that moves pts by 12 ticks (0.75 ms).
- **(3) Fragment-start check:** the boundary keyframe's dts must be ≥ prev dts + prev `pkt.duration`, or movenc rewrites its pts. Either set the video `pkt.duration` to the grid step, or clamp the keyframe up to that. (2) alone fixes the crash but not the per-boundary pts loss.

**Spec questions answered:**
- (a) as written is not sufficient: the synthesis branch is dead for MP4 and MKV. It is harmless to add as a guard.
- (b) Negative durations never reach `vDur` (the `> 0` guard at `:1051`), and `aNextDTS`'s `max(duration, 1)` already handles negatives. There is nothing to fix.
- Boundary `:1011-1013` with no-pts packets: yes, the cut would never fire. One giant segment would follow, and the remux would stall or "truncate" at EOF. Both demuxers we route natively always supply pts, so this stays latent. Note it in a comment.
- (c) As written it cannot be implemented cheaply. `MediaProbe.probe` reads packets only in `scanP7ELKind` (`:172-193`, P7 only). `find_stream_info` reads some, but nothing exposes their pts. A scan would cost probe time (already 2.0–2.2 s of a 4 s cap) to detect a condition that does not occur here. **Drop (c)**; if it lands anyway, `PlayerEngineRouterTests.swift` and the DEBUG `selfCheckFailures` need cases.

**Unit test.** Extract a `nonisolated struct RemuxVideoGrid` with `mutating func stamp(pts:duration:) -> (dts, pts)` and the state anchor / slack / index / prevDTS / learned dur. The spec's `video(pts:dts:…)` signature is wrong: source dts is never read, and the vDur state has to persist between calls. Inputs:
- (i) The exact collision: prevDTS 590016, a grid value ≥ 590005, pts 590005. Expect dts 590017 and pts ≥ dts.
- (ii) 3000 packets: stts cycle 667/667/668, tb 1/16000, hierarchical-B decode order (mini-GOP 8), keyframe every 36 frames. Assert pts ≥ dts, strictly increasing dts, **no pts rewritten** (proves the root fix, not only the net), and dts ≥ prev dts + prev duration at every 144th-frame keyframe. The old formula fails (ii), so the test proves the regression.
- (iii) A reposition anchor (vAnchorOut ≠ 0, index reset).

Device/sim fixture: re-mux any 23.976 B-frame HEVC clip of 60 s or more to MP4 with `-video_track_timescale 16000`. The spec's `setts=pts=NOPTS` fixture tests the wrong thing.

**Why `HDR10`.** The probe found no `AV_PKT_DATA_DOVI_CONF`: the MP4 carries no dvcC/dvvC box. The remux signalled plain `hvc1.2.4.L150.90 VIDEO-RANGE=PQ` with no SUPPLEMENTAL (log :85), while the MKV of the same film signalled `dvh1.08.06` (`console-165-native.log:58`). Routing and labelling are correct for what the container declares. Without the record, AVPlayer ignores any in-band RPUs, so this plays as HDR10. That is fine if the base layer is P8.1-compatible. If it is P5 (IPT), colours would be wrong on both engines, so check colour in the device pass. In-band RPU detection would be a separate feature.

## 3. W3-2

**(a) Knob references, the complete list.** A recursive grep of the clone and the outer `scripts/`, `.claude/` finds:
- `Screens/Home/HomePerfKnobs.swift:6,8,9,12,13,16,17`. The header comment says "three A/B knobs"; reword it to one.
- `Screens/Home/StripPager.swift:943,947` and `:958,964`.
- `NuvioTVTests/HomePerfKnobsTests.swift:22,25,52-55,60,61`. The `keys` array, `testKeysAreTheDocumentedLaunchArguments` and `testKnobsAreIndependent` need rewriting, not just trimming. `testKnobsAreIndependent` loses its meaning with one key, so delete it or make it a two-key check against an arbitrary key.
- No rig script passes `homeNoStripEdgeMask` or `homeNoPageOpacity`. Outer docs mention them (`batch-p-w2-critique`, `batch-p-steven-rc10-plan`, the device-pass README); that is history, leave it.

Keep both modifiers. Collapse them to their else-branches (`StripEdgeMaskModifier` → `.mask`, `StripPageOpacityModifier` → `.visualEffect`). Inlining at `:474`/`:548` is also fine.

**(b) Destructive row.** The focused-row colour rule is `SettingsAccentTint` (`SettingsRowViews.swift:98-113`): on the platter it hands back `.primary` and forces `.environment(\.colorScheme, .light)`. `SettingsRowLabel` (`:340`) and `SettingsPlatterInk` (`:198-209`) do the same scheme flip for container platters. Never pin a fixed colour, except as below.

The destructive row gets none of this: `iconTint: .inherit` plus `role: .destructive`. The title and the `.secondary` subtitle (`:336`) derive from the dark-scheme system red, which is the pale pink in `52-remove-row.small.png`.

Change: inside the Button label, read `@Environment(\.isFocused)` (plus `settingsRowIsFocused` / `settingsRowPlatterActive`). When on the platter:
- title and subtitle → `.primary` / `.secondary` under `.light` (black / grey), like every other row;
- glyph → a fixed dark red #D70015 (systemRed, accessible light variant): 5.4:1 on white, so it passes even as text.

At rest, keep the system red. The app is dark-only (`NuvioTVApp.swift:164 .preferredColorScheme(.dark)`) and the platter is always white, so "both themes" means the accent presets. The rule must not touch `Theme.Palette.accent`, so it holds under every preset, including White.

Make the colour choice a pure `static func` (on-platter → title/glyph style) for the unit test. Explicit inner `foregroundStyle` should beat the role tint, but only the device can prove that: check Sources :116/:182/:442, Services and Account.

**(c) Focus after Remove.** It cannot be done from the alert action as specified (wrong struct). Even after hoisting, a write inside an `.alert` button action is unreliable on tvOS. The alert's dismissal restores focus to its presenter (the Remove row) after the action runs. Then the row disappears asynchronously when the Kotlin flow emits, and the List re-picks.

Do this:
- hoist `@FocusState var repoFieldFocused: Bool` into `SourcesSettingsPane`;
- pass a `FocusState<Bool>.Binding` into `PluginRepoEntryRow` (`.settingsDescription(..., focused:)` at `:549` reads its `wrappedValue`);
- record `justRemovedRepoURL` in the action;
- set focus in the existing `.onChange(of: plugins.repositories.map(\.manifestUrl))` at `:476-482` once that URL leaves. That runs after dismissal and after the row is gone.

If the device still shows the List winning, add a ~300 ms `Task.sleep` before setting it. Caveat: with a long expanded provider list, the entry row may not be materialised by the lazy List, and a focus write then does nothing. Test with the 4-provider fixture repo and a longer one.

**(d)** Set `statusMessage = nil` in `removeRepository` before the Kotlin call. Separately and out of scope: `:382` colours the line by `status.hasPrefix("Installed")` on a localized string, so any non-English locale shows success in red.

## 4. Test coverage

- **W3-1:** the new `RemuxVideoGridTests` cover the rule. Nothing covers the movenc fragment-start rewrite unless (ii) asserts it, so make sure it does. The rest is gated by a device or sim pass on the rc11 file (Test 2 profile) or the 16000-timescale fixture.
- **W3-2:** `HomePerfKnobsTests` rewritten (see the list above); the destructive-ink pure-function test; no `PluginsViewModel` test. `init` is constructible, but `removeRepository` calls `PluginRepository.shared` (Kotlin singleton) and `statusMessage` is `private(set)`. Neither has a clean seam, so skip it. Focus after Remove and the platter contrast are device-only.
- The NuvioTVTests target uses synchronized groups, so new files need no pbxproj edit.

## 5. File ownership

The two sets are **disjoint**.
- **A** needs nothing outside its set. It only reads the env keys in `DesignSystem/FlatControlStyles.swift`. It must add no user-facing strings (`Localizable.xcstrings` is closed), and the hoisted FocusState stays inside `SourcesSettingsPane.swift`.
- **B** needs one new test file (`NuvioTVTests/RemuxVideoGridTests.swift`). It needs `PlayerEngineRouterTests.swift` only if (c) survives; recommend it does not. `MediaProbe.swift`, `PlayerEngineRouter.swift` and `NativePlaybackCoordinator.swift` then need **no edits**, and B's real footprint is `RemuxSession.swift` plus that test.
- Both agents build the same target, so serialise their builds (build lock).
