# Wave 3c review r2, 2026-10-21

Read-only Opus review in `NuvioMobile-wave3c` (branch `claude/wave3c`, tip `a1e766d8a`). Scope: the r1 fix diff `git diff 4751fcf80..HEAD` (9 fix commits + the owner's `a1e766d8a`, 15 files) against `docs/wave3c-review-r1-2026-10-21.md`, then the whole branch `94a66f597..HEAD` re-checked for anything the fixes broke. Spec: `docs/wave3c-critique-2026-10-21.md`. `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor`. Paths are relative to `iosApp/`. No build or test was run for this review; the plan records "141 tests green" for the fix pass (`docs/open-items-plan-2026-10-21.md:100`).

**Verdict: FINDINGS (P1 0 / P2 0 / P3 3).** All nine r1 findings are closed: the three P2s correctly and completely, the six P3s as asked. The three new P3s:
- the White dim greys whole labels;
- test gaps on the new pure helpers;
- a duplicated light-accent threshold.

None blocks R1 or the merge. Two of the three P2 fixes are inert in what ships today:
- P2-1 does nothing until the owner wires `DetailView.swift`.
- P2-2 changes only `-debug.cardDepthRender 2`.

Only P2-3 changes shipping behaviour (the picker).

## r1 findings: status

**P2-1 (White accent hides the on/off cue): CLOSED.** `NuvioTV/Screens/Detail/DetailActiveGlyph.swift:67-110`.
- Colour half:
  - `color()` (`:84-88`) returns `Color.secondary` for inactive at rest when `isLight(accent)`.
  - `isLight` (`:98-110`) is Rec. 709 luminance over `accent.resolve(in: EnvironmentValues())` components, `>= 0.8`.
  - Focus still wins outright, and active at rest is still the accent.
  - Among the seven swatches only White crosses (0.96). The rest are ≤ 0.60 (Amber 0.60, Ocean 0.47).
- Scale check: `testOnlyTheWhiteAccentIsLight` matches `Theme.Palette.luminance(fromHexString:)` to 0.005 for F5F5F5, 1E88E5 and FB8C00. That also proves `Color.Resolved.red` is gamma-encoded here: a linear read would put White at 0.91 and fail the test's 0.01 accuracy.
- Shape half:
  - `shuffleOnGlyph = "shuffle.circle.fill"` / `shuffleOffGlyph = "shuffle"` through `glyph(active:onGlyph:offGlyph:)`.
  - `shuffle.circle.fill` ships from tvOS 14.2 (CoreGlyphs `name_availability.plist`: `2020.1`); the deployment target is 26.0. `testShuffleGlyphsExistOnTvOS` asserts both via `UIImage(systemName:)`.
- The owner snippet in the doc (`:46-55`) matches `DetailView.swift:2255-2260`'s current `actionLabel(...).font(Theme.Font.meta)` shape inside `actionButtonPadding`.
- The tests r1 asked for are present:
  - on/off contrast ≥ 1.5 at rest for White and Ocean (pre-fix White pair < 1.5);
  - (glyph, colour) differs for Watched, Library and Shuffle × focused/rest × White/Ocean.
- Still unwired (owner, after wave3b): `.tint` at `DetailView.swift:2220`, `:2238`, `:2265`; `systemImage: "shuffle"` at `:2258`. See new P3-1 before wiring.

**P2-2 (variant 2 stretches on an animating frame): CLOSED.**
- `animatesSize: Bool = false` threads `nuvioCardDepth` (`DesignSystem/CardDepthStyle.swift:452`) → `CardDepthModifier` (`:465`, `:479`) → `CardDepthOverlay` (`:534`).
- `rendered` (`:588`) sends it to `liveLayers(p).drawingGroup()`, the same fallback as halo and unkeyable shapes.
- Only `Screens/InlineTrailerCard.swift:2627-2629` passes `true`.
- I re-swept the other ten call sites for animated frames:
  - all draw into fixed `.frame`s: `PosterCard.swift:1127/1385`, `SagaCard.swift:143`, `EpisodesSection.swift:512/672`, `TrailerThumbnail.swift:114`, `BrowseComponents.swift:5925`, `SearchResultViews.swift:290`, `DetailView.swift:3252`;
  - `CollectionsUI.swift:850`'s ring band is a `.scaleEffect` after the overlay, a render transform both variants share.
- The signature stays source-compatible. Variants 0 and 1 are untouched.

**P2-3 (dwell grows the row below the fold): CLOSED in code; the rig confirms.** `Screens/StreamPickerView.swift:283`, `:705-710`, `:1601-1633`.
- `ScrollViewReader` wraps the `ScrollView`. `git diff -w` shows the re-indent is otherwise byte-identical, and every modifier that sat on the `ScrollView` (frame, background, overlays, alert, `onChange`, `onAppear`) now sits on the transparent reader with the same effect.
- `onExpanded` is a `var` with a default `{}`, outside `==` (`:1509-1515`). `StreamRowModelTests:202-205` still compiles. `StreamRowDescription` is private, and its only constructor is `:1537`.
- `.id(key)`:
  - is the same value as the `ForEach` identity (`StreamRowModel.id { key }`, `StreamsViewModel.swift:449`), so there is no identity change and no state reset;
  - keys are unique across groups (`rowKeys`: `"\(groupId)#…"` + `~n`, `StreamsViewModel.swift:120-128`);
  - headers, the test row and the failover key carry no `.id`, so there is no collision.
- Stale closures:
  - the closure captures only `key` and the reader's `ScrollViewProxy`, both stable for the row's life;
  - an `.equatable()` skip keeps an older closure that does the same thing;
  - the `.task` closure captures the `self` of the body that restarted it.
- Cancellation:
  - `.task(id: focused)`: focus loss restarts the task, which cancels the old one, so both `guard !Task.isCancelled` checks (after the dwell, after `revealDelay`) stop a departed row;
  - lazy unload, `.disabled(loadingCoverVisible)` and `onDisappear` all cancel it too.
- `anchor: nil` is a minimal reveal: a row that grew without overflowing, or a description that fits in 3 lines, does not scroll.
- Unanimated, unlike r1's `easeOut(0.2)` suggestion. That is a defensible choice (the grow is unanimated too); see device check 3.

**P3-1 (BUG-211 stale comments): CLOSED.**
- `HomeRowPreviews.swift:16-31`, `:51-57`: `releaseInfo` feeds `StageCopy.make` → `classicMeta`, plus BUG-173's de-dup.
- `StageCopy.swift:19-22`, `:35-40`.
- `HomeView.swift:6574-6576`, `:6626-6628` (owner).
- Each claim was checked against code: `HomeHeroForeground.nuvioLayout`/`classicLayout` (`HomeView.swift:6843-6900`) take `folderBox` for a collection hero, so `metaLine` (`:6988`) is never drawn for a folder. The `longSynopsis` guard `isCollectionHero && showsCTA` is unchanged.

**P3-2 (W3-19 notes): CLOSED.**
- P7 scan: `MediaProbe.swift:194-196` logs `[PlayerRouter] probe cap hit in the P7 RPU scan after … reads (… video packets) → elKind missing → mpv` when `deadline.expired`. `.missing` routes to mpv (`PlayerEngineRouter.swift:88-89`). It carries no host and no title. `grep 'probe cap hit'` catches both forms.
- Redaction: `PlayerRouterLog` (`PlayerScreen.swift:187-218`).
  - Release prints `<redacted>.<tld>`.
  - It prints `<redacted>` for IPv4, IPv6 (`:` test; `URL.host` drops the brackets), a dotless name, or a trailing dot.
  - `-debug.playerRouterHosts YES` reveals the host. It is launch-latched and Release-readable (`bool(forKey:)` reads the `YES` string).
- DEBUG is unchanged: `revealsHosts` is `true`, so the full host prints. The only difference is that an empty host now prints `-` instead of nothing.
- The routing line (`:180`) carries title and reason only.
- `print` was kept on purpose, and the comment says why.
- The rig gets what it needs: a Release walk passes the flag when the host matters, and a Debug walk always has it. See owner note 9 on staging.

**P3-3 (DetailRowAnchor doc): CLOSED.** `DetailRowAnchor.swift:119-125`, `:149-151`. It says "not yet called". The launch argument is the device recipe, and `defaults write` is sim-only.

**P3-4 (knob log at 0): CLOSED.** `HomePerfKnobs.swift:21-29`, `:56-66`.
- The line logs whenever the key exists, 0 included.
- An unclean raw value is flagged, with the variant actually resolved:
  - `YES` → 0 flagged; `5` → 0 flagged; `2.5` → 2 flagged;
  - an NSNumber from `defaults write -int` is clean.
- It still prints only when a depth overlay first renders (the static is first read in `CardDepthOverlay.rendered`), so a depth-off walk logs nothing. That is expected, and worth knowing when reading R1 logs.

**P3-5 (`exempt=` restated the rule): CLOSED.** `BrowseComponents.swift:1044-1062`, `:1576-1616`.
- `slideHoldDecision` returns `exempt: true` only from the focused in-band branch. `slideHoldVerdict` is its `.verdict`, so the existing matrix tests cover it unchanged.
- `.track` previously passed a literal `true`; that branch only returns from the exempt path, so it is equivalent.
- `.apply`'s old predicate (`target != 0 && focused && inBand && !holding`) implies the exempt branch, so it is equivalent too.
- `exempt` feeds only the probe line (`:1704`); there is no behaviour change.

**P3-6 (second literal 42): CLOSED.**
- One literal: `NavigationChrome.pillRadius = 42` (`NavigationChrome.swift:157`).
- Two readers: `NavigationChrome.cornerRadius` (`:126`) and `RailMetrics.cornerRadius` (`NavigationRail.swift:231`).
- Same values, so Centre and Corner render the same. `NavigationChromeTests:314` still pins 42.

## New findings

**P3-1: with White, the colour half greys the whole label, so on a default Detail page three of the five secondaries look disabled.** `NuvioTV/Screens/Detail/DetailActiveGlyph.swift:84-88`, `:67`; doc `:45-46` ("colours everything in the label").
- In Classic's text labels, "Mark Watched", "Add to Library" and "Shuffle" all turn `Color.secondary`, while Trailer, Start Over and Play stay primary.
- Unwatched, not saved, shuffle off is the common state, and Steven runs White. On tvOS a dimmed label is the disabled look.
- r1 offered (a) the glyph pair or (b) the dim. Both landed. Since (a) now carries state in shape for all three, (b) only adds at-rest colour contrast.
- Fix (owner, decide on the box when wiring):
  - keep it if it reads as on/off;
  - if it reads as disabled, either confine the dim to the glyph (a `LabelStyle` that applies `.detailActiveGlyph` to `configuration.icon` and leaves `configuration.title` primary at rest);
  - or drop it (`return active ? accent : restingLabel`; delete `testInactiveAtRestBesideALightAccentIsTheSecondaryLabelColour` and the White half of `testOnAndOffDifferAtRestForWhiteAndOcean`). The glyph test still passes.

**P3-2: the new pure helpers have no tests, and one of them is the privacy guard.**
- `PlayerRouterLog.host` (`PlayerScreen.swift:208-217`), in `PlayerEngineRouterTests`:
  - `https://a.b.example.com/x` → `<redacted>.com`;
  - `http://192.168.1.10:8080/` → `<redacted>`;
  - `http://[fe80::1]/` → `<redacted>`;
  - `http://nas/` → `<redacted>`;
  - `http://example.com./` → `<redacted>`;
  - `reveal: true` → the full host;
  - a host-less URL → `-`.
- `PlayerRouterLog.probeOutcome` at 3949 / 3950 / 4000 with cap 4000.
- `HomePerfKnobs.cardDepthRenderLogLine` (`HomePerfKnobs.swift:60`), on the suite's `UserDefaults(suiteName:)`:
  - absent → nil;
  - `"0"` → `cardDepthRender=0` with no flag; `"2"` clean;
  - `"YES"`, `"5"`, `"2.5"` flagged.
- `slideHoldDecision(...).exempt` (`BrowseComponents.swift:1051`): loop the existing `PinnedRowSlideHoldTests` matrix and assert `exempt == (target != 0 && focused && inBand && !holding)`.
- `DetailActiveGlyphTests.swift:105-109` hard-codes Watched/Library's glyph names, so nothing ties them to `DetailView.swift:2213`/`:2232`. At wiring, move them to `DetailActiveGlyph` constants (as Shuffle's are) and have `DetailView` read them.

