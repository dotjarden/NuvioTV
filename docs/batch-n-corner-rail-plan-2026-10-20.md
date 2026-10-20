# Batch N: FEAT-80 corner rail + two Batch M device-pass P3s (plan, 2026-10-20)

**Status: PLAN, awaiting Christian's go. Nothing built.**

Sources:
- Steven's FEAT-80 answer (DM 2026-10-19 21:12–21:14Z, two mock-ups in `docs/research/steven-feat80-answer-2026-10-19/`).
- The Batch M device pass (`docs/batch-m-steven-rc9-plan-2026-10-19.md`).
- A read-only code survey of `tvos-shared-extraction` at `86af6a69b`.

Paths are under `NuvioMobile/iosApp/NuvioTV/`; DS = `DesignSystem/`.

**Decided 2026-10-20 (Christian):**
- Corner is a **new Rail Position** that replaces rc8's Top; the existing visibility setting decides the rest state.
- Build the **unroll animation**.
- The **glass is flush to the edges, the icons are inset** in the safe area.
- **Its own batch now.**

## Steven's design, read from the mock

- **At rest (Always Visible):** only a small Home-icon tab in the very top-left corner. Its glass touches the top and left edges and has a rounded bottom-right corner.
- **At rest (Hidden):** nothing.
- **Open (Menu, or Left at a page's leading edge):** the panel unrolls downward from the tab into the vertical icon column (Home, Search, Discover, Library, Add-ons, Settings, profile), still flush, with the page dimmed. Rail Labels (Shown / Icons Only) still applies.
- **Reduce Motion:** a fade.

## N1. FEAT-80 Rail Position = Corner, M–L

**Model** (`DS/NavigationChrome.swift`):
- Add `RailPosition.corner` (`:51`).
- `railPosition(raw:)` (`:64`) maps both `"top"` and `"corner"` to `.corner`. A saved rc8 Top therefore shows as Corner with no write; Settings reads the normalised value (`AppearanceSettingsPane.swift:355`).
- Unknown values stay `.centre`.

**Drawing** (`DS/NavigationRail.swift`): one column, laid out at its final geometry, with only the glass height and a mask animated.
- **Glass background:**
  - `.frame(height: expanded ? columnHeight : tabHeight, alignment: .top)`;
  - an `UnevenRoundedRectangle` with only the bottom-trailing corner rounded (about 42), shared by the tab and the column;
  - zero leading and top padding, so it touches both edges.
- **Items** stay at their final positions; a `.mask(alignment: .top)` of the same animated height reveals them.
  - No `offset` or `scaleEffect` on the items: the Orivio trap at about `:447`, where focus frames must not move.
  - The mask and the height change in the same `expanded` transaction, so a non-Home item focused by `takeFocusAfterReveal` is never clipped.
- **Safe area:** the first cell's icon sits at the tvOS safe-area origin (x 80, y 60), so the column's leading and top padding become 80 and 60 in Corner. The tab is about 152 × 132. `expandedWidth` and the label width follow.
- **Collapsed:** items other than Home are non-focusable (`armed` false) and `accessibilityHidden`.
- **Animation:** a spring on the height, with the icons fading in top to bottom. Reduce Motion drops the height animation and fades the lower items.
- **Transition** for Hidden → shown: opacity, or a short move toward the top-left, instead of `move(edge: .leading)`.
- **Unchanged:** the dim, `expanded`, `.ignoresSafeArea()` and `RailFocusPolicy` (arming doesn't depend on position).

**Reserved space:**
- Corner reserves **0**. `RailVisibilityRule.reservedLeadingInset` (`:323`) and `reservesWidth()` (`:130`) take the position, and so do `contentSafeAreaExtra` (`:164`) and `rowEdgeMargins` (`:180`).
- Callers: `shellInset` (`:337`), `contentInset` (`:346`), `HiddenTabBarFocusBlocker.setReservedLeadingInset`, `RailReservedWidthModifier`.
- **Risk:** the tab (up to about 152 × 132) can overlap a fixed top-left header (Stage title area, Detail compact logo, folder logo header, Discover pill band). The device pass checks each page; the fallback is a small top inset on any page that collides.

**Settings and strings:**
- `AppearanceSettingsPane.swift:97–100`: replace `(.top, "Top")` with `(.corner, "Corner")`.
- `SettingsDescriptions.swift:269`: the Rail Position copy becomes "Where the rail sits: centred on the left edge, or as a small Home tab in the top-left corner that unrolls into the full rail when you open it. Default: Centre."
- `appearanceRail` copy: pages make room for the rail, except in Corner.
- `Localizable.xcstrings`: add "Corner" and the new copy in five languages. Keep "Top", because the Card Depth picker uses it.

**Probes and tests:**
- Add `pos=` to the `rail_state` probe, and a Corner `navigation_rail_bounds`.
- Update `NavigationChromeTests` (`" Top "` → `.corner`, plus a "corner" case) and add the position parameter cases.
- New UI leg `Rail12` in `NavigationRailUITests`:
  - at rest with `-rail_position corner`, the tab's minX = 0 and minY = 0 and only Home is hittable;
  - after Menu, every item exists;
  - with Hidden, nothing exists at rest.

## N2. Classic Rows collection page: the focused row's heading is hidden (P3, from the Batch M pass), S

**Cause:**
- The page (`Screens/CollectionsUI.swift:1575`) is a logo, a 352 pt hero, then a `ScrollView` whose viewport starts under the hero.
- Rows use `CatalogRowView` with `rowCardTopReach = 0`, so the heading is a plain `Text` above the shelf, outside any focusable frame.
- tvOS scrolls only the focused card into view, so the heading of the newly focused row scrolls under the clip.

**Fix:** use Classic Home's pinned-row mode on that page only (when `heroFocus != nil`):
- `.environment(\.rowCardTopReach, Theme.Size.heroPinnedRowTopPad)` and `.environment(\.rowCardBottomReach, Theme.Size.heroPinnedRowBottomReach)`;
- LazyVStack spacing 0, as in `HomeView.swift:1450/1511`;
- retune the first-row top padding.

**Test:** a UI leg that moves Down to row 2 and checks the heading sits below the hero's maxY.

**Risk:** reach above 88 freezes focus resolution (Home's note); keep the Home values.

## N3. Stage Home: an Up pressed during the collection pop is lost (P3), S–M

**Cause:**
- `StageController.noteViewerInput` (`Screens/Home/StageController.swift:~440–465`) retires the restore on a viewer press. It replays only through `replaySwallowedRowMove` (`:410`), which requires `target.landedAt != nil`.
- So an Up before landing is dropped; the `pending=1` branch (pager not yet back) never replays either.

**Fix:**
- A pure `UncoverReplayPolicy.decide(kind:stripOwnsFocus:currentRowKey:rowKeys:pressAt:lastRowChangeAt:)` returns the destination row, or nil when the engine already moved within `regrabDefer` (0.15 s) after the press, or at the strip's bounds.
- Both retire branches use it. After `retireUncover(cancelsPager: true)`, wait one `regrabDefer` beat, re-check that no row change happened, then `requestFocus(reason: "uncover-replay")`.
- The pending branch waits for `pagerHandle.isInstalled` (the `attemptUncoverRestore` poll).
- The anchor is `currentRowKey` when the strip owns focus, else the restore target row.

**Tests:** `UncoverReplayPolicyTests` covering:
- Up and Down, before and after landing;
- row 0 and the last row;
- the engine already moved;
- the strip not owning focus;
- pending.

Plus a UI leg pressing Up right after Back.

**Device:** the rig run from the Batch M pass (Back, then Up 0.62 s later) should end on the row above.

## Order, agents, gates

- **Clone** `~/Claude/Projects/NuvioMobile-batch-n`, branch `claude/batch-n` off `86af6a69b`.
- **Agents, disjoint files, edit-only:**
  - Agent A (Opus): N1, in `DS/NavigationRail.swift`, `DS/NavigationChrome.swift`, `DS/HiddenTabBarFocusBlocker.swift`, `AppearanceSettingsPane.swift`, `SettingsDescriptions.swift` and their tests.
  - Agent B (Sonnet, exact spec): N2 + N3, in `CollectionsUI.swift`, `Home/StageController.swift`, `Home/UncoverRestorePolicy.swift` and tests.
- **Main session:** strings (populate + translate), builds, UI legs.
- **Reviews:** Opus rounds to CLEAN; Codex once its quota is back (10-29), if the batch runs past then.
- **Gates:** as Batch M (Kotlin trio, NuvioTVTests, Release + Debug sim on FA87, Debug device build), plus the new UI legs.
- **Device pass** (dev build, Test 2, `ready.sh` first; `-accent_focus_ring YES` makes focus visible):
  1. Corner + Always Visible: the tab sits flush top-left. Menu unrolls the column; Left from a page's leading edge does too; Right and Menu close it.
  2. Corner + Hidden: nothing at rest, and it still opens.
  3. Rail Labels Shown in Corner widens correctly.
  4. Every main page (Home both layouts, Discover, Library, Search, Detail, collection pages): the tab doesn't cover a header.
  5. Reduce Motion: fade.
  6. A saved Top reads as Corner.
  7. N2: Classic Rows collection, Down to row 2, and its heading shows.
  8. N3: Back from a collection, then Up within 0.6 s, lands on the row above.
- **Release notes:** Settings › Appearance › Rail Position is now **Centre / Corner** (Corner replaces Top; a saved Top becomes Corner). Default Centre. No other new settings.
- **Comms:** after the merge, a short DM to Steven with a screenshot of Corner, through SlopMonster, NOT SENT until Christian's go.

## Risks

- **Glass morph:** `glassEffect` may redraw or flicker while its frame height animates; the device pass decides. The fallback is a plain material plus a stroke during the morph.
- **Header overlap** in Corner (N1, above).
- **N3 double move** if the engine's own move lands after the check; that's what the deferral is for.
- **Free-team provisioning expires 10-22 00:23 EST**; the first device build after that re-signs.
