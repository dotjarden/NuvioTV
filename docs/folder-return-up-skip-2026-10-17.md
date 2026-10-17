# Folder-return Up-skip (2026-10-17)

Pre-existing Classic Home focus bug, found during the 10-17 SwiftUI performance + focus device pass
(`docs/swiftui-perf-and-focus-review-2026-10-17.md`, device-pass table). The base `f78fe7ea8`
reproduces it, so the Home split did not cause it.

**Branch:** NuvioMobile `claude/folder-return-up-skip`, off `tvos-shared-extraction` `2353a5e9b`.
It lives in the local clone `~/Claude/Projects/NuvioMobile-up-skip`, where MPVKit is a symlink, so
stage files by explicit path. Not pushed, not merged.

| Commit | What |
|---|---|
| `0af0a9236` | First fix: CW / Upcoming re-identified after a pop, redirect of an Up that lands on the hero, two UI legs, gate tests |
| `a14d0e8a0` | Review r1 fixes (0 P1 / 3 P2 / 6 P3) |
| `6697deb3c` | Review r2 fixes (0 P1 / 1 P2 / 4 P3) |
| `f4a041626` | Device-pass findings: stranded-container redirect, scroll then ask, CW / Upcoming re-identify on redirect, probe logs |
| `498e9d6d3` | Review r3 fixes (0 P1 / 3 P2 / 5 P3): stranded state read directly (`RowsContainerFocus`) |

## Repro (Living Room ATV, Test 2, Classic, Nuvio-style hero, Rail mode)

Rows: Continue Watching, Upcoming, Test Collection (one folder tile), then the catalogs. Focus the
tile, Select (folder page), Menu back (the restore lands on the tile), then Up. The Up sometimes
goes to the hero CTA without the rows scrolling, and Upcoming / CW can't be reached (Down goes back
to the tile). A second Up from Upcoming can do the same.

## What was actually wrong

There were three mechanisms. The simulator shows the first one. Only the Apple TV shows the other
two.

1. **After a push and pop, Continue Watching and Upcoming lose their ability to take focus.** These
   two rows are plain siblings above the `ForEach` in the rows `LazyVStack`. In the simulator, after
   the pop the engine found no Up candidate in CW, so the BUG-112 ladder ran. Every `@FocusState`
   write it sent to CW was dropped (`apply … after=nil`), even with CW on screen, its buttons
   enabled and present in the accessibility tree. The ladder's last rung then handed focus to the
   hero. Catalog and collection rows (the `ForEach` cells) came back fine. A fresh `.id` for the two
   rows fixes it. Root cause inside SwiftUI unknown.
2. **The rows container can take focus.** The rows `ScrollView` has `.onMoveCommand`, which makes it
   a focusable container on tvOS. On hardware, an Up that finds no row above it can focus the
   container itself: `[Focus] next=PlatformGroupContainer frame={{0, -408.5}, {1840, 5127}}`.
   Nothing is drawn as focused, no row and not the hero owns focus, the next Up does nothing, and
   the carousel auto-advances. This is the "vanished focus" case.
3. **On hardware, CW drops programmatic focus writes from the CTA, and any write issued during a
   scroll is lost.** Down from the CTA reaches CW at once, yet asks sent while the CTA held focus
   were dropped even after the scroll had settled, until the row was given a fresh identity. Asks
   sent together with a `scrollTo` were dropped for every row.

The console's `upFallback … declined reason=staleInput` and `reason=rail` lines (the brief's
suspects) were side effects:

- On hardware the Up press reaches the app 30–180 ms after the focus update it caused, so the hero's
  focus gain always looks stale at first.
- The up-into-hero reveal declined outright in Rail mode.

## The fix

