# Plan: the fixes promised in the rc5 reply (2026-10-17)

Source: the reply SENT to Steven 2026-10-17 06:08:08Z (`docs/comms-dm-drafts-2026-10-17-rc5-reply.md`), triage
`docs/steven-beta19-rc5-verdict-2026-10-17.md`, master plan §4.4b (B11–B15). Written with the
`swiftui-ui-patterns` skill (performance, focus, scrollview, overlay, media references) and the
`swiftui-liquid-glass` skill (where glass belongs and where it does not). Base: `tvos-shared-extraction`
`9ee8597d4` (rc5 + the SwiftUI Pro review fixes).

## What the reply promised, and what it did not

| # | Reply line | Promise | Row | Plan item |
|---|---|---|---|---|
| 1 | "The next build halves the remaining gap between the heading and the posters, and I'll check it on my TV with your settings" | **Next build, rig-verified in his config** | BUG-146 | P2 |
| 2 | Wide posters "at rest … the same size as your collection tiles … grow to the big size when the trailer starts … brings the heading down on those rows" | **The plan** (stated, not dated) | BUG-162 (+ BUG-146 landscape half) | P1 |
| 3 | "The next build drops the one at the top, so the name appears once" | **Next build** | BUG-173 | P3 |
| 4 | "The next build won't show an empty box there, only the time" (native player) | **Next build** | BUG-168 native half | P4 |
| 5 | Watched tick "is in the next batch for Home and collections" | **Next batch** | FEAT-64 | P5 |
| 6 | "The Animals case on mpv is next on my list" | Repro, no cause promised | BUG-168 mpv half | Separate card (BUG-165/168 DV P5 repro); not in this batch |
| — | Two-move return: "won't promise it for the next build" | Not promised | BUG-156 | B13, after this batch |
| — | HDR late: "looking into it", asked which player | Not promised | BUG-170 | P5 player batch, after his answer |

Items 1, 3, 4 are dated promises ("next build"); 2 and 5 are near-dated. All five go in one batch so the next
build (rc6) carries them.

## Skill guidance that shapes the work

From `swiftui-ui-patterns`:

- **performance.md, stable identity + narrow observation.** The rows are `LazyHStack`s with `.id(item.id)` per card
  and a morph that changes one card's frame. P1 must not change the identity of a card when it grows (no view
  swap between a "rest" and a "grown" card: one view whose frame animates), and P5 must not make every card on
  Home observe the whole watched store: one store, each card reads one key.
- **performance.md, keep a stable root, vary modifiers.** P4's "no empty box" is a modifier/flag on the existing
  player setup, not a second player path.
- **focus.md, "avoid aggressive focus changes during animation".** P1's growth happens under a focused card; the
  grow must not move focus or the row's scroll anchor (the M3 morph-scroll math already handles a width change;
  P1 feeds it the right resting width).
- **scrollview.md, stable IDs for scroll targets.** P2 changes a constant the `StripPager`'s page height derives
  from; page IDs stay, only heights change, so `.scrollPosition(id:)` keeps working.
