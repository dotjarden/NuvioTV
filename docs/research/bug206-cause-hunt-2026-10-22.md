# BUG-206 cause hunt: Cinematic Detail choppier, rc7 → rc11 (2026-10-22)

Read-only. No source edits, no builds. Inputs:
- `git diff tvos-v0.3.0-beta.19-rc7..tvos-v0.3.0-beta.19-rc11` in `~/Claude/Projects/NuvioMobile-wave3c` (`claude/wave3-all`). The measured build `823450355` has **no diff from rc11** on any Detail or DesignSystem path, so "rc11-class" is exact for this page.
- The three R0 traces in `~/Library/Logs/nuviotv-traces/` (`r0-detail-cinematic`, `r0-detail-classic`, `r0-rc7-detail-cinematic`), re-read with `xcrun xctrace export`. The Animation Hitches template also records a **1 kHz symbolicated user-stack CPU profile** (`time-profile` table, NuvioTV symbols included) and per-frame `hitches-renders` (offscreen passes), `hitches-gpu` and `hitches-updates` tables. Every number below comes from those tables. 1 main-thread sample = 1 ms.
- Steven's isolation (tracker row BUG-206, 10-21): Classic Detail smooth, Cinematic not; Classic Home made the whole app smoother; "sidebar disabled and all depth effects removed → much smoother".

## 0. Bottom line

1. **The rig has not confirmed a regression yet.** The rc7 trace contains **no walk**: NuvioTV never leaves Home after launch (zero `SearchView`/`DetailView` frames in 111 s). The rc11-class Cinematic trace's walk **started 13 s before Instruments launched the app** (`WALK_T0` 00:01:58Z, trace start 00:02:11Z). Search was never reached; the stray "down ×4, select" most likely opened Classic Home's row-4 title (a series: `EpisodesSection` runs) at ~7 s, while Home was still loading. **44 of the 65 hitches and 1185 of the 1552 ms are launch plus that stray push.** The walk proper is **21 hitches / 367 ms**. The PLAN.md line "BUG-206 CONFIRMED as a regression" rests on a void baseline.
2. **What the rc11-class page costs** (both layouts): every move is **GPU-bound**. Median GPU per frame is 13–15 ms, p90 is 17–38 ms, and there are 16–23 offscreen passes per frame while the hero or the top rows are on screen. Home at launch runs at 1.5 ms and 1 offscreen pass. The main thread is only 20–30 % busy and `DetailView.body` is about 2 ms per move. The **Detail push** costs about 1 s of main thread, 60–70 % of it **CPU rasterising Card Depth gradient strokes**.
3. **Most likely rc7→rc11 delta on the walk path in Steven's config: BUG-177** (rc8, Batch G `60f041180`). It covers the Season, Episode and Trailer tiles: system highlight → SwiftUI ring + manual lift + 22 pt platter shadow, a container clip, and a poster-tinted depth rail. Next come **FEAT-60** (compact logo with a shadow, Cinematic-only) and **BUG-178** (top-scrim ramp), both rc8. Nothing rc9–rc11 on Detail is on the walk path in his config, or it measures at about 0. **Build rc8 first.**
4. **Biggest absolute cost: the Card Depth rail/sheen raster.** It predates rc7 in kind, matches Steven's "depth off → much smoother", and Wave 3 W3-13 on this branch targets it. Verify the `.colorMultiply` it adds does not raise per-frame offscreen passes.
5. The page has **no GPU headroom**. Even deep in the rows, with only 4 offscreen passes, it needs about 14.5 ms per frame for the full-screen backdrop stack, so any rc8 addition (one shadow, a few container clips) tips frames over 16.7 ms. That is a plausible mechanism for "choppier again" from small changes.

## 1. Trace audit (read before any total)

| Trace | Start (UTC) | What the CPU profile shows | Verdict |
|---|---|---|---|
| `r0-rc7-detail-cinematic` (build 139) | 04:06:34 | Home frames 1–10 s, then the main thread idles (≤ 20 samples/s, an 8 s Home timer) to 111 s. No `SearchView`, no `DetailView`. | **Void.** No press reached the app. The likely cause is the "Instruments launch came up behind the tvOS Home screen" failure that `walks.sh` documents (02:11Z). Its 5 hitches / 133 ms are launch only. |
| `r0-detail-cinematic` (`823450355`) | 00:02:11 | `WALK_T0` 00:01:58 (`summary-attempt1.txt`). Home 1–6 s, **Detail from 7 s with `EpisodesSection`** (a series), no Search anywhere. `DETAIL_T0` 00:02:25 → 14 s. Downs land 21.2–30.3 s (bursts every ~0.9 s, only 6 move focus); Ups land 41.0–49.4 s (6 moves). | **Partial.** Down/Up valid on a Home-row-4 series, not Severance. The push overlaps Home's first load. |
| `r0-detail-classic` (`823450355`) | 02:00:43 | Search 36–48.5 s, push 48.6 s, Downs 59–64.5 s, Ups 72–79 s. | **Valid** full walk. |

