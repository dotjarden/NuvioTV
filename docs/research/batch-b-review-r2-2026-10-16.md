# Batch B review, round 2 (read-only, 2026-10-16)

Range: `8e8090806..07b482c1e` on `claude/batch-b` (clone `~/Claude/Projects/NuvioMobile-batch-b`), focus on the r1 fix
commit `07b482c1e`. Reviewer: Opus read-only round (Codex on its limit until 10-29). Nothing in the clone was edited.
Paths are relative to `NuvioMobile-batch-b/iosApp/`.

**Counts: P1 0 · P2 1 · P3 7.** All three r1 P1/P2 items are fixed correctly; the one new P2 is in B5's input clock.

## r1 fixes: verdicts

- **P1-1 (cover Menu recogniser after an in-place swap): FIXED.** `MPVPlayerView.swift:741-749` now re-enables
  unless an ancestor `isBeingDismissed` (`coverIsBeingDismissed`, `:3604-3611`); `closeFailover()` stays on
  `isLeavingPlayer`. Every case I traced comes out right: Up Next / failover / "retry on native" `.id` swap
  (`StreamPickerView.swift:474-487`) re-enables, so the next probe screen and the native engine get their Menu back;
  the post-play card re-enables as before and `viewDidAppear` disables it again on Replay; a Menu exit dismisses
  through `@Environment(\.dismiss)` (`:4144`, `:4264`), which is a UIKit dismissal of the presented hosting controller,
  so the ancestor walk sees `isBeingDismissed`; the representable's controller is a child of that hosting controller.
  Ordering on a swap: the old controller's `viewWillDisappear` (synchronous on removal) runs before the new
  controller's `viewDidAppear`, so a direct mpv→mpv swap ends disabled, as it should. Two small gaps, P3-1 below.
