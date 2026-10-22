# Wave 3c review r1, 2026-10-21

Read-only Opus review of `git diff 94a66f597..HEAD` in `NuvioMobile-wave3c` (branch `claude/wave3c`, tip `4751fcf80`, 14 commits, 25 files). Paths are relative to `iosApp/`. Spec: `docs/wave3c-critique-2026-10-21.md` (W3-11, W3-13…W3-19) and `docs/open-items-plan-2026-10-21.md` §4. `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor`. No build or test was run for this review.

**Verdict: FINDINGS (P1 0 / P2 3 / P3 6).** Every item matches the critique's spec, and Centre and the cards outside the depth overlay are render-identical. The three P2s sit in the new mechanisms, not the old paths:
- W3-17's glyph cue disappears with Steven's White accent.
- W3-13 variant 2 stretches its bitmaps on a card whose frame animates.
- W3-16's dwell can grow a row below the fold.

None blocks R1. P2-1 must be fixed before the owner wires `DetailView.swift`. P2-2 gates choosing variant 2.

## Findings

**P2-1: With the White accent, the W3-17 glyph cue makes active and inactive look the same, and Shuffle loses its on/off state.** `NuvioTV/Screens/Detail/DetailActiveGlyph.swift:39`, `:44-46`.
- At rest: active is `accent` and inactive is `Color.primary`. White's accent is `#F5F5F5` (`DesignSystem/Theme.swift:51`); `Color.primary` in the dark scheme is `#FFFFFF`. On the glass they are indistinguishable.
- When focused, both states return `inkOnPlatter`, so there is no cue under focus either.
- Watched and Library survive on their glyph swap (`checkmark.circle` → `.fill`, `plus` → `checkmark`, `DetailView.swift:2213`, `:2232`).
- Shuffle does not:
  - one `shuffle` symbol for both states (`DetailView.swift:2256-2258`);
  - icon-only in Cinematic (`actionLabelBody`, `:2567`), so "Shuffle On" is never drawn;
  - Steven runs White.
- The old `.tint(accent)` made the active glass bright, which was the cue. The critique required "Shuffle keeps its on/off cue". Nothing in the tests checks that the two states differ (`DetailActiveGlyphTests` only checks the table).
- Fix (before the owner wiring):
  - (a) In the wiring, give Shuffle a state glyph (`shuffle` / `shuffle.circle.fill`, or `.symbolVariant(.fill)` when enabled), so every one of the three carries its state in its shape. Add a test asserting that each button's (glyph, colour) pair differs between on and off for the White accent.
  - Or (b) in `color(active:focused:accent:)`, when the accent's contrast against `restingLabel` is below ~1.5:1, return `Theme.Palette.textSecondary` for inactive, so active stands out. Test it with `#F5F5F5`.
  - (a) is the smaller change and keeps Trailer and Start Over unchanged.

**P2-2: Variant 2 keys its bitmaps on the final layout size, so they stretch while a card's frame animates.** `NuvioTV/DesignSystem/CardDepthStyle.swift:605-628` (`cachedLayers`, `GeometryReader`).
- `GeometryReader` reports the post-animation size once. SwiftUI interpolates the drawn frame, and `Image(uiImage:).resizable()` stretches into it.
- The live rail (variants 0 and 1) re-strokes at every interpolated size, so its line width stays constant.
- The surface that animates its depth-carrying frame is the inline trailer tile:
  - `InlineTrailerCard.swift:2622-2626`: `nuvioCardDepth` on the art framed to `geometry.rect`;
  - the morph runs in `withAnimation(Self.morphAnimation)` (`:591`, `:916`).
- On the collapse the rail is visible (BUG-110, "the rail shows during the collapse dissolve"). The poster-size bitmap is then drawn into a frame up to ~1.8× wider: the side rails thicken by that ratio (Bold 3 pt → ~5.4 pt) and the corners elongate for the 0.35 s morph. The expand stretches the sheen's rounded top the other way.
- The agent's pixel diff (≤ 2/255) was static and cannot see this.
- Fix: in `rendered(_:)` (`:563-577`), take variant 1 (`liveLayers(p).drawingGroup()`) for a surface whose frame animates. The smallest version:
  - an `animatesSize: Bool = false` parameter on `nuvioCardDepth` → `CardDepthModifier` → `CardDepthOverlay`;
  - `InlineTrailerCard` passes `true`.
  - The signature stays source-compatible for `EpisodesSection.swift:512` and `DetailView.swift:3252`.
