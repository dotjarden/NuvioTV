# Folder-return Up-skip: root-cause pass (2026-10-17)

Follow-up to `docs/folder-return-up-skip-2026-10-17.md`, whose fix is three workarounds: Continue
Watching and Upcoming re-identified after every pop (`remountTopRowsAfterPop`), a redirect for an
Up the engine skipped into the hero, and stranded-container detection. This pass looked for the
cause and tried to replace the re-identify with a structural change.

**Outcome:** no structural fix ships. The one that cured the simulator (Continue Watching and
Upcoming built outside the rows `LazyVStack`) broke Down from Continue Watching on the Apple TV
after 3–6 pops, so it was reverted and the re-identify stays, now justified by that device result.
Kept from the pass: the stranded detector also recognises SwiftUI's lazy filler item, a probe line
naming the focused item, and corrected docs (the stranded "container" is a lazy filler, not
`.onMoveCommand`).

**Branch:** NuvioMobile `claude/folder-return-up-skip` in the clone
`~/Claude/Projects/NuvioMobile-up-skip`, on top of `498e9d6d3`:

| Commit | What |
|---|---|
| `ef914d575` | Eager top rows, re-identify removed (the experiment) |
| `1a34d7b06` | Opus review r1 fixes on it (0 P1 / 2 P2 / 4 P3) |
| `3a5c9d974` + `072654dfb` (docs) | Reverts the eager structure and restores the re-identify; keeps the filler match, the probe line and the docs. Net against `498e9d6d3`: 3 files, +36 / −12 |

Not pushed, not merged.

## The brief's two options, tested on the simulator (FA87)

Every run had the re-identify switched off by a DEBUG knob passed from the test runner. The legs were
`testBatchC_ClassicFolderPopThenUp_Pinned` and `testBatchC_ClassicDetailPopThenUpWalk_Pinned`. The
knobs and probes are in `docs/research/up-skip-rootcause-device-2026-10-17/sim-bisect-knobs.patch`;
none of them ship.

| Change (re-identify off) | Result |
|---|---|
| Base `498e9d6d3` | both legs fail on the Continue Watching step |
| **Option 1:** Continue Watching and Upcoming as cases of the rows `ForEach` | fail |
| Continue Watching behind an `Equatable` cell, like the catalog rows | fail |
| No hold menu / no strip restore and reorder scroll / no settle tracking / no focus report (one at a time) | fail |
| `.focused` outside the `.contextMenu` (the catalog order) | fail |
| Short-row floor off (`-debug.pinnedShortRowFloor NO`) | fail |
| Tab-bar content scroll link off (`-debug.bug66ContentScrollView NO`) | fail |
| A 0 pt, then a 1 pt, non-focusable first child above Continue Watching | fail |
| **Option 2:** no `.onMoveCommand` on the rows `ScrollView`, the ladder fed by the window press catcher | fail (and the stranding still happens, see below) |
| Detail opened six rows down: every culled catalog row above takes its focus write | Continue Watching alone fails |
| Continue Watching rendered second (the collection row first, culled during the cover) | **pass**, shallow and deep |
| Continue Watching and Upcoming built eagerly, above the `LazyVStack` | **pass**: Up from the collection row moves into Continue Watching on the engine's own move |

What the probes showed:

- After the pop, UIKit lists Continue Watching's cards as focusable (`UIFocusDebugger.checkFocusability`:
  "This item should be focusable", each under a `FocusStateBindingResponder` container), yet a
  `@FocusState` write produces no focus update and the engine skips the row on Down from the CTA.
  SwiftUI refuses the update somewhere the focus debugger cannot see.
  `simulateFocusUpdateRequest` and `focusGroups(for:)` both throw outside the debugger on tvOS 26.5,
  so the API goes no further.
- On the simulator the failure follows Continue Watching as the first lazy row under the pinned hero.
  It does not follow culling (culled rows come back fine) or the first slot alone (the collection row
  in that slot passed).

## The stranded "container" is a lazy filler item

With `.onMoveCommand` removed, an Up past a culled row still landed on
`PlatformGroupContainer {{0, -450}, {1840, 3151}}`. The new probe line names the focused item:
`[Focus] item=UIKitFocusableFillerItem`. That is the `LazyVStack`'s placeholder for the culled row
above, and the row is never realized around it. `nextFocusedView` was only the item's nearest hosting
view. So option 2 could not have removed `redirectIfUpStrandedFocus`. `.onMoveCommand` stays.

`RowsContainerFocus` now matches a focused item whose class name contains `FocusableFillerItem`, with
the old size test (focused view taller than 1.5 windows) as the fallback. Review r1 P2-2 found the
gap: the size test fails once the container is short, and a filler can also be shaped like a single
card (`{{140, 321.5}, {360, 575.5}}` on the box).