- **P1-2 (folder loading anchor): FIXED, one assumption unproven (P3-2).** `CollectionsUI.swift:1783-1842`: the band
  always mounts while `isActive`, with a `folder.goBack` button when there is nothing to edit.
  `FolderRowsPage.requestInitialFocus` (`FolderRowsPage.swift:398`) is gated on `box.pendingInitialFocus`, not on where
  focus is, so it still pulls focus from Go Back to row 0's first card once a row is focusable. The band can't hide
  under its own focus (`refreshFocusDerived` only closes `rowsAtTop` while a strip row holds focus, `:465`). Menu on
  Go Back pops normally. The `.empty`/`.failed` panels now carry two Go Back buttons (theirs and the band's); the
  identifiers differ, so no leg ambiguity.
- **P2-1 (stale per-folder Grid): FIXED.** `FolderPageLayout.resolve(homeLayout:defaultGrid:)`
  (`FolderRowsPlan.swift:27-29`); `FolderLayoutStore` is gone and nothing else references it or the
  `folder_layout_grid` key (only comments and the harmless `-folder_layout_grid ""` launch arg remain). The project
  uses file-system synchronized groups, so the deleted test file needs no pbxproj edit. `FolderLayoutDefaultTests` pins
  the new rule.
- **P3 items:** comment rewritten (P3-1 r1, fine); layer hop (P3-2 r1, see P3-5 below); `MenuExitShieldRule` wired
  (P3-3 r1, see P3-4 below); leg comment (P3-4 r1, fine).

## P2

### P2-1 · `ViewerInputRecognizer` fails itself at the END of a press while a touch is still down, so a resting thumb's later clicks and swipes are never stamped → the pop restore reads the viewer's move as the engine's and re-grabs against it

`Screens/Home/ViewerInputClock.swift:87-95` (`pressesEnded`/`pressesCancelled` → `failIfIdle()`), `:139`. One
recognizer tracks both indirect touches and presses. When a press ends while a clickpad touch is still in progress,
the recognizer goes to `.failed`; a failed recognizer receives nothing more until UIKit resets it at the end of the
whole sequence, i.e. when the thumb lifts. Until then, new presses never reach `pressesBegan` and the swipe check in
`touchesMoved` never runs.

That is the exact hand the file header describes ("a thumb resting on the clickpad (Steven's hand on the Back
press)"): thumb on the clickpad, Back pressed (recorded at `pressesBegan`, before the pop, so it does not count),
Back released → recognizer fails while the touch continues → the viewer clicks Down/Right or swipes after the pop
without lifting → nothing recorded → `UncoverRestorePolicy.decide` sees a row change with no viewer input since the
pop → `.regrab` up to `maxRegrabs(clockLive: true)` = 3 inside 1.5 s of the landing. The viewer's first move after a
pop gets pulled back, which is the BUG-156 "jump" in a new form, on the box the batch is for. `HomeUpSwipeCatcher` is
not a precedent here: it uses a separate press tap recognizer and a touch-only baseline recognizer.

Smallest fix: fail only when nothing else is in flight: in `pressesEnded`/`pressesCancelled` call `failIfIdle()` only
when `touchStart == nil`; in `touchesEnded`/`touchesCancelled` only when no press is down (track a `pressesDown`
count). Or split into a press-only and a touch-only recognizer. Device check either way: thumb resting on the
clickpad, Back, then one click Down within 1 s → expect `restore retired … why=viewer input=down`.

## P3

1. **P1-1 is unverified on both of its paths, and no leg was added.** Nothing shows that an in-place `.id` swap
   delivers `viewWillDisappear` to the old controller at all (if SwiftUI removes the representable without
   appearance callbacks, the recogniser stays off exactly as before), nor that the exit path reads
   `isBeingDismissed` rather than only `isMovingFromParent` (the device logs only print `isLeavingPlayer=true`, which
   either flag satisfies; if it is the latter, the re-enable on exit returns, i.e. the pre-BUG-165 behaviour). Smallest
   fix: add `cover=\(coverIsBeingDismissed)` to the `[Failover] viewWillDisappear` print at `MPVPlayerView.swift:740`
   and read it on one exit and one Up Next swap in the device pass; the UI leg r1 asked for (mpv episode → swap → Menu
   during `.deciding` → app foreground, cover dismissed) is still owed.
2. **The anchor relies on an opacity-0 SwiftUI button being focusable, and nothing tests it any more.** The band is
   `.opacity(menuFocused ? 1 : 0)` (`CollectionsUI.swift:1801`) and becomes visible only once focused. The old test105
   asserted "Up from the strip's first row must reach folder.editMenu"; that assertion went with the rewrite, and no
   leg looks up `folder.goBack` or `folder.editMenu` now. Add one leg: open the fixture folder (Cinemeta only, so the
   band is Go Back), press Up from row 0, assert focus on `folder.goBack`; ideally also a slow-source variant with
   Menu at once (r1's leg).
3. **Every folder open may now flash the Go Back pill.** With the strip not yet focusable at push time the focus
   engine's only candidate is the band, which turns opaque while focused until `requestInitialFocus` moves focus to
   row 0 (and stays visible after a Settings layout switch, where `requestsInitialFocus` is false). Before r1 this
   happened only for folders with a TMDB source. Look for it on the device pass (FEAT-71's "immersive" ask); if it
   shows, keep the band at opacity 0 while `!stripHasFocusedOnce`, or delay the fade-in by ~0.3 s.
4. **`MenuExitShieldRule` is checked after the press is already claimed.** `MenuExitShield.swift:92-98`: the guard
   runs in the action handler at `.ended`; by then the recogniser has recognised and the chain got
   `pressesCancelled`, so a press "past the ceiling" is still swallowed, just unlogged. The comment says "is not
   ours". Edge only (the timer and the handler both run on main; the window is a few ms). To make the rule real, put it
   in `gestureRecognizerShouldBegin(_:)` via a delegate; or reword the comment.
5. **The layer hop is not airtight.** `MPVPlayerView.swift:3678-3683`: the outer `eventQueue` block still captures
   `layer`, so the last release depends on the outer block being freed on `eventQueue` before main runs the inner
   block. In practice the outer one goes first; to make it certain, pass the layer as
   `Unmanaged.passRetained(layer)` (outer captures only the unmanaged value) and `release()` it in the main block.
6. **Stale doc comment on the band.** `CollectionsUI.swift:1760-1763` still says the band "mounts nothing focusable at
   all" with no editable source and "drops the band's role as the page's BUG-47 anchor"; the body comment two screens
   down says the opposite. Delete the paragraph.
7. **Folder legs 104/106/107/108 were not re-run after the band change** (the commit lists test105, S13, S16). They
   only press Up from row ≥ 1 or Menu from row 0, so they should hold, but run them in the gate since the fixture
   folder (no TMDB source) now has a focusable band it never had.

## Fresh pass (device-owed areas), checked and clean apart from the above

- **`UncoverRestorePolicy` + `StageController` wiring:** `viewerMoved` uses `>= requestedAt`, and Menu is stamped at
  `pressesBegan`, before the pop, so the popping press never retires its own restore; the pending (no pager) path and
  the live path both retire on input; re-grabs are deferred `regrabDefer` and re-checked against the clock and the
  generation; `cancelsPager` only inside the window; observer removed in `deinit`. `FolderPushOrigin` with the clock
  requires a `select` within 2 s of the loss, which covers the hold menu's "Go to Details" (the loss happens when the
  menu opens, ~0.5–1 s into the hold). r1 P3-7 (40 pt threshold) still stands.
- **B4 `InlineTrailerCard`:** `fadesBaseCard` is true for shape rows only; the tile, base card, art decode size and
  `artworkWidth/Height` all read `cardWidth/cardHeight`, so the tile covers the faded card exactly; the overlay title
  takes the faded card's title slot (the tile height equals the card height on a shape row). The global toggle path is
  unchanged (r1 P3-9 stands).
- **B1 reactive reads:** every consumer reads `show_catalog_details_in_headings` through `@AppStorage` (Home, Stage
  Home, folder page, Discover, Settings), including inside the `onFolderFocusChange` closure, so a flip shows on the
  next focus report. An already committed stage keeps its old line until the next focus change, which is fine.
