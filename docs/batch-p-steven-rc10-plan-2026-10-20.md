# Batch P: Steven's rc10 verdict → the next rc (plan, 2026-10-20)

**Status: APPROVED 2026-10-20 as recommended (D1–D7).** Wave 0 started the same day. The reply DM is drafted (`docs/comms-dm-drafts-2026-10-20-rc10-reply.md`, NOT SENT).

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
| D6 | BUG-153 + UX-16: how to find the lag | **Wave 0 on the rig in HIS configuration** (from his 20:34Z video, 0:41–1:30: Stage, Medium+, Hide Titles ON, No Zoom OFF, **Row Edge Fade OFF**, Card Depth ON with Subtle / Soft / Full and depth-takes-poster-colour ON, accent ring ON with ring-takes-poster-colour ON, theme White, **Deep Black ON**, Rail Corner, **Hidden at rest**, Labels Shown (he switched from Icons Only during the video), Rounded corners, Discover off, Show Catalog Details ON): `debug.homeScrollProbe` hitch counts and Time Profiler over the tunnel on (a) a 20-row Stage Home walk, (b) the rail open/close, (c) a big-series Detail walk with the ring on and off, on rc9 (build 141) and rc10 (build 142) back to back. Fix what the profile names; no blind reverts. | Revert the rc10 UI batches (N, O) on suspicion. Rejected: nothing proves it is them, and his "20 fps" started before Corner existed (rc9 verdict). |
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
| P8 | **BUG-190 Classic collection title block** | Photo in (his 20:34Z reply, `docs/steven-beta19-rc10-reply-2026-10-20.md`): the Netflix folder's Classic rows page, row 2, shows the title block ~45 % down the header panel with no folder logo above it, so it reads as "the logo in the centre". `Screens/FolderRowsPage.swift` §2.5 (`FolderStageLogoLayer`, `stageBlockTop`): pin the block to the panel top when the folder logo is missing or has not risen. Agent B. S. |
| P9 | **BUG-195 Search opens on ~0.9 s of black** (new, from his video at 2:00) | Home → Search: the Home dim, a one-frame white flash, then black until the Search page paints. Measure on the rig (`debug.homeScrollProbe` is not it; time the Search page's first body against the tab switch), then keep the previous page up or fade through the dim until Search has laid out. Agent A or main session. S–M. |
| P10 | **BUG-196 Icons Only pill darkens ~1 s after opening** (new, Settings close-up in his video) | Same material question as P3 / D3: the collapsed pill alternates between two tints across opens. Likely the glass sampling the dim behind it after the dim finishes; settle the material once in P3 and re-check this frame. Agent A. S. |

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

---

## OUTCOME

### Wave 0 findings (2026-10-20, Living Room, Test 2 in Steven's configuration)

Setup: `ready.sh` READY (after the box dropped off the LAN twice; the devicectl tunnel also dropped after each Instruments session and came back within a minute). Release builds of rc9 (141, `2baa390f`) and rc10 (142, `1bf7866a`) built from their tags in the P5 clone with the bundle-ID override. Test 2 set to his look through Settings: Poster Size **Medium+** (was Large), **Hide Titles ON**, **Card Depth ON** (Subtle / Soft), accent ring ON, No Zoom OFF, OLED True Black ON, Rail; `-home_layout stage -rail_position corner -rail_labels shown` by launch argument. Instruments only works when it **launches** the app itself (`xcrun xctrace record --device <udid> --template 'Animation Hitches' --launch -- com.youngchris29.NuvioTV <args>`); `--attach` by name or pid is refused over the tunnel. Traces live in `~/Library/Logs/nuviotv-traces/` (130 MB each, out of the repo); `docs/research/batch-p-wave0-2026-10-20/{walk-home.sh,walk-detail.sh,hitches.py,compare.py,timeprofile.py}` are the protocol and the parsers.

**The walk** (`walk-home.sh`): 20 Down then 20 Up on the Stage Home at 0.6 s, identical on every run; the window 16–52 s of each recording holds exactly those 40 presses. Animation Hitches, app process only:

| Run (rc10 unless noted) | Hitches | Hitch time | Longest | ≥ 100 ms |
|---|---|---|---|---|
| rc9, Stage, his config | 132 | 5.19 s | 150 ms | 19 |
| **rc10, Stage, his config** | **153** | **5.72 s** | **167 ms** | **20** |
| rc10, Stage, Row Edge Fade Off + inline trailers Off | 127 | 4.72 s | 133 ms | 12 |
| **rc10, Classic, his config** | **97** | **1.79 s** | **83 ms** | **0** |

Readings:
1. **The rc9 → rc10 regression is real but small**: +16 % hitches, +10 % hitch time on the same walk. Nothing in Batches L–O doubled anything; his "even worse" is on top of a baseline that was already bad.
2. **The baseline is the problem, and it is the Stage layout.** Stage hitches ~4 times per second during a walk, with 100–170 ms stalls on most presses; Classic does the same walk with a third of the hitch time and no stall over 83 ms. That is the "20 fps" he describes, and it matches his standing preference for Classic.
3. **His look options are a sixth of it, not the cause.** Fade off + trailers off removes 26 hitches and 8 of the 20 long stalls; the floor stays at ~3 hitches per press. (Card Depth is profile-synced, not A/B'd by argument; the CG gradient time below is the likely place it would show.)
4. **Where the time goes** (Time Profiler, rc10 Stage walk, 16–54 s, main thread 31 % busy, 11.6 k samples): AttributeGraph `propagate_dirty` / `UpdateStack::update` / `Subgraph::update` ≈ 2.0 k samples (SwiftUI re-evaluating a large dependency graph per press), Swift refcounting ≈ 0.5 k, `objc_msgSend` 0.65 k, **CoreGraphics `argb32_shade_axial_RGB` 369 + `argb32_image_mark` 153** (gradients and images rasterised on the CPU), **CoreFoundation `_CFStringCheckAndGetCharacterAtIndex` 357 + `characterAtIndex:` 190** (string scanning per press). App symbols nearest the top of the stacks after `atos`: `CachedImageLoader.load` and its completion (`CachedAsyncImage.swift:1375`, `:1417`; image work landing on main), `InlineTrailerCardModel.setPhase` / `beginMorph` / `InlineTrailerCard.expandingCard`, `StripPager.pages` closures, `CatalogRowView.body`, `ArtworkLetterbox.measuredZoom` (image analysis on main), `TitleHoldMenuModifier.body`, `AmbientWashModel.incomingOpacity.setter`, `WatchedBadgeReader.init` (rc6, small), `ArtworkCacheEntry.deinit`.
5. The hitch narratives name both halves: "expensive app update(s)" (main-thread SwiftUI) and "expensive render, 35–36 offscreen passes" (masks, shadows and gradients per card and per row).

**P1 scope (Wave 1, from the numbers):** the Stage Home's per-press cost, in this order: (a) take image decode, `ArtworkLetterbox.measuredZoom` and the `CachedImageLoader` completion off the main thread or off the press path; (b) cut the SwiftUI invalidation fan-out on a row move (what re-evaluates per press: `StripPager.pages`, `CatalogRowView.body`, the trailer card model; `.equatable()` / value snapshots on the row inputs); (c) the offscreen passes: Card Depth's edge + sheen and the fade mask drawn as layers per card (`drawingGroup` or pre-rendered images), and the string scanning on the press path. Target: Stage ≤ Classic's 1.8 s on the same walk, no stall ≥ 100 ms. Measure with the same protocol after each step.

**BUG-153 (Detail ring), NOT REPRODUCED on this box.** `walk-detail.sh`: rail → Search → type → the Series row (the Top result tile prefers films: "Monstre", "Simpsons" and "Severance" all gave the film first) → Detail of the Severance series (2 seasons, Episodes / Season / Trailers rows) → 10 Down, 10 Up at 0.8 s. Animation Hitches, app process, ring ON vs ring OFF, same launch, same presses:
- the 20 Detail presses (≈ 43–67 s of each run) produced **no hitch cluster in either run** (ring on: 0 between 37 s and 85 s; ring off: 2 in 45–64 s); the page scrolls clean here with or without the ring.
- the clusters are elsewhere: **the Search results page while posters load** (ring on 28–36 s: 46 hitches, peak 17 in one second; ring off 30–40 s: 68) and the **full-screen trailer** the page opened on its own at the end of both walks (ring on 86–93 s, ring off 70–95 s, video on the compositor).
- Reading: Batch M's "ring on = +0.6 ms" measurement stands for this page; his lag on Monstre with his add-ons (more trailer tiles, more episode rows, his network) is not on Test 2. BUG-153 waits on his video and Appearance settings (asked in the rc10 reply). **Found instead:** the Search results page hitches as hard as the Stage walk while its grid fills; worth a row of its own if he mentions it, and the same image-on-main fix (P1a) applies.
- Side fact: a Detail walk that reaches the Trailers row and presses Up past the top opens the full-screen trailer with no Select, on both runs. Not in the verdict; check in the device pass whether a human remote does it too.

**Wave 0 cost:** ~2 h on the rig, 9 traces (`~/Library/Logs/nuviotv-traces/`, ~1.2 GB, out of the repo). Test 2 keeps Steven's look settings (Medium+, Hide Titles, Card Depth); rc10 Release (build 142) is the build on the box. The P5 Debug build must be reinstalled for the P5 device pass.

### Steven's 20:34Z reply folded in (2026-10-20, triaged by another session: `docs/steven-beta19-rc10-reply-2026-10-20.md`)

- **The ring A/B was negative on his box** ("no difference … the previous version was smoother. Now the first scroll is too abrupt"). That agrees with Wave 0's Detail runs (no hitch cluster with or without the ring): BUG-153 is the page's first scroll, not the ring, and it stays with UX-16 under P1.
- **His video cannot rank rc9 against rc10** (identical pacing on a 30 fps phone recording), as he himself warned; the rig numbers above are the measurement. His stutter list for P1: rail open/close, the watchlist hold menu, synopsis scrolling, collection → Home; Settings is smoother than Home.
- **Wave 0's configuration matched his** except two rows: Row Edge Fade (he runs OFF; runs 1–2 used Soft, run 3 OFF, which is the closer one: 127 hitches / 4.7 s) and the rail at rest (he runs Hidden; the walk never opened the rail). The readings stand: the Stage floor is ~3 hitches per press whatever the look options.
- **New items:** P9 BUG-195 (Search opens on 0.9 s of black), P10 BUG-196 (Icons Only pill darkens). P8 BUG-190 is unblocked by the photo. FEAT-80: he accepts the proposal (today's pill by default, the flush rail as an option) and says Centre works well as is, Corner less so; the Icons Only grey slab on Home is on camera at 0:20 (P3).
- Reply 2 SENT 21:44:28Z; nothing promised beyond "in the batch". Next DM after Wave 1's device pass, with the hitch numbers.

### Wave 1 (2026-10-20 late): BUILT + reviewed, device pass HALF DONE (rig dropped), not merged

- Clone `~/Claude/Projects/NuvioMobile-batch-p`, branch `claude/batch-p` off `44200c23a` (the P5 merge), MPVKit symlinked, Debug sim build warmed.
- **Critique first** (Opus, read-only): `docs/batch-p-w1-critique-2026-10-20.md`. Drift: the FEAT-61 rule lives in `DesignSystem/PinnedRowGeometry.swift:489-596` (HomeView is only the call site); FEAT-82's buttons are at `DetailView.swift:2093-2482` and there are up to five icon buttons whose SF Symbol + 32 pt padding already differ, so the fix is a fixed square frame; BUG-190's photo is the Stage folder page (`StageView.swift:240`: the title logo bottom-aligned in a 150 pt slot with the folder logo missing above it); the Stage UI leg is `StageStripUITests` S01–S17. **P1's top find:** the target builds with `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor`, and `ArtworkLetterbox` (plus four `TrailerHeroPlayerView` constants) is the one helper called from `Task.detached` that is not `nonisolated`, so the image analysis Wave 0 saw on the main thread really runs there; second, `CachedAsyncImage.swift:1375`'s `@Published` writes publish unchanged values and re-render every card per load. P1's remaining items (strip pager fan-out, the string scanning's caller, the A/B flags for the mask / page opacity / Card Depth) stay with the main session after the rig says what pays. Strings: four, not six.
- **Agents** (Sonnet, parallel, disjoint files): A = P2 Rail Style + P3/P10 glass variants behind a launch flag; B = P4 FEAT-82 square frame, P5 FEAT-61 (logo may shrink to 48 pt, stop and report below that), P6 BUG-193 backdrop, P8 BUG-190; C = the three safe P1 items, P7 BUG-194, the P9 probe. DetailView.swift and HomeView.swift are closed to agents: they hand back exact hunks for the main session to apply.
- **Built** (agents A/B/C in parallel, the main session applied their DetailView hunks): checkpoint `623ffc31e` (gate: Kotlin green, NuvioTVTests 2075/0, UI compile, Debug + Release sim; strings populated: Rail Style, Floating, Edge + the description; a stray "synopsis backdrop" key removed).
- **Review r1** (`docs/batch-p-w1-review-r1-2026-10-20.md`): **P1 1 / P2 2 / P3 11.** The P1 was in the main session's own FEAT-82 hunk (the square frame reached Classic's text buttons and Play). Both P2s were in the BUG-194 wiring: a `.hold` could swallow the last focus change for good, and the Collection / More Like This rows had the hold but not the default-focus half. All fixed (main session for DetailView, a Sonnet pass for the rest); the pop bookkeeping moved into the focus-memory box so it never re-evaluates the body.
- **Review r2** (`docs/batch-p-w1-review-r2-2026-10-20.md`): **P1 0 / P2 0 / P3 6**, all applied. The key question was answered in code: the pop's own Back press is recorded while the biography is still on top, before Detail goes live, so it does not end the restore. The extracted handler is byte-equivalent to the old closure (103 identical lines). Final commit on `claude/batch-p`: the r1 + r2 fix commit on top of `623ffc31e`; NuvioTVTests **2078 / 0**, Release sim green.
- **What the rig has to answer** (device pass, Test 2, his config): whether tvOS re-reads `.defaultFocus` on a pop (the BUG-194 probe's `moves=` / `held=` / `landed=` on cast → biography → Back says which half did the work); the hitch walk repeated on this build against Wave 0's 153 / 5.7 s (the P1 trio: letterbox off main, publish guards, URL memo); the glass variants (`-debug.railGlass clear|tinted|material`) at +0.1 s and +1.5 s in Icons Only on a dark and a bright hero, which picks P3/P10's material; Edge in Centre and Corner incl. the rest glyph 12 pt from the edge (overscan); the square buttons on a series and a film in Square; four synopsis lines at Medium+ (and **Steven's typeface**: the change only matters for Open Sans, the system font already fit four lines); the synopsis sheet's backdrop + scrim (0.72, to tune); the Stage folder page's title block in the Netflix folder, row 2 (the missing folder logo in his photo is still unexplained); `[SearchOpen]` timings for BUG-195 (P9 is a probe only).
- **Not in this wave:** the rest of P1 (strip pager fan-out, the string-scanning caller, the mask / page-opacity / Card Depth A/B flags) waits for the rig numbers on this build; BUG-195's fix; the letterbox "fails to compile if MainActor" claim is unverified in Swift 5 mode (the rig profile is the real check).
- **Device pass, part 1 (2026-10-20 ~21:20–21:35Z, Test 2, his look, batch Debug build; record `docs/research/batch-p-device-pass-2026-10-20/README.md`):**
  - **BUG-194 answered:** the rungs do the work, not `.defaultFocus`. Cast pop: forced rung at +32 ms, row landed at +585 ms, one drift the +802 ms rung corrects, ends on the card (`moves=3 held=0`), identical on two runs; studios pop: no rung, `moves=1`. The probe now also logs `[DetailPop] live|rung applied|end` (the on-screen label is unreadable on hardware).
  - **Two defects found and fixed in-pass, rebuilt, NOT re-walked:** (1) **FEAT-35 regression** from the BUG-194 wiring: the two sentinel `.defaultFocus(..., priority: .userInitiated)` are not inert; on a long-synopsis Detail (Dune) focus opened on the synopsis teaser, the pre-batch build (A/B on the box) opens on Play. Removed, root and `DetailPosterLinkRow`. (2) **FEAT-82**: the square frame on the Button rendered the three icons as one abutting bar, 70 pt tall against Play's 80. The padded label is now the square (side = Play's padded label height).
  - **PASS:** BUG-193 sheet (backdrop + 0.72 scrim); FEAT-61 four lines at Medium+ in the system font; FEAT-80 Edge in Centre and Corner.
  - **Glass (P3/P10):** over the Stage's black left margin `regular` = `clear` = black-`tinted` = near-black, `material` = no platter; that margin, not the material, is BUG-196 (the Labels pill only looks lighter because it reaches the artwork). `tinted` is now white 0.12, to shoot.
  - **Rig dropped** (Companion "Host is down", `ready.sh` refused: re-pair) before the Release hitch walk, `[SearchOpen]`, the bright-hero glass, Open Sans and the folder title. Those, plus a re-walk of the two fixes, are **part 2**. Release build of the fixed tree is ready in the clone.

