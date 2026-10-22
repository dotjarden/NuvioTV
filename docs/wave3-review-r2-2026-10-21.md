# Wave 3 review r2, 2026-10-21

Read-only Opus review of `git diff 6baddab46 HEAD` in `NuvioMobile-wave3` (branch `claude/wave3`, tip `40a04d3eb`, MPVKit ignored). The focus is on `40a04d3eb` ("review r1 fixes"). Paths are relative to `iosApp/`. A Python port of `RemuxVideoGrid.stamp` and of the old loop was run against the test generator and four MKV models (results below).

**Verdict: FINDINGS (P1 0 / P2 1 / P3 3).** Every r1 item is fixed. One P2 is left: the moved observer is always present in the view tree, but it sits on a lazy List row, so it can still miss the common case.

## r1 findings

- **P2-1 FIXED, with a residual (see P2-1 below).** The `.onChange` now sits on `PluginRepoEntryRow` (`SourcesSettingsPane.swift:382-400`).
  - The row is unconditional inside `pluginsSection`, and `pluginsSection` is unconditional at its call site (`:237-239`).
  - Both pending states are cleared on any removal path: alert or sync.
- **P2-2 FIXED.** `testObservedMillisecondCadenceStaysOrderedWithNoRewrites` uses `[656, 672, 672]`.
  - The generator declares by decode index, and GOP 36 means keyframe 144 sits at decode index 144, so `144 % 3 = 0` gives 656. The test asserts this.
  - The port of the old loop on that generator gives fragment-start dts **92065, 188833, 285601**, the log's exact values.
  - Doc comment and commit text are corrected.
  - The 667/667/668 case is kept as (b2).
