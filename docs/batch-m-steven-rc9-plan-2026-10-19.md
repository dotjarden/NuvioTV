# Batch M: Steven's rc8 + rc9 verdict → the next rc (plan, 2026-10-19)

**Status: APPROVED 2026-10-19 as recommended (D1–D8).** Wave 0 started the same day; the FEAT-80 question to Steven is drafted (NOT SENT) in `docs/comms-dm-drafts-2026-10-19-feat80-question.md`.

Sources:
- `docs/steven-beta19-rc9-verdict-2026-10-19.md` (verdict, photos, video review).
- Three read-only code surveys of `tvos-shared-extraction` at `c9e54872d`: Detail; player + Home; Discover + rail.

Scope as decided 2026-10-19:
- **Fixes:** BUG-153 (regression), BUG-186, BUG-191, BUG-185, BUG-187, BUG-188, BUG-189, BUG-190, BUG-192, FEAT-61, FEAT-82, plus the FEAT-80 rescope.
- **Kept separate:** the FEAT-81 Detail redesign and the UX-17 Home layout (their own design batch), and FEAT-73 Discover.
- **Taken in the Q&A:**
  - BUG-153 = **measure, then fix** (no blind revert).
  - FEAT-61 + BUG-192 = **drop the Synopsis Length setting and the "more"**.
  - BUG-189 = **app labels plus a standard-genre map**.

---

## Decisions for Christian (recommendation first)

| # | Question | Recommendation | Alternative |
|---|---|---|---|
| D1 | FEAT-80: what "a bar along the very top-left" means | **A horizontal icon strip at the top-left** (about 7 icons, capsule glass, left-aligned at the safe-area line). Rail Position becomes **Centre / Top Bar**, replacing rc8's Top. The focused icon shows its label below it; Up reveals the bar and Down exits it. Confirm with Steven before building (one DM line with a mock screenshot). | A compact top-left corner cluster (a short pill or one menu button that expands). This is a smaller change but is further from his words. |
| D2 | FEAT-80: Icons Only "goes flat" | **Screenshot it at rest and focused on the rig first.** The survey found no code path that drops the glass, so the likely cause is that a collapsed 84 pt `.glassEffect(.regular)` over the 0.55 dim reads as flat. Then add a collapsed-state treatment (`.regular.interactive()`, or a stroke plus highlight behind the glass). | Ship a guess with no screenshot. |
| D3 | BUG-192: after removing "more" | **No affordance at all**: the focused glass platter already says it's clickable (his words). | Bring the ⌄ back. |
| D4 | FEAT-82: scope | **The Detail action buttons only** (Play, Start Over, Trailer, the compact glass buttons). They go square when Poster › Corners = Square; Rounded and Round keep capsules. Chips stay as they are. | Chips too. |
| D5 | BUG-190: what the Classic collection page shows | **Classic Home's "Show Hero OFF" panel** (`HomeHeroForeground`, `showsCTA: false`), driven by the focused card, under the collection's logo header. | The Stage rows page's hero. |
| D6 | BUG-185: how to close the player | **Both:** (a) dismiss the player and the picker covers in one non-animated pass, and (b) draw the close-time hold as plain black with no logo, since the logo is for starts only. External hand-off: dismiss the picker before leaving the app. | (a) only. |
| D7 | BUG-187: scope | **Every NavigationLink out of Detail** (cast, More Like This, collections). Remember the focused row and card on push and restore them on pop. | Cast row only. |
| D8 | FEAT-61: how many lines on Classic without the setting | **4 lines whenever they fit**, using `LongSynopsis.grant`'s fit logic with Long always on. If his font and poster size can't fit 4, grow the synopsis slot rather than dropping a line, because his "3 lines, not 4" came from the fit falling back. Settings › Home Screen › Synopsis Length is removed. | Fixed 4 lines; the logo slot shrinks to make room. |

---

## Items

### Wave 0 (main session on the rig, Test 2): measure before writing fixes

- **BUG-153.**
  - Add three launch-time debug knobs:
    - `debug.detailImmediateTrailerMount`: restore rc7's immediate mount.
    - `debug.detailNoCompactLogo`: skip `DetailCompactLogo`.
    - `debug.detailNoTileRing`: `drawsOwnRing = false` on Trailers, Episodes and Season tiles.
  - Then run `debug.detailScrollProbe` (hitch counter, `[BUG41] hitches=…`) on Animals and on a big series Detail page (Monstre or similar). Compare:
    - an rc7 build (from tag `tvos-v0.3.0-beta.19-rc7`);
    - the tip;
    - the tip with each knob.
  - The existing knobs `debug.detailScrollAB`, `debug.detailEdgeEffectShown` and `debug.detailTopScrimStep` cover the G8 and Batch C scrim suspects.
  - Suspects, most likely first:
    1. Batch K's deferred trailer mount (`9dbedc482`, `DetailView.swift` 1428-1446), which moves the `AVPlayerLayer` burst into the next Down.
    2. G7's `@FocusState focusedTrailerIndex` on the whole 3300-line `DetailView` body (`:534`), plus the per-tile ring and lift work (`DetailTileFocus.swift`).
    3. G8's `.scrollEdgeEffectHidden` (`:~745`).
    4. The `DetailCompactLogo` overlay, always mounted with a shadow.
  - The fix is whatever the probe names, in Wave 1, Agent A. The record keeps the numbers.
