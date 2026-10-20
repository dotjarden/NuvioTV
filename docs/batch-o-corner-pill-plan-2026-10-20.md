# Batch O: Corner rail redesign (plan, 2026-10-20)

**Status: APPROVED 2026-10-20 as mocked; building.**

Christian, after Batch N's device pass:
- He doesn't want the grey box around the resting Home icon.
- He wants the open rail to look as close to the Centre rail as possible.
- The glass should surround only the icons, or the icons and labels, never the whole top-left corner.

Mock: `docs/research/batch-o-corner-pill-mock-2026-10-20/corner-pill-mock.png`. Paths are under `NuvioMobile/iosApp/NuvioTV/DesignSystem/`.

**Decided 2026-10-20:**
- Open rail = **the Centre rail's pill**, at the Centre rail's left edge, anchored at the top.
- Resting Home glyph gets a **soft shadow**.
- With Labels Shown, the rest state is **the Home icon only**.
- Keep the **unroll**: the pill grows down from the Home icon.

## What changes

**At rest (Corner + Always Visible, both Rail Labels modes):**
- Only the Home glyph, with no glass, no box and no label.
- A soft dark shadow on the glyph alone (about radius 4, y 2, black at 0.5–0.6 opacity), so it reads on bright artwork.
- It sits exactly where the open pill's Home icon will be, so nothing jumps on open.
- Not focusable at rest, as today (the rail arms on Menu or Left).
- Hidden still shows nothing at rest.

**Open:**
- The **same pill as Centre** (`pill`, `NavigationRail.swift:533`):
  - padding 12 horizontal and 22 vertical;
  - item spacing and avatar gap unchanged;
  - width 84 with Icons Only, 300 with Labels Shown (`RailMetrics.collapsedWidth` / `expandedWidth`);
  - `RoundedRectangle(cornerRadius: 42)` with `glassEffect(.regular)` and all four corners rounded;
  - the same focus capsule and label behaviour.
- Placed `bezelInset` (16 pt) from the left edge, like Centre.
- Top: the pill's top edge sits so the Home glyph lands on the tvOS top safe-area line (pill top ≈ 60 − 22 = 38 pt).
- The pill is never flush to an edge and never covers more than the icons, or icons and labels.

**Animation:**
- Opening: the glass fades in as a Home-sized pill (84 × 104, a capsule around the Home icon), then grows down to the full column height. With Labels Shown it widens to 300 at the same time, as the Centre pill widens today.
- The lower items keep their top-to-bottom fade.
- The selected tab's item is still never faded (the Batch N r1 P2-1 rule: focus is written to it while the rail opens).
- Closing reverses this: it shrinks back to the Home pill, then the glass fades out, leaving the bare glyph.
- Reduce Motion: a fade, with no grow.
- The Orivio rule stays: items never move; only the glass's frame and a top mask animate.

**Unchanged:**
- The Corner position setting, the `top` → `corner` migration and the reserved inset of 0.
- `RailFocusPolicy`, the dim, and the Centre rail itself.

## Work

- **One Opus agent** in a clone `NuvioMobile-batch-o` off `34c538545` (`claude/batch-o`). It touches:
  - `NavigationRail.swift`: rewrite `cornerPanel` / `cornerItem` / the Corner `RailMetrics` (`cornerTab*`, `cornerExpandedWidth`, `cornerLeading` / `cornerTop` padding).
  - `NavigationChrome.swift`: only if a metric moves.
  - `NuvioTVTests/NavigationChromeTests.swift`.
  - `NuvioTVUITests/NavigationRailUITests.swift`: update `Rail12` / `Rail12b`. At rest the `navigation_rail_bounds` glass has zero opacity or height and the Home glyph sits at the pill's Home cell; open, the glass frame is x = 16, width 84 or 300, height = the column, and every corner is inside the screen with a gap.
- Settings copy for Rail Position becomes "…or at the top-left as a Home icon that opens into the rail". Strings in five locales (main session).
- **Gates:** NuvioTVTests, the Release + Debug sim builds, the Debug device build, and the Rail12 legs.
- **Opus review** to CLEAN.
- **Device pass** (Test 2), with screenshots side by side against the Centre rail:
  - rest (Icons Only and Labels Shown);
  - open (both modes);
  - opening from Settings and Profile;
  - the glyph on a bright backdrop;
  - Hidden;
  - Reduce Motion.

## Risks

- **Glass fading in and growing at once** may shimmer on hardware; the fallback is to fade in at full height under the mask.
- **A bare glyph over a white poster** is the case for the shadow; the device pass checks a bright hero.
- **Pill top at about 38 pt** puts the glass's top edge above the top safe area, as Centre's pill already sits outside the horizontal safe area. It's fine on overscan-off TVs; if it crops on Steven's TV, lower it.

---

## OUTCOME