- Gate: a 30 fps capture of a trailer-tile collapse at `-debug.cardDepthRender 2` before variant 2 can win R1.

**P2-3: The F2 dwell grows the focused row after the engine has scrolled, so the bottom of a long release name can land below the fold.** `NuvioTV/Screens/StreamPickerView.swift:1576-1601` (`StreamRowDescription`).
- The focus engine reveals the row at its 3-line height. 0.5 s later `dwelled` flips and the row grows downward by up to several caption lines.
- Nothing re-reveals it: there is no `ScrollViewReader`, and UIKit does not scroll for a focused view's later resize.
- So on the bottom-most visible row, and always on the list's last row, the full name BUG-16 promised can sit off-screen. The user's only way to scroll further (Down) collapses it.
- Severity hangs on the engine's bottom margin, so confirm on the rig.
- Fix, if it reproduces:
  - wrap the picker's `ScrollView` (`:280`) in a `ScrollViewReader`;
  - give the row an `onExpanded` closure (not part of `==`, like the other closures) that the description calls after `dwelled = true`;
  - the closure runs `proxy.scrollTo(key, anchor: nil)` in `withAnimation(.easeOut(duration: 0.2))`. `anchor: nil` is a minimal reveal, so it moves only when the row overflows.
- Either way the dwell is a visible BUG-16 change: name it in the rc12 DM.

**P3-1: BUG-211 left stale comments behind, and one new comment names the wrong reader.**
- `NuvioTV/Screens/Home/HomeRowPreviews.swift:16` and `:51` say `releaseInfo` is "read by `HeroLogo`'s text fallback". `HeroLogo` reads `item.name`, the folder title (`HomeView.swift:7292`). `releaseInfo` is read by `StageCopy.make` (`StageCopy.swift:55`) for Stage's meta line and BUG-173's de-duplication. A reader who believes the comment and drops the field breaks Stage.
- Still describing the three-slot panel:
  - `HomeRowPreviews.swift:25-28` ("the hero-OFF panel's synopsis slot stays empty; the meta line … unchanged");
  - `HomeView.swift:6574-6575` (`longSynopsis`: "the Show Hero OFF panel draws a folder's description in the same column");
  - `HomeView.swift:6624-6628` (`splitsAsFolderHero`: "The panel renders a folder through the three-slot column");
  - `StageCopy.swift:34-36` ("Classic's hero-OFF panel … needs that line").
- The code is right: the panel keeps the title-hero gives, so the box height equals the old column's sum, and the frame and rows plan are unchanged.
- Fix: comments only. Say the panel draws the merged box, that it keeps the title-hero split only so its total height is unchanged, and that `releaseInfo` feeds Stage's meta line.

**P3-2: W3-19: the critique's three P3 notes are still open.** `NuvioTV/Screens/PlayerScreen.swift:167-175`.
- (1) A deadline cut inside the P7 RPU scan returns a non-nil `.missing` probe, so it never reaches this line.
- (2) `host=` now lands in rig console logs, under the staging rule: a self-hosted add-on, proxy or home-server host is private. Redact it before any `docs/` commit.
- (3) The line uses `print`. That reaches the rig's console stream but not a tester's sysdiagnose or Console.app, so "read off the log" holds only on our rig.
- Fix:
  - log `host=` only in DEBUG or under `-debug.playerRouterHosts`, else `host=<redacted>` with the TLD only;
  - switch both `[PlayerRouter]` probe lines to `NSLog` if Steven's own logs are meant to carry them;
  - optionally, a pure `probeOutcome(ms:capMs:)` with a test.

**P3-3: W3-15: the `debug.detailAnchorSeconds` knob does nothing until the owner wires `DetailView.swift`, and the doc says otherwise.** `NuvioTV/Screens/DetailRowAnchor.swift:146` ("what `DetailView` calls"); `DetailView.swift:1504`, `:1526`, `:1551`, `:1573` still use the fixed 0.3 s / 0.45 s.
- `:120`'s `defaults write com.nuvio.media.NuvioTV …` works on the simulator only. A tvOS device takes the launch argument, and a device build may carry the `com.youngchris29` bundle ID.
- Fix: "what `DetailView` calls once wired (owner, after wave3b)". Keep the launch-argument form as the rig recipe.

