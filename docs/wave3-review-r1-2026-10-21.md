# Wave 3 review r1, 2026-10-21

Read-only Opus review of `git diff 6baddab46 HEAD` in `NuvioMobile-wave3` (branch `claude/wave3`, tip `abd22f780`, MPVKit ignored). Paths are relative to `iosApp/`. Context: wave3 plan (W3-1, W3-2, "Critique applied"), the critique, the commit message, `console-165-native3.log`.

**Verdict: FINDINGS (P1 0 / P2 4 / P3 7).** The grid rule is right for the file that failed, and the MKV-equivalence test is faithful. Four items need changes before merge: the focus-after-Remove observer is gone in the most common case; the regression test models the wrong cadence; the pts net turns a hard failure into silent corruption; and the outlier rule depends on a single packet.

## What the log actually says about the cadence (read this first)

The six fragment-start lines are exactly 96768 ticks apart (92065, 188833, … 575905), and every one reads −671. 96768 = 144 × 672. That fits the old formula only if:
- declared durations are **656/672**: ms-rounded timestamps (41/42 ms) ×16, i.e. a Matroska-origin MP4;
- the boundary keyframe itself declares 656, so with `vDur` re-learned the grid collapses below the previous dts and gets bumped to prev+1. Check: prev = 96768k − 7·672, so the keyframe dts is 96768k − 4703; k=1 gives 92065, k=2 gives 188833.
- movenc's ref is prev + 672, so the difference is −671.

The 667/667/668 cycle in the commit, the code comment and the tests does not produce constant values. `testFragmentStartNetLiftsTheKeyframe` uses exactly these 672 numbers, so the agent saw it, but the main regression test does not. The fix still holds: for a mov source the summed stts durations equal the source dts deltas, so the accumulated grid is the source dts shifted by a constant (`grid = dts_src + ctts(kf) − 6u`). It stays ≤ pts whenever the keyframe's composition offset is ≤ 6 frames, and it does not drift. See P2-2.

## Findings

**P2-1: Focus after Remove never fires when the LAST repository is removed.** `NuvioTV/Screens/Settings/SourcesSettingsPane.swift:484-488`.
- The `Color.clear … .onChange(of: plugins.repositories…)` observer sits inside the `else` branch of `if plugins.repositories.isEmpty` (:390/:394 … :479).
- When the only (or last) repository is removed, that branch is torn down in the same update, so the observer never sees the change. `manifestFieldFocused` is never set and `pendingFocusAfterRemoval` stays set.
- That is the device fixture's case (one repo). The stale value can also fire later: reinstall the same URL, then a sync removes it, and focus jumps to the field out of nowhere.
- The existing r2 P3-3 clear of `pendingPluginRepoRemoval` has the same gap.
- Fix: move the observer out of the `if/else`, e.g. attach the `.onChange` to `PluginRepoEntryRow` at :382 (always present), or put the `Color.clear` before the `if`.

**P2-2: The regression test does not model the failing file's cadence.** `NuvioTVTests/RemuxVideoGridTests.swift:102-135` uses 667/667/668; the log says 656/672 (above).
- The new rule passes both, but the test that "proves the regression" proves a different one.
- The doc comment (`RemuxSession.swift:1775`) and the commit message state the wrong cadence too.
- Fix: add a case `durations: [672, 672, 656]` (or ms-rounded `Int64((n·1001/24).rounded())·16` pts with declared = decode-order deltas). Have it assert zero clamps, zero nets, `pts` untouched, and the fragment-start invariant, and assert the old formula fails it (it does: the keyframe-656 collapse). Correct the comment and the commit text.
- Gate W3-1 on the device pass's `[Remux] grid probe` line for the real file. It must show the 656/672 histogram, `clamps=0 nets=0`.

**P2-3: The pts net converts a loud fallback into silent, session-long corruption.** `NuvioTV/Screens/RemuxSession.swift:1870-1871` (net) and `:1061-1066` (logged once).
- When the grid runs systematically AHEAD of pts, the clamp and bump fire on most B-frames and the pts net rewrites their pts. The old code hit EINVAL there and handed over to mpv.
- Cases where the grid runs ahead:
  - an MKV whose DefaultDuration is a rounded 42 ms (672 vs a 667.33 mean: +4.67 ticks/frame, so the slack is gone after about 860 frames);
  - a mov source whose keyframe composition offset is more than 6 frames;
  - VFR content faster than its declared rate.
- The new code now presents reordered frames at the wrong times for the rest of the film and logs it once.
- Fix: count `ptsNetFirings` per segment (or per session). Past a small cap (say > 2 in one segment, or > 8 per session), set `runEnd = .error` so `NativePlaybackCoordinator`'s MID-PLAY fallback takes over, as before. Add the counter to the existing `seg N done` line.

