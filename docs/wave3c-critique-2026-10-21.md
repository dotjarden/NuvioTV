# Wave 3c critique (Phase 1c: W3-11, W3-13…W3-19), 2026-10-21

Read-only Opus critique of `docs/open-items-plan-2026-10-21.md` §4 against clone `NuvioMobile-wave3c` @ `4e12442de` (Wave 3 tip + the nine Home up-skip commits + W3-19). Paths are relative to `iosApp/NuvioTV/` unless noted. Three read-only sub-reads (Classic Home trio, first Down, picker + Watched) fed this; every claim kept here was spot-checked at the cited lines. Decisions taken as given: D1 (Corner flush top + left, expands downward; Centre and Edge untouched), D3 (Square stays), D5 (magnifier only).

## Verdicts

| # | Verdict | In one line |
|---|---|---|
| W3-11 | **Needs change** | D1 applies to the OPEN column; the rest stays Batch O's bare glyph. "Sideways" is `glassWidth` following `frameOpen` (`NavigationRail.swift:713`). Two tests assert "never flush" and must invert. S–M. |
| W3-12 | **Holds (no code)**, config wrong | His rc11 video shows Rounded buttons and the system font; "Open Sans + Icons Only + Square" comes from the triage, not his settings. Capture list below. |
| W3-13 | **Needs change** | Diagnosis right (CPU-rasterised gradients). Drop `StripPager.swift`. Two structural costs come first (rail inserted/removed on every focus move; tinted rail re-rasterised when the poster colour lands), then a 3-variant knob A/B. M. |
| W3-14 | **Needs change, all three** | 209 is the designed held-slide release (rest-law class), not FEAT-61. 210's hypothesis is refuted in code and the evidence frame is a camera blend: repro first. 211 is one token in `HomeView.swift:6844` (owner). |
| W3-15 | **Needs change** | Two causes, not one. Detail confirmed: press 1 is our `easeOut(0.3)` over ~766 pt, presses 2–3 are the engine's one-row reveal; the fix needs `DetailView.swift` (owner, after wave3b). Home has no curve difference: measure before code. Not Sonnet. |
| W3-16 | **Needs change** | Not "cache the row layout": BUG-16's focus expansion re-lays two rows per move, and every row's body reads the parent's `@FocusState`. S–M. |
| W3-17 | **Needs change** | No longer curve exists in code; Watched and Library are identical except `.tint(accent)` on the active state over `.glass`. A/B with the existing `-debug.detailScrollAB 4` first; fix touches `DetailView.swift`. XS. |
| W3-18 | **Holds** | Use `.hidden()` on the prompt `Text`, never delete it (the magnifier would rise and jump at the hand-off). XS. |
| W3-19 | **Built** (`4e12442de`), holds | Two P3 notes: a P7 scan cut by the deadline is not reported as a cap hit; the host goes into console logs (staging rule). |

## W3-11 Corner rail (D1)

**Where it lives today.**
- Model: `RailPosition` `DesignSystem/NavigationChrome.swift:59-62`; `RailStyle` `:74-83`; `pillLeading` `:87-89` (Edge = 0); `cornerSafeTop` `:111` (60); `cornerPillTop` `:116` (38).
- Rail: Corner metrics `DesignSystem/NavigationRail.swift:244-269` (`cornerTop` `:251` = 38, `cornerRestHeight` `:254` = 104, `cornerGrowDelay` `:261`, `cornerUnroll` `:269`). State: `isCorner` `:353`, `cornerOpen` `:359`, `cornerResting` `:363`, `cornerGrown` `:374`, `cornerArmedAtRest` `:383`, `cornerFrameOpen` `:386-388`, `glassOpacity` `:394-396`, `cornerOpenHeight` `:431-433`.
- Placement: `body` `:518-525`, `cornerPanel.padding(.leading, pillLeading(style)).padding(.top, cornerTop)`, inside a `.topLeading` ZStack that ignores the safe area (`:536`), so coordinates are screen coordinates.
- `cornerPanel` `:709-752`: `glassWidth` `:713` = `frameOpen && showsLabels ? 300 : 84`; `glassHeight` `:714`; mask `:728-732` and glass `:733-737`, both `.animation(grow, value: frameOpen)`. Phase 2 = `updateCornerGrowth` `:814-823`. Label fade `:880`.

**How Edge went flush in rc11.** `pillLeading(.edge)` = 0 at `:523`/`:528` plus `pillShape` `.edge` (`:616-626`, leading radii 0). In Corner + Edge today the glass touches the left edge but sits 38 pt down, with the Home cell at x 12.

**What he sees (Corner, Hidden, Labels Shown).** The panel fades in (`:525`) as an 84 × 104 pill at (16 or 0, 38). 0.08 s later one spring grows the height to ~492 **and** the width 84 → 300 (`:713`). That width growth is the "sideways". With Icons Only there is no sideways part.

