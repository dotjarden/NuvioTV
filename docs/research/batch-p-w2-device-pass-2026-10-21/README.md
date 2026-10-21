# Batch P Wave 2 device pass, 2026-10-21 02:10–02:40Z (Test 2, Living Room, tvOS 27.2)

Build: `claude/batch-p-w2` `d2c99e30c`, Debug for the visual items, Release for the walks. Steven's look stays in Test 2 (Medium+, Hide Titles, Card Depth, OLED); Rail Corner + Labels Shown by launch argument unless noted. Probe lines come from `-debug.searchOpenProbe YES` / `-debug.trailerProbe YES`.

| Item | Result | Evidence |
|---|---|---|
| **BUG-195 Search placeholder, Rail Corner** | PASS on timing, six visits: `placeholder shown` 61–76 ms after the rail select (with `appear`), `hidden reason=signal` at **+1.08 to +1.17 s**, the rail's `keyboard` write 4–30 ms after it. Nothing of the black second is left uncovered. The hand-off ladder logs rung 0 at +0.13 s and "focus already landed" at 0.35 s, "still nowhere" at 1.0 s, as agent B's spike predicted. | `console-corner*.log` |
| BUG-195, Rail Centre / Always Visible | PASS, same timeline (+1.10 s hidden by signal). | `console-centre.log` |
| BUG-195, Tabs | PASS on timing (+1.09 s hidden by signal; no `keyboard` mark, that write is Rail-only). The real field sits at the same place as in Rail (x 104, prompt y ≈ 96 pt), so the shared constants line up. | `console-tabs.log`, `23-tabs-field` |
| BUG-195, the placeholder frame itself | **Not captured.** `devicectl` screenshot latency varied from < 0.3 s to > 2 s across seven attempts (frames landed on the open rail or on the mounted field). Geometry on hardware therefore rests on the sim's 1 pt match (before the safe-area rewrite) and the rewrite's arithmetic; Christian's eyes on the TV are the remaining check. | `10-*`, `12-*` |
| **BUG-198 series trailer gate** | PASS: with Background Trailer on and duration Always, the hero player was live on Sheriff Country (`attach live=1`), Play (`Next Up · S2E1`) → `[TrailerPipeline] teardown live=0` **100 ms after the press**, `view destroyed`; Menu back to Detail → `view created` / `attach live=1` again. A stream pick then loaded the player with no hero player alive. | `console-trailer2.log`, `32`, `33` (picker, not staged), `34` |
| **BUG-197 Plugins pane** (fixture `scripts/device/fixtures/plugin-repo-fixture.py`, four stub providers in scrambled order) | PASS end to end: install by manifest URL → the lone repository shows **expanded by default**, header "4 of 4 providers on"; providers listed `alpha provider`, `Provider 2`, `Provider 10`, `Zeta Provider` (Finder order, lowercase first); one toggle flips one provider → "3 of 4"; Remove Repository is its own row with the description pane; Select → the alert once, Cancel focused, Menu cancels with focus back on the row; header Select collapses (chevron right, count line, description "Select shows or hides…") and expands again; Right → Remove → the repository is gone, focus lands on the manifest field. Payload removed. | `48`, `51`, `52`, `53`, `55`, `56`, `57` |
| BUG-197 nits | (1) The focused destructive row's red label washes out on the white focus platter (`SettingsDestructiveRow`, shared component, pre-existing). (2) The "Installed Device-pass fixture repo." status line stays after removal (pre-existing `statusMessage`). | `52`, `57` |
| **Light tint, as shipped** (Release, no flag) | PASS: Icons Only pill luminance `YAVG` 75.9 over the dark hero (regular was 55.1, black tint 49.6). | `60-release-tint-icons` |
| Knob walks (Release) | see below | |

## Rig notes
- `-detail_trailer_autoplay YES` is the FULL-SCREEN auto-trailer; the background hero trailer is `-detail_trailer_background YES` with autoplay NO. The pipeline lines need `-debug.trailerProbe YES`.
- Settings: Account & Profiles is the first row (never Select it); Sources is six Downs; the Plugins section is ~30 Downs into the Sources pane; the manifest field's keyboard: `text=` sets the whole text, Done is three Downs from the letter row.
- Two Menus in a row from a page (rail open → root) eject to the tvOS Home and start the screensaver; a single Select wakes it.
- Companion dropped twice (`_systemInfo`, `Connect call failed`) and came back on the next command.

## Knob walks (Release `d2c99e30c`, his config, `walk-home.sh` 40 presses, Animation Hitches, window 14–50 s of each recording; traces `~/Library/Logs/nuviotv-traces/w2-*.trace`)

| Run | Hitches | Hitch time | Longest | ≥ 100 ms |
|---|---|---|---|---|
| Wave 1 build (2026-10-20, same window) | 146 | 5.87 s | 133 ms | 23 |
| **Wave 2 baseline, run 1** | **140** | **4.44 s** | 133 ms | **8** |
| **Wave 2 baseline, run 2** | **151** | **5.09 s** | 133 ms | **14** |
| `-debug.homeNoPageOpacity YES` | 167 | 5.06 s | 150 ms | 12 |
| `-debug.homeNoCardDepth YES` | **120** | **3.89 s** | **100 ms** | **1** |
| `-debug.homeNoStripEdgeMask YES`, run 1 | 447 | 10.79 s | 200 ms | 13 |
| `-debug.homeNoStripEdgeMask YES`, run 2 | 394 | 9.64 s | 150 ms | 17 |

Reading (two baselines put the noise at roughly ±5 % on the count and ±10 % on the time):
- **The fan-out cut shows in hitch time and in the long stalls, not in the count:** against the Wave 1 build on the same walk, hitch time is down ~19 % (5.87 → 4.76 s mean) and the stalls of 100 ms or more fall from 23 to 8–14. The count stays ~146: the Stage still hitches about 3.5 times per press, each one shorter.
- **Card Depth is the one knob that pays:** without it the count falls 18 %, the time 18 %, and the long stalls all but vanish (1). That is the CoreGraphics axial shading Wave 0 named. Steven runs Card Depth ON (Subtle / Soft, poster colour), so the Wave 3 target is to make Card Depth cheap (pre-rendered edge + sheen per card size, or a single layer), not to turn it off.
- **Page opacity is not a cost** (167 / 5.06 s is inside the noise of the baselines, if anything worse). Delete the knob in Wave 3.
- **The strip edge mask is a saving, not a cost:** without it the rows above the strip top composite over the stage and the walk hitches 2.7× as much on two runs. Keep the mask; delete the knob.
- The page-opacity recording crashed `xctrace` once (`libc++abi: terminating due to uncaught exception`, no trace); the re-run worked.