**P3-4: W3-13: R1 cannot fully prove which variant a walk measured.** `NuvioTV/Screens/Home/HomePerfKnobs.swift:24`.
- The `[HomePerfKnobs] cardDepthRender=` line prints only for 1 and 2. A walk at 0 and a walk with a mistyped argument (`-debug.cardDepthRender=2`, or one landing on the wrong process) read the same.
- test50 at 1 and 2 was run ad hoc; no committed leg passes the argument.
- Fix: log whenever `defaults.object(forKey:) != nil` (including `=0`), and on an unparsable value. Optionally parameterise test50 by an env var for the R1 window; it is deleted with the knob.

**P3-5: BUG-209: the probe's `exempt=` flag restates the verdict's predicate rather than reading the verdict.** `NuvioTV/Screens/BrowseComponents.swift:1595`.
- `target != 0 && focused && inBand && !holding` duplicates `slideHoldVerdict`'s rule (`:1036-1042`). If the rule changes, the device-pass oracle (`exempt=1`, `via=immediate`) can report a path that did not run.
- Fix: return it from the verdict (`case apply(exempt: Bool)`), or a `static func isExempt(...)` that both call.

**P3-6: W3-11: Corner's radius is a second literal 42.** `NuvioTV/DesignSystem/NavigationChrome.swift:125` vs `RailMetrics.cornerRadius` (`NavigationRail.swift:230`).
- The doc says "Centre's pill radius", but nothing ties the two (the other new chrome numbers were mirrored).
- Fix: `static let cornerRadius: CGFloat = NavigationChrome.cornerRadius` in `RailMetrics`. That keeps Centre's value, so Centre still renders the same.

## Against the spec, item by item

**W3-11 (D1).** Matches all seven critique points.
- Glass and mask:
  - share `cornerShape` (`UnevenRoundedRectangle(bottomTrailingRadius: 42)`) at `cornerGlassFrame`, origin (−8, −8);
  - are offset on the background and the mask only, never as padding on the column, so the `.focusSection()` is unchanged.
- Width depends only on `labels` (316 / 100 on screen); only the height follows `frameOpen`.
- The column sits at `bezelInset` whatever the style, so the Home cell is at (28, 60). No `offset` or `scaleEffect` on items.
- Rest stays the bare glyph: `glassOpacity` 0, label opacity `railOpen ? 1 : 0` (`NavigationRail.swift:917`), so the wider rest mask reveals no label.
- Rows below Home stay at `rowOpacity` 0, and the vertical mask range (−46…104 in column space) covers the same rows as before.
- The Hidden path and the r1 fixes are untouched (`cornerArmedAtRest`, `.identity` insertion).
- The Settings row hides on `railPosition == .centre`; the stored style is kept; nothing is keyed to that row's focus. No string change.
- One visible change for Edge users on Corner: the rest glyph moves from x 42 to 58. This is intended and asserted in Rail13b.

**W3-13.**
- (1) The structural `if` is gone; `railVisibility` is opacity with `.animation(nil, value:)`, applied identically in all three variants.
- (2) The rail strokes white, `.colorMultiply` sits on the rail only, the sheen is untouched, and the halo is white too (inert).
- (3) The knob is launch-latched, Release-readable and logged.
- `DebugAXIdentifier` sits on the root, outside every `drawingGroup`.
- The BUG-110 clamp still feeds width, stops and halo through `effectiveEdgeStrength`.
- The cache key carries size px, scale, shape kind (rounded radius ×100 + style, or circle), width, the three stop alphas, coverage and sheen. The bitmap is rendered from the key, so two cards sharing a key share pixels. `strokeBorder`'s inset path and the `destinationIn` coverage band reproduce the live layers.
- An unkeyable shape or a revived halo falls back to variant 1.
- The signature is unchanged for `EpisodesSection.swift:512` and `DetailView.swift:3252`. `StripPager.swift` is not touched. `CardDepthRailStyleTests` is unchanged.
- Not yet proven: that fixes (1) and (2) actually avoid a CPU re-raster in variant 0. SwiftUI may cull an opacity-0 subtree or bake a multiply into the drawn content. R1's Time Profiler decides (device checks below).