**Fix, Corner branch only** (`pill`, `pillShape` and every Centre path untouched):
1. **Items stay put.** The Home cell stays at (28, 60): Batch O's resting glyph and Rail12's (58, 90) centre. Corner ignores Rail Style: `:523` uses `RailMetrics.bezelInset` when `isCorner`. Edge's x 0 would move the Home icon, and the rest glyph with it, to x 12.
2. **Glass and mask flush.** Add a `cornerShape = UnevenRoundedRectangle(bottomTrailingRadius: 42)`: top-leading, bottom-leading and top-trailing square (Steven's 10-19 mock). Draw it from the screen corner, frame (w + 16 + b, h + 38 + b) at offset (−16 − b, −38 − b), with b ≈ 8 pt of bleed so the Liquid Glass rim on the two screen-edge sides lands off-canvas. Give the mask (`:728-732`) the same shape, frame and offset, so no focus capsule shows outside the glass. Put the bleed on the background and mask, never as padding on the column: padding would grow the `.focusSection()` (`railPillChrome` `:657`) into the corner.
3. **Downward only.** In Corner, `:713` becomes `showsLabels ? 300 : 84`, independent of `frameOpen`.
   - Phase 1 (arm): the glass fades in as a flush top bar, 316 × 142 with labels or 100 × 142 Icons Only, with Home's label fading in (`:880`).
   - Phase 2: only the height springs, to the column + 38.
   - Close: the height shrinks to 142, then the glass fades (timings `:796-807` unchanged).
4. **Rest unchanged: the bare Home glyph** (`cornerResting`, `itemGlyph` `:896`, `RailRestingGlyphShadow` `:1514`). Do not revive Batch N's 152 × 132 resting tab (`6b3e06ce5`, retired in `b0f9bb7aa`): Christian rejected the grey box at rest on 10-20 (memory `chrome-glass-hugs-content`), and D1 speaks to the open column. Steven runs Hidden, so he never sees the rest state. Owner to confirm; the default is the bare glyph.
5. **Hidden at rest:** same path as today. The arm mounts the panel with `cornerArmedAtRest` false, so the frame starts at rest size and grows on the next turn (`:814-823`). The flush bar fades in, then unrolls down.
6. **Settings.** Rail Style does nothing in Corner, so hide its row while Position = Corner (`Screens/Settings/AppearanceSettingsPane.swift:384-393`; `railPosition` is already `@AppStorage` at `:49`). No copy change: the Rail Position copy (`SettingsDescriptions.swift:271`, a wave3b file) still reads true. No new strings, so no translation.
7. **NavigationChrome.** Rewrite the `cornerPillTop` doc. Add a pure `cornerGlassFrame(labels:open:columnHeight:) -> CGRect` (origin −bleed; width independent of `open`) for the unit test.

**Safe area.** (0, 0) is the screen corner. The Home cell's top sits on the 60 pt top line. x 28 is inside the side overscan margin, exactly where Centre's Floating pill has sat since FEAT-45. An overscanning TV crops the glass (harmless) and can shave the icon by the same amount as Centre's.

**Can break.**
- Focus: nothing, provided the items never move (no `offset` or `scaleEffect` on items, only background and mask frames: the Orivio trap).
- Batch O's r1 fixes (the selected row's `.identity` insertion, the frame laid out on the arm turn) carry over untouched.
- Tests that encode the old geometry:
  - `NuvioTVTests/NavigationChromeTests.swift:301-307`: `testCornerPillGeometry` asserts "never flush".
  - `NuvioTVUITests/NavigationRailUITests.swift:732-734` (origin (16, 38), height 492) and `:798-804` ("anchored at the top, never flush", "every corner inside the screen with a gap").