Hitches by phase (count / ms):

| Phase | rc11-class Cinematic | rc11-class Classic | rc7 |
|---|---|---|---|
| Launch + Home | 9 / 284 (0–6.95 s; the **100 ms at 5.34 s is Home's first load**) | 9 / 517 | 5 / 133 (whole run) |
| Search | not reached | 8 / 467 (283.6 ms GPU at 38.54 s) | — |
| Detail push, first ~7 s | 35 / 901 (stray push during Home load; **the 166.8 ms at 7.93 s and 8.56 s are here**) | 40 / 1151 (166.8 ms at 49.14 s, 183.5 ms at 49.67 s, ~30 single frames 49.9–50.85 s) | — |
| 10 Down (6 effective) | 7 / 133 | 17 / 350 | — |
| 10 Up (6 effective) | 14 / 234 (**12 consecutive at 46.21–46.68 s**) | 12 / 200 | — |

**Gate for every future run:** before reading a total, export `time-profile` and check for `SearchView` and `DetailView.body.getter` frames in the expected windows. As a second check, compare `--toc` `start-date` with `WALK_T0`; a walk that starts before `start-date` is void.

## 2. What the rc11-class page costs

Per-frame stats join `hitches-renders` (offscreen passes), `hitches-gpu` (GPU ms) and `hitches-updates` (app commit ms) by `swap-id`:

| Window | Frames | GPU ms med / p90 / max | Offscreen med / p90 | Frames > 14 ms GPU |
|---|---|---|---|---|
| Cine launch + Home 2–6.9 s | 199 | 1.5 / 9.6 / 13.5 | 1 / 10 | 0 |
| Cine stray push 7–13 s | 315 | 6.0 / 15.6 / 57.3 | 7 / 14 | 67 |
| Cine Down 21–27.5 s | 239 | 14.3 / 25.6 / 50.0 | 16 / 23 | 128 |
| …21–23 s (hero exit, top rows) | 73 | 13–14.5 / 17–38 | **23** / 23–25 | 35 |
| …25–27 s (bottom rows) | 91 | 14.4–14.9 / 17–31 | **4** / 4 | 53 |
| Cine Up 41–47.5 s | 143 | 13.4 / 29.4 / 38.1 | 7 / 20 | 59 |
| Cine 46.1–46.8 s (Up into the hero) | 20 | **29.4** / 31.1 / 34.8 | 7 / 7 | 13 |
| Classic push 49–55 s | 230 | 12.4 / 27.4 / 50.3 | 16 / 28 | 87 |
| Classic Down 59–64.5 s | 272 | 13.7 / 17.4 / 38.6 | 23 / 31 (max 41) | 119 |
| Classic Up 72–79 s | 193 | 14.1 / 25.7 / 39.0 | 21 / 28 | 99 |

Main thread (ms of samples in the window):

| Window | Main | `PaintShapeLayer.draw` (rail `Stroke<StrokeablePath>+Gradient` / `Primitive+Gradient`) | SwiftUI `ViewGraphDisplayLink.displayLinkTimer` | Focus engine `_UIFocus*` | `DetailView.body` |
|---|---|---|---|---|---|
| Cine push 7–13 | 2918 | **1841** (1393 / 435) | 226 | 41 | 84 |
| Cine Down 21–27.5 | 1299 | 155 (137 / 17) | 172 | 157 | 15 |
| Cine Up 41–47.5 | 1021 | 135 | 123 | 158 | 32 |
| Classic push 49–55 | 1839 | **720** (553 / 161) | 380 | 39 | 106 |
| …Classic 49.85–50.9 | 948 of ~1050 | **662** (515 rail) | — | 2 | — |
| Classic Down 59–64.5 | 1814 | 158 | **584** | 148 | 18 |
| Classic Up 72–79 | 1490 | 140 | 323 | 165 | 32 |

Readings:
- **Walk hitches are GPU frames.** 19 of the 21 Down/Up hitches on the Cinematic run are single 16.7 ms frames marked "Potentially expensive GPU work"; the others are one unlabelled frame (21.82 s) and one 33 ms "app update + GPU" frame (25.54 s). The body is not the problem: `DetailView.body` is ~2 ms per move, and DetailRowAnchored plus the other app bodies are single-digit ms per walk.
- **The push is CPU raster.** The stack is `shape.strokeBorder(LinearGradient)` → `PaintShapeLayer.draw(in:)` → RenderBox `GenericItem1<Coverage::Stroke<StrokeablePath>, Fill::Gradient>` → `CGContextDrawLinearGradient` → `argb32_shade_axial_RGB`, all inside `CA::Layer::display_` during the commit. That is the Card Depth rail; `Primitive+Gradient` is the sheen and the full-screen scrims. In Classic it holds the main thread ~95 % for 1.05 s, which shows up as the ~30 single-frame hitches.
- **Classic's per-frame main-thread cost is Liquid Glass.** Under the display link: `SDFLayer.update…backdropGroupID`, `GlassContainer.Entry.shapeBounds` and `GlassAnimatableMaterialValue.updateValue` (chips, action row, synopsis panel), plus `ScrollViewCommitMutation.apply` (the anchor glide `scrollTo`, driven by SwiftUI frame by frame).
- **Base fill.** Deep in the rows (25–27 s, 4 offscreen passes) the GPU still needs ~14.5 ms per frame. Composited under the rows at every frame: the 4K backdrop, the masked poster backdrop, three full-screen scrims, the 0.85 dim and the top scrim. That is ~85 % of budget before any card effect.

## 3. Ranked suspects

Ranking key: (a) runs per move in Steven's config, (b) per-row cost × rows mounted, (c) shared by Classic. **Δ** = new since rc7. Lines are at rc11.

### S1. BUG-177 Detail tiles: ring, manual lift, platter shadow, container clip, tinted rail. **Δ rc8** (`60f041180` Batch G; `12649dc93` rc10 trimmed it)
- **Where:** `Screens/Detail/DetailTileFocus.swift:66–120` (`DetailTileFocusLift`: band `scaleEffect`, ring `strokeBorder` overlay, poster-ring `ArtworkColorStore` sampling :126–138); `DesignSystem/PosterCard.swift:882–899` (`manualLift`: black `RoundedRectangle` + `.shadow(radius: 22, y: 10)` under the focused tile, `scaleEffect` + `.animation(.easeOut 0.15)`); `Screens/EpisodesSection.swift:151/157` (`cardFocusButtonStyle()` → `.ring` = `RingCardButtonStyle` + `.focusEffectDisabled(true)`, `.zIndex` flip), `:397–450` (`SeasonPosterRow`), `:511` (`.clipShape(shape)` on the still+scrim ZStack), `:512` (tinted `nuvioCardDepth`), `:526` (lift), `:547` (card-wide `.animation(value: isFocused)`), `:672/:677` (`SeasonPosterCard`); `Screens/TrailerThumbnail.swift:109/113` (container clip over image + `Color.black.opacity(0.2)`), `:114`, `:131`, `:163`.
- **Per move:** these are the first rows under a series hero, so the 1st Down and the last Up of every walk enter or leave them, and Left/Right inside them pays every time. The focused tile gets a SwiftUI scale animation over a 22 pt black platter shadow (a large blur on every animating frame). Also a ring stroke, an `ArtworkColorStore` lookup plus an animated `posterRingTint` write (Ring Takes Poster Color), a whole-card animation (art and caption) on `isFocused`, and a `zIndex` reorder.
- **Per frame:** the clip moved from each layer to the container: masksToBounds + continuous corners over two sublayers, so **one offscreen pass per visible Episode or Trailer tile** (rc7 clipped the image and the scrim separately).
- **Per mount:** rails now take the poster colour (`DetailTileRailTint`, `DetailTileFocus.swift:165–183`). On a colour-store miss the rail rasterises white, then **again** tinted when the colour lands, so the CPU rail raster runs twice per tile.
- **Why rc7 did not pay it:** rc7 tiles were `.cardFocusButtonStyle(lift: .plain)` → `.borderless` + `tileFocusLift` → system `.hoverEffect(.highlight)`, with per-layer clips and white rails.
- **Classic:** shares it. `EpisodesSection` and `TrailerThumbCard` are used by both layouts.
- **Cheapest fix:** (i) `focusShadow: false` for the three tiles (the `-debug.detailTileRingNoShadow` path as default); (ii) put the clips back on each layer as rc7 had them; (iii) keep these tiles' rails white until W3-13's multiply lands, or tint only on a store hit; (iv) drop the card-wide `.animation(value: isFocused)` (the lift animates itself).
- **No-build A/B:** `-debug.detailTileRingNoShadow YES`; `-debug.detailNoTileRing YES` is only a **partial** revert (back on `TileFocusLift`, but `RingCardButtonStyle`/`focusEffectDisabled`, the container clip and the tinted rails stay).

### S2. Card Depth rail and sheen rasterised on the main thread. Δ partial (pre-rc7 in kind; S1 widened it)
- **Where:** `DesignSystem/CardDepthStyle.swift:391–399` (`CardDepthModifier`, `railSuppressed: isFocused`), `:427–439` (sheen `LinearGradient.clipShape(shape)` = a CPU `Primitive+Gradient` fill), `:440` (structural `if edge > 0 && !railSuppressed`), `:508–521` (`edgeStroke` = `strokeBorder(LinearGradient)` = CPU `Stroke+Gradient`). Call sites on Detail: `PosterCard` (More Like This), `SagaCard` (Collection), `CastCard` (`DetailView.swift:3252`), and the three S1 tiles.
- **Measured:** push 553–1393 ms rail + 161–435 ms sheen/scrim of CPU raster; walk ~23 ms per move (the newly unfocused card's rail is re-inserted and re-rasterised, and cards entering the LazyHStacks raster theirs).
- **Per move:** yes. **Rows:** every mounted card. The page's outer stack is a plain `VStack`, so every row builds on push. **Classic:** yes. **Steven:** depth off → "much smoother".
- **Why rc7 did not pay it:** it did, for posters, cast and episodes; only S1's tint re-raster is new. S2 explains the **size** of the push stall more than the regression.
- **Cheapest fix:** at **Full** coverage (Steven's) the Subtle stops are 0.35 / 0.28 / 0.28, so stroke one `Color`. A colour-filled shape is a CA shape layer, so there is no CPU raster. Keep the gradient for Top/Half. For the sheen, draw a plain `LinearGradient` inside the card's existing clip: `.clipShape` on the gradient is what turns it into a CPU shape fill. W3-13 (§5) covers the per-move and tint re-rasters; its RasterCache variant covers the push.

### S3. FEAT-60 compact logo. **Δ rc8** (`ddbd0541d`, `38bd6b932`), Cinematic only
- **Where:** `DetailView.swift:200–229` (`DetailCompactLogo`, `.shadow(color: .black.opacity(0.5), radius: 8)` at **:220**), overlay `:810–815` (reads `focusedRow` in the body), `:912–920` (5th `onScrollGeometryChange`, `heroGone`).
- **Per move:** while focus is in the rows past the hero, a shadowed image layer is composited on every frame (offscreen pass + 8 pt blur), so it costs on every scrolling frame below the hero. Its 0.25 s fade lands inside the hero exit/return glide, the heaviest frames on the page (S4). It also observes the whole `ScrollDimModel`, so it re-evaluates on every 0.05 dim step and every `isScrolling` flip. That part is cheap but needless.
- **Why rc7 did not pay it:** the logo did not exist. **Classic:** no, which fits Steven's Cinematic-vs-Classic split.
- **Fix:** drop the shadow (the logo sits on the 0.96-black top scrim) or bake it into the image; pass `heroGone` as a Bool instead of the model. **A/B:** `-debug.detailNoCompactLogo YES`.

### S4. The hero exit/return glide, plus the rc8 work layered on it (Cinematic)
- **Where:** `DetailView.swift:1539–1556` (`heroTopPass`), `:1560–1580` (`anchorPass`), `withAnimation(.easeOut(duration: 0.3)) { detailScrollPosition.scrollTo }` at `:1551/:1573` (SwiftUI-driven, `ScrollViewCommitMutation.apply` per frame, plus glass SDF updates for the hero's chips and buttons); `DetailTopScrim` `:177–197` (**BUG-178, rc8**: opacity follows every 0.05 dim step with a fresh 0.12 s animation; rc7 animated only the on/off flip); `.scrollEdgeEffectHidden` `:805` (rc8; removes the system edge effect, a saving).
- **Measured:** the Up into the hero (6th Up at 45.7 s) produced **12 consecutive GPU-bound frames at ~30 ms**, 46.21–46.68 s, with the main thread at 10–25 %.
- **Why rc7 did not pay it:** the glide (FEAT-35) predates rc7; rc8 put the compact-logo fade and the scrim ramp into the same frames. **Classic:** no hero glide.
- **Fix:** keep extra work out of these frames (S3). On Wave 3, hold the glide at 0.3 s until the page is under budget (§5: W3-15 roughly doubles it).

### S5. Page base fill. Not a regression; it is why small additions bite
- **Where:** `backdropImage` `:1638` (decoded at 3840 px), `posterBackdropLayer` `:1668` (`.mask(LinearGradient)` → offscreen pass), `cinematicScrimOverlay` `:1794` (three full-screen scrims, CPU-rastered 4K bitmaps), `ScrollDimOverlay` (black at 0.85), `DetailTopScrim`.
- **Measured:** ~14.5 ms GPU per frame with 4 offscreen passes at the bottom of the page.
- **Fix to measure:** in the rows (`dimModel.value` = 0.85), flatten the static backdrop stack into one layer (`.drawingGroup()` on the stack, rendered once while it does not change) or swap in a pre-composited image. Either removes ~4 full-screen blends per frame.

### S6. Liquid Glass per frame. Pre-rc7; the rc8 teaser platter mounts only on the teaser
- **Where:** chips `detailChipBackground` `:1959` (glass whenever trailers are off: `chipGlassFlat` = `trailerActive || leg`, so **always glass in Steven's config**), action row `GlassEffectContainer` `:2076`, Classic synopsis panel `detailPanelBackground` `:2004`, teaser platter `DetailCinematicHero.swift:358–366` (rc8, only while the teaser holds focus).
- **Measured:** Classic Down 584 ms under the display link, against 172 ms on Cinematic. It explains the rig's Classic ≥ Cinematic, not Steven's split. **A/B:** `-debug.detailScrollAB 2` (chips flat), `4` (all Detail glass flat; live read, so a launch argument works).

### S7. BUG-153 deferred trailer mount. Δ rc9, inert in his config
- `pageScrolling` `:535` is written from `.onReceive(dimModel.$isScrolling…)` `:1026` and read only inside `updateTrailerMount()`, never in `body`, so it causes no invalidation. With trailers off, `trailerMountCandidate` stays false. Rule out.

## 4. Ruled out on the profile (≈ 0 samples on the walk) or off the walk path

- **Body-level focus reads:** `DetailView.body` re-runs per row change in **both** rc7 and rc11 (`onChange(of: focusedRow)`, `DetailAboutSection(isFocused: focusedRow == .about)`). 15 ms over 6 moves. rc11 adds the compact-logo overlay and three closure-carrying child rows to that body.
- **BUG-187/194 focus memory and pop gate** (`:572–585`, `:837–866`, `:1075–1080`, `DetailFocusMemory.swift`): a reference box, active only on a pop. 0 samples (`DetailFocusMemory`, `DetailPopGate`); `ViewerInputClock` 1–4.
- **FEAT-82 square / `playButtonHeight`** (`:490`, `:2580`, `:2586–2600`): in Cinematic, Play is not icon-only, so the `onGeometryChange` returns 0 and never writes. `GeometryActionBinder` is 3–13 samples per walk. Side note: in Cinematic `squareSide` can never resolve, because Play is never measured.
- **Rail, Corner + Hidden:** `RailVisibilityRule.shown` is false on Detail (hidden + immersive), so the panel is out of the tree. `HiddenTabBarFocusBlocker`'s per-focus `apply()` has a comment-only diff since rc7. 0 samples for `NavigationRail`, `NavigationChrome` and `HiddenTabBar`. Steven's "sidebar off → smoother" is app-wide (Home), not this page.
- **Synopsis sheet backdrop (BUG-193, rc11 W1):** runs only while the sheet is open. **Four-line synopsis (FEAT-61, W1)** is Classic **Home** (`PinnedRowGeometry.swift:460+`), not Detail. Open Sans does not apply (he runs System).
- **`DetailTrailerGate` (rc11 W2):** a pure function of 8 bools.
- **Rows as child views (rc10 Batch M):** `DetailPosterLinkRow` `:3095`, `DetailTrailersRow` `:3153`, `SeasonPosterRow`. Structural; their closure parameters re-run them with the parent body, as the inline rows did in rc7.
- **`@AppStorage` in rows:** rc11 replaced the tiles' `@AppStorage("no_zoom_on_focus")` with `\.focusAppearance`. CastCard keeps two, unchanged since rc7.
- **Hook counts in `DetailView.swift`:** `onGeometryChange` 1 → 2 call sites (the new one is per icon-only label and never writes), `onScrollGeometryChange` 4 → 5, `GeometryReader` 3 → 3, `detailRowAnchored` 11 → 12, `onReceive` 1 → 3 (`isScrolling`, `ViewerInputClock.didRecord`), `.shadow` 0 → 1 (S3). `DetailRowAnchor.swift` itself is unchanged rc7→rc11.
- **No change on the walk path:** studio chips and parental guide (only BUG-187 `onChange` added), the hero text (`DetailCinematicHero` diff is the teaser platter and backdrop URLs), the Batch C darker band (stop values only, same layers), `CachedAsyncImage` (rc11 P1 only removed work: publish on change, no per-image `.task`).

## 5. Wave 3 commits on `claude/wave3-all` that touch a suspect (none are in `823450355`)

| Commit | Suspect | Effect | Risk / check |
|---|---|---|---|
| `c493fe6c4` W3-13 (1)(2) | S2, S1(iii) | Rail always built, hidden by `.opacity` on focus (no per-move re-raster); stroked white then `.colorMultiply(tint)` (no re-raster when the tint lands) | `.colorMultiply` is either folded into the RB raster (a tint change re-rasters again) or applied as a layer filter (possibly an offscreen pass **per railed card**, on a GPU-bound page). Check: push `Stroke+Gradient` ms falls **and** `offscreen-passes` per frame does not rise by the visible card count. |
| `869c96e18`, `25febcc17`, `68c05a4bb` W3-13 (3) | S2 | `-debug.cardDepthRender 1` = `drawingGroup` per card; `2` = `CardDepthRasterCache` (one raster per geometry key); `animatesSize` routes animating frames to variant 1 | Variant 1 adds an offscreen pass per card; **avoid on Detail**. Variant 2 is the push fix. |
| `7b387aacf`, `6b44a8c82` W3-15 | S4 | Distance-scaled glide: hero exit/return 766 pt goes 0.3 s → ~0.6 s (cap 0.65 s) | **Roughly doubles the GPU-bound frames** in the page's heaviest moment. A/B `-debug.detailAnchorSeconds 0.3`. |
| `a929d6f50`, `6b44a8c82` W3-17 | S6 | Watched/Library/Shuffle drop the glass `.tint(accent)` for a glyph colour | Neutral to a small GPU win. |
| `dc1f23a22`, `751d550e4` FEAT-82 glyph | — | Fixed symbol frame and scale | Static; no per-move cost. |
| `45a48b039`, `0bed3fa4e`, `0603211ea`, `eed9c7c20`, `75f10bbe4` BUG-194 r3 | — | Pop path only | Not on the walk. |
| `3c56e34fd`, `4a795fa93` BUG-200 | — | Cast and studio-chip lift in the **default cell** (ring off, zoom on) | Not Steven's cell. |
| `bd8fbe07a`, `20564febe` FEAT-83 | S1 rows | `.contextMenu` on **every** episode card and season poster; `EpisodeHoldMenuItems` calls `meta.previousReleasedEpisodesBefore` (Kotlin) | Check `EpisodeHoldMenuItems.body` = 0 samples outside a hold. If the menu builds eagerly it is per card, per body. |

## 6. Time Profiler plan

**Prerequisites:** `scripts/device/ready.sh` (stop if it refuses). Test 2 only. `-debug.rememberLastProfile` is **DEBUG-only in rc7 and rc11** (`ProfileAutoEnter.swift:34`), so a Release launch auto-enters the last-used profile. The launch screenshot must show Test 2 before any press; if it shows Chris, abort. Install the build under test (`xcrun devicectl device install app --device "$ATV_UDID" <app>`; rc7 is `~/Claude/Projects/NuvioMobile-wave3/iosApp/build/rc7-app/NuvioTV.app`, rc11-class is `…/rel-app/NuvioTV.app`), and reinstall `rel-app` at the end.

The run is the `walks.sh` launch phase with the template swapped, in two phases behind a screenshot:

```sh
cd "/Users/christianturnbull/Claude/Projects/Nuvio tvOS"
source ~/.config/nuviotv-device/atv.env            # or NUVIOTV_DEVICE_CONF=/tmp/nuviotv-device-v6 when IPv4 is down
NAME=tp-rc11-cine                                  # tp-rc7-cine, tp-rc8-cine, …
TR=~/Library/Logs/nuviotv-traces/bug206-$NAME.trace
PID=$(xcrun devicectl device info processes --device "$ATV_UDID" 2>/dev/null | grep "NuvioTV.app/NuvioTV " | awk '{print $1}' | head -1)
[ -n "$PID" ] && xcrun devicectl device process signal --device "$ATV_UDID" --pid "$PID" --signal SIGKILL && sleep 6
xcrun xctrace record --device "$ATV_UDID" --template 'Time Profiler' --time-limit 110s --output "$TR" \
  --launch -- com.youngchris29.NuvioTV \
  -detail_trailer_autoplay NO -detail_trailer_background NO -sidebar_style rail -rail_visibility hidden \
  -rail_position corner -rail_labels shown -rail_style floating -ui_font system -accent_focus_ring YES \
  -focus_ring_poster_color YES -depth_rail_poster_color YES -no_zoom_on_focus NO -row_edge_fade off \
  -show_catalog_details_in_headings YES -settings_style default -detail_action_icons_only NO \
  -detail_layout cinematic -home_layout classic \
  > ~/Library/Logs/nuviotv-traces/bug206-$NAME.log 2>&1 &
sleep 15; SHOT_SMALL=1 scripts/device/shot.sh docs/research/wave3c-r0-2026-10-21/launch-$NAME | tail -1
# READ the screenshot: NuvioTV Home, in front, Test 2. Only then:
echo "WALK_T0 $(date +%s)"; docs/research/batch-p-wave0-2026-10-20/walk-detail.sh
```

Run the same sequence with `--template 'Animation Hitches'` (`walks.sh launch/walk`). It is the **comparator**: its `time-profile` table already carries 1 kHz stacks, and only it has per-frame GPU ms and offscreen passes, the numbers that move here. Two runs per build: the Classic depth runs varied between 72 and 46.

**Analysis** (the existing script reads exactly this export):

```sh
xcrun xctrace export --input "$TR" --xpath '/trace-toc/run[@number="1"]/data/table[@schema="time-profile"]' > "${TR%.trace}.tp.xml"
python3 -I docs/research/batch-p-wave0-2026-10-20/timeprofile.py "${TR%.trace}.tp.xml" <t0> <t1>
# GPU side (Animation Hitches trace): join by swap-id
#   …/table[@schema="hitches-renders"]  → offscreen-passes per frame
#   …/table[@schema="hitches-gpu"]      → GPU duration per frame
```

Windows come from `DETAIL_T0` minus the trace `start-date`. The push is the ~6 s before the first Down burst. The Downs are the first 10 bursts about 7 s after `DETAIL_T0` (Companion connect), and the Ups are the next 10.

**Symbols to read:**

| Symbol (main thread) | Means | rc11-class reference |
|---|---|---|
| `PaintShapeLayer.draw(in:)` → `GenericItem1<Coverage::Stroke<StrokeablePath>, Fill::Gradient>` → `argb32_shade_axial_RGB` | Card Depth rail CPU raster (S2/S1) | push 553–1393 ms; ~23 ms per move |
| `PaintShapeLayer.draw(in:)` → `GenericItem1<Coverage::Primitive, Fill::Gradient>` | sheen and full-screen scrims | push 161–435 ms |
| `ViewGraphDisplayLink.displayLinkTimer` → `ScrollViewCommitMutation.apply` | SwiftUI-driven anchor glide (S4) | — |
| `SDFLayer.update…`, `GlassContainer.Entry.shapeBounds`, `GlassAnimatableMaterialValue.updateValue` | Liquid Glass per frame (S6) | Classic Down 584 ms under the display link |
| `DetailTileFocusLift.body`, `CardArtworkFocusLift.body`, `EpisodeThumbCard.body`, `TrailerThumbCard.body`, `SeasonPosterCard.body`, `ArtworkColorStore.color(for:use:completion:)` | S1 per move | ~0 now (the cost is GPU) |
| `CardDepthOverlay.body`, `DetailCompactLogo.body`, `TitleLogoHeader.body` | S2 / S3 bodies | ~0 |
| `DetailView.body.getter` | page body | ≤ 3 ms per move |
| `EpisodeHoldMenuItems.body` (Wave 3) | FEAT-83 menus | must be 0 outside a hold |
| `HiddenTabBarFocusBlocker…apply`, `DetailPopGate.decide`, `ViewerInputClock.record` | rail / pop / input | ~0 |
| `_UIFocus*` | focus engine | ~150 ms per walk, same in Classic |

**Decision rule.** On a valid rc7 run, look at the Down window (rows on screen):
- GPU median ≲ 11 ms and offscreen ≲ 10 → the regression is GPU-side. Bisect on offscreen passes and GPU ms.
- GPU matches rc11, but push `PaintShapeLayer` ms is clearly lower → the tint re-raster (S1 iii) or more mounted cards.
- Both match → there is no code regression on this walk. Re-check Steven's rc7-era settings against today's (Card Depth coverage, poster-colour rail and ring) and his tvOS version.

## 7. Bisect order

0. **Knob A/B on the installed rc11-class `rel-app` (no build).** One Animation Hitches walk each, Cinematic, Steven's arguments plus:
   1. baseline ×2;
   2. `-debug.detailTileRingNoShadow YES` (S1 shadow);
   3. `-debug.detailNoTileRing YES` (S1, partial revert);
   4. `-debug.detailNoCompactLogo YES` (S3);
   5. `-debug.detailTopScrimStep YES -debug.detailEdgeEffectShown YES` (rc7's scrim and edge behaviour, S4);
   6. `-debug.homeNoCardDepth YES` (S2, all surfaces; Steven's own A/B);
   7. `-debug.detailScrollAB 2`, then `4` (S6).

   All seven are Release-readable (`DetailBug153Knobs`, `DetailDim`, `HomePerfKnobs`, `DetailScrollAB` sit outside `#if DEBUG`). Compare Down/Up GPU median/p90 and offscreen passes, and push `PaintShapeLayer` ms.
1. **rc7 (build 139), a valid run.** The baseline does not exist yet. Repeat it until the gate in §1 passes.
2. **rc8 `09b901c20` first.** It holds every rc7→rc11 change on the walk path in his config: BUG-177 (S1), FEAT-60 (S3), BUG-178 (S4), the teaser glass platter, and Batch C. It is also the build right after Steven's "smooth" verdict. rc9 touches Detail only through the deferred trailer mount (inert with trailers off) and the Search/Home wash. rc10 changes the same tiles (BUG-153 **cheaper** ring), restructures rows (neutral) and adds the Corner rail (off Detail). rc11 W1/W2 is off the walk path in his config.
   - **rc8 ≈ rc11:** bisect inside rc7..rc8 (8 commits, in order: `457a38d34`, `ddbd0541d`, `38bd6b932`, `60f041180`, `fc962bab1`, `0b690c731`, `8430362ff`, `ea09c4ea8`). Build **`38bd6b932`** first: it carries Batch C/FEAT-60 and not yet Batch G/BUG-177, so it splits S3 from S1. Then `60f041180` if needed. rc8 has no `detailNoTileRing` knob; the knob arrives in rc10.
   - **rc8 ≈ rc7:** build **rc10 `1bf7866aa`** (Batch M tile and row changes, Batch N/O Corner rail). If rc10 is bad, build **rc9 `2baa390f1`** to split Batch K from M/N/O. If rc10 is clean, the change is in rc11 W1/W2 (`623ffc31e`, `c7c49686c`); build `623ffc31e^`.
3. **Mechanics:** in the `~/Claude/Projects/NuvioMobile-wave3` clone (never a worktree): `git checkout <tag>`, device Release build into its own `iosApp/build/<tag>-app`, then check the branch out again. Delete the extra app dirs once the bisect is recorded.
4. **Metric per build:** Down/Up GPU median and p90, offscreen median and p90, push `PaintShapeLayer` ms, and walk hitch count. Never the whole-run total, which includes launch and Home and moves with timing.

## 8. Notes for the next writer of PLAN.md / the tracker

- Replace "BUG-206 CONFIRMED as a regression (5 vs 65)" with the §1 table: the rc7 run is void, and the rc11-class Cinematic walk is 21 hitches / 367 ms plus a 35-hitch push.
- The device `[BUG41]` `HitchCounter` (`-debug.detailScrollProbe YES`) counts **main-thread** vsync gaps. It cannot see these GPU-bound hitches; use Animation Hitches.