- **BUG-191:**
  - Reproduce on Stage Home: No Zoom on, a Collections row above the last row.
  - Read `fit row=… h=…` and `P=` from the Stage probe.
  - A/B with Developer › Short Rows Fit off.
  - Suspect: Batch F's fit pages (`StripPager.swift:500-503`, `fitPageHeight = min(page, measured + 2 × focusLift)`). In No Zoom `focusLift` is 0, so there's no slack and the row above's content spills into the next page.
- **BUG-188:** capture `StageStripProbe` `restore pop/landed/gate` plus `swap phase=in id=` across a collection pop. Two `phase=in` lines in the uncover window would confirm that the engine lands on an intermediate card first.
- **BUG-186:**
  - Play on the native engine and screenshot: is the "Infos" capsule from his `IMG_9023` AVPlayerViewController's system Info pill?
  - On mpv, try Menu within 100 ms of the top panel presenting.

### Wave 1: three agents, disjoint files

**Agent A, Detail** (`DetailView.swift`, `Detail/*`, `DetailCinematicHero.swift`, `PersonDetailView.swift`)
- **BUG-153:** the fix Wave 0 justifies; keep the knobs that proved useful as Developer toggles.
- **BUG-187 (D7):**
  - Record the focused row and card at each `NavigationLink` push.
  - Restore them on re-appear after a pop with a three-rung retry (the FEAT-79 pattern).
  - Guard against `claimLatePlayFocusIfNeeded` (`:2237-2265`) and `.defaultFocus($heroFocus, .play)` (`:1085`).
  - Check whether `model.stop()/start()` on disappear/appear (`:1102-1117`) re-emits `meta` and rebuilds the rows; skip the reload on a pop if so.
- **BUG-192 (D3):** delete the "more" `Text` and its `HStack` (`DetailCinematicHero.swift` 306-312); keep `teaserText` and its platter.
- **FEAT-82 (D4):** in `prominentActionButtonStyle` and `compactActionButtonStyle` (`DetailView.swift` 1967-1990) and Start Over (`~2295`), use `.buttonBorderShape(posterStyle.cornerRadius == 0 ? .roundedRectangle(radius: 0) : .capsule)`. Verify that the glass styles honour it on tvOS 26 (sim screenshot).

**Agent B, Home and collections** (`HomeView.swift`, `PinnedRowGeometry.swift`, `HomeScreenSettingsPane.swift`, `CollectionsUI.swift`, `Home/StripPager.swift`, `Home/StageController.swift`, `Home/StageStripHome.swift`)
- **FEAT-61 removal (D8):**
  - Delete `SynopsisLength`, `home_synopsis_length`, the picker row (`HomeScreenSettingsPane.swift` 57-60, 172-181) and `LongSynopsisTests`'s setting cases.
  - Classic always asks `grant` for 4, growing the slot when the fit falls short.
  - The new Home is unchanged; it already shows the maximum.
- **BUG-190 (D5):**
  - `FolderDetailView.classicRowsContent` (`CollectionsUI.swift` ~1560) feeds `onItemFocusChange` into a `HomeHeroFocusModel`.
  - Mount the Show-Hero-OFF `HomeHeroForeground` panel under the logo header (`~1860`).
  - The folder backdrop stays unpainted (BUG-38).
- **BUG-191:** the fix Wave 0 justifies. Likely a No Zoom minimum slack in `fitPageHeight`, or a bottom-allowance clip per page.
- **BUG-188:** hold stage swap commits for non-target items while `uncoverRestoreTarget != nil` or the gate is closed (`StageController.swift` 232-279).

**Agent C, player, picker, Discover and rail** (`StreamPickerView.swift`, `FirstPlayAutoPlay.swift`, `Player/PlayerPanelHost.swift`, `NativePlayerScreen.swift`, `Discover*`, `NavigationRail.swift`, `NavigationChrome.swift`, `AppearanceSettingsPane.swift`)
- **BUG-185 (D6):**
  - Close both covers in one pass with `UIView.performWithoutAnimation` plus a disabled-animations Transaction (`StreamPickerView.swift` 1397-1462).
  - Add `FirstPlayAutoPlayOverlay(showsLogo: false)` for the close hold.
  - For external hand-off (`openExternallyNow` `:1155`), dismiss the picker before opening the external URL.