**P2-4: Learn-once plus the outlier rule make the first packet's duration a single point of failure.** `NuvioTV/Screens/RemuxSession.swift:1848-1856`.
- `unit` is the FIRST positive declared duration for the whole session, and any later duration > 8·unit is replaced by `unit`.
- If the first packet declares an atypically small duration (a 1-tick leader sample, or an edit-list remnant), every normal frame counts as an "outlier":
  - the step is `unit` for every packet, so the grid crawls;
  - the written duration is `unit`, so the trun sample durations collapse and the composition offsets grow to the segment length.
- The old per-packet re-learning recovered on the next packet; this never does.
- An overestimated first duration is benign (more slack).
- Fix (smallest): re-learn when the outlier branch fires on 3 consecutive packets that agree (`learnedDuration = duration`). Alternatively, learn from the mode of the first ~16 durations; the histogram is already collected.

**P3-1: (c) The outlier rule versus legitimate long frames.** `:1855`.
- A real still (VFR mov, a held title card longer than 8 frames) gets `step = unit` and `written = unit`. The grid then lags pts by (d − u) for the rest of the run.
- That lag is safe for ordering: pts is untouched, so there is no audio desync, and dts only moves further below pts. The still's trun duration is short only when it is a fragment's last sample.
- Acceptable. Document it as "grid lags, never leads" next to the rule.

**P3-2: (a) MKV drift is unbounded, but behind pts, and identical to before.** `:1786-1790`.
- With the truncated 41 ms default (656) against a 667.33-tick mean, dts falls behind pts by 11.3 ticks/frame. That is about 2 minutes of composition offset by the end of a 2-hour film.
- The clamp bounds only a grid that runs AHEAD; nothing bounds the lag.
- The old code did exactly the same, so the equivalence claim holds and the replay test covers it (`:141-144`).
- At a run seam (reposition) the next run restarts at `anchor − 6u`, so tfdt jumps forward by the accumulated lag, also as before.
- Say "lags unboundedly, as before" in the MKV paragraph rather than implying the clamp bounds it.
- If a 656/672-ALTERNATING MKV exists (per-block BlockDuration), the new grid tracks it exactly, where the old one jittered by 16·index. That is a strict improvement, though not "identical stamps".

**P3-3: (d) Fragment-start net and the reorder window.**
- The net lifts dts only to prev + prevDuration, which equals the unclamped grid value unless an earlier clamp or bump pushed prev up. In the healthy case it cannot exceed a later packet's pts.
- In the degraded case (grid ahead), the lifted dts can sit above the keyframe's own pts and a following leading picture's pts (open GOP). The pts net then rewrites those pts. That is the P2-3 situation, so the cap there covers it.
- Also: the "the opening keyframe keeps its pts" claim (`:1777-1780`) holds only when the keyframe was not clamped. Qualify it.

**P3-4: The `scanToBoundary` tolerance is in the wrong time base (pre-existing; the touched line).** `:763`.
- `videoGrid.learnedDuration` is in the OUTPUT time base (1/16000 for MKV) but is compared with SOURCE pts (1/1000).
- So the tolerance is 656 ms instead of 41 ms: the scan accepts a keyframe up to ~0.65 s early, and the abort check is 16× looser.
- Same as with `vDur`. Fix: keep the session's video out time base after the first `makeMux` and rescale with `av_rescale_q(learned, outTB, videoTB)`.

**P3-5: Declared durations ≤ 0 are written back as-is.**
- In `:1852`, `written = duration`, so a 0 or negative duration reaches movenc while the grid steps by `unit`.
- The net's `prevDuration = max(written, 0)` keeps it consistent with movenc's ref, so nothing breaks, but the frame's sample duration is 0.
- Fix: `written = duration > 0 ? duration : unit`. That changes the MKV-equivalence only for packets without a duration.