**P3-3: two "light accent" thresholds.** `DetailActiveGlyph.swift:73` (`>= 0.8`, on resolved components) vs `DesignSystem/Theme.swift:78` (`onColor(forFillHex:)`, `> 0.75`, on hex).
- Today they agree:
  - the seven swatches sit at ≤ 0.60 or 0.96;
  - an accent at exactly 0.8 counts as light;
  - `applyTheme`'s `default:` branch is Crimson, so no eighth colour can reach `Theme.Palette.accent`.
- A future accent between 0.75 and 0.8 would get dark ink on its fills (`accentText`) but an undimmed inactive label.
- Fix: one shared constant (`Theme.Palette.lightAccentLuminance`) read by both. Nit.

## The regressions asked about

- **`scrollTo` during a user scroll / focus restore.**
  - tvOS scrolls only through focus moves, and each move cancels the pending reveal, so a reveal only fires on a row that has held focus 0.52 s, by which time the engine's reveal animation has finished.
  - A minimal reveal of a fully visible row is a no-op, so restore after the player cover, the collapse retarget, `focusListAfterAutoPlay` and the initial `focusedRow` all end in the same place.
  - Programmatic scroll never moves focus.
  - The one ordering hazard is a long programmatic jump (the auto-play overlay lifting onto a far row) whose engine animation runs past 0.52 s. The reveal would then end it at the row's edge instead of the engine's margin. That is cosmetic: device check 3.