**W3-14 BUG-209.**
- The 0-target snap is still checked first, and its tests cover all eight combinations.
- `.track` applies only to a focused row with an in-band target and no running hold. rc14's departing-row guard and beta.18's double-ease guard come out as the matrix in `PinnedRowSlideHoldTests`.
- `slideInBand` uses the lifted clearance + 2, the corrector's own low edge.
- The focus mirror is the live `tracking.isFocused` (`onChange` at `:1427`), not the captured value.
- A nudge after a tracked landing would also be tracked (still moving, still in band), not eased twice.
- Up keeps the two-step by design (`holding`).
- The probe is Release-readable; the write is unanimated via `disablesAnimations`, and Reduce Motion is handled.

**W3-14 BUG-211** (owner commit). One token, as specified.
- The box height is the exact sum the column used. `longSynopsis` and `splitsAsFolderHero` still treat the panel folder as a title hero, which keeps that sum unchanged.
- Description line only with Show Catalog Details. Logo capped at 160. No test touches the panel's folder text. Comments: P3-1.

**W3-15.**
- `anchorDuration` = clamp(0.3 × |travel| / 380, 0.3, 0.65), ≈0.605 s at 766 pt. NaN travel takes the floor.
- `verifyDelay(for:)` = max(0.45, d + 0.1). The override is clamped to ≤ 2 s.
- Every new member is `nonisolated`, and `verifyDelay` became `nonisolated static let` so the pure function can read it.
- Not wired (owner, after wave3b): P3-3.

**W3-16.** F1–F4 as specified.
- The row reads no picker state.
- `==` covers the spinner, the rejected flag, the badge settings (through `display` and the baked size/top/column fields), the Instant-suffix title, and the players with their default.
- `.focused($focusedRow, equals: key)` stays at the call site; the picker body no longer reads `focusedRow` outside closures, so a focus move re-runs no picker body and no row body.
- Initial focus (`:460-465`), the collapse retarget (`:654`) and `focusListAfterAutoPlay` (`:1218-1227`) still go through the parent binding and the unchanged `rowKeys`.
- Closures carry only the key and look the stream up live (`liveStream(forRowKey:)`). Every other capture is the picker's `@State`/`@StateObject`/`@AppStorage`, all live through a stale copy, or launch-time `let`s, which the existing `@StateObject` already assumes are stable.
- `apply()`:
  - reuses a group only when streams, name and `display` are equal;
  - rebuilds on a badge-settings or Instant-suffix change (`reapplyIfDisplayChanged` from both watchers);
  - guards every `@Published` write.
- `.onChange(of: model.groups.map(\.id))` is unaffected (equal values never fired it).
- Equivalences checked against the old `streamRow`: `hasBadgeRow` and `showSize`, description and logo nil-on-empty, the rejected test, and the YouTube flag.

**W3-17.** The modifier, the pure table and the tests are as specified; `DetailView.swift` is not touched. `restingLabel = Color.primary` is `Theme.Palette.textPrimary` (`Theme.swift:133`), so the doc and the code agree. Finding: P2-1.

**W3-18.** `.hidden()`, not deleted. The layer is already `.accessibilityHidden(true)`. The key is still used by the real field's prompt. UI tests only strip that string as a field value (`NuvioTVUITests.swift:672`, `BatchASearchPerfUITests.swift:143`).

**W3-19.** A nil probe always routes to mpv (`PlayerEngineRouter.decide`: "probe unavailable"), so "→ mpv" is true. The 50 ms slack is fine. Notes: P3-2.

## Verified fine (cross-cutting)

- **Centre rail.**
  - `pill` is untouched apart from `pillGlass` → `railGlass(in: pillShape)`: the same two branches, the same `AnyShape`, the same tint.
  - The `RailMetrics` mirrors carry identical values (300, 12, 60).
  - `pillLeading(style)` still drives Centre.