**P3-6: `SettingsDestructiveInk` docs and test describe a rule the view does not apply.** `NuvioTV/Screens/Settings/SettingsRowViews.swift:783-795, :823`.
- The docs say `title == nil` means "leave the system role colour", but the view pins `AnyShapeStyle(.red)` at rest (:823).
- They also say "nil here means use `.primary`" while the focused branch returns `Color.primary`.
- The at-rest `glyph: Color.red` is never used (rest = `.inherit`). `testAtRestKeepsTheSystemRole` asserts a nil the view ignores.
- `Color.red` in the dark scheme is systemRed (#FF453A), very likely what the role drew, so the visual risk is low. But if tvOS's destructive list tint differs, the rest look changes.
- Fix: either return `.red` at rest and test that, or leave the rest state unstyled (apply the foreground only on the platter) so the role colour stands. Fix the comments either way.

**P3-7: Minor wording.** `NuvioTVTests/HomePerfKnobsTests.swift:4`: "knob resolve" should be "knob resolves". The `HomePerfKnobs` header is fine.

## Answers to the brief

**1(b) Reposition.** `reposition` resets slot, index, prevDTS and prevDuration and keeps the learned duration; this is the right call, since the unit is a stream constant. The run's first packet opens a new muxer context, so it correctly carries no `fragmentStart`. For mov, run seams are continuous: both runs equal `dts_src + ctts(kf) − 6u` when keyframe offsets match.

**1(e) `opensFragment`.** Declared per loop iteration (:1016), set only after a successful cut (:1033), consumed by the next `stamp`, so it covers exactly one packet. The pre-origin drop cannot eat a boundary keyframe (pts ≥ boundary ≥ origin).

**1(f) Isolation.** `RemuxVideoGrid` is a `nonisolated struct` held as a local of the remux function on the remux thread. `scanToBoundary` captures it on the same thread. There is no main-actor touch.

**1(g) Memory.** Both logs are latched per session (`gridNetLogged`; `gridProbeCount` never resets across runs). The histogram does at most 1000 dictionary inserts, then nothing on the hot path. Bounded. Note that the probe prints at packet 1000 (~42 s, about segment 7); a session failing earlier prints only the net line.

**MKV equivalence.** It holds for constant declared durations, which is the real matroskadec path: DefaultDuration truncated to ms, or framerate-derived with round-down, gives a constant 656. The test replica of the old loop (`RemuxVideoGridTests.swift:14-38`) matches 6baddab46 :1051-1063 line for line, including `vDur` surviving reposition. For alternating durations the stamps are not identical, but the old code was broken there anyway.

**2. Destructive row.**
- For a plain `Button(role: .destructive)` in a native settings List, only `\.isFocused` is written. The flip depends on the same label-level read that `SettingsRestPlatter`'s fade and the FEAT-50 explainer already rely on, so it should fire on hardware.
- `settingsRowIsFocused` and `settingsRowPlatterActive` are never published for this row: no custom ButtonStyle and no FocusState. They matter only inside a custom container, where they correctly treat the container platter as "on platter".
- `.light` on the platter matches `SettingsAccentTint` (which also flips on `\.isFocused`), not `SettingsPlatterInk` (container keys only, by design for Menus). That is the right model for a Button label.
- The "Settings toggle rows never report focus" note is about XCUITest `hasFocus`, not the SwiftUI environment.
- Whether the explicit `.foregroundStyle` beats the system's focused label tint is device-only: check Sources :116/:182/Remove Repository, Services, and Account in the Test profile.

**3. Hoisted focus.**
- `FocusState<Bool>.Binding` with `.focused(fieldFocused)` and `fieldFocused.wrappedValue` is correct.
- The onChange can fire while the alert is still dismissing. `TvOsPluginRepository.removeRepository` updates `_uiState` synchronously, so the FlowWatcher emission lands within a runloop turn or two.
- If the device shows the List winning, wrap the write in `Task { try? await Task.sleep(for: .milliseconds(350)); manifestFieldFocused = true }`.
- `pendingFocusAfterRemoval` is cleared only when the URL leaves the list. It is not cleared on the empty-list path (P2-1), and not if the Kotlin removal never happens.

**4. Knob collapse.**
- Render-equivalent to 3cf873994: `.mask(alignment: .top) { StripEdgeMask(gutter: StripGeometry.stageBottomGap) }` and `.visualEffect { … pageOpacity(minY:…, pageHeight:) }`. The capture is now the hoisted `page` copy of `pageForRow`, the same value.
- Not byte-identical: the modifier structs remain as wrappers, which is harmless. The call-site comments survive.
- No reference to `noStripEdgeMask`/`noPageOpacity` remains in `iosApp/` or the outer `scripts/`.
- `HomePerfKnobsTests` stays meaningful: the key, the default-off check, the YES coercion, suite isolation, and the latched value.

**5. Tests.**
- The tests exercise the real `RemuxVideoGrid`, not a mock.
- The old-formula replica is faithful.
- A regression to per-packet re-learning of the slot step would trip `testNetflixCadence…`'s `clampCount == 0` / `netFirings == 0`. Re-learning `learnedDuration` would trip `testReposition…:196`. A wrong slack unit would not be caught (minor).
- Gaps: the 656/672 cadence (P2-2), and nothing covers the remux-loop wiring (`opensFragment`, the logs). That is device-only.

**6. Rules.**
- No `.xcstrings` or pbxproj changes.
- No new user-facing strings: the Settings titles and the alert are unchanged, and the `[Remux]` prints are logs.
- `nonisolated` is on `RemuxVideoGrid` and `SettingsDestructiveInk`.
- Both remux logs fire once per session.

## What is good

- The accumulate-durations rule is the right root fix for mov. It reduces the grid to "source dts plus a constant", so movenc's fragment-start check holds by construction. The rational-rate alternative was correctly rejected for MKV.
- The rule is extracted into a pure, documented `nonisolated` struct whose tests include a line-for-line replica of the old loop and assert that the old loop fails.
- The diagnostics are cheap and bounded, and they are exactly what the device pass needs: the histogram, the clamp count and the net count.
- The knob deletion is clean and complete; the Card Depth knob and its tests survive intact.
- The destructive-row ink follows the kit's established `.primary`-under-`.light` flip instead of pinning a colour onto the platter, and the glyph red (5.4:1) is the only fixed colour.
- The hoisted `FocusState` is the right shape. `statusMessage = nil` on removal closes W3-2 (d).
