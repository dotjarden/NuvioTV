# Batch P: Steven's rc10 verdict → the next rc (plan, 2026-10-20)

**Status: DRAFT, awaiting Christian's approval.** Nothing built. The reply DM is drafted (`docs/comms-dm-drafts-2026-10-20-rc10-reply.md`, NOT SENT).

Sources:
- `docs/steven-beta19-rc10-verdict-2026-10-20.md` (verdict, 6 photos).
- Christian's decisions in-session (2026-10-20): the rail stays as it is by default, the flush Nuvio-style rail becomes a Settings option.
- Code anchors from the current tip `1bf7866aa` (rc10): `DesignSystem/NavigationChrome.swift:55-102` (`RailPosition` centre / corner, `RailLabels`, `bezelInset` 16, `collapsedWidth` 84), `DesignSystem/NavigationRail.swift` (the pill), `Screens/DetailView.swift:417` (FEAT-82 square buttons), `Screens/Detail/DetailSynopsisSheet.swift` (BUG-193), `Screens/HomeView.swift:6289-6301` (`PinnedRowGeometry.LongSynopsis.grant`, FEAT-61), Batch N's pop replay in `Screens/Home/StageController.swift` (the pattern for BUG-194), `debug.homeScrollProbe` in `HomeView.swift` / `BrowseComponents.swift` (the hitch counter).

Scope as proposed: everything from the rc10 verdict except the player items (those are P5, on `claude/player-p5`). Performance first, because it is his headline and because every later cosmetic fix adds to the same Home path.

---

## Decisions for Christian (recommendation first)

| # | Question | Recommendation | Alternative |
|---|---|---|---|
| D1 | What the next rc carries | **rc11 = Batch P + P5** once both have their device pass; P5 is on its own branch and merges first (its device pass is pending, the free-team profile expires 10-22 04:23Z). | rc11 = Batch P alone, P5 in rc12. |
| D2 | FEAT-80 (c): the flush rail as an option | **Settings › Appearance › Rail Style: Floating (default, today's pill 16 pt in) / Edge** (the pill sits against the left screen edge, outer corners square, inner corners rounded, no inset; Centre keeps the vertical centring, Corner keeps the top). Both positions × both styles. | A third position instead of a style (Centre / Corner / Edge). Rejected: Edge is a look, not a place; it must work with Corner too. |
| D3 | FEAT-80 (b): Icons Only loses its glass | **Measure first on the rig** (Batch M D2 was never done): screenshot the collapsed 84 pt pill at rest and focused in Icons Only; if the `.glassEffect(.regular)` reads flat over the 0.55 dim, give the collapsed pill the same tint/material the expanded one has. | Drop Icons Only. |
| D4 | FEAT-82: which buttons get equal widths | **The three icon buttons (trailer, watched, add) become one fixed square, side = the Play button's height; Play keeps its text width.** His photo shows the icon squares narrower than Play's height. | Every button the same width (Play shrinks to a square with an icon only). |
| D5 | FEAT-66: collection logo on the right | **Not in this batch.** Product call; it changes the collection page's reading order and the Stage/Classic hero placement. Decide with the FEAT-81 / UX-17 design batch. | Do it now on Classic collections only (his explicit case). |
| D6 | BUG-153 + UX-16: how to find the lag | **Wave 0 on the rig in HIS configuration** (Stage, Medium+, Hide Titles ON, No Zoom OFF, Card Depth ON, accent ring ON, Rail Corner + Labels Shown; confirm from his settings photo when it arrives): `debug.homeScrollProbe` hitch counts and Time Profiler over the tunnel on (a) a 20-row Stage Home walk, (b) the rail open/close, (c) a big-series Detail walk with the ring on and off, on rc9 (build 141) and rc10 (build 142) back to back. Fix what the profile names; no blind reverts. | Revert the rc10 UI batches (N, O) on suspicion. Rejected: nothing proves it is them, and his "20 fps" started before Corner existed (rc9 verdict). |
| D7 | FEAT-61: 4 lines at Medium+ | **Measure the grant on the rig at Medium+ with his font; if the fit falls back to 3, grow the synopsis slot** (Batch M D8 said grow, not drop). | Force 4 lines and let the hero compress. |

---

## Items

### Wave 0 (main session, rig, Test 2 in his config): the performance profile

- **P0-a, the baseline pair.** Install build 141 (rc9) and build 142 (rc10) Release side by side (two bundle ids are not needed: install one, measure, install the other). For each: `console.sh start … -- -debug.homeScrollProbe YES`, the same 20-row Stage walk (`atv.sh seq down ×20` at 0.6 s), the rail open/close ×5 (Corner), then a Detail walk on a big series (Monstre) with `-accent_focus_ring YES` and `NO`. Record `[BUG41] hitches=…` / the probe's frame-time lines and the `[NavRail]` timings.
- **P0-b, the profile.** Time Profiler through the devicectl tunnel on the rc10 Debug build for the Stage walk and the rail (Batch M did this for Detail: 305 → 247 ms). Main-thread work per press: SwiftUI body counts (`HomeRowsList.top` body counter exists), the stage swap (`StageController`), the glass pill's redraw, `WatchedBadgeIndex` reads (rc6), the Corner rail's `[NavRail] focus write` path (rc10).
- **P0-c, the ring half.** If the Detail lag only shows with the ring on (as in Batch M), the fix is in `DetailTileFocusLift`'s per-tile ring path; if it shows without the ring, it is the page, not the ring.
- Output: a findings section in this plan naming the stage(s), then P1 below is scoped from it. Budget: half a day on the rig.

### Wave 1 (three Sonnet agents, disjoint files; Opus critique of the specs first)

| # | Item | Shape / files |
|---|---|---|
| P1 | **UX-16 + BUG-153 fixes** from Wave 0 | Whatever the profile names. Unknown until measured. Owner: agent A if small, else the main session. |
| P2 | **FEAT-80 (c) Rail Style option (D2)** | `NavigationChrome.swift`: `enum RailStyle { floating, edge }`, key `rail_style`, default floating; `NavigationRail.swift`: pill x = 0 and asymmetric corner radii for `.edge`, both positions; the Corner rest glyph keeps its 16 pt in Floating and sits at the edge in Edge; `AppearanceSettingsPane`: the row under Rail Position, shown in Rail mode; strings ×6; UI leg: Edge pill frame x = 0 in both positions; the `[NavRail]` first-write focus unchanged. Agent A. S–M. |
| P3 | **FEAT-80 (b) Icons Only glass (D3)** | After the rig screenshot: the collapsed pill's material/tint in `NavigationRail.swift`. Agent A. S. |
| P4 | **FEAT-82 equal widths (D4)** | `DetailView.swift:417`: the icon buttons get `frame(width: h, height: h)` with `h` read from the Play button's height; Rounded/Round unchanged. UI leg: three equal frames in Square. Agent B. S. |
| P5 | **FEAT-61 Medium+ lines (D7)** | `PinnedRowGeometry.LongSynopsis.grant`: measure, then grow the slot at Medium+; `StripGeometryTests` / the pinned-row tests re-derived. Agent B. S. |
| P6 | **BUG-193 synopsis screen** | `DetailSynopsisSheet.swift`: replace the heavy blur with the page's own backdrop under a dark scrim (the rc8 Detail band), a plain 0.25 s fade in. Agent B. S. |
| P7 | **BUG-194 Detail ← biography in one move** | The BUG-187 restore (Batch M D7) gets Batch N's rule: while a pop restore is pending, a non-target focus change does not move the page, and the remembered card is the only default candidate; compare row positions, not timestamps (Batch N's lesson). Files: `DetailView.swift` push/pop capture, the Detail focus section controller. UI leg: cast → biography → Menu → one landing. Agent C. M. |
| P8 | **BUG-190 Classic collection logo** | Waits for his photo / answer. Not scheduled. |

