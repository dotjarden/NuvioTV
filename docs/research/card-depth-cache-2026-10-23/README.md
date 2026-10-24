# Card Depth raster cache revived without BUG-221 (2026-10-23)

Clone `~/Claude/Projects/NuvioMobile-depth`, branch `claude/card-depth-cache`, base `61fd98c1c`
(tvos-shared-extraction), tip **`888961236`**, 3 commits, not pushed, not landed.

- `8ba3ccee9` harness: the folder legs (test106 / test107 ×2 / test108) launch with
  `-debug.cardDepthOn YES`; new `CardDepthCrashProbeUITests` (regression leg + opt-in walk).
- `9adbb2993` rendering: `CardDepthBitmapLayers`, `CardDepthRasterCache.LayerKeys` / `placeholder`
  / `layerImage(for:)`, 6 new unit tests, comments.
- `888961236` review P3s (review of `9adbb2993`: CLEAN with four P3s):
  - P3-1: narrower root-cause wording (§1).
  - P3-2: the true bitmap cost, written in the code.
  - P3-3: a probe pass with Depth Takes Poster Color on.
  - P3-4: test50 forces Card Depth on.

No knob. The live layers stay only where they were already the fallback (an animating frame,
`animatesSize` on the inline trailer tile; a shape the cache can't key; a revived halo).

## 1. Root cause

The parked rendering was a `GeometryReader` in Card Depth's overlay on the card artwork, and its
content read `proxy.size`. With it, Home trapped about 1.5 s after the profile pick, during the
first publishes. A row's `LazyHStack` measured a card (`LazyHVStack.flexibleMinorSize` →
`_AspectRatioLayout.spaceOffered` → `LayoutProxy.size`). That measurement updated a
`DynamicLayoutComputer` under the card, and its item removal asserted:
`DynamicContainerInfo.tryRemovingItem ← updateItems ← updateValue`, EXC_BREAKPOINT, with no app
frames. The fresh traces (`~/Library/Logs/DiagnosticReports/{,Retired/}NuvioTV-2026-10-23-18*.ips`,
24 files) match the 2026-10-22 box and UI-leg traces frame for frame. The 10-22 `.ips` files have
already rotated out of `Retired/`.

The bitmaps were not the cause. Bisect on FA87 (Debug, Card Depth forced on; each run is 2 Stage
+ 2 Classic launches with the folder seed, then a 20 s watch after the profile pick):

| # | Overlay content | Crashes |
|---|---|---|
| 0 | live layers (the tip) | 0/4, 0/4 |
| 1 | the parked `cachedLayers` (GR, `proxy.size`, bitmaps) | **4/4, 4/4** |
| 2 | `GeometryReader { _ in liveLayers }` (proxy ignored) | 0/4, 0/4 |
| 3 | live layers + `.overlay(GeometryReader { _ in Color.clear })` | 0/4 |
| 5 | GR, `Image(uiImage: UIImage())` framed by `proxy.size` | **4/4** |
| 11 | GR, one shared static `UIImage` framed by `proxy.size` | **4/4** |
| 8 | GR, `Color.clear` framed by `proxy.size` (no image at all) | **4/4** |
| 7 | GR, live layers + bitmaps rendered from `proxy.size` and discarded | **4/4** |
| 10 | GR `{ _ in }`, `UIImage()` made + live layers | 0/4 |
| 4 | **no GR: size from `onGeometryChange` → `@State`, bitmaps** (landed shape) | 0/4, 0/4 |

Within this overlay, the crash follows one thing: a `GeometryReader` whose content reads
`proxy.size`. Which view the content draws doesn't matter (8 has none). UIKit image work doesn't
matter (10). Sub-pixel bitmap sizes don't matter (8 has no bitmap). The 10-22 "structure-stable"
fix only made the ZStack's `if`s independent of the cache's answer. It left the `proxy.size`
dependency in place, so it still crashed.

A size-reading `GeometryReader` is not enough on its own, though (review P3-1). Three others frame
content by `geo.size` inside the same `LazyHStack` cards and have never crashed:

- `ShimmerView` (`CachedAsyncImage.swift` ~1464), the loading shimmer.
- `PosterCard`'s progress bar (`PosterCard.swift` ~1469).
- `PosterCard`'s watch-badge bar (`PosterCard.swift` ~1645).

What sets Card Depth's reader apart is where it sits: in an overlay on the artwork under
`_AspectRatioLayout`, probably while `CachedAsyncImage` swaps its shimmer for the image. So the
fix is proven by the bisect (variant 4 against 1, 5, 7, 8 and 11). It is not a full account of
SwiftUI's mechanism.

## 2. The rendering as landed

1. `CardDepthOverlay.rendered`: `!animatesSize && haloSpread == 0 && ShapeKind(shape) != nil` →
   `CardDepthBitmapLayers`, otherwise `liveLayers` (with no `drawingGroup`; this branch is fixed per
   call site).
2. `CardDepthBitmapLayers` is always the same `ZStack` of two `.resizable()` `Image`s: sheen, then
   rail. There is no `if`, no `GeometryReader` and no `.id`.
3. Its size is `@State`, written by `.onGeometryChange(for: CGSize.self)`. That runs after layout,
   so nothing in the overlay depends on layout while a layout pass runs.
4. `CardDepthRasterCache.LayerKeys(size:scale:shape:sheen:edge:…)` builds the two keys from that
   size and `displayScale`. A key is nil for no size yet, strength 0 or a zero rail width.
