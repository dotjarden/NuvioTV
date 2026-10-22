# Wave 3 (`claude/wave3-all`) review r3, 2026-10-22

Read-only Opus review in `NuvioMobile-wave3c`, branch `claude/wave3-all`, tip `0bed3fa4e`. Scope: the three late commits, `git diff 6b44a8c82..0bed3fa4e` (5 files, +464/−31):
- `dc1f23a22` FEAT-82: `DetailActionGlyphScale` + `DetailView.actionLabelBody`.
- `45a48b039` BUG-194: `DetailPopGate.Decision.regrab`, the away clock, `DetailPopRegrabTests`.
- `0bed3fa4e` BUG-194: `regrabPopTarget` wiring, `[DetailPop]` lines in every build under `-debug.detailFocusProbe YES`.

Context read: `docs/research/wave3c-r0-2026-10-21/PLAN.md` (R0 findings), `docs/design/hig-hybrid-contract.md`, `docs/research/batch-p-device-pass-2026-10-20/README.md`, `ViewerInputClock`, `UncoverRestorePolicy`, `StageController`'s Home regrab, the BUG-187/194 tests. `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor`. Paths are relative to `NuvioMobile/iosApp/`. No build or test was run for this review. The recorded "full gate green (2274/0)" (`2512bc9`) predates these commits; the late commits carry only "84 Detail tests green".

**Verdict: FINDINGS: P1 0 / P2 1 / P3 4.**
- BUG-194's re-grab is sound and bounded. Its fallback is exactly rc11's behaviour (hold, then the late rungs), so it cannot ship anything worse than rc11. It needs the rig's video before anyone calls it fixed.
- FEAT-82's mechanism is right (layout-neutral, contract-compliant), but it covers three of the seven secondary glyphs Cinematic can show. In Steven's config Start Over appears on every title with a saved position, so the complaint survives on a common screen (P2-1).

## Findings

**P2-1: FEAT-82 covers three of seven secondary glyphs; Start Over, Shuffle and the In Library checkmark keep their own optical size.**
- `Screens/Detail/DetailActionGlyphScale.swift:17-24` measures `play.rectangle.fill`, `checkmark.circle` and `plus`. `checkmark.circle.fill` is a safe alias of the ring.
- `checkmark` is a guess at ×1.25 (`:22`, "unmeasured; treated alike").
- Everything else falls to ×1 (`:27-30`). In Cinematic, `usesIconOnlyLabel(primary: false)` is always true (`DetailView.swift:2309-2311`), so these all render icon-only beside the scaled ones:
  - Start Over `arrow.counterclockwise` (`DetailView.swift:2625`). It shows on every title with a saved position: Steven's Continue Watching titles, in his own Detail look.
  - Shuffle `shuffle` off / `shuffle.circle.fill` on (`:2291-2293`, `DetailActiveGlyph.swift:80-81`): series, when the global switch is on.
  - In Library `checkmark` (`:2264`): unmeasured; ×1.25 may overshoot.
- His rc11 words were "the icons are still not all the same size". On a resumable film the row will again show one glyph at its own size.
- Fix:
  - Measure the four on the box in the same R0 session, with the same crop method as `21-detail-rest` / `22-detail-btn*`:
    - a film with a saved position, In Library;
    - a series with Shuffle off and on.
  - Add the four to `measured`.
  - Make the table's coverage enforceable: move the secondary symbol names into constants (as `DetailActiveGlyph.shuffleOnGlyph` already is), have `DetailView` read them, and add a test that every constant has a `measured` entry. A new glyph then cannot ship unscaled.
  - Alternative (design call): move the bare glyphs to their `.circle` siblings (`plus.circle`, `arrow.counterclockwise.circle`, `shuffle.circle`). They then share the ring's optical size by construction, and only the trailer needs ×0.89.
  - Either way, do not size glyphs with `.font(.system(size:))`: the contract's Typography row bans it at call sites. `scaleEffect` is the contract-safe tool, and it is not a focus chain.