- **`revealDelay` race (focus moves inside the 20 ms).**
  - Normally the `.task(id:)` restart cancels the task first.
  - The residual window: a press handled in the same run-loop turn the 520 ms continuation is serviced, before SwiftUI flushes the focus change. In that case `scrollTo(oldKey)` targets the adjacent, still-visible row, which is a no-op. Benign.
  - The 20 ms itself is ordered after the `dwelled` flush: CFRunLoop runs BeforeWaiting at least every other turn, and a 20 ms timer cannot resume first.
  - Optional hardening: trigger the reveal from `.onGeometryChange(for: CGFloat.self) { $0.size.height }` on the description when `focused && dwelled`, and drop `revealDelay`.
- **Trailer tile, variant 1 vs 2.** Both now draw `liveLayers(p).drawingGroup()`, so they are pixel-identical to each other. Against neighbouring posters on bitmaps, the tile matches the static ≤ 2/255 diff r1 accepted. If variant 2 wins R1, the knob cleanup must keep the variant 1 path: it is variant 2's fallback for `animatesSize`, halo and unkeyable shapes.
- **Luminance edge cases.** Exactly 0.8 counts as light (`>=`); the nearest swatches are 0.60 and 0.96. Opacity is ignored, and every accent is opaque. Extended-range components are clamped. Non-swatch colours cannot arrive today (P3-3).
- **Shuffle glyph pair on tvOS 26.** Both symbols exist (tvOS ≥ 14.2). Square layout pins the frame (`DetailActionSquareUITests`), so nothing moves. In Rounded, Shuffle's capsule width follows the glyph, and Shuffle is last in the row, so only its own width changes (device check 6).