- **BUG-186:**
  - Fix the latch in `PlayerPanelHostController.close` (`PlayerPanelHost.swift` 195-201): `closing` is never reset. If the dismiss is dropped (a Menu during the 0.25 s present, or during `reclaimFocus`), every later Menu is swallowed. Reset it when `presentingViewController` is still set after about 0.6 s, and retry.
  - Native: if Wave 0 shows the system Info pill can take focus with the bar hidden, add an exit fallback in `NativePlayerHostController.pressesBegan` (`:108-117`).
  - UI legs: Menu within 100 ms of the panel presenting; swipe-up then an immediate Menu. Both must leave within 2 s.
- **BUG-189:**
  - Display-only mapping, `DiscoverGenreNames.display(_:)`. It covers the Cinemeta set (Action … Western, Reality-TV, Talk-Show, Game-Show, News, Film-Noir, Music, Musical, Short) plus the TMDB aliases (Science Fiction, TV Movie, Action & Adventure, Sci-Fi & Fantasy, War & Politics, Kids, Soap). Matching is case-insensitive and trimmed; unknown values pass through.
  - The same applies to standard catalog names (Popular, Featured, Trending, New, Top Rated) in `catalogLabel`. Compare raw names for clash detection first, then localize.
  - Selection, persistence and fetch keys stay raw.
  - Add the missing xcstrings entries "Genre" and "Browse".
  - Seed the fr/es/de/it/vi strings from upstream's 9 `collections_editor_tmdb_genre_*` keys and write the rest.
- **FEAT-80 (D1, D2):**
  - New `RailPosition.topBar` replaces `.top`: an HStack pill, capsule glass, left-aligned at `topInset`.
  - The reserved inset moves from leading to top in Always Visible mode, with `reservedLeadingInset` / `HiddenTabBarFocusBlocker` updated.
  - `RailFocusPolicy` reveals on Up from the top row and exits on Down.
  - Check the Discover pill band (`DiscoverPillBandGeometry.railTop`) and the Stage/Detail headers for overlap.
  - Plus the Icons Only collapsed glass treatment from D2's screenshot.
  - Migration: a saved `rail_position = top` reads as `topBar`.

**Integration (main session):**
- `SettingsDescriptions.swift`: remove `home.synopsisLength`; reword `appearance.railPosition`.
- `Localizable.xcstrings`: all new keys, five locales through `scripts/populate-localizable-xcstrings.py`.
- The Wave 1 merges, in the order A, B, C, under the build lock.

### Reviews, gates, device pass

- Two Opus review rounds to CLEAN. Codex is back 10-29; if the batch runs past then, the last round goes through `codex-review/tools/review.sh --base <branch point>`.
- Gates, as Batch L ran them:
  - the Kotlin trio;
  - NuvioTVTests (`NuvioTVTests` scheme);
  - Debug + Release sim on the FA87 destination;
  - a Debug device build with the bundle-ID override;
  - the new UI legs: BUG-186 Menu timing, BUG-187 cast pop focus, FEAT-82 button shape probe, BUG-189 genre labels under `-AppleLanguages (fr)`.
- Device pass (dev build, **Test 2**, `ready.sh` first):
  1. **BUG-153:** big Detail pages, first Down and a full scroll, `detailScrollProbe` hitches at or below rc7's.
  2. **BUG-191:** No Zoom on, the last Home rows show no posters from the row above.
  3. **BUG-188:** collection → Back, the landed logo doesn't flicker (probe: one `phase=in`).
  4. **BUG-185:** Back from the built-in player goes straight to Detail with no logo flash. Remote check by Christian: an external player hand-off returns with no loading flash.
  5. **BUG-186:** open the top panel and press Menu immediately; the panel closes and a second Menu exits.
  6. **BUG-187:** Detail → cast member → Back lands on that cast card; the same for More Like This.
  7. **BUG-190:** Classic Home, Rows layout, a collection: the focused card's poster and synopsis show under the collection logo.
  8. **FEAT-61:** Classic synopsis shows 4 lines; the setting is gone.
  9. **BUG-192:** no "more"; the focused glass still opens the full synopsis.
  10. **FEAT-82:** Corners = Square gives square Detail buttons; Rounded gives capsules.
  11. **BUG-189:** French: Discover's Genre/Browse labels and the standard genres are in French.
  12. **FEAT-80:** Top Bar at the top-left, Up reveals and Down exits; Icons Only keeps the glass at rest.

**Settings changes for the release notes and the DM:**
- Settings › Home Screen › **Synopsis Length removed**; Classic always shows up to 4 lines.
- Appearance › **Rail Position**: Centre (default) / **Top Bar**, which replaces Top.

