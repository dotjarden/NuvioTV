# Batch P Wave 1 device pass, 2026-10-20 (Test 2, Living Room, tvOS 27.2)

Probe lines (`-debug.detailFocusProbe YES`, batch Debug build 911dae1ef + probe log lines), cast → biography → Back, twice, then studios → studio page → Back:

```
2026-10-20 21:24:09.129  [DetailPop] live row=cast key=5
2026-10-20 21:24:09.161  [DetailPop] rung applied row=cast key=5 force=1 t=32
2026-10-20 21:24:09.490  [DetailPop] rung applied row=cast key=5 force=1 t=360
2026-10-20 21:24:09.931  [DetailPop] rung applied row=cast key=5 force=0 t=802
2026-10-20 21:24:10.446  [DetailPop] end row=cast key=5 moves=3 held=0 landed=585 focused=cast idx=5
2026-10-20 21:25:04.550  [DetailPop] live row=cast key=5
2026-10-20 21:25:04.582  [DetailPop] rung applied row=cast key=5 force=1 t=32
2026-10-20 21:25:04.911  [DetailPop] rung applied row=cast key=5 force=1 t=361
2026-10-20 21:25:05.353  [DetailPop] rung applied row=cast key=5 force=0 t=802
2026-10-20 21:25:05.879  [DetailPop] end row=cast key=5 moves=3 held=0 landed=589 focused=cast idx=5
2026-10-20 21:25:35.047  [DetailPop] live row=logos key=1
2026-10-20 21:25:36.350  [DetailPop] end row=logos key=1 moves=1 held=0 landed=589 focused=logos idx=1
```

## Results

| Item | Result | Evidence |
|---|---|---|
| BUG-194 pop gate, cast row | PASS, deterministic across two runs: restore live → forced rung applies at +32 ms and +361 ms, the row lands at +585/589 ms, focus leaves the row once (the non-forced rung at +802 ms finds the cast state nil and pulls it back), the restore ends at +1.3 s on the right card with nothing held (`moves=3 held=0`). The rungs do the work; no `.defaultFocus` is involved. | probe lines above; `08-cast`, `10-pop-early`, `11-pop-settled` |
| BUG-194 pop gate, studios row | PASS: no rung needed, one move, landed at +589 ms (`moves=1`). | probe lines; `12-studios`, `14-studio-pop` |
| **FEAT-35 regression (new)** | **FAIL on the batch build, fixed in-pass.** A Detail with a long synopsis (Dune, from Search) opened with the synopsis teaser focused, not Play. Pre-batch build (`44200c23a`, A/B on the box): Play. Cause: the two `.defaultFocus(..., priority: .userInitiated)` the BUG-194 wiring added with a sentinel value; the engine honours them, matches no card and falls to the first focusable item. Fix: removed them (root and `DetailPosterLinkRow`); the rungs restore the pop (row above). Rebuilt, NOT re-walked (rig refused). | `39-dune-detail` (batch: teaser focused) vs `70-baseline-dune-detail` (Play) |
| **FEAT-82 square buttons** | **FAIL on the batch build, fixed in-pass (unverified on the box).** With `-debug.posterCornersOverride square` + Icons Only, the three icon buttons rendered as one continuous bar: abutting with hairline seams, 92 pt wide, 70 pt tall against Play's 80 pt. The fixed `side × side` frame sat on the Button, and the button style draws its platter outside that frame. Fix: the padded icon label is the square (side = Play's padded label height), the style adds the same insets to every button. | `21-crop-buttons` (square) vs `04-crop-buttons` (rounded) |
| BUG-193 synopsis sheet | PASS: the backdrop under a 0.72 scrim, logo top-left, the full synopsis legible. | `41-dune-sheet` |
| FEAT-61 four lines at Medium+ | PASS with the system font (Lizzie Borden's Home hero: four lines + ellipsis; Dune's Detail teaser: four lines). Open Sans not shot (rig refused before the `-ui_font openSans` launch). | `00-launch`, `39-dune-detail` |
| FEAT-80 Rail Style Edge | PASS in both positions: flush left, square outer corners, rounded inner corners; Corner keeps the top (y 38), Centre the vertical centre; the Corner rest glyph moves in to the edge (≈12 pt). | `50`–`53` |
| FEAT-80 Icons Only glass (P3/P10) | Over the Stage's dark hero, `regular`, `clear` and a black `tinted` are indistinguishable near-black pills; `material` has no visible platter at all. The Labels Shown pill reads lighter only because its 300 pt reaches over the artwork; the 84 pt pill sits on the Stage's black left margin, where glass is black (= BUG-196). `tinted` is now a WHITE 0.12 tint, to shoot next. Bright-hero shots were missed: Left from the second card moves a card instead of opening the rail (open it from the Upcoming row instead). | `glass-sheet-dark-tight`, `37-left` (labels) |
| Hitch walk vs Wave 0 (153 / 5.72 s) | NOT RUN (rig refused before the Release build went on). Release build of the fixed tree is built in the clone. | |
| `[SearchOpen]` timings (BUG-195) | NOT RUN (same). | |
| Stage folder title (BUG-190) | NOT RUN (same). | |