- **Cards outside the overlay.** No card file changed. `PosterCard`'s inset is reserved whether or not the card is focused ("Do NOT collapse the band on focus"), so variant 2's `GeometryReader` never re-keys on focus for posters. BUG-91's inner radius reaches the cache key unchanged.
- **test50 / test60.** test50's identifier is on the root. test60's 80 is right: `railTopAlpha(0.56)` = 0.80. It had been stale since rc14 and is now fixed.
- **Equatable rows and stale closures.** See W3-16. `StreamRowView.==` is `nonisolated` over a `nonisolated` value model, so there is no isolated-conformance trap under default MainActor isolation.
- **Badge cache.**
  - `nonisolated(unsafe) static let` NSCache: NSCache is thread-safe. It is written only from `BadgeImageCache` (an actor) and peeked from main, and is unbounded exactly as the actor's private cache was.
  - The seeded `State(initialValue:)` only acts on first install, which is the case F3 targets.
  - The offset-keyed chip `ForEach` keeping a stale image for one frame on a badge change predates this diff.
- **MainActor / nonisolated.** New pure helpers are `nonisolated`:
  - `NavigationChrome`, `SlideHoldVerdict` / `slideInBand`, `DetailRowAnchor`'s glide members;
  - `CardDepthStyle`'s identity helpers and `CardDepthRGBA`;
  - `CardDepthRasterCache` (`@unchecked Sendable` over NSCache), `HomePerfKnobs`;
  - `StreamRowDisplay`/`StreamRowPlayer`/`StreamRowModel`/`StreamBadgeInfo`.
  - Kotlin-touching builders (`StreamRowModel.make`, `.title`) are `@MainActor`.