- `remountTopRowsAfterPop` (`HomeView.swift`). 0.6 s after a pop to Home's root, CW and Upcoming
  get fresh identities (tokens passed to `HomeRowsList` outside `HomeRowsRefresh`, so the
  `.equatable()` cells don't re-render). It skips a row that holds focus and the pop's origin. An
  origin CW / Upcoming that the restore missed is re-identified after the restore expires. A pop
  serial guards both closures.
- `redirectUpIntoHero`. When an Up from a row that has a row above it lands on the CTA or strands
  focus on the rows container, focus goes to the row above. The sequence:
  1. A CW / Upcoming target is re-identified first.
  2. The scroll runs alone.
  3. Focus asks follow at 0.4 s and 0.8 s, with another re-identify at 0.6 s if it hasn't landed.
  4. It gives up at 1.3 s. If focus is still on the container, the CTA takes it, so focus is never
     left invisible.

  It runs through the Up-fallback bookkeeping, so the landing logs `action=landed`, and a Down or a
  carousel page turn supersedes it.
- `HomeUpIntoHeroGate.isEngineSkip`. The redirect fires only for the engine's own skip: no
  programmatic hero write inside the window (Menu to top, the ladder's hero rung, a rail exit), the
  hero's gain arriving in the same update as the row's release, and the Up input between 0.3 s
  before and 0.8 s after that gain. When those hold, the gate waives `notPastTop`, because the
  engine's scroll to the CTA runs before the gate. Any other hero gain keeps the old behaviour.
- `redirectIfUpStrandedFocus`. Runs on every Up press or swipe (the window-level catcher), plus one
  check 0.25 s later. It fires only when `RowsContainerFocus.isFocused` is true, meaning the focused
  view is taller than 1.5 windows (set in the catcher's focus observer). The tab bar, the rail and a
  hold menu are therefore never pulled back.
- The redirect works in Rail mode. The plain scroll-to-top keeps its Rail decline, under the rc7
  rule that no Up surfaces the chrome.
- The pop restore's hero regrab waits 0.2 s and stands down if an Up press arrives late. A live
  redirect retires the restore, and the restore's rungs leave a fallback's request alone.
- New probe-gated logs (`-debug.homeScrollProbe YES`): `[HomeReturn] own row= / own hero / up press
  / apply row= … before= after=`, `[HomeReturn] remount rows=… reason=`, and a `[Focus]`
  UIFocusSystem logger (view type, window frame, heading).

## Gates (FA87, `498e9d6d3`)

- Debug + Release builds (FA87 destination, not the generic one): green.
- NuvioTVTests: 1853 executed, 0 failures, 5 skipped (the base had 1838 executed; this branch adds
  15 gate unit tests).
- BatchAHomeReturnUITests: 9/9 pass, including the two new `testBatchC_*_Pinned` legs.
- HomeUpIntoHeroUITests test74: passes.
- StageStripUITests: 14 pass, S09 skipped. S11 (hold menu on a strip poster) fails, as it does on
  the base.

Simulator UI legs:

- `testBatchC_ClassicFolderPopThenUp_Pinned`: failed 3/3 before the fix.
- `testBatchC_ClassicDetailPopThenUpWalk_Pinned`: Detail pop, then Up through every row; failed on
  the CW step before the fix.
- Both take the ladder path. The simulator's engine never consumes this Up, so the hero and
  container redirects are proven on the device only.

## Device pass (Living Room ATV, Test 2, the rig)

Cycle: on the tile → Select → Menu (150 ms) → wait 0.5 / 1.0 / 2.5 s → Up → Up. Screenshot and log
after each Up. Evidence is in `docs/research/up-skip-device-2026-10-17/`: `console-*.log` with the
row geometry noise stripped, and 960-px JPGs. The `L*` shots are from the last loop.

| Build | Cycles | Upcoming then CW | Notes |
|---|---|---|---|
| first fix (`6697deb3c`) | c1–c3 | 1st Up: invisible focus, or Upcoming; 2nd Up: CTA, redirect never landed | led to the `[Focus]` logger |
| + remount on redirect (`console-8`) | 10 | 9 | one dead second Up |
| + early re-identify (`console-9`) | 8 | 7 | one dead second Up |
| + press log (`console-10`) | 10 | 8 | L1: the rig's press never reached the app (no `up press` line); L6: redirect into Upcoming dropped, give-up left the CTA focused with the rows revealed |
| **`498e9d6d3`** (`console-11`) | **10** | **10** | the CTA held focus about 0.5–0.75 s before the redirect landed on CW in 5 of 10 |

## Still open

- **Root cause.** It is unknown why the two sibling rows lose focusability after a pop, and why CW
  drops writes from the CTA. Both fixes are workarounds. A structural option: move CW and Upcoming
  into the `ForEach` (the cells come back fine), or drop `.onMoveCommand` from the rows `ScrollView`
  so it stops being a focusable container. The BUG-112 ladder needs the latter, so it is not a small
  change.
- **Visible CTA flash.** On the second Up the CTA can hold focus for about 0.5 s before CW takes it.
- **Re-identify cost.** A re-identified CW or Upcoming row comes back on its first card, losing its
  horizontal position.
- **Dead Up just after a pop.** One Up pressed about 0.6 s after a pop moved no focus at all
  (`console-10` L1, first Up). One sample, cause unknown.
- **Stray captions.** A first Up that landed on Upcoming showed faint CW captions under the hero
  (`h1-up1.jpg`). Cosmetic; likely pinned-rest overdraw.
- **Coverage gaps.** Not walked: Tabs mode, Show Hero OFF, Detail opened from a CW card (the
  `originMissed` remount), and swipes.