Strings through `scripts/populate-localizable-xcstrings.py` after the wave; translations with the P5 pass.

### Reviews, gates, device pass

- Opus critique of P2–P7 specs before the agents start; two Opus review rounds to CLEAN (Codex from 10-29).
- Gates as always: jvm / K/N / composeApp (nothing shared changes here, so a quick run), NuvioTVTests, UI legs incl. the new ones, Debug + Release sim, Debug device.
- Device pass (Test 2, **his config**, rig + Christian's eyes for the rail): Rail Style Edge in Centre and Corner, Icons Only glass at rest and focused, the square buttons on a series and a film, 4 synopsis lines at Medium+, the synopsis screen, cast → biography → Back in one move, and the Wave 0 walk repeated on the batch build with the hitch counts next to rc10's.
- Release notes / DM: Rail Style (Floating default), the four small fixes, the performance result in numbers he can feel ("the Home walk drops N hitches per 20 presses"), plus P5's DV MP4 line if rc11 carries P5 (D1).

### Agents and cost

Wave 0 is the main session on the rig (no agents). Wave 1: one Opus critique, three Sonnet agents (A rail, B Detail trio, C BUG-194) in parallel on disjoint files, two Opus review rounds. Never more than three agents at once; builds serialised with `iosApp/build/with-lock.sh`.

## Risks

- **Wave 0 may name nothing.** If the rc9/rc10 hitch counts match in his config, his "worse" is subjective or network-bound (artwork), and the honest reply is a question, not a fix. Say so.
- **Edge rail × Corner × Hidden** is six combinations; the UI leg must cover the rest glyph in each.
- **BUG-194 touches the Detail focus restore** that Batch M just built; its UI leg must also keep the More Like This and collections returns (D7 of Batch M) green.
- **The profile for the box expires 10-22 04:23Z**; Wave 0 after that needs a re-sign.