- **P2-3 FIXED.** `segmentNetCap` 8 / `sessionNetCap` 64.
  - Reset points: the segment count resets on `fragmentStart` (before the boundary keyframe's own stamp, so its net counts toward the new segment) and in `reposition`. The session count never resets.
  - The check runs before the write (`RemuxSession.swift:1076`). `break` leaves the packet `while` (no enclosing switch). `.error` reaches `fail("grid net cap…")` at `:1143`, ahead of the `everRepositioned` self-heal, and `failIfPreplayback` then calls `fallbackMidPlay` when the phase is `.playing`.
- **P2-4 FIXED.** The unit is now the mode of the first 16 durations, and the outlier rule is gated on `learnedFromDuration`.
  - A tiny first packet can no longer poison the unit (`testSmallFirstDurationDoesNotPoisonTheUnit`).
  - The case of an atypically LARGE first duration is new; see P3-1.
- **P3-1 FIXED.** The "grid lags, never leads" comment sits beside the outlier rule.
- **P3-2 FIXED.** The MKV paragraph now says "lags pts unboundedly, as before".
- **P3-3 FIXED.** The keyframe-pts claim is qualified ("as long as its dts was not clamped").
- **P3-4 FIXED.** `av_rescale_q(learned, videoOutTB, videoTB)` (`:766`).
  - `videoOutTB` is set at `:876` in every run, right after `makeMux`/`reposition`.
  - On a fresh session no scan runs before the first run (`isFirstRun`), so nil never matters there.
  - The one exception: an audio switch before the first run clears `isFirstRun`, so the scan runs with `videoOutTB == nil` and `learnedDuration == 0`, giving tolerance 2 source ticks. That is the same value as before the commit; Cue/stss targets are exact keyframe pts, so it passes.
  - On the reposition path the previous run's out time_base is used, and it is identical every run (same timescale per the makeMux notes).
- **P3-5 FIXED.** `written = duration > 0 ? duration : unit`, and `prevDuration = written` is always ≥ 1. Covered by `testMissingDurationWritesTheUnit`.
- **P3-6 FIXED.** `SettingsDestructiveInk` is the one source.
  - The label applies `ink.title` in both states (`.red` at rest, `.primary` under `.light` on the platter) and `.fixed(ink.glyph)` on the platter.
  - At rest the glyph `.inherit`s the same `.red` that `ink.glyph` reports. The docs and the test match the view.
- **P3-7 FIXED.** "knob resolves".

## Cap model: can a legitimate MKV trip it?

Each model ran 30000 frames: ms-rounded presentation (`round(n·1001/24)` ms ×16), GOP 36, mini-GOP 8 pyramid, a fragment every 144 frames.

| Source model | unit | clamps | ptsNet | cap trips |
|---|---|---|---|---|
| mov, test generator 656/672/672 | 672 | 0 | 0 | no |
| mov, real ms-rounded stts | 672 | 0 | 0 | no |
| MKV, constant 656 (truncated 41 ms default), also 172k frames (2 h) | 656 | 0 | 0 | no (dts lags pts, as before) |
| MKV, per-block BlockDuration 41/42 ms (presentation order) | 672 | 0 | 0 | no |
| MKV, constant 672 (a 42 ms default) | 672 | 29134 | 24284 | yes, decode 652 (~27 s, segment 5) |

- With 41/42 ms durations, legitimate MKV (and mov) playback never comes near the cap.
- The only model that trips is a constant 42 ms default on 23.976 content. That grid runs ahead by 4.67 ticks a frame and is the same grid as the old formula, so 6baddab46 hit EINVAL at the same point and also went to mpv. That is not a regression, and it is now loud rather than silent.
- Open-GOP leading pictures after a reposition anchor can net a few frames per run start. That is also pre-existing (the old code wrote an error there), and the session cap of 64 is strictly more lenient.

## Unit rule: the settle at packet 16

- The provisional unit is the running max, and max ≥ mode. So at settle `6·unit` can only shrink, and dts steps forward by `6·(max − mode)` (6 ticks for 667/667/668, 0 for 656/672). It never steps back.
- A forward step satisfies movenc's fragment-start rule. Post-settle dts is exactly the steady-state value.
- Before the first duration arrives, the provisional `pts − anchor` guess is cleared (`learnSamples.isEmpty` branch), so it never feeds the max.

## Findings

**P2-1: The observer still sits on a lazy List row, so the common removal case can still miss it.** `NuvioTV/Screens/Settings/SourcesSettingsPane.swift:382-400`.
- The pane returns rows into the scaffold's lazy `List`; the file's own note at `:17` says the List re-fires `onAppear`. A row that is not realised does not run its `.onChange`.
- The Plugins section is the last one in the pane. With a repository expanded (Nuvio repos list 10–30 providers), the Remove row sits well below the entry row, so the entry row is very likely scrolled off-screen when Remove is confirmed.
- When the LAST repository is removed, the List shrinks and the entry row is re-realised with the new value. `onChange` does not fire on first appearance, so focus does not move and `pendingFocusAfterRemoval` stays set. That is r1 P2-1's fixture case again.
- The stale value then fires on the next repositories change (the next install), which is mostly harmless because the user is already in the field.
- `pendingPluginRepoRemoval` has the same gap for a sync removal while the row is off-screen.
- Smallest fix: move the body into `private func reconcilePendingRemoval(_ urls: [String])` and call it from the existing `.onChange` and from `.onAppear { reconcilePendingRemoval(plugins.repositories.map(\.manifestUrl)) }` on the same row. The re-realised field then takes focus when it is actually in the tree.
- Alternative: `.onChange(of:initial: true)`.
- Verify on device in the Test profile with a repository of more than 8 providers expanded.

**P3-1: The provisional "largest so far" lets a long or corrupt FIRST duration inflate the slack for up to 15 packets.** `NuvioTV/Screens/RemuxSession.swift:1898-1903`.
- Example: a 2 s leading still (32000 on 1/16000).
  - `slot − 6·32000` is negative, so dts is clamped to 0 and bumped to 1, 2, … 15. The first fragment gets 1-tick trun durations, composition offsets up to ~2.6 s, and one sample spanning the jump at settle.
  - The jump is forward and the result is valid ISO BMFF. It is bounded to the first 16 packets of the session (samples survive reposition).
- A corrupt huge duration among packets 1–15 is worse: the outlier rule is still off, so `step` takes it and the grid stays ahead after settle. That ends in clamps, nets and the cap, so mpv takes over: loud, not silent.
- Smallest fix: make the provisional unit the running MODE of the samples so far (ties → the larger) instead of the max. One odd packet then poisons at most one packet; `[1, 672]` still gives 672.
- Optionally, also apply the outlier test against the provisional unit once 3 or more samples exist.

**P3-2: The grid-cap failure classifies as `.unknown`.** `NuvioTV/Screens/RemuxSession.swift:1143` with `Player/PlaybackFailureClassifier.swift:150-164`.
- `"grid net cap at segment N"` is not engine-internal and carries no code, so it classifies as `.unknown`. This matches the old write-error path, which also passed no code.
- If an earlier read error in a repositioned session set `_lastErrorCode`, that stale code classifies the cap instead.
- Fix: add `|| stage.hasPrefix("grid net cap")` to `isEngineInternalStage`, which gives `.local`, the engine's own limit.

**P3-3: The main regression test does not pin the log's numbers.** `NuvioTVTests/RemuxVideoGridTests.swift:151`.
- It asserts only `oldFragmentViolations > 0`. Collecting the old loop's fragment-start dts and asserting that the first two are `[92065, 188833]` would tie the test to the device log byte for byte. The generator already produces these values.

## Rules re-check

- No `.xcstrings` or pbxproj changes.
- No new user-facing strings: the only touched `String(localized:)` line is the pre-existing "Repository manifest URL". The cap message and the `fail` stage are logs and diagnostic stage keys, as the existing "read/write error at segment" is.
- `nonisolated` is on `RemuxVideoGrid` (the new `private learn` is inside it) and on `SettingsDestructiveInk`.
- Logs:
  - The net line is latched by `gridNetLogged`.
  - The probe fires once (`gridProbeCount` == 1000).
  - The cap line prints once, then the session ends.
  - `ptsNets=` rides on the existing every-15-segments line.
- Hot path:
  - `learnSamples` appends at most 16 times per session, then one 16-entry dictionary at settle, then nothing.
  - `netCapExceeded` is two compares.
  - The `stamp` path has no other allocation.

## What is good

- The 656/672 test is now the primary case. Its generator reproduces the device log's fragment-start dts exactly, and the old formula fails it.
- The cap restores the pre-W3 "loud fallback" contract for every grid-ahead source while tolerating sporadic nets. The model shows no legitimate ms-rounded MKV or mov goes near it.
- The settle switch can only move dts forward.
- `SettingsDestructiveInk` and its tests now describe exactly what the view draws.

**Tally: P1 0 / P2 1 / P3 3.**