## Device pass (Living Room ATV, Test 2, Classic, Nuvio-style hero, Rail; the rig)

The cycle: on the Test Collection tile → Select → 4 s → Menu (150 ms) → wait 0.5 / 1.0 / 2.5 s → Up →
Up. The rig then puts focus back on the tile by reading the owning row from the log (Down from
Continue Watching, Upcoming or the hero; Up from anything else), and reports STUCK if it cannot.
Logs: `docs/research/up-skip-rootcause-device-2026-10-17/console-*.log` (probe on, add-on tokens not
present in these lines). Profile rows: Continue Watching (6 cards), Upcoming (1), Test Collection
(1 tile), then the catalogs.

| Build | Cycles | Up → Upcoming → Continue Watching | Down from Continue Watching |
|---|---|---|---|
| eager top rows, no re-identify (`1a34d7b06`, `console-3`) | 10 | 10/10; no CTA on the second Up in any cycle | **stuck from cycle 10** (filler, bounces back to Continue Watching) |
| same, relaunched (`console-4`) | 12 | first 3 valid | **stuck from cycle 3** |
| eager top rows + eager card shelves (`console-5`) | 10 | first 5 valid | **stuck from cycle 6** |
| eager top rows + re-identify restored (`console-6`) | 12 | first 5 valid | **stuck from cycle 6** |
| base `498e9d6d3` (`console-8-base`) | 10 | 7/7 at 1.0 / 2.5 s; 0.5 s: 1/3 (one give-up with the CTA held, one dead first Up) | never stuck |
| **final** (`console-9-final`) | 10 | 7/7 at 1.0 / 2.5 s; 0.5 s: 0/3 (two dead first Ups, one give-up) | never stuck |

When stuck, Down from Continue Watching put focus on a filler item and the engine moved it straight
back to Continue Watching, every press, from any card, with Upcoming on screen. Upcoming and every row
below it were unreachable until a relaunch. The base and the final build never did this over 20
cycles, each of which walks Continue Watching → Upcoming → tile.

The 0.5 s failures are the same on the base and the final build, and are timing, not the rows. The
rig's Up arrives within ~20 ms of the pop restore landing on the tile:

- **Dead first Up (H2, H8):** the press reaches the app (`up press own=test-collection-1004`) while the
  restore's last rung is still landing, and focus does not move. This explains the record's
  "dead Up just after a pop" item.
- **Give-up (H5, B2):** the engine's late pop restoration puts focus on the CTA 11 ms after the tile
  took it, the Up arrives 20 ms later, the redirect aims at Upcoming, and both of its asks are dropped
  because the 0.6 s re-identify of Upcoming lands between them. The CTA keeps focus.

A viewer at 1.0 s or later did not hit either case in 14 cycles.

## Gates on `3a5c9d974` (FA87)

`BatchAHomeReturnUITests` 9/9, `HomeUpIntoHeroUITests` test74, NuvioTVTests 1853 executed / 0
failures / 5 skipped, Release build green, Debug device build green and installed (the box is left on
this build, in Test 2). The eager commit's wider sweep: `StageStripUITests` S11 and both
`RowLeadingEdgeTests` legs fail, and fail the same way on `498e9d6d3`.

## Review r1 (Opus, read-only; Codex is out of quota until 10-29)

On the eager commit: 0 P1 / 2 P2 / 4 P3. P2-2 (the size-only stranded test) is fixed and kept in the
final state. P2-1 (first catalog row in the failing slot) was answered by the deep "rendered second"
run. The rest (an extra 48 pt under the classic placeholder, stale lazy-stack comments, a doubled body
counter, the eager rows never culled) applied to the eager structure and left with it. P3-3 still
stands: `HomeRowsRefresh`'s `coverDepth` / `resumeCovered` / `focusRequest` were restored as a guard
against this same skip and re-render every cell on each push, pop and ladder rung. An A/B without
them is a follow-up.

## Still open

- The SwiftUI mechanism behind both failures. On the simulator: the first lazy row under the pinned
  hero refuses focus after a pop. On hardware: with that row built eagerly, the next row (Upcoming)
  stops taking focus from Down after a few pops.
- The 0.5 s timing cases above: the re-identify at 0.6 s collides with a redirect started just before
  it. Candidate: have the redirect re-identify only when it targets a row the pop's re-identify has
  not yet renewed, or move the pop re-identify into the restore's landing. Not built.
- Second-Up CTA flash: still present. The CTA took the second Up in 5 of the 7 good final cycles
  (6 of 7 on the base) and held it for 0.52–0.57 s before the redirect landed on Continue Watching
  (`own hero from=upcoming`). The eager build had none in 10 cycles but cannot ship.
- Coverage: Tabs mode, Show Hero OFF, swipes, and a profile without Continue Watching were not walked.