- **overlay.md, overlays never change layout.** P5's tick is an overlay on the artwork (it already is in
  `PosterWatchBadgeView`); it must ride the focus lift and never move the caption (BUG-29's row math).
- **media.md, decode at the drawn size.** P1's rest card is smaller (416 × 234): the base card decodes at the
  rest size, the tile at its expanded size (`InlineTileArtSource.tileSize` already is the expanded size).

From `swiftui-liquid-glass` (tvOS 26 deployment target, so `glassEffect` is available without an availability gate):

- **Glass is for controls and chrome, not content.** None of the five items adds glass. The watched tick (P5)
  stays the solid accent/white symbol the Library uses (upstream Nuvio's badge is a solid accent circle); a glass
  badge on poster art would read as a control and fight the focus lift. The landscape cards (P1) are content:
  no glass.
- **Native transport (P4) is AVKit's own glass chrome.** The empty box is AVKit's scrub-preview slot. We do not
  draw over or restyle AVKit's transport; the fix is to stop advertising a preview source AVKit then never uses.
- **Where glass would matter later:** if P4's rig gate shows AVKit keeps an empty slot no matter what, the
  fallback is not a custom glass overlay over AVKit's bar (fragile, two transports on screen); it is to say so
  to Steven.

## P1 — BUG-162: wide cards rest at the collection-tile size, grow with the trailer (D16)

**Facts (code at `9ee8597d4`):**
- `PosterStyle.cardWidth/cardHeight` (DesignSystem/PosterStyle.swift:29–37): a shape-landscape row
  (`landscapeFromShape`) is `height × 16/9` × `height` = 624 × 351 at Medium+.
- A landscape folder tile is `style.width × 16/9` × `style.width` (`FolderTile`, Screens/CollectionsUI.swift:608–633)
  = **416 × 234 at Medium+**. That is "your collection tiles".
- `InlineTrailerCard.artworkWidth/artworkHeight` (Screens/InlineTrailerCard.swift:2676–2688) return the card size
  for every landscape row, so the tile never grows there; portrait rows grow width only at `.wide`
  (`model.layoutExpanded`), height constant (UX-4a).
- `CatalogRowView`'s morph-scroll plan (Screens/BrowseComponents.swift ~5577) passes
  `restingWidth: posterStyle.width` (234), wrong for any landscape row (it should be the card's resting width).
- The row's `LazyHStack(spacing:)` (BrowseComponents.swift:5212) uses the default **center** vertical alignment.
- The strip plans a shape-landscape row at the portrait height (`landscapeRowGeometry` false), so a 351 pt slot
  is reserved under the heading. That is what lets the card grow without the row breathing.

**Change:**
1. `PosterStyle`: shape-landscape **rest** = `width × 16/9` × `width` (the folder-tile rule); add
   `expandedCardWidth/Height` = `height × 16/9` × `height` for the grown tile. Global Landscape Posters keeps
   360 × 203 (rest = expanded, unchanged). Comment the D16 rule at the site.
2. `InlineTrailerCard`: shape-landscape rows take the portrait morph stages. `artworkWidth` =
   `layoutExpanded ? expandedCardWidth : cardWidth`, `artworkHeight` = `layoutExpanded ? expandedCardHeight :
   cardHeight`; `.reveal` dissolves at the rest size (rc1 R2 rule: never grow while translucent), `.wide` grows.
   Same view, same identity, frame animates with the existing stage animation (performance.md). `tileSize`
   stays the expanded size (decode once at the drawn size, media.md).
3. Vertical anchoring: the card grows **downward** into the reserved slot, so the heading never moves. Give the
   shelf's `LazyHStack` `alignment: .top` for shape-landscape rows only (portrait rows have one height, so the
   change is a no-op there; check the folder row's own top-aligned stack is not the same view).
4. `RowMorphScroll.plan`: `restingWidth: posterStyle.cardWidth`, `expandedWidth: posterStyle.expandedCardWidth`
   for landscape rows, so the grow scrolls the row the same way a portrait grow does.
5. Lift and ring: the base card fades under the tile (B4's `fadesBaseCard`), the tile takes the portrait lift
   rule (`CardSystemLiftStyle`); with No Zoom the BUG-164 rule stands. Check the poster-colour ring follows the
   grown frame.
6. Classic Home: `PinnedRowGeometry` reads `landscapeRowGeometry` (false for shape rows), so its reach budget is the
   portrait one, unchanged. Search/Library draw shape-landscape cards through the same `PosterStyle`: they get the
   smaller rest size too (they never grow: no trailers there), which is what he asked for.

**Tests:** `PosterStyleLandscapeRowTests` (rest = folder-tile size at every Poster Size, expanded = poster height ×
16/9, global toggle unchanged); a pure `InlineTrailerGeometry` table (stage → width/height for portrait, shape,
global); `RowMorphScrollTests` case for a landscape grow; UI leg `testLandscapeShapeCatalogDrawsLandscapeCards`
re-pointed (rest card height == 234 at Medium+, heading → card gap == the portrait row's, tile grows to 351 tall
with its top at the rest card's top).

**Rig (Test 2, his config: Medium+, Hide Titles ON, No Zoom OFF, Card Depth ON, trailers in the row):** the stub
add-on `scripts/device/fixtures/landscape-addon.py`; screenshots at rest and after the trailer starts; burst
frames across the grow (no jump of the heading, neighbours slide right).

## P2 — BUG-146: halve heading → posters on the strip (24 → 12 pt)

**Facts:** heading → shelf = `StripGeometry.headingGap` 12 + `StripGeometry.shelfTopPadding` 12 = 24 pt
(Screens/Home/StripGeometry.swift:197, 212). The heading is `Theme.Font.sectionTitle` (`.callout` token,
semibold), line box `sectionTitleLineHeight` 38 pt. The strip always shows the focused row, so one card is always
lifted: the zoom lift raises it 20 pt (`heroPinnedRowFocusLiftAllowance`), 0 with No Zoom. At 24 the lifted art
clears the line box by 4; at 12 it enters the line box by 8.

**Change:** `shelfTopPadding` 12 → 0 on the strip (`StripShelfPadding`), `headingGap` stays 12: heading line box →
resting art = 12. `catalogRowHeight` / `collectionRowHeightMax` follow (every page −12, the stage +12; re-derive
`StripGeometryTests`, the synopsis-line and compact-logo boundaries move).

**Gate before the number is final (pure test + rig):** the lifted art must not touch the heading's GLYPHS. Add
`StripGeometry.liftClearsHeadingGlyphs(gap:lift:font:)` from `UIFont` metrics: the empty band under the
descender = `lineHeight − (ascender − descender)` split per the line's layout; pass if `gap + band ≥ lift + 2`.
- If it passes at 12 (likely for `.callout` at 38 pt line height with the band ≥ 10): ship 12.
- If it fails: ship the smallest gap that passes (at most 16), and the next DM states the real number. Not an
  option: moving the heading up while a card is lifted, which would shift the heading on every focus change
  (focus.md: no layout moves during focus animation). The reply said "halves"; the rig photo decides.
- With No Zoom the lift is 0, so 12 always passes.

**Rig:** Test 2 in his config; screenshot a portrait row and a landscape row (after P1) on Home and on a folder
page; measure heading baseline → unfocused art top in points from the 1920-wide screenshot; compare with
`p2-folder-open` (rc5 baseline). Classic is untouched (`headingGap(inStrip:)`).

## P3 — BUG-173: the collection title once on Home

**Facts:** `HomeRowPreviews.swift:55` gives a folder preview `releaseInfo = collection.title`; `StageCopy.make`
(Screens/Home/StageCopy.swift:29) prints `releaseInfo` as the stage meta line via `classicMeta`; the strip row
right below has the same collection title as its heading. The same preview feeds Classic's hero-OFF panel,
which needs the meta line (rc14 BUG-119), so the fix cannot be in the preview builder.

**Change:** `StageCopy.make(item:progress:rowHeading:)`: a folder preview's meta line is dropped when it equals the
visible row heading (`sameText`, the helper already there). `StageView` (line 234) passes the focused row's
heading (it has the row key; read the heading from the same source the strip's `CatalogRowView`/`CollectionRowView`
draws). The folder page intro (`FolderRowsPlan.swift:255`) passes nil (its headings are catalogs), so it keeps
"Netflix / Services de Streaming". Logo-less folders still show their name in the logo slot.

**Tests:** `StageCopyTests`: folder + same heading → meta ""; folder + different heading → meta kept; a title whose
release text happens to equal the heading is untouched (only folder previews are matched, `isFolderPreview`).
UI leg: Stage Home, focus a collection row's folder, the stage meta label is empty and the heading reads once.

## P4 — BUG-168 native half: no empty preview box

**Facts:** the native engine plays through `AVPlayerViewController` with AVKit's own transport
(`NativePlayerScreen.swift`). P3 publishes an `EXT-X-I-FRAME-STREAM-INF` rendition in the loopback master when
`SeekPreviewMode.current().allowsIFrames` (`NativePlaybackCoordinator.swift:986`, default `.harvest` → on). AVKit
then shows a preview slot while scrubbing, but on tvOS 27 its paused-scrub preview never requests an I-frame (P3
spike, runs 1–4): the slot stays empty. The rendition's only working use is FF/RW scan pictures (and those stop at
the per-film byte budget). The mpv bar already draws no card without a frame (`PlayerTransportBar.scrubCard`).

**Change:** split the switch per engine. `SeekPreviewMode.allowsNativeIFrames` = false by default; a Developer A/B
row "Native I-frame Scan (A/B)" (off) turns it back on for FF/RW scan pictures. mpv's harvest/decode untouched.
Settings description says what the row costs (no scan pictures) and gains (no empty preview box).

**Gate (rig, before claiming it):** play a native title (Spirited Away class: HEVC MKV, native route) with the
rendition off; scrub while paused and while playing; screenshot. Pass = AVKit shows the time only, no box.
If AVKit still draws an empty slot without the rendition, P4 does not ship as promised: record it, and the next DM
says the box is Apple's and cannot be removed from the app (no custom overlay on AVKit's bar, see the glass note).

**Tests:** `SeekPreviewModeTests` (native default off, A/B on), the master-playlist golden for both states
(`SegmentMap` test already has the I-frame line case).

## P5 — FEAT-64: watched tick on Home and collection rows

**Facts:** `PosterCard.watchBadge` + `PosterWatchBadgeView` (DesignSystem/PosterCard.swift:961, 1535): white
`checkmark.circle.fill` over the background colour, top trailing, inside the artwork, rides the lift; only
`LibraryView` sets it. Shared `WatchedRepository` exposes `uiState` (watched items), `fullyWatchedSeriesKeys`, and
`isWatched(…)`; `HomeView` / `StageStripHome` / `TitleHoldMenu` already touch it (Mark as Watched).

**Change:**
1. One `@Observable` `WatchedBadgeIndex` (Swift, main actor) built from `WatchedRepository.uiState` +
   `fullyWatchedSeriesKeys` (one `watchFlow` subscription for the app, the pattern Search & Discover used),
   exposing `isWatched(_ item: MetaPreview) -> Bool` over a precomputed `Set<String>` of keys (movie id; series =
   fully watched). Injected once at the root with `.environment(...)` (ui-patterns: shared app service).
2. `CatalogRowView` (portrait and landscape cards, Home strip, Classic rows, folder pages) passes
   `watchBadge: index.isWatched(item) ? .init(isWatched: true, progress: nil) : nil`. Progress bars stay out of
   these rows (Continue Watching owns progress). CW and Upcoming rows: no tick (upstream rule).
3. Observation scope (performance.md): cards read `index.isWatched(item)`, which reads the one `Set`; a mark
   changes the set once and only cards whose result flips re-render their overlay. No per-card task, no per-card
   repository call.
4. Hold menu "Mark as Watched / Unwatched" already writes the repository: the tick appears without a refresh.
5. Hide-watched toggle (D4) stays out of this batch.
6. Glass: none (solid symbol, see the liquid-glass note).

**Tests:** `WatchedBadgeIndexTests` (movie key, series fully watched vs partly watched, profile switch clears);
UI leg: mark a fixture title watched from the hold menu on Home, the tick shows on its card, and on the same title
inside a collection.

## Execution

- One clone `~/Claude/Projects/NuvioMobile-rc5-promises` off `9ee8597d4` (MPVKit symlink, `local.properties`, cloned
  build caches, `with-lock.sh`), branch `claude/rc5-promises`.
- Wave 1, two agents with disjoint files: **α** P1 (PosterStyle, InlineTrailerCard, BrowseComponents row stack +
  morph plan, their tests); **β** P3 + P4 + P5 (StageCopy/StageView, SeekPreviewMode/NativePlaybackCoordinator/
  Developer pane, WatchedBadgeIndex + CatalogRowView badge wiring). P5's `CatalogRowView` edit and α's
  `BrowseComponents` edit touch the same file: β edits only the card's `watchBadge:` argument, α only the stack
  alignment and the morph plan; targeted edits, no rewrites.
- Main session: P2 (StripGeometry + tests) after wave 1 builds, since its re-derived tests depend on P1's row
  heights staying portrait.
- Gates: NuvioTVTests, Debug + Release sim, the touched UI legs with `-collect-test-diagnostics never`.
- Review: an Opus read-only round (Codex quota resets 10-29) until 0 P1 / 0 P2.
- Device pass in **Test 2** on the rig, his config: P1 rest + grow, P2 measured gap (portrait + landscape, Home +
  folder), P3 title once, P4 native scrub with no box, P5 tick on Home + in a collection. The P2 and P4 gates
  above decide the wording of the next DM.
- Cost: 2 agents + 1 review agent (inside the ≤3 guardrail). About a day including the rig pass.
- Then: fast-forward on Christian's go, rc6 per `scripts/cut-rc.sh`; notes say the wide cards now rest small and
  grow with the trailer, the heading gap number, the native scrub change and its Developer A/B row, the tick.

## Out of scope here

BUG-156 two-move return (B13), BUG-170 HDR timing (P5 player, after his engine answer), BUG-168 mpv Animals (its
own repro card), FEAT-76 per-collection layout (D17), FEAT-77 loading animation (D18).

## OUTCOME (2026-10-17, built + reviewed + device-passed; NOT merged, NOT cut)

Branch `claude/rc5-promises` in the clone `~/Claude/Projects/NuvioMobile-rc5-promises`, off `9ee8597d4`, local only
(not pushed): `aa617f2dc` wave 1 (agents α = P1, β = P3/P4/P5) + `523ad97db` review r1 fixes.

| Item | Result |
|---|---|
| P1 BUG-162 (D16) | `PosterStyle` shape rest = `width×16/9 × width` (416×234 at Medium+), `expandedCardWidth/Height` = `height×16/9 × height`, `artworkSize(expanded:)`; `InlineTrailerCard` grows at `.wide` inside a poster-height slot (`shapeSlotSizer`, trailers on or off); morph scroll + `rowArtworkHeight` read the new sizes. **Device PASS** (Test 2, stub add-on, his config): rest cards ≈412×230 pt, heading right above (`f1-down11`), the trailer picture on the grown tile (`f2-trailer`), a third card grows on screen with the row following (`f3-third-grown`). |
| P2 BUG-146 | **No constant change.** The A/B on the box (same config: Medium+, Hide Titles ON, zoom ON, Card Depth ON) found rc5's gap from heading baseline to the unfocused posters ≈64 pt (`g1-base-catalog-row`, `g2-base-folder`), matching Steven's photo, and this build's ≈30 pt (`b3-catalog-row`, `c1-folder-open`). Cause: `CatalogRowView`'s shelf `LazyHStack` centred its cards, and the focused trailer card lays out taller, so every other card sank ~34 pt. Fix: `.top` on every row (wave 1). That is the "halved" gap without trimming the 24 pt band, so the zoom lift still clears the heading. The rejected trim (24 → 12) would have put the lifted tile into the heading's descenders. |
| P3 BUG-173 | `StageCopy.make(rowHeading:)` + headings recorded per shown item in `StageCopySource`. **Device PASS:** "Test Folder" alone on the stage above the "Test Collection" heading (`b2-test-collection`; rc5 read "Test Folder / Test Collection"). |
| P4 BUG-168 native | `SeekPreviewMode.allowsNativeIFrames`, Developer "Native I-frame Scan (A/B)" off by default. **Device PASS:** native route (`[PlayerRouter] native — SDR`), `[HLS] master iframes=0`, a paused scrub 02:08 → 03:43 shows the time only, no box (`h5-scrub2`). |
| P5 FEAT-64 | `WatchedBadgeIndex` (@Observable, two FlowWatchers) + `WatchedBadgeReader` per card; `LandscapeCard` gains `watchBadge`. Tick on every `CatalogRowView` row (Home, Classic, folder pages, Search, Discover rows); CW / Upcoming / grid pages none. **Device PASS:** Mark as Watched → tick on Spider-Man with no refresh (`d3-rest-tick`), survives a reinstall + relaunch (`i2`), Mark as Unwatched removes it (`i3`). |

Reviews: Opus r1 1 P1 (the morph-scroll guard still skipped every landscape row, so a growing wide card never
scrolled) + 4 P3; fixed (guard on `landscapeRowGeometry`, `ensureLoaded()` on every shell appearance, comment);
the stale-heading P3 left (self-heals on the next focus report). r2 CLEAN (one optional P3: `InlineTrailerCard.expandedWidth`
is now test-only). Gates: NuvioTVTests 1838/0 (5 skipped) on wave 1, the touched classes 49/0 after r1, Release sim
green, UI leg `testLandscapeShapeCatalogDrawsLandscapeCards` PASS (rest 415.9×234, grown 623.9×351 from the same
top). Device evidence `docs/research/rc5-promises-device-2026-10-17/` (960 px shots + crops; consoles redacted).
Test 2 cleaned: watched mark undone, fixture add-on removed, app relaunched plain, TV asleep.

Seen on the way, not in scope: the Stage's Continue Watching and Upcoming headings still float ~100 pt above their
203 pt cards (`a1-launch`, `b1-collection-row`, the pre-existing Batch B observation), the same centring class as P2
in a different row view (`UpcomingRow.swift`, the CW row in `HomeView`); a cheap follow-up if Steven names it.
For the next DM: the heading gap fell from ≈64 to ≈30 pt in his config (the row alignment, not a spacing change);
the native player shows the time only while scrubbing, and FF/RW scan pictures are behind the Developer row.
Next: Christian's go to fast-forward `claude/rc5-promises` into `tvos-shared-extraction`, then rc6.