- Liquid Glass flicker while a taller frame animates (Batch N's open risk): check the 30 fps unroll frames.
- Header overlap: only while open, over the dimmed page.
- Release-only: none. Up-skip: none.

**Gate.** Sim shots: Labels Shown and Icons Only × Always Visible and Hidden, rest + mid-unroll + open. Rig shots over a dark hero and a bright one. **Size** S–M, one Opus agent.

## W3-12 Detail trio re-test (rig, no code): what it must capture

- **Config: install from his rc11 video, not from the triage.**
  - The video at 44–48 s shows the "Lire" capsule with round icon buttons (Rounded corners) and SF text (system font).
  - The rc10 Appearance table agrees: Système, Arrondi, rail Labels switched to Shown at 1:07, accent White, ring on with poster colour, depth on (Subtil / Doux / Complet, poster colour), OLED, Medium+, Hide Titles, catalog details on, Discover off. Home is now Classic; Detail is Cinematic.
  - "Open Sans + Icons Only + Square" (triage reading #2) is unsupported; only his rc10 photo 4 was Square.
  - Run the Detail items in both Rounded and Square. Ask him for an Appearance screenshot (one line in the pending reply).
- **FEAT-82.** Action-row screenshots, film and series, in both corner styles. Measure every **glyph** bounding box as well as every button frame. The rig measured frames. "The icons are still not all the same size" may be optical glyph size: `checkmark.circle` draws its own ring inside the button, `plus` and the trailer glyph don't (`DetailView.swift:2213`, `:2232`).
- **BUG-194.** Cast → biography → Back, ×5, with the `[DetailPop]` lines and `moves=`, plus a 30 fps recording.
- **BUG-206.**
  - `docs/research/batch-p-wave0-2026-10-20/walk-detail.sh` on Release, Cinematic vs Classic Detail, Animation Hitches + `compare.py`.
  - The same walk on a build of the rc7 tag (his "smooth" verdict). Without it, "regression" stays unproven.
  - `-debug.detailScrollProbe YES` (Release-readable, `DetailView.swift:291`): W3-15's press-1 data comes from the same run.
- **Same session, no code (session R0 below).**
  - W3-13 baselines.
  - W3-14 BUG-209 slide lines and the BUG-210 repro.
  - W3-15 press-1 windows.
  - W3-16 picker baseline (needs the stub add-on).
  - W3-17 A/B.
  - Nothing 4K, so the box's Wi-Fi drop is not in play.

## W3-13 Card Depth

**What it draws.**
- Per card, `CardDepthModifier` (`DesignSystem/CardDepthStyle.swift:426-445`) overlays `CardDepthOverlay` (`:451-490`) with two layers:
  - a sheen: a `LinearGradient` clipped to the shape (`:466-477`);
  - the rail, `edgeHighlight` (`:525-548`): `shape.strokeBorder(LinearGradient, 3 stops)` (`edgeStroke` `:550-563`). At Top/Half coverage it also gets a gradient `.mask` (`:543-546`, `coverageMask` `:581-593`).
- His config (Subtle 28, Soft sheen, Full, poster colour) = sheen + a 1 pt tinted gradient stroke, no mask.

**Why it costs.**
- Wave 0's Time Profiler found `argb32_shade_axial_RGB` (369 samples): CoreGraphics filling gradients on the CPU. No app code draws gradients directly; a gradient-filled stroke cannot be a solid shape layer.
- In Wave 2, Card Depth off removed 18 % of hitches and 10 of 11 stalls ≥ 100 ms.
- The rasterisation happens:
  - (a) per card **mount**: every strip page or row brings 8–12 cards, which is where the long stalls are;
  - (b) twice **per focus move**: `if edge > 0 && !railSuppressed` (`:485`) is a structural branch on `\.isFocused` (`:440`, `:445`), so the rail is torn down on the card gaining focus and rebuilt on the one losing it;
  - (c) per **tint arrival**: `depthRailTint` is written after `ArtworkColorStore.color` (`DesignSystem/PosterCard.swift:1071-1077`), which redraws a tinted gradient. He has poster colour on.
- No per-frame animation exists inside the overlay. The ring-mode lift transforms the layer.

**Plan drift.**
- `StripPager.swift` is not involved: its only depth link was the W2 knob, now `Screens/Home/HomePerfKnobs.swift`. Drop it; W3-15's Stage half owns that file.
- "Default stays on": the setting's default is **Off** (`CardDepthStyle.swift:38`, shared). Read it as "nobody's setting changes".
- The off baseline is one run (120 / 3.89 s / 1); re-run it twice in R0.

**Fix, measure-first, one agent.**
1. **Value, not structure:** always build the rail and apply `.opacity(railSuppressed ? 0 : 1)` with animations disabled. This kills (b). BUG-110's "no rail on a focused card" holds.
2. **White rail × tint:** stroke white with the stop alphas, then `.colorMultiply(railTint ?? .white)` on the **rail only, never the sheen**. This equals `railColor(tint).opacity(stop)` at every stop. A tint arrival becomes a colour change, not a redraw, which kills (c).
3. **The raster, three variants** behind a Release-readable, launch-latched `-debug.cardDepthRender` in `HomePerfKnobs.swift` (the `noCardDepth` pattern):
   - 0 = today;
   - 1 = `.drawingGroup()` on the overlay's ZStack (Metal, one offscreen texture per card, about 1 MB at 2×, about 40 MB for 40 mounted cards; watch jetsam);
   - 2 = a nonisolated `CardDepthRasterCache` (`NSCache`) of white rail and sheen `UIImage`s, rendered once per key with `UIGraphicsImageRenderer`.
     - Key: size in pt rounded, inner radius, `railWidth`, stops × 100, coverage, sheen, displayScale, shape kind.
     - Draw as `Image(uiImage:)`; the rail takes the tint by multiply.
     - Size comes from a `GeometryReader` inside the overlay (a layout pass, no state write).
     - Cast's `Circle()` (`DetailView.swift:3252`) is another shape kind: key it, or fall back to variant 1 for it.
   - Ship the variant that lands inside the off baseline's noise (±5 % count, ±10 % time), then delete the knob (W3-2's pattern).
- Keep the signature `nuvioCardDepth(_:surface:artworkPresent:railTint:)`: `EpisodesSection.swift:512` (wave3b's file) and `DetailView.swift:3252` call it.

**Measure.**
- Release build, his config, Test 2. `walk-home.sh` on **Stage** (comparable to W2) and on **Classic** (his current look; no Classic baseline exists yet).
- Two runs each for: today, off, and variants 1 and 2. `compare.py 14 50 <traces>`.
- One Time Profiler run per finalist: `argb32_shade_axial_RGB` should fall to about 0.
- Pixel-diff rig shots of a Subtle/Full tinted rail and a Bold/Top white rail, variant vs today.

**Can break.**
- UI test50: the `card_depth_rail` frame must equal the artwork's. Keep `DebugAXIdentifier` on the overlay root, outside any `drawingGroup`.
- UI test60: the levels must stay distinguishable, so the key carries width and alphas.
- BUG-91's inner radius, the BUG-110 placeholder clamp (`artworkPresent`), and `CardDepthRailStyleTests` (pure functions, untouched).

**Size** M (Opus) + one rig walk session (~1 h).

## W3-14 Classic Home trio

### BUG-209: the heading lands high, then drops a notch

- **Where.**
  - Heading overlay: `Screens/BrowseComponents.swift:5425-5438` (`Text(section.title)` → `.pinnedRowTitleTracking` → `.padding(.top, heroPinnedRowTitleInset)`).
  - Down runs no app scroll: `HomeView.swift:1760` (`guard direction == .up, pinned`). The engine reveals the link frame from `PinnedRowGeometry.plan` (`DesignSystem/PinnedRowGeometry.swift:653-830`); rest law `predictedRestMargin` `:904`.
- **His regime** (`P351c0p1r0z0t38hzrt4`, Hide Titles: restRange 10.05).
  - The heading rests at margin −10.5, clipped 10.5 pt but in band: `bandLow = −clearance.focused` = −10, with ±2 slack (`BrowseComponents.swift:3974-3980`). So no nudge.
  - The slide target `min(max(visibleMinY, 0), 72)` (`:701`) is **held** while the rows move or a rest decision is pending (`slideHoldVerdict` `:999-1005`, `commitSlide` `:1500-1531`).
  - It is released by the settle decision about 0.25 s after rest (`:2761`) and eased over 0.22 s (`applySlideTarget` `:1613`).
  - The code documents this as the design (`:1448-1466`: "at the next rest it eases once, by the measured amount (≈8pt)"). That ease is the notch.
- **FEAT-61 refuted.**
  - The hero frame is fixed (`HomeView.swift:2844`), the text swaps inside a fixed ZStack (`:6683-6696`), and the synopsis slot is fixed (`:6872`).
  - W1's `623ffc31e` only added `fourLineLogoFloor` (`PinnedRowGeometry.swift:516-521`, `:564-566`, `:591`), which affects the carousel.
  - `PinnedRowGeometryTests:1840` pins his numbers.
  - Hide Titles changes no heading height. It does give the deepest held rest (with captions: restRange 4, rest −7.5).
- **Fix (S, `BrowseComponents.swift` only, no `HomeView.swift`).**
  - In `commitSlide`, for the **focused** row only (`tracking.isFocused`) with an in-band target (`target ≤ clearances.focused + 2`), stop waiting for `restPending`. While the rows still move, apply **without animation**: the heading tracks the clip edge over the last ~10 pt and lands once with the posters. Keep the 0.22 s ease only at rest.
  - `applySlide` (`:1482-1484`) passes the `Reading` in, for the clearance.
  - Conservative variant: skip only the `restPending` wait.
  - Do not take the geometry half (`PinnedRowGeometry.swift:783`): it grows the hero 4 pt, moves test 1840, and still clips 8.5 pt.
- **Can break.**
  - rc14's title painted across a departing row: guarded by focused-only.
  - beta.18's double ease: guarded by in-band (never nudged).
  - Never touch the 0-target snap.
  - Per-frame `@State` writes on one title for ≤ 10 frames.
- **Tests.**
  - `PinnedRowSlideHoldTests` (`:15-50`): add focused/unfocused × in/out of band × moving/pending; update `testNonzeroTargetHoldsWhileMovingOrPending` (`:37`).
  - `PinnedRowGeometryTests:1840` and `PinnedRowSettleRc14Tests` stay green.
  - Device: `-debug.homeScrollProbe YES` (Release-readable, `BrowseComponents.swift:123`) should log `slide apply … via=immediate`, not `settle`; 30 fps frames should show a single landing.
- **Size** S, Opus (rest-law history).

### BUG-210: old title text under a collection logo

- **Path.**
  1. Folder focus: `CollectionsUI.swift:420-428` → `Screens/Home/HomeRowsList.swift:325` → `HomeView.swift:659-697`.
  2. `folderHeroPreview` `:3400` → `HomeRowPreviews.folder` (`Screens/Home/HomeRowPreviews.swift:28-71`).
  3. 0.2 s dwell (`:3638`, `:3802`) → `HomeHeroDriver` (`Screens/Home/HomeHeroLeaves.swift:172-176`) → `HeroArtResolver.present(isFolder: true)` (`HomeView.swift:4323`).
  4. The resolver keeps the old hero whole until the folder art lands, for up to `folderDeadline` 1.5 s (`:4141-4146`, used at `:4542`).
  5. Then the text swap (`:7052-7054`; `HeroTextSwap.swift:29`: 0 / 0.12 / 0.12 s).
- **Refuted.** "Clear the text with the logo" changes nothing. `HeroLogo` (`:6856`) is inside the same block: a ZStack keyed `.id(textPresentation.identity)` with `.transition(.identity)` (`:6683-6696`). The old text and the new logo cannot be on screen together.
- **Evidence.**
  - `prime-open-3fps.jpg` shows the overlap in one frame of row 5 (≤ 0.33 s), with the row band double-exposed in the same frame.
  - His phone blends TV frames on every motion frame: the rc11 video at 48 s holds three Detail states in one frame.
  - That is not 0.7 s of real overlap.
- **Next, before code (R0, XS).**
  - A 60 fps recording plus `[HomeHero] present item=nuvio.folder:… waited=` and DEBUG `debug_heroText … maxLive=` (`:7062-7066`).
  - If `waited` > 0.3 s:
    - (a) `folderDeadline` 1.5 → 0.4 s (XS), at the cost of a cold folder showing its logo over no backdrop for a beat (Wave H's budget);
    - (b) the resolver publishes its pending identity and `HeroTextLayer` fades the old text when the wait starts (M).
    - Both are **`HomeView.swift` edits** (`HeroArtResolver` lives there): owner.
  - If `maxLive=1` and `waited≈0`: close it as a camera artefact and say so in the DM.
- **Tests if coded:** `HeroPresentArtWaitTests`, `HeroArtResolverLateBackdropTests`, `HeroTextSwapModelTests`, UI `HeroFolderSwapTests` test54/test55. The `heroFolderDeadlineMs` knob is DEBUG-only; Release uses the constant.

### BUG-211: catalog name twice

- **Where.** `HomeHeroForeground.nuvioLayout` (`HomeView.swift:6842-6883`).
  - The merged folder box is gated `isCollectionHero(item) && showsCTA` (`:6844`), so his panel (no CTA) gets the three-slot column.
  - Slot 1 is the wordmark in `logoSlotHeight` (~110, `:6635-6641`).
  - Slot 2 is `Text(metaLine)` (`:6860`). `metaLine` (`:6983-6991`) = `releaseInfo` = the collection title (`HomeRowPreviews.swift:55`), which is the row heading.
- **Fix (XS, owner).** `:6844` → `if isCollectionHero(item)`.
  - The panel then uses the existing box (`folderBox` `:6953`): no name line; the wordmark capped at `heroFolderLogoSlotHeight` 160 (`Theme.swift:991`), about 45 % larger, tunable on the rig with `-debug.heroFolderLogoHeight` (`:1005`).
  - The details line shows only with catalog details on (`HeroFolderBoxLayout` `:7121-7135`).
  - The box height is the column's sum (`:6845-6846`), so the hero frame and the rows plan are unchanged.
  - Update the comments at `:6845-6851` and `HomeRowPreviews.swift:13-27`, `:46-53`.
- **Notes.**
  - This reverses rc14 BUG-119 (his rc13 ask). The name still shows through `HeroLogo`'s text fallback when a folder has no logo bitmap.
  - In the box the wordmark is centred, not bottom-aligned.
  - Classic panel only by construction: Stage is `StageCopy.swift:30-50` (de-duplicated in rc5's BUG-173), and the folder rows page never presents a folder.
  - No string orphaned.
- **Tests:** `PinnedRowGeometryTests` 1571 and 1968-2010, `HeadingDetailsSettingTests:39/55`, `StageCopyTests:162-195`, plus a sim shot of the panel on a folder tile.

## W3-15 BUG-153 first Down

**Detail: the cause is confirmed in code.**
- Press 1 is the hero exit: `DetailRowAnchor.heroExit` (`DetailView.swift:2360-2366`) → `startBlendAnchor("hero-exit")`.
- The geometry handler (`:1002-1009`) waits for ≥ 0.5 pt of engine motion (`DetailRowAnchor.swift:271`). Then `anchorPass` (`:1559-1580`) runs `withAnimation(.easeOut(duration: 0.3))` to rowTop + inset − 108 (`DetailRowAnchor.swift:68`, `:80`).
- The hero is container − 236 (`DetailCinematicLayout.swift:25`, `:39`), so the glide is about 766 pt.
- `easeOut` starts at about 1.7× its mean speed, roughly 4,400 pt/s, and it takes over from the engine's slow start.
- Presses 2–3 (Down) arm no blend (`:2380-2405`): the engine reveals one row.
- Press 1 also pays the dim ramp (17 writes, `:923-950`), the trailer teardown at dim 0.8 (`:1037`) and the first build of the rows.
- Up into the hero (`heroTopPass` `:1534-1556`) has the same 0.3 s / 766 pt in reverse.

**Detail fix (S).**
- Agent, `DetailRowAnchor.swift`: a pure `anchorDuration(travel:)` (0.3 s floor, about 0.3 × travel / 380, 0.65 s cap) plus a Release-readable `debug.detailAnchorSeconds` knob.
- Owner, `DetailView.swift`, ~6 lines, **after wave3b lands**:
  - `:1573` and `:1551` use the new duration;
  - the verify sleeps (`:1504`, `:1526`) become `max(verifyDelay, duration + 0.1)`. Otherwise the 0.45 s verify (`DetailRowAnchor.swift:93`) restarts a 0.3 s easeOut mid-glide, which shows as a kink.
- Can break:
  - A double Down under 0.4 s during the longer glide: the task cancel at `:2345` does not stop the animation. Test it.
  - The UI oracle `DetailScrollMotion` (splits on a 0.10 s pause) passes with the longer verify.
  - BUG-194's pop restore is untouched.

**Home: no curve difference.**
- **Stage:** every press is `easeOut(0.5)` over k·P (`Screens/Home/StripPager.swift:703-723`; `StripGeometry.swift:399`, `:414`; `StripGeometryTests:238`).
  - Press 1 only: the `atTop` `@State` (`StripPager.swift:353`) is written in the same update as the glide (`:671`).
  - So the whole pager body and every mounted row re-evaluate at frame 0. Presses 2–3 touch only `StripScroller`.
- **Classic (his look):** every Down is the engine's reveal (`HomeView.swift:1760`).
  - Press 1 only: the tab-bar latch flips at 300 pt (`DesignSystem/TabBarVisibility.swift:261`, `:330-333`). That writes `isScrolledDown` (`HomeView.swift:217`), which the body reads unconditionally (`:1087`), so the whole HomeView body re-runs mid-glide.
  - His 4 fps sheet also fits presses 2–3 feeling softer because of BUG-209's two-step, not press 1 being harsher.
- **Measure in R0 before any code.** Release build; `-debug.homeScrollProbe YES`; Animation Hitches in the press-1 window vs presses 2–3; Time Profiler for `StripPager.body` and `HomeView.body`.
- **If confirmed:**
  - Stage: `atTop` moves into `StripPagerBox` with a stable Menu handler in Rail mode (S, `StripPager.swift` only).
  - Classic: `TabBarScrollAutoHide` (`TabBarVisibility.swift:281`) writes the binding when scrolling goes idle (S). Opt-in costs one line at `HomeView.swift:1692` (owner); otherwise Discover (`DiscoverGridPage.swift:395`) gets it too.
  - Risk: BUG-27 Menu-to-top sees the latch about 0.3 s late, with the hero on only. `handleHeroUp` (`:1897`, `:1911`) is still covered by `revealTopAfterUpIntoHero`.

**Owner and size.** Detail S, Opus (the curve and the verify sleep are coupled; not Sonnet), plus the owner's wiring. Home S per look, after measurement.

## W3-16 BUG-207 stream picker scroll

**Structure.**
- `ScrollView` (`Screens/StreamPickerView.swift:280`) → `LazyVStack` (`:284`) → per-group `VStack` + `.focusSection()` → a nested `LazyVStack` (`:324`) → `ForEach(zip)` (`:325`).
- The row is a method, `streamRow` (`:662`), not a View: never Equatable, never skipped.

**Per focus move.**
1. `.lineLimit(focusedRow == key ? nil : 3)` with `.fixedSize(vertical)` (`:698-700`): BUG-16's focus expansion. Two rows change height on every move while the engine scrolls a nested lazy stack running on estimated heights. This is the main cost.
2. Every built row's body reads the parent's `@FocusState` (`:135`), so each one re-runs:
   - Kotlin bridging (`:664-666`) and `rowTitle` (`:833-846`);
   - two SHA-256s per row once any link was rejected (`:714`; `PlaybackModels.swift:340-363`);
   - new `ExternalPlayMenu` closures (`:739-741`);
   - the zip allocation (`:325`).
3. The style on the two changed rows: the colour-scheme flip (`DesignSystem/FlatControlStyles.swift:101`) re-resolves the badge ladder. The 16 pt shadow sits on every row even at rest (`:109`).
4. The `ViewThatFits` badge ladder (`:773-806`) plus `BadgeImageView`'s empty first frame (`DesignSystem/StreamBadges.swift:229-247`): two layout passes per new row.
5. `apply()` republishes on every emission, with a SHA per stream (`Screens/StreamsViewModel.swift:229-236`, `:105-129`).

**Fix (S–M; files `StreamPickerView.swift`, `StreamBadges.swift`, `StreamsViewModel.swift`).**
- F1: `StreamRowView: View, Equatable` + `.equatable()` over a value `StreamRowModel`. The row reads expansion from `@Environment(\.settingsRowIsFocused)` (`FlatControlStyles.swift:105`). `.focused($focusedRow, equals: key)` stays at the call site.
- F2: expand after a ~0.5 s dwell (a local `.task(id:)`), with no animation.
- F3: seed `BadgeImageView` from a synchronous cache peek.
- F4: build the rows, keys included, once in `apply()`; skip identical republishes.
- Leave the at-rest shadow in the shared `.settingsRow` style alone this wave: wave3b is restyling the Settings rows that share it.

**Can break.**
- Initial focus and restore (`:438-460`, `:649`, `:1339`) rely on the stable `rowKeys` and the parent binding.
- `==` must include the spinner (`:684`), the rejected flag, the badge settings, the Instant-suffix title (`:846`), and the player list with its default.
- F2 is a visible BUG-16 change: name it in the DM.
- Strings unchanged (`"%lld streams"` `:629`, "Failed recently").
- UI tests match labels only (`NuvioTVUITests.swift:8872-8875`; `FirstPlayAutoPlay.swift:619`, `:638`).

**Measure and test.**
- Device only. Test 2 has no provider, so use a 40–64-row Torrentio-shaped stub add-on (copy `scripts/device/fixtures/*-addon.py`).
- Animation Hitches over 30× Down and 30× Up at 0.35 s, before and after; `HomeBodyCounter.tick("StreamRow")`.
- Unit: a pure `StreamRowModel.make` and its `==` (build `StreamItem` as in `StreamsViewModelListableTests.swift:15-21`).

**Size** S–M, Sonnet with this spec.

## W3-17 BUG-205 Watched icon colour lag

- **The code has no longer curve.**
  - Watched (`DetailView.swift:2206-2223`), Library (`:2225-2240`) and Shuffle (`:2253-2265`) share `compactActionButtonStyle` (`.glass` + border shape, `:2055-2063`) inside `GlassEffectContainer` (`:2071-2079`), with the same padding, label and font.
  - No `.animation`, `.contentTransition` or `.symbolEffect` sits on the row.
  - The only difference is state: `.tint(model.isWatched ? accent : nil)` (`:2220`; Library `:2238`, Shuffle `:2264`).
- **Likely cause** (inferred, not proven): the system `.glass` style restores an **accent-tinted** glass more slowly once focus leaves. His accent is **White** (rc10 table), which makes the tinted glass bright and the crossfade most visible.
  - Predictions: Library (saved) and Shuffle On lag too; Watched on an unwatched title does not.
- **Step 0 (R0), using the existing Release-readable knob.** Watched vs unwatched title, Library saved vs not, White accent, leg 0 vs `-debug.detailScrollAB 4` (`DetailView.swift:389-395`: `.bordered`, no container). Take a screenshot burst after a Right press.
- **Fix (XS).** Move the active colour from the glass tint to the glyph.
  - Agent: a new `Screens/Detail/DetailActiveGlyph.swift`, using `ProminentAccentLabel`'s mechanism (`FlatControlStyles.swift:265`): active at rest = accent; focused = the on-platter ink.
  - Owner, after wave3b: drop `.tint` at `:2220`, `:2238`, `:2264` and add the modifier inside each label.
  - Shuffle keeps its on/off cue. Titles and `.accessibilityLabel` (`:2567`) stay for `DetailActionSquareUITests` and the label matches.
- **Test:** a pure `color(active:focused:)` test.

## W3-18 BUG-195 cold-start placeholder (D5)

- **Code:** `SearchPlaceholderLayer` (`Screens/SearchView.swift:123-214`): `HStack { magnifier; Text("Search movies & shows") }` (`:133-138`). The warm path never draws it (`.already`, `:156-162`).
- **Fix:** `Text(...).hidden()`. It keeps its layout, so the magnifier holds its leading x and vertical centre. Deleting the Text would raise the magnifier by half the line-height difference, and it would jump when the real field mounts. Update the doc at `:119`.
- No string orphaned: the key is also the real field's prompt (`:313`). `SearchPlaceholderPolicyTests` is unchanged.
- **Rig:** cold launch → rail → Search, 60 fps recording: the magnifier alone until +1.1 s, no jump.
- **Size** XS, Sonnet.

## W3-19 probe cap (built)

- **Built:** `Screens/PlayerScreen.swift:167-175` (`4e12442de`). On a nil probe it logs `[PlayerRouter] probe cap hit|probe failed early after <ms>ms (cap 4000ms) host=… → mpv — <title>`, beside the existing `probe took … result=nil` (`:166`). Routing is unchanged.
  - The prefix is `[PlayerRouter]`, not the plan's `[Router]`: grep for `probe cap hit`.
  - FFmpeg only polls the deadline, so a cap hit can read above 4,000 ms. The 50 ms slack is fine.
- **P3 notes.**
  - (1) A deadline cut inside the P7 RPU scan (`MediaProbe.swift:180`, `!deadline.expired`) returns a non-nil probe marked `.missing`. It routes as "DV P7 (no convertible RPU)" (`PlayerEngineRouter.swift:88-89`) and is never logged as a cap.
  - (2) The host is now in console logs; rig logs stay under the redaction rule (a self-hosted add-on or proxy host can be private).
  - (3) Optional: a pure `probeOutcome(ms:capMs:)` with a test.
- **Re-test:** needs Steven's stream name, then a rig replay of that title, reading this line.

## Risks, ranked

**P1**
1. W3-15 (Detail) and W3-17 must edit `DetailView.swift`, which wave3b's W3-4 is editing and the owner edits. Sequence them after wave3b merges and wave3c rebases; agents write only `DetailRowAnchor.swift` and the new modifier file.
2. W3-11 built literally from Batch N brings back the flush 152 × 132 resting tab Christian rejected on 10-20. D1 covers the open column; the rest stays the bare glyph.
3. W3-14 BUG-210 as planned is a no-op fix: logo and text share one identity. No code before the repro.
4. W3-12 run in the triage's config would give the fourth "passed on the rig, not on his box". Use the config from his rc11 video and both corner styles.

**P2**
- BUG-209's in-band apply leaking to unfocused rows, or easing while moving, reopens rc14's title across a departing row and beta.18's double ease.
- W3-13:
  - variant 1's texture memory;
  - variant 2 cache-key misses (radius, width, stops, coverage, shape kind) draw wrong rails;
  - a tint multiply that touches the sheen;
  - test50 and test60.
- W3-16: Equatable rows going stale; BUG-16's dwell is visible.
- W3-15 Detail: the longer glide is coupled to the verify pass; double Down.
- W3-11: Rail12 and `testCornerPillGeometry` encode "never flush", so the gate fails until they are rewritten; glass flicker on a taller animated frame.

**P3**
- W3-18: the magnifier jumps if the Text is deleted.
- W3-19: the P7 scan cap; the host in logs.
- W3-11: the Rail Style row is inert in Corner (hide it); icon x 28 sits in the overscan zone, as Centre's does.
- BUG-211: reverses BUG-119; the logo is centred in the box.
- W3-15 Classic: a deferred latch delays BUG-27's Menu-to-top (hero-on only).

**Cross-cutting.**
- **Localization:** no recommended fix adds or orphans a string, so Phase 1c needs no translation pass.
- **Release-only:** every knob and probe used is Release-readable: `HomePerfKnobs` (static let), `debug.homeScrollProbe` (`BrowseComponents.swift:123`), `debug.detailScrollProbe` (`DetailView.swift:291`), `debug.detailScrollAB` (`:390`).
- **Up-skip** (`823450355..94a66f597`: BrowseComponents +25 lines of `[Focus]` logger, HomeRowsList, HomeUpIntoHeroGate, HomeUpSwipeCatcher, HomeView 755–3367 and 7374, PinnedRowUpFallback, tests): no proposed hunk overlaps it. The Classic latch is not read by up-skip code (it reads `rowsScrolledPastTop` and the `upInput` box).

## Tests to add or change

| Item | Unit (NuvioTVTests) | UI / device |
|---|---|---|
| W3-11 | `NavigationChromeTests`: rewrite `testCornerPillGeometry` (flush origin; width independent of open; Home cell (28, 60)); a `cornerGlassFrame` case per label mode | `NavigationRailUITests` Rail12/12b: origin flush, width 100/316 in both phases, height column + 38, Home centre (58, 90) unchanged; sim + rig shots |
| W3-13 | `HomePerfKnobsTests` (new key); a cache-key test (distinct per width, alpha, radius, shape); the tint-multiply equality as a pure function | test50, test60; R1 walks (Stage + Classic, Release, ×2) |
| W3-14 | `PinnedRowSlideHoldTests` new matrix + `:37` updated; 1840, rc14 settle tests stay green; BUG-211: the HeroFolderBox tests, `HeadingDetailsSettingTests`, `StageCopyTests` | probe `via=immediate`; 30 fps landing; panel-on-folder sim shot; BUG-210 R0 repro |
| W3-15 | `DetailRowAnchorTests`: 0.3 s floor, ~0.6 s at 766 pt, cap, monotonic, verify ≥ duration + slack; `StripGeometryTests:238` unchanged | `[UX6]` per-frame lines; double-Down < 0.4 s; Home press-1 hitch window |
| W3-16 | `StreamRowModel.make` + `==` | stub add-on, Animation Hitches before/after |
| W3-17 | `DetailActiveGlyph.color(active:focused:)` | R0 A/B; screenshot burst vs Library |
| W3-18 | none (policy untouched) | cold-start 60 fps |
| W3-19 | optional `probeOutcome` | his title on the rig |

## Sizes (replacing §4's owner/size column)

| # | Owner, size |
|---|---|
| W3-11 | Opus, S–M (rail files + the two tests) |
| W3-12 | main session on the rig (R0), ~2 h with the baselines below |
| W3-13 | Opus, M + R1 walks (~1 h) |
| W3-14 | 209 Opus S; 210 R0 XS, then owner XS/M only if `waited` > 0.3 s; 211 owner XS |
| W3-15 | Detail: Opus S (helper) + owner XS (wiring, after wave3b); Home: measure in R0, then S per look |
| W3-16 | Sonnet, S–M |
| W3-17 | R0 XS; Sonnet XS (new file); owner XS (wiring, after wave3b) |
| W3-18 | Sonnet, XS |
| W3-19 | done; P3 follow-ups XS, optional |

## Wave split

Phase 1c stays on `claude/wave3c` (this clone). It does not ride wave3b's Sonnet wave B: that is another branch and another device pass. At most two agents at a time; builds go through `with-lock.sh`.

| Step | Who | Files (disjoint within a step) | Needs |
|---|---|---|---|
| **R0** rig, no code | main session | none. W3-12 capture; W3-13 baselines (Stage + Classic, depth on/off ×2); 209 probe; 210 repro; W3-15 windows; W3-16 stub baseline; W3-17 A/B | `ready.sh` |
| **C1** (parallel; may start before R0) | Opus A: W3-11 | `DesignSystem/NavigationRail.swift`, `DesignSystem/NavigationChrome.swift`, `Screens/Settings/AppearanceSettingsPane.swift`, `NuvioTVTests/NavigationChromeTests.swift`, `NuvioTVUITests/NavigationRailUITests.swift` | D1 |
| | Opus B: W3-13 | `DesignSystem/CardDepthStyle.swift`, new `DesignSystem/CardDepthRasterCache.swift`, `Screens/Home/HomePerfKnobs.swift`, `NuvioTVTests/HomePerfKnobsTests.swift`, new CardDepth cache tests | — |
| **C2** (parallel, after C1) | Opus C: W3-14 BUG-209 + W3-15 Detail helper (+ the Home halves if R0 confirms) | `Screens/BrowseComponents.swift` (PinnedRowTitle only), `NuvioTVTests/PinnedRowSlideHoldTests.swift`, `Screens/DetailRowAnchor.swift`, `NuvioTVTests/DetailRowAnchorTests.swift`, (`Screens/Home/StripPager.swift`, `DesignSystem/TabBarVisibility.swift`) | R0 |
| | Sonnet D: W3-16 + W3-18 + W3-17's file | `Screens/StreamPickerView.swift`, `DesignSystem/StreamBadges.swift`, `Screens/StreamsViewModel.swift`, `Screens/SearchView.swift`, new `Screens/Detail/DetailActiveGlyph.swift`, new tests | R0 (W3-17 A/B) |
| **Owner, now** | Christian | `HomeView.swift`: BUG-211 `:6844` + comments; BUG-210 `:4141-4146` or the resolver, only if R0 says so; optional W3-15 Classic opt-in `:1692` | R0 |
| **Owner, after wave3b merges** (rebase wave3c first) | Christian | `DetailView.swift`: W3-15 `:1551`, `:1573`, `:1504`, `:1526`; W3-17 `:2220`, `:2238`, `:2264` + labels | wave3b merged |
| **R1** rig | main session | W3-13 variant walks → pick → delete the knob; then the Phase 1c device pass in his config (both corner styles) | C1, C2 |
| Gate, r1/r2, merge | as §4 | | |

**Conflicts with wave3b.**
- Only `DetailView.swift` is unavoidable (W3-15 Detail, W3-17): sequenced above.
- Avoided on purpose:
  - `EpisodesSection.swift` (W3-13 keeps the `nuvioCardDepth` signature);
  - `SettingsDescriptions.swift` (W3-11 leaves the rail copy alone);
  - `FlatControlStyles.swift`'s shared `.settingsRow` shadow (W3-16's F5 deferred).
- `AppearanceSettingsPane.swift` uses `SettingsRowViews` types: compile coupling only; rebuild after wave3b's merge.
- **`HomeView.swift` edits** (owner): BUG-211, BUG-210 (conditional), the optional W3-15 Classic opt-in.
- **`DetailView.swift` edits** (owner, after wave3b): W3-15 Detail, W3-17.