**P3-1: the re-grab runs one run-loop turn after the stray. Home defers 0.15 s (`regrabDefer`). The residual is input the window recognizer never sees.**
- Code: `DetailView.swift:2500-2509` vs `Screens/Home/StageController.swift:404-417` / `UncoverRestorePolicy.swift:30-34`.
- The question asked: does the clock stamp presses at begin? Yes.
  - `ViewerInputRecognizer.pressesBegan` stamps every arrow, Select, Menu and Play/Pause press as it begins (`Screens/Home/ViewerInputClock.swift:101-107`). Window gesture recognizers see the event before the responder chain's focus move.
  - Swipes are stamped at 40 pt of travel (`:127-134`), below the engine's move threshold.
  - `record` sets `lastAt` synchronously and posts `didRecord` (`:56-60`). That ends the restore at once (`DetailView.swift:1098-1100`).
- So a viewer move normally reaches `onChange(of: focusedRow)` either with `popRestoreRow == nil` (gate not consulted) or with `hasInput == true` (`.release`). The "press stamped after the move it caused" case does not arise for anything the recognizer sees.
- `regrabDefer`'s doc cites `HomeUpSwipeCatcher`'s note. That note is about the `UISwipeGestureRecognizer` callback, which recognizes after the engine moved (`HomeUpSwipeCatcher.swift:203-215`), not this passive recognizer. Detail skipping the defer is consistent with the clock's design.
- Residual: moves the recognizer never sees (VoiceOver gestures, a game controller's thumbstick) are undone, at most 3 times within 1.3 s. Pre-rc11 the free rungs did the same at 0.8 and 1.1 s, so this is the same class, just sooner.
- A second, smaller residual: strays before the first landing (`landed=0`) spend the 3-regrab budget during the transition, where forced writes do not stick. If they exhaust it, the real post-landing stray falls back to `.hold` (rc11 behaviour).
- Fix:
  - Keep the immediate re-grab.
  - Say the residual in `regrabPopTarget`'s doc.
  - Add the rig checks below (items 5, 6).
  - If item 5 ever shows a lost press: re-grab immediately only for the `.defaultFocus` signature (`row == nil && heroFocus == .play`, the analogue of Home's `regrabsImmediately(fillerFocused:)`), and use the `regrabDefer` path with a clock re-check otherwise.
  - If item 1 shows `landed=0` strays eating the budget: gate `.regrab` on `popLandedAt != nil`. The ladder's forced rungs already cover the transition.

**P3-2: four gaps in the new Release probe, each of which would hide the failure it is meant to show.**
1. `end … via=viewer` does not say which input (`DetailView.swift:2519-2527`).
   - The case it hides: a resting thumb rolling 40 pt on the clickpad records `.swipe`. That releases the restore, and the engine's Play stray then stays: the BUG-187 symptom.
   - Home's retire line carries `input=` (`StageController.swift:508`).
   - Fix: add `input=%@` with `ViewerInputClock.shared.lastKindLabel`.
2. `land` prints the target key, not the focused card (`:2589-2593`).
   - Focus can land on the row's `UIKitFocusableFillerItem` (the BUG-188 class: the row binding is set, the card state is nil). That decides `.landed`, so no re-grab runs, and the line reads as the card.
   - Fix: add `idx=\(popProbeFocusedKey)` (`-` for a filler).
3. A re-grab that `shouldApply` refuses is silent but still spends a re-grab (`:2537-2551`): the rows' focus state not yet nil, or a cast index gone after the reload.
   - Fix: when `via` starts with `regrab`, log `rung skipped … current=…` on the refusal.
4. Play focused before the first landing is invisible.
   - `focusedRow` stays nil → nil, so no `stray` line, and `away=` starts only after a landing (`DetailFocusMemory.swift:119-122`).
   - If the pre-landing frames show Play, that is a visible "first move" the probe calls clean.
   - Fix: in `.onChange(of: heroFocus)` (`DetailView.swift:1173`), while `focusMemory.restoreLive`, log `[DetailPop] hero new=… t=…`.

**P3-3: the replay tests drive a copy of the view's switch, not the view's bookkeeping.**
- `DetailPopRegrabTests.swift:82-103` (`report`) re-implements `DetailView.swift:855-880`. If `DetailView` dropped `noteStray` or the `popRegrabs += 1`, every test still passes.
- Fix: move the per-decision bookkeeping into `DetailFocusMemory`, e.g. `func record(_ d: DetailPopGate.Decision, old:, new:, at:)`. Call it from both the view and the test.
- Smaller items:
  - `testRegrabDecisionIgnoresCallOrder` (`:66-77`) cannot fail for a pure function. Replace it with a test of `regrabPopTarget`'s stand-down rule, extracted as a pure `DetailPopGate.regrabStillWanted(current:restoreLive:inputSincePop:)`.
  - Drop the defaults on `decide`'s `regrabs:` / `clockLive:` (`DetailFocusMemory.swift:189-190`) so a new caller cannot silently get the pre-rc11 hold. Pass `clockLive: false` explicitly in `DetailFocusReturnTests.swift:140-155`.
- Timing: no test sleeps, dispatches or reads a real clock (all stamps are fabricated, accuracies 0.0001–0.0005 s), so nothing here can flake.

**P3-4: the "card is the only default candidate" model is still written down, and it is the model behind the Wave 1 misread.**
- Where it stands:
  - `DetailFocusMemory.swift:74`, `:77`, `:148-153` ("the remembered card is the ONLY default candidate (so the engine's late restoration lands on it, not Play)");
  - `DetailView.swift:576-581` ("the remembered card is the default focus target … Ended on the landing … the default-focus modifiers read them").
- Since the sentinel `.defaultFocus` was removed in the Wave 1 pass, Play is the only default. The re-grab exists because the engine's late restoration lands on it.
- `DetailPopGate.defaultTarget`, `landedWindow` and `landedHoldActive` (`:171`, `:179-181`, `:199`) have no production caller; only `DetailFocusReturnTests.swift:161-169` call them.
- Fix: rewrite those docs to the rc11 mechanism (forced rungs → landing at the end of the transition → the engine's restoration to Play → re-grab), and delete the three dead members and their tests.

## Checked and fine

**FEAT-82**
- Layout: `.scaleEffect` on the `Image` inside the icon-only `Label` (`DetailView.swift:2663-2671`) is a render transform.
  - Layout, `onGeometryChange` (Play's measured height, `:2697`) and the square side (`squareSide`, `:2680-2686`) are untouched.
  - The scale is centred, so the ×1.25 `plus` overhangs its layout box by 2.5 pt into `Theme.Spacing.md` padding. Nothing clips it: `.glass` does not clip its label.
- VoiceOver: `.accessibilityLabel(Text(title))` stays on the `Label`. `Text(title)` with a `String` is verbatim, as `Label(String, systemImage:)` was, so there is no localization change.
- Play: in Cinematic it never takes the icon-only branch. In Classic + Icons Only it does, with `play.fill` → ×1.
- Classic text labels: the else-branch is byte-for-byte the old `Label(title, systemImage:)`.
- `.labelStyle(.iconOnly)` still sits on the `Label` itself, so `DetailActiveGlyphTitleStyle` (outer) is still shadowed, as `DetailActiveGlyph.swift:127-130` requires.
- Factors: 25/28 = 0.893, 25/20 = 1.25, both within the tests' 0.8–1.3 band. They are ratios, so valid at any Size step and for Open Sans: symbols scale linearly with the font's point size.
- Icons Only + Square: the squares are the label frame at Play's height (`DetailActionSquareLabel`), unchanged. `DetailActionSquareUITests` measures frames, which do not move.
- Contract: a static, non-focus `scaleEffect` is neither a "custom `scaleEffect` focus chain" (Focus row) nor a point size at a call site (Typography row).

**BUG-194 decision**
- `decide` (`DetailFocusMemory.swift:188-196`) order: viewer input → `.release`; target row (key passed only when the row matches) → `.landed`; otherwise `.regrab` only with `clockLive && regrabs < 3`, else `.hold`.
- The clock is live on Detail by itself (`ViewerInputClockInstaller` at `DetailView.swift:1095`), not only after Home's strip mounted.
- Existing `DetailFocusReturnTests` keep `.hold` through the defaults.

**BUG-194 re-grab**
- `regrabPopTarget` (`:2500-2509`) re-checks three things on the next turn: the same generation (a newer restore stands it down), `restoreLive` (retire or viewer end stands it down), and no input since the pop.
- Then a forced rung. `shouldApply(force: true)` makes it a no-op if focus already returned.
- `n` is read after the increment, so the first is `regrab-1`.
- A retire that races the pending block either ends first (block stands down) or runs after it (harmless).

**Bookkeeping**
- `goLive` resets the regrab, landing and away state (`:78-88`, tested). `endRestore` leaves the probe counters, which only the next `goLive` resets and nothing reads while idle.
- The stray to Play fires `onChange(of: heroFocus/heroHasFocus)` → `focusMemory.clear()` (`DetailView.swift:1175`, `:1813`). That empties the remembered row/key but not `liveTarget`, and the landing re-notes the card through `noteDetailFocus`. If the re-grab fails and focus stays on Play, the memory is correctly empty.

**Interactions**
- Hero return: `.regrab` returns before `handleFocusRowChange`, exactly like `.hold`, so the engine's stray never arms `armHeroReturn`. The landing drops the held change, so `endPopRestore` replays nothing. Unchanged: the second landing runs `handleFocusRowChange(old: nil, new: .cast)`, as the free rung's landing did in rc11.
- BUG-27 Menu-to-top is Home-only: Detail has no exit handler, and Menu = back. A Menu press during the live restore is stamped (`.menu`), ends the restore, and any pending re-grab stands down on `restoreLive`. The Home pop path is untouched.
- FEAT-35: `.defaultFocus($heroFocus, .play)` is unchanged (`:1104`). A first entry has no armed restore, so the gate is idle. The late Play claim is gated on `userInteracted`, which any row visit sets (`:2356`), so it cannot fight a re-grab.
- Rows:
  - Studios: re-grabs through `focusedCompanyIndex`, the same path as cast (now logged `applied`).
  - Poster rows: re-grab through the request, applied by the row's `onChange(of: restore)` (`:3255-3259`), one SwiftUI update after a cast re-grab.
  - A different card in the target row is a landing (row-only, review r1 P3-1), as before.

**Concurrency, Release cost, privacy**
- Concurrency:
  - `DetailActionGlyphScale` and `DetailPopGate` are `nonisolated`, with Sendable statics.
  - `DetailFocusMemory` is `@MainActor`, hence Sendable.
  - The `DispatchQueue.main.async` closure is MainActor-inferred, the same pattern as the existing rungs.
  - `focusedItemSummary` is MainActor by default, called from the view.
  - The tests are `@MainActor`.
- Release with the probe off:
  - `DetailFocusProbe.enabled` is a launch-latched `static let` (one `UserDefaults` read, then a load and branch).
  - Every logger guards first, and `focusedItemSummary()` and `popProbeFocusedKey` are evaluated only inside guarded calls.
  - Per focus change during a live restore: one `systemUptime` read, and one `"regrab-\(n)"` string per re-grab (≤ 3).
  - No new code references DEBUG-only state (`detailFocusProbeKey` is gone from `end`).
- Privacy: probe lines carry row names, indices, item ids, UIKit class names and coordinates. No hosts, so the rig-log staging rule's redaction is not triggered (still stage by name).

## Rig checks the owner must see

Run `scripts/device/ready.sh` first. Use Test 2, Steven's config (Cinematic Detail, Classic Home, Rounded, then Square for items 8 and 9), and a **Release** device build of `0bed3fa4e` (the probe logs in Release now) with `-debug.detailFocusProbe YES -debug.rememberLastProfile NO`.

0. **Gate on `0bed3fa4e`** before the box:
   - sim Debug + Release builds (the Release compile of the un-`#if`'d lines);
   - full NuvioTVTests;
   - `DetailActionSquareUITests`;
   - the BUG-187 cast/More Like This Back leg.
1. **Cast → biography → Back, ×5.** Each run, in order:
   - `live row=cast`;
   - `rung applied … force=1 … via=ladder` ×2 (≈17 / ≈368 ms);
   - `land … n=1` (≈570);
   - `stray to=hero item=… landed=1 regrab=1 n=1`;
   - `rung applied … force=1 … via=regrab-1` within ~35 ms;
   - `land … n=2 away≤50`;
   - **no `force=0` line**;
   - `end … regrabs=1 away≤50 via=retire focused=cast idx=<key>`.

   `moves=` will still read 3 with the fix. It is no longer the criterion; `away=` is.

   FAIL signals:
   - `stray … regrab=1` with no `via=regrab-1` after it (a silent refusal, P3-2.3);
   - `regrabs=2–3` (the engine re-asserting: ping-pong);
   - `away>100`;
   - any `force=0` line;
   - `stray … landed=0` lines (P3-1, pre-landing budget).
2. **`rec.sh` at 30 fps on two of those runs.** This is the verdict, not the log. Between Back and the card settling:
   - no frame with Play highlighted;
   - no upward page movement;
   - the FEAT-60 compact title logo does not blink (`inRows` reads `focusedRow != nil`, nil for the stray's frame or two).

   Before the landing too (P3-2.4: the probe cannot see a pre-landing Play).
3. **Studios chip → studio page → Back, ×3:** `moves=1 regrabs=0 away=0` as in Wave 1, or, if a stray appears, the same re-grab sequence as cast.
4. **More Like This (and a Collection if the title has one) → Back, ×3:** `rung sent … via=ladder`, `land`; any `stray` followed by `rung sent … via=regrab-1` and `land n=2`.
5. **Lost press, ×5 each, separate pops.** Press once right after the card lands (~0.7 s after Back), and once early (~0.3 s, inside the transition):
   - Up → studios row (or hero);
   - Down → next row;
   - Right → next cast card.

   Expect: `end … via=viewer` before any re-grab line; focus where the press sent it; one press = one move. A `stray … regrab=1` followed by focus back on the card is a lost press → P3-1's narrowing.
6. **Thumb resting on the clickpad across the Back press** (Steven's grip), ×3: expect `via=retire regrabs=1`. A `via=viewer` with no deliberate input is the fake-swipe release; it needs P3-2.1's `input=` to confirm.
7. **FEAT-35 unchanged:** a fresh long-synopsis film from Search (Dune) opens on Play, and logs no `[DetailPop]` lines.
8. **Square corners: item 1 ×3.** Same expectations.
9. **FEAT-82 at rest and with each secondary focused,** Rounded then Square, full-size PNGs as in R0 `21/22-*`:
   - Trailer, Watched and Library glyph boxes at 25 ± 1 pt on the longer side.
   - Platters unchanged against R0 (300 px focused).
   - Zoom the crops: `plus` (×1.25) not visibly heavier-stroked than the ring; the ×0.89 trailer rectangle's edges crisp.
   - Then measure the four P2-1 glyphs: a resumable film for Start Over; In Library; a series with Shuffle off and on.
10. **Classic Detail** (Appearance → Detail look Classic):
    - Icons Only OFF: text labels' glyphs identical to R0.
    - Icons Only ON + Square: the squares are equal and as tall as Play. Note whether Play's unscaled `play.fill` now reads smaller than the 25 pt secondaries. Not Steven's config; decide only if it looks wrong.

## Tracker note: yes, the Wave 1 "PASS" needs one

`docs/research/batch-p-device-pass-2026-10-20/README.md:24` marked "BUG-194 pop gate, cast row" PASS while its own log showed:
- `moves=3` on both cast runs (`:10`, `:15`);
- its own text describing focus leaving the row and the `+802 ms` rung pulling it back.

The pass judged "lands on the right card", not "one move". The `moves=1` it leaned on was the studios row (`:17`, `:25`). That PASS fed three records:
- the tracker's SHIPPED line ("lands on the cast card in one move … twice on the box", `docs/beta-feedback-tracker.md:356`);
- the rc11 triage's config theory ("the rig's probe saw one move … re-test in his exact Detail config, then look at what differs", same row);
- R0's A/B to-do list (`PLAN.md:47`: Card Depth, Medium+, Classic Home, White accent).

R0 then reproduced `moves=3` in his config and with the ring off. The bug was never config-dependent; rc11 shipped no fix for the cast row.

Note to add, on the BUG-194 row and in `docs/beta-feedback-items.json`:
- the rc11 "one move" claim was a misread of the Wave 1 log (cast `moves=3`, a ~230 ms Play stray pulled back by the 0.8 s rung);
- Steven's report was right in every config; drop the config A/B list;
- rc12's change is the engine-stray re-grab (`0bed3fa4e`);
- the device criterion is now `away=` ≤ 50 ms with a 30 fps recording, never `moves=`.

Correct the README row to FAIL (cast) / PASS (studios) with that pointer. The Batch P memory line "one drift fixed at +802 ms" is the same stray and should say so.

The rc12 DM should say plainly that rc11 did not fix this for the cast row, and claim "one move" only after rig items 1 and 2 pass.
