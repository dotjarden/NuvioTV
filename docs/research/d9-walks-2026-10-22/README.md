# D9 (BUG-206) walks and checks — 2026-10-22, `claude/d9-action-row`

Christian's decision D9 (20:05Z): the Cinematic Detail action row drops Liquid Glass (`.bordered` / `.borderedProminent` in a plain `HStack`), the tile-lift shadow stays. Built early while the rc12 cut is held. Commits `79e1a33cb` (the swap) + `5c08cd429` (review r1: comments, `actionRow` folded).

## Hitch walks (Animation Hitches, Release, Test 2, Steven's settings with numeric Bool args, Cinematic Detail walk: rail → Search → Severance → series Detail → 10 down / 10 up; `walks.sh` here)

| Run | Build | Knob | Hitches / app ms | max |
|---|---|---|---|---|
| t0-base-leg0 | `7239c706` (tip before D9) | 0 | **99 / 2069** | 166.8 |
| t1-base-leg4 | `7239c706` | `-debug.detailScrollAB 4` (bordered row + chips flat + dim off) | **46 / 1318** | 183.5 |
| d0-leg0 | `79e1a33c` (D9) | 0 | **70 / 1602** | 133.5 |
| d1-leg0 | `79e1a33c` | 0 | **69 / 1652** | 150.2 |

Reading: the bordered row alone takes the walk from 99 to 70 / 69 (−30 %); leg 4's further drop to 46 is the chips' glass and the dim ramp, which D9 leaves in place (both are separate knobs; the dim is the UX-6 overlay). The earlier cause-hunt §9 numbers (98 → 51) were leg 4, so they credited all three to the row; the D9 code comment and the tracker carry the split. The traces live in `~/Library/Logs/nuviotv-traces/d9-*.trace` (not committed).

Note on the earlier walks: the cause hunt's "Steven's settings" used `YES`/`NO` for the `@AppStorage<Bool>` keys, which the app ignores, so those walks ran with Test 2's stored values for the trailer, ring and headings settings (the Detail background trailer was ON). These four walks used `1`/`0` (the ring is visible on every launch shot, the Detail trailer stayed off).

## Device checks (Release `5c08cd429`-equivalent binary stamped `79e1a33c`; the fold commit changed no layout)

- **`.bordered` glyph states, White accent (`g03`–`g11`):** Play `.borderedProminent` white; compact buttons at rest = dark translucent platter, focused = light platter with dark ink. Watched active = filled `checkmark.circle.fill` in white at rest; In Library active = bare `checkmark` in white at rest; both inactive = dimmed glyphs (the "keep the dim" rule). Both active glyphs read dark on the focused platter. Row restored to inactive after (`g11`): Animals is not in the library and not watched.
- **Square corners (`g12`–`g16`, Corners set to Square in Test 2 for the check, then back to Rounded):** the icon buttons are equal squares at Play's height with `.bordered` too; the FEAT-82 label-frame rule holds on hardware. The Square UI leg (`DetailActionSquareUITests`, 4 / 0 / 1 skipped) passed on the simulator on the folded tip.
- **Trailer button absent on the Square visits (`g12`–`g16`):** the Watch Trailer button is gated on `model.trailerVideoURL`; on the two Square visits it never appeared (40 s, then a fresh open at 12 s), while the first visit of the same launch (Rounded, `g04`) had it, and the console carried no `[TrailerExtract]` line for the whole launch. See the log below for the Rounded re-check.

## Log

- 21:20Z Corners set back to Rounded in Test 2 (`q24` read, then deleted with the other navigation shots). The Animals page re-opened with Rounded (`g17-rounded-revisit-12s`): the trailer button is STILL absent, so the absence is not Square's. Within this one process the first Detail visit (Rounded, `g04`) had the button and the next three (two Square, one Rounded) did not, and the console carried no `[TrailerExtract]` line at all this launch: the first visit's URL came from `HeroTrailerResolver`'s cache, the later visits attempted no extraction and published nothing. Filed as BUG-222 (P3, to confirm with `-debug.trailerProbe YES`, which logs `hero resolve candidate=`). Not a D9 item: the button is gated on `model.trailerVideoURL` alone (`DetailView.swift:2183`).
- Test 2 left as found: Rounded, Animals not in the library and not watched, Steven's device-local args only for the session. The console stream stopped (the app with it).
- The pixel scan (`pngbox.py`, scratchpad) could not isolate the platters from the backdrop on these shots; the Square sizing is read by eye on the box and measured by the simulator leg.