## Verified fine (cross-cutting)

- **Concurrency.**
  - `DetailActiveGlyph`, `PlayerRouterLog`, `HomePerfKnobs` and `SlideHoldDecision` are `nonisolated`.
  - `resolve(in: EnvironmentValues())` from nonisolated code compiles (the plan's green run).
  - The task closure in `StreamRowDescription` is MainActor, so `onExpanded`/`scrollTo` run on main.
  - `StreamRowView.==` is still `nonisolated` over the model only.
- **Performance.**
  - The 30× Down/Up at 0.35 s walk never reaches the 0.5 s dwell, so the reveal adds nothing to W3-16's Animation Hitches measurement.
  - `.id(key)` adds one `IDView` per materialised row and does not affect `LazyVStack` laziness.
  - `isLight` costs one `resolve` per inactive-at-rest label body.
- **Shipping exposure of the fixes.**
  - P2-1: unwired.
  - P2-2: variant 2 only.
  - P2-3: the picker dwell, already a named BUG-16 change for the rc12 DM.
  - P3-2: log lines only.
  - P3-4: a launch line only.
  - P3-5 and P3-6: no rendering or behaviour change.
- **Localization.** No new keys. `"Shuffle On"` / `"Shuffle"` are unchanged, and `.accessibilityLabel(Text(title))` (`DetailView.swift:2567`) keeps the AX label on the icon-only form, whatever the glyph.
- **Nothing outside the 15 files changed.** No pbxproj, xcstrings or UI-test edits.

## Device checks the owner must run

All in Test 2, Steven's config (rc11 video + rc10 table: Rounded, system font, White accent, ring on with poster colour, depth Subtle/Soft/Full with poster colour, Classic Home, Cinematic Detail), Release unless noted. Run `scripts/device/ready.sh` first. These supplement r1's list; r1's items 2–10 still stand.

1. **Gate on `a1e766d8a`.** Kotlin + sim Debug/Release + the full NuvioTVTests + UI legs:
   - Rail08/12/12b/13/13b/13c;
   - test50 at 0/1/2;
   - test60;
   - the picker legs (`NuvioTVUITests.swift` ~8872, `FirstPlayAutoPlay` 619/638);
   - test54/55;
   - `DetailActionSquareUITests`.
   The recorded "141 tests green" is not the gate.
2. **W3-16 reveal, bottom-most visible row and the last row** (40–64-row stub add-on, long release names):
   - after 0.5 s the full name ends on screen, above the bottom overscan;
   - the focus platter's 1.02 scale and 16 pt shadow are not clipped by the viewport edge (`anchor: nil` aligns the row flush to it).
3. **W3-16 look.**
   - The grow, then the jump about one frame later: if it reads as a glitch, wrap the `scrollTo` in `withAnimation(.easeOut(duration: 0.2))` (`StreamPickerView.swift:705`).
   - Up from a revealed last row: the list settles with no blank band left under it (the collapse shrinks content below the revealed offset).
   - A row that does not overflow never moves at the dwell.
   - After the auto-play overlay lifts onto a far row, no early stop at the row's edge.
4. **W3-16 focus.** Initial focus, the collapse retarget, focus after the overlay lifts, and focus back from the player cover all land as before. A Down at about 0.5 s into a dwell does not pull the list back.
5. **W3-13 at `-debug.cardDepthRender 2`.**
   - Inline trailer tile expand and collapse at 30 fps: rails keep a constant width and the corners do not elongate.
   - The console shows `[HomePerfKnobs] cardDepthRender=2` with no `unparsed` suffix; a `0` walk shows `=0`.
6. **W3-17, after the owner wiring.**
   - White: Watched, Library and Shuffle on/off × rest/focused × Cinematic icon-only and Classic text. Decide P3-1: do the grey inactive labels read as off or as disabled?
   - Rounded: Shuffle's capsule width step on toggle is acceptable.
   - `shuffle.circle.fill` under focus: ink disc with knocked-out arrows legible on the platter.
7. **W3-19.**
   - Steven's title in Release without the flag shows `host=<redacted>.<tld>`; with `-debug.playerRouterHosts YES` it shows the full host.
   - A P7 title cut mid-scan prints the `probe cap hit in the P7 RPU scan` line.
8. **BUG-209.** r1's checks are unchanged: `exempt=1` still marks the focused in-band lines.
9. **Staging (no code).** `scripts/device/console.sh` launches the Debug device build, which always prints the full `host=`, and its logs land under `docs/research/device-rig-<date>/` in the public outer repo. The rig-log staging rule (redact before `git add`) still governs every Debug rig log. Add `-debug.playerRouterHosts` to the knob list in `docs/device-rig-2026-10-15.md`.

**Verdict: FINDINGS: P1 0 / P2 0 / P3 3.** Every r1 finding is closed. Before the W3-17 wiring, decide P3-1 on the box. P3-2 and P3-3 can land with the wiring or the knob cleanup.
