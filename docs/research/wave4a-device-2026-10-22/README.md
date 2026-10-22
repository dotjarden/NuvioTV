# Wave 4a device check — 2026-10-22, `claude/wave4a` (BUG-219, UX-18, UX-19)

Christian's call (22:05Z): fix the three design-review P2s before rc12. Release build stamped `8bb6e391` (the UX-19 predicate fix `c20c6bfdb` after it changes no layout), installed over the D9 build, Test 2, Steven's device-local settings as numeric launch args, Detail trailer off.

| Item | Check | Result | Shots |
|---|---|---|---|
| BUG-219 | Settings › Subtitles & Audio › Audio → language page → Menu | **PASS**: focus lands back on Audio (was Bold on `7239c706c`) | `w06-after-menu` |
| BUG-219 | the same two rows down: Subtitles → page → Menu | **PASS**: lands on Subtitles | `w08-after-menu-2` |
| UX-18 | The Simpsons (series) Cinematic Detail, the meta and ratings lines over the yellow key art | **PASS**: both lines read; the band's background luminance (lower quartile, x 0.04–0.52, y 0.455–0.535) 94 → 70 against the design-review shot `a16-detail-series`; the synopsis block and the art right of centre unchanged | `w17-simpsons-detail` |
| UX-19 | Stage Home launch: the logo lockup at 2 s and 9 s, no text title, no id | **PASS** on this launch (the logo was warm); the late-logo path and the id guard are unit-covered (`HeroArtResolverLateBackdropTests`, `HeroTitleTextTests`); the cold-cache case cannot be forced on the box without clearing the app's caches | `w01-launch-9s` |

## Review fixes re-checked (Release `c32669a6`, the r2 tip; the r2 follow-up `7acd8c008` changes only the own-id match and a test)

- **Stage trailer still arms with a logo (review r1 P1):** the first Wave 4a build keyed the swap core's rest on the logo-aware key, which would have stopped the hero trailer arming on any title with a logo. On the fixed build the hero trailer plays on Lizzie Borden (a title with a logo) 20 s after a Right + Left (`r04-after-right-left-20s`, the courtroom frame; the hero region's luminance matches the D9 launch that showed the trailer). On a launch with NO input it had not armed within 55 s (`r00`–`r03`); the D9 tip showed the same split (2 of 4 input-free launches armed), so the launch case is the pre-existing rest/focus timing, not Wave 4a. The `trailer arm key=` probe line never reached the console on either build.
- **BUG-219** holds on the r2 build (not re-walked; no code in that path changed after the first pass).
- **UX-18 baked shelf (review r1 P2-6):** the masked gradient pair became one 192 × 108 bitmap stretched over the screen; on the box the Simpsons page reads the same as the masked build (`r09-simpsons-detail-baked`: band lower-quartile luminance 70 vs 71 on `w17`, both against 94 before UX-18).

Rig notes: a Right press on the recents row at 0.8 s after a Select landed as a hold and opened "Remove from history" on a chip (`w12`, dismissed with Menu, nothing removed); the Simpsons search's Series row is five Downs from the chips (not four as in the Severance walk). Test 2 left as found.