5. `layerImage(for:)` is never nil. It returns the cached bitmap, rendered once per key on the
   first ask, or `placeholder` (one clear 1 × 1 pixel) for a nil or empty key.
6. The rail is white × `.colorMultiply(railColor(tint))` with `.opacity(railSuppressed ? 0 : 1)`
   and `.animation(nil)`. That's the W3-13 tint and focus rules, unchanged.
7. Each bitmap is the overlay's box rounded to whole pixels, so the resizable stretch is under
   1 px (unit-tested).
8. For one update after a card mounts, both layers show the placeholder (size `.zero`).
9. `DebugAXIdentifier("card_depth_rail")` stays on the overlay root, and the layers are
   `accessibilityHidden`.
10. Removed: `cachedLayers`, `bitmap(_:size:)`, the overlay's `displayScale`.

## 3. Sim repro, before / after (FA87, Debug)

| Build | CardDepthCrashProbe launches | Folder legs (depth on) |
|---|---|---|
| Parked cache re-enabled (variant 1) | **8 crashes / 8 launches** (two runs) | not run (the probe already traps 1.5 s after the pick) |
| `9adbb2993` | **0 / 12** (3 Stage + 3 Classic, twice) | **8 / 8 passed** (4 legs × 2 runs, after an earlier 8 / 8 on the pre-commit build) |
| `888961236` | **0 / 6** (2 Stage + 2 Classic, plus one per layout with `-depth_rail_poster_color 1`) | not re-run (only comments and test files changed) |

`test60DepthEdgeLevelsAreDistinguishable` passed 2/2 on the bitmaps, so the three levels still
render distinctly. `test50DepthRailHugsArtworkInStillMode` now launches with
`-debug.cardDepthOn YES`, so it measures the bitmap rail on any fixture. It **passed** on
`888961236`:

- still mode: card (388, 526.5, 220 × 330), rail = artwork (392, 530.5, 212 × 322), inset 4 pt.
- default: rail = card (388, 526.5, 220 × 330).

**Bitmap memory** (review P3-2): pixels × 4 bytes. A 220 × 330 poster at 2x is about 1.16 MB per
layer, an episode tile about 1.6 MB, and a typical Home holds about 10–15 MB. The cache's
64-entry / 48 MB bounds cover that.

## 4. Hitches

The simulator can't record Animation Hitches (`xctrace`: "Hitches is not supported on this
platform"), so the R1 device walk method doesn't run on the sim. Proxy measurement: Time Profiler
(all processes) during the opt-in `testDepthWalkClassicHome` leg (Classic Home, depth on, 20 Down /
20 Up at 0.6 s), NuvioTV main-thread samples at 1 ms inside the walk window:

| Rendering | Main samples | `PaintShapeLayer` (live rail/sheen raster) | `UIGraphicsImageRenderer` (whole run) |
|---|---|---|---|
| live layers, run 1 / 2 | 3272 / 3122 | **59 / 58** | 0 / 0 |
| bitmaps, run 1 / 2 | 3361 / 3189 | **0 / 0** | 8 / 6 (first key per size, before the walk) |

The per-mount gradient raster disappears from the main thread. On the Mac the total main-thread
time doesn't move measurably, because rasterising is cheap there. The device number to compare
against is R1: 95 / 89 hitches live, 85 for the cache, 46–72 with depth off.

## 5. Gates

On `888961236`:

- NuvioTVTests **2346, 0 failures, 5 skipped**.
- Release sim build **succeeded**.
- UI: CardDepthCrashProbe 6/6 alive (poster-colour passes included), test50 **passed**.

On `9adbb2993`:

- NuvioTVTests **2346, 0 failures, 5 skipped** (`CardDepthRasterCacheTests` 27/27, 6 new).
- Release sim build (FA87 id) **succeeded**; Debug sim and UI targets build.
- UI: CardDepthCrashProbe 6/6 alive, folder legs 4/4 ×2, test60 1/1.
- Kotlin `:shared:jvmTest :shared:tvosSimulatorArm64Test :composeApp:iosSimulatorArm64Test` **BUILD SUCCESSFUL** (no Kotlin was touched).

## 6. Device script (coordinator; Test 2, never "Chris")

1. `scripts/device/ready.sh --walk`, then install the Debug device build of `888961236`, profile
   **Test 2**, Card Depth ON in Steven's config (Full, Depth Takes Poster Color on).
2. Do the original 3 s repro first: **Classic** Home, cold launch, pick Test 2, watch 30 s with a
   Continue Watching update (play a title for ~1 min since the last launch, exit, relaunch). Then
   **Stage**, the same way. Pass = no exit; `devicectl` lists no new `NuvioTV-*.ips`.
3. Look: rails tinted per poster, the Top coverage arc and Full closed stroke match the rc11 look,
   no rail on the focused card, and it returns on unfocus with no flash. Detail: the cast circle
   rail, More Like This, Season / Episode tiles. Inline trailer tile: live layers through the morph.
4. Change Edge strength Subtle → Bold in Settings, go back to Home. Rails update with no crash.
5. Optional, Release: `walks.sh` R1 Classic 20 Down / 20 Up, two runs. Expect about 85 hitches
   against 95 / 89 live.
6. Teardown: Test 2 back in Steven's config, no payloads left, console logs unstaged.

## Not done / open

- Device verification (above). The 10-22 note said the crash "never reproduced in Release on the
  sim"; this repro and the fix are Debug-sim. Release was built but not run in a UI leg.