### Agents and cost

1 Opus critique of the Wave 1 specs after Wave 0, then 3 build agents (A ∥ B ∥ C, disjoint files) and 2 Opus review rounds. Never more than three agents at once; builds serialised.

## Risks

- **BUG-153's cause may be cumulative.** No single knob may restore rc7. Then the fix is to undo the deferral and move G7's focus state into a child view, measured step by step.
- **FEAT-80 is the largest item** (layout, focus, insets). If Steven's answer to D1 changes the shape, it moves to the FEAT-81/UX-17 design batch and the rest of Batch M ships without it.
- **BUG-186 is seen once and unreproduced.** The latch fix is real code hardening, but it may not be his case. The DM asks which player and what he pressed.
- **BUG-188 and BUG-191 are hardware-timing bugs**; the simulator won't show them. Wave 0's rig logs are the spec.
- **Removing a setting that shipped in rc9** (Synopsis Length) needs a release-notes line, because his saved value just stops applying.
- **Free-team provisioning expires 10-22 00:23 EST**; the first device build after that re-signs.

---

## OUTCOME

### Wave 0 (started 2026-10-19)
- **BUG-153 A/B, measured on the rig** (Release builds; Test 2; The Boroughs Detail from the Library; a scripted walk of 8 Down + 8 Up at 0.7 s, starting 2.5 s after the page opens; `debug.detailScrollProbe` hitch counter, gaps over 25 ms). Knobs added in `782b31be6`. Raw numbers: `docs/research/batch-m-w0-2026-10-19/bug153-probe-results.txt`.
  - **Two walk kinds.** The first Down either lands shallow (about 1,700 frames, `detailBodyEval=20`) or deep (about 1,250 frames, 40 evals, a ~766 pt first scroll). Compare within a kind.
  - **Ring off (Test 2's own setting):** rc7 and the tip match. Shallow: rc7 17/16 vs tip 17 (knob runs 12–19). Deep: rc7 21/25 vs tip 22/22/20/23. No single knob clearly helps; the immediate trailer mount came out best (12/15 vs 17), within the noise.
  - **Ring on (`-accent_focus_ring YES`, as on Steven's box), deep walk:** rc7 17/21, tip 23/26, tip + `debug.detailNoTileRing` 19. Shallow: all about 15–17.
  - **Conclusion:** the regression shows only with the accent ring on, on deep walks where the Episodes, Season and Trailer rows are built. That points to G7's tile ring path (BUG-177: `DetailTileFocusLift`'s per-tile ring, lift, `onChange` and colour sample, plus the `@FocusState focusedTrailerIndex` on the whole `DetailView` body). Batch K's deferred mount is not the cause.
  - **Fix direction for Agent A:**
    - Make the tile ring cheap: no per-tile `ArtworkColorStore` sample on focus, one shared ring overlay per row, and the trailer focus state moved into a child view so a focus move doesn't re-evaluate `DetailView.body`.
    - Keep `debug.detailNoTileRing` as the A/B, and re-measure ring-on deep walks against rc7's 17/21.
- **BUG-188, measured** (Stage Home, Test Collection → folder → Back; `debug.homeScrollProbe`; `console-bug188.log`):
  - `restore pop` → rungs 1 and 2 miss → `restore landed … after=589` → gate.
  - Then, **205 ms later, `restore regrab … from=outside age=53`**: the focus engine moves off the landed folder card and the restore pulls it back. That out-and-back move is the single flicker.
  - Fix direction for Agent B: while the gate is closed, don't let the engine's late move commit a stage change. Hold the stage on the restore target until the gate opens (`why=window`, here 1.6 s), so the regrab is invisible. Also look at why rungs 1 and 2 miss (the landing took 589 ms).
- **BUG-191, not reproduced on the rig:** Test 2's Home has no collection row above its last rows; "Test Collection" is the third row. Walking to the bottom with No Zoom on showed no bleed, and no `fit row=` lines were logged on that walk.
  - Agent B takes it from code (the Batch F fit-page slack, `StripPager.swift:500-503`, `focusLift = 0` in No Zoom).
  - It adds a simulator UI leg with a fixture Home order (a collection row second to last) and checks with Short Rows Fit (`-debug.stripFitRows NO`) as the A/B.
  - It asks Steven for his row order if the fix can't be confirmed.
- **BUG-186: not run on the rig.** Test 2's Comet DV streams route to mpv, so the native "Infos" pill check needs a native-routed source. Agent C ships the panel-host latch fix (code-level, with UI legs), and the DM asks Steven which player he was in.
- Rig note: one `console.sh start` launch came up in the background, and 12 Downs were lost; follow it with `atv.sh launch com.youngchris29.NuvioTV`.