## Rig notes
- Select on a Continue Watching card opens the stream picker, not Detail; use a collection poster or Search.
- Detail opened from a Test Collection poster expanded its hero trailer full screen and ate the Downs; relaunch with `-detail_trailer_autoplay NO -detail_trailer_background NO` for Detail walks.
- Corner rail (Labels Shown, glyph at rest): Menu at the Home root scrolls to the top and does NOT open the rail; Up from the first row does not reach the glyph; **Left from the first card opens it** (`[NavRail] arm reason=left`). Series row in Search = 4 Downs (Top result prefers films).
- The BUG-194 probe label is invisible on hardware; the pass added `[DetailPop] live|rung applied|end` NSLog lines under the same flag.
- The submodule's `DerivedDataDevice` had package artifacts resolved into a deleted clone; `-clonedSourcePackagesDirPath` at the batch clone's `SourcePackages` fixed the baseline build.
- 21:3xZ: pyatv Companion lost the box ("Host is down") while the devicectl tunnel kept answering; `ready.sh` refused (re-pair with `pair.py`). Device steps stopped there per the standing rule.

## Part 2 (2026-10-20 21:50–22:15Z, Companion came back on its own; no re-pair was needed)

| Item | Result | Evidence |
|---|---|---|
| FEAT-35 re-walk (fixed build) | PASS: Dune from Search opens on Play, the teaser unfocused. | `80-fix-dune-detail` |
| FEAT-82 re-walk (fixed build) | PASS: three equal icon squares (≈129 × 90 pt platters, equal widths, 5 pt taller than Play's platter), normal gaps. | `80-crop-buttons` |
| BUG-195 `[SearchOpen]` | Measured twice: tab select → `appear` +66 / +83 ms → `firstBody` +68 / +110 ms → `keyboard` **+1.13 / +1.13 s**. The page's body exists within 0.1 s; the search keyboard reports focus 1 s later. The black ~0.9 s is the keyboard mount, not the page. | `console-fix.log` lines |
| FEAT-61, Open Sans | PASS: `-ui_font openSans` gives **five** synopsis lines at Medium+ on the Home hero (the slot fits five of the narrower Open Sans lines; the system font gives four). | `90-opensans-home` |
| BUG-190 Stage folder title | PASS: the folder name sits as a small heading above the focused title's logo slot (empty when the title has no logo), on row 1 and row 2 alike. | `96-folder-page`, `97-folder-logo`, `98-folder-row2` |
| Glass, light tint (white 0.12) | **PICK.** On the rebuilt Debug build the collapsed Icons Only pill reads as a visible mid-grey glass over the dark hero and the sunset hero alike: pill luminance `YAVG` 75.9 / 78.6 against 55.1 (`regular`) and 49.6 (black tint). (`92`/`94` were shot on the pre-tint build and are pixel-identical to the black tint, 49.6.) | `100-lighttint-dark`, `101-lighttint-bright`, `glass-sheet-tints` |

**Hitch walk, Release build of the fixed tree (`3cf873994`), his config, same `walk-home.sh`, Animation Hitches, each run over its own 40-press window (single runs; ±10–15 % is noise on this protocol):**

| Run | Hitches | Hitch time | Longest | ≥ 100 ms |
|---|---|---|---|---|
| rc9 (Wave 0, 20–58 s) | 145 | 5.46 s | 150 ms | 19 |
| rc10 (Wave 0, 20–56 s) | 172 | 6.19 s | 167 ms | 20 |
| **Batch P, his config (14–50 s)** | **146** | **5.87 s** | **133 ms** | **23** |
| rc10, fade off + trailers off (Wave 0, 20–55 s) | 147 | 5.12 s | 133 ms | 12 |
| **Batch P, fade off + trailers off (15–52 s)** | **157** | **6.07 s** | **150 ms** | **24** |

Reading: the P1 trio (letterbox analysis off main, publish guards, URL memo) made **no measurable difference** on this walk. The count is back at rc9's level in his config and worse in the fade-off variant; hitch time and the number of ≥ 100 ms stalls are unchanged or worse. The Stage floor of ~3.5 hitches per press stands, which matches Wave 0's profile: the bulk was AttributeGraph re-evaluation and CPU rasterisation (gradients, masks, offscreen passes), with image-on-main a small slice. The rest of P1 (strip pager fan-out, the string-scanning caller, the mask / page-opacity / Card Depth A/B flags) is where the time is. The two Batch P traces are `~/Library/Logs/nuviotv-traces/batchp-home-hitches*.trace`.

Rig notes, part 2: the box dropped off Wi-Fi three times in 25 minutes (Companion "Host is down" / `_hidC failed`, xctrace "Timed out waiting for device to boot"); each time it came back within a minute and `ready.sh` reported READY. A single retry worked twice. Record with the walk started 15 s after `xctrace record --launch`; the presses then fall in ~14–50 s.