- **Release-readability.** `-debug.cardDepthRender`, `debug.detailAnchorSeconds`, `-debug.homeScrollProbe` (BUG-209's lines) and the `[PlayerRouter]` lines are all outside `#if DEBUG`. `RAIL_SHOT_DIR` lives in the UI-test runner only.
- **Memory.**
  - The raster cache is bounded at 64 entries / 48 MB, with cost = px × 4 at 8-bit sRGB (`preferredRange = .standard`). A Home plus Detail needs roughly 20 keys.
  - Shared `UIImage`s share one CA texture.
  - A miss renders on the main thread once per key (a new card family or size), not per card.
  - `drawingGroup`'s per-card texture (variant 1) is the critique's jetsam watch item (device check).
- **Localization.** No new keys.
  - `"%@ - %@ Instant"` only moved file (`StreamsViewModel.swift`).
  - "Failed recently", "Open in %@", "Rail Style" and "Search movies & shows" are unchanged; `Text(verbatim: "YouTube")` stays verbatim.
  - No `.xcstrings` change, and no pbxproj change: synchronized groups pick up the two new source files.

## Tests

- **New and meaningful:**
  - `NavigationChromeTests`: `testCornerPillGeometry` rewritten to flush; three `cornerGlassFrame` cases;
  - Rail12/12b/13b/13c: flush origin, fixed width, the Home cell unmoved; Hidden now in both label modes;
  - `HomePerfKnobsTests` (+5);
  - `CardDepthRasterCacheTests` (22): key distinctness per width, alpha, radius, shape, size, scale and coverage; rail and sheen pixels; the white × tint identity against SwiftUI's own `.opacity` resolution;
  - `PinnedRowSlideHoldTests`: the full matrix, a running hold kept, Steven's Down reading by reading;
  - `DetailRowAnchorTests`: floor, ≈0.6 s, cap, monotonic, NaN, verify ≥ d + slack, knob parse;
  - `StreamRowModelTests`: `make`, every `==` field, apply reuse, republish skipping, key stability;
  - `DetailActiveGlyphTests`.
- **Stale, fixed:** test60's Bold 90 → 80. Nothing else references the removed `rowTitle`/`streamRow`/`cornerPillOrigin`.
- **Gaps:**
  - nothing asserts that W3-17's on and off differ for the White accent (P2-1);
  - no unit or UI test covers `liveStream(forRowKey:)` or the dwell (device);
  - BUG-211 is a sim shot only;
  - test50 at variants 1 and 2 is uncommitted (P3-4).
- **Gate evidence:** the plan records green suites for C1 and C2a. Nothing is recorded for the C2b tip `4751fcf80` (W3-16/17/18). The full gate and the picker's UI legs are owed on the tip.

**Verdict: FINDINGS: P1 0 / P2 3 / P3 6.** P2-1 must be fixed before the `DetailView.swift` wiring. P2-2 gates choosing variant 2 in R1. P2-3 is confirmed or closed on the rig.

## Device checks the owner must run

All in Test 2, in Steven's config (rc11 video + rc10 table: Rounded + system font, White accent, ring on with poster colour, depth Subtle/Soft/Full with poster colour, Classic Home, Cinematic Detail), Release unless noted. Run `scripts/device/ready.sh` first.

1. **Gate on the tip `4751fcf80`.** Kotlin + sim Debug/Release + NuvioTVTests + UI legs: Rail08/12/12b/13/13b/13c, test50 (at 0, 1 and 2 by hand), test60, the stream-picker legs (`NuvioTVUITests.swift` ~8872, `FirstPlayAutoPlay` 619/638), HeroFolderSwapTests test54/55.
2. **W3-11 Corner.**
   - Labels Shown and Icons Only × Always Visible and Hidden: rest, mid-unroll (30 fps), open; over a dark hero and a bright one.
   - No Liquid Glass rim visible on the top or left screen edge (is 8 pt of bleed enough?), with the TV's overscan on.
   - No flicker during the unroll; nothing moves sideways.
   - Focus lands on Settings or Profile when the rail opens on those tabs.
   - An Edge-stored profile shows the rest glyph at x 58.
   - The Rail Style row disappears or appears as Position flips.
3. **W3-13 R1.**
   - `walk-home.sh` on Stage and on Classic, two runs each at `-debug.cardDepthRender` 0, 1 and 2, plus depth off; also a build of `5f0e7c1a0` (or rc11) as the true before, since knob 0 already carries fixes (1) and (2). `compare.py 14 50`.
   - Time Profiler, per finalist and at 0:
     - `argb32_shade_axial_RGB` during a Left/Right-only walk along a row: does opacity 0 really keep the raster?
     - the same symbol on a fresh row's poster-colour arrival: is the multiply really free?
   - Pixel diff of a Subtle/Full tinted rail and a Bold/Top white rail against the pre-W3-13 build.
   - Memory footprint at variant 1 with Home fully mounted.
   - At 2: a 30 fps inline trailer tile expand and collapse (P2-2).
   - Focus-out look: the rail now returns at full opacity at once.
4. **W3-14 BUG-209.**
   - `-debug.homeScrollProbe YES`, Classic + Hide Titles, Down ×10: runs of `slide apply … via=immediate anim=track exempt=1` and no `via=settle` for the focused row.
   - 30 fps frames show one landing.
   - Up still shows the old two-step (expected).
   - No title painted across a departing row.
5. **BUG-211.** The Classic panel on a folder tile with Show Catalog Details off and on: the wordmark centred in the box, capped at 160; a folder with no logo shows its name. Stage's folder meta line is unchanged.
6. **W3-15**, after the owner wiring:
   - the press-1 glide ≈0.6 s with no kink at the verify;
   - a double Down under 0.4 s mid-glide;
   - Up into the hero;
   - the `DetailScrollMotion` oracle;
   - an A/B with `-debug.detailAnchorSeconds 0.3`.
7. **W3-16**, stub add-on with 40–64 rows.
   - Animation Hitches over 30× Down and 30× Up at 0.35 s, before and after.
   - Focus behaviour:
     - initial focus on the first row (single group) and on the header (several groups);
     - the collapse retarget;
     - focus after the auto-play overlay lifts;
     - the long-press menu with an external player installed (`.focused` now wraps the context-menu modifier).
   - The resolve spinner and "Failed recently" land on the right row.
   - Badge images show on the first frame.
   - The dwell on the bottom-most visible row and on the last row: is the full name on screen (P2-3)?
8. **W3-17**, after the P2-1 fix and the owner wiring: White accent; Watched, Library and Shuffle on and off, at rest and focused, icon-only (Cinematic) and text labels; a screenshot burst after Right confirms the lag is gone.
9. **W3-18.** Cold launch → rail → Search at 60 fps: the magnifier alone until the field mounts (~+1.1 s), with no jump at the hand-off.
10. **W3-19.** Steven's title on the rig, read the one `[PlayerRouter] probe cap hit|probe failed early` line, and redact `host=` before any log is staged.
