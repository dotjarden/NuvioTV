# Design review pass (public beta plan §6) — 2026-10-22, merged tip `fccfabb3b`

**Why now:** the cut is held (Christian, 16:50Z); the review needs no cut, only the merged tip on the box. The build under review is the Release device product of `fccfabb3b` built from the main checkout (`iosApp/build/DerivedDataDeviceRelease`), installed over the Wave 3 device-pass build.

**Looks.** A = Steven's (device-local settings as launch args below; the synced ones are already set in Test 2: accent White, Card Depth Subtle / Soft / Full, Medium+, Rounded, Hide Titles, OLED). B = Test 2 as stored (no launch args; the "Chris" profile is off limits, so this stands in for "Christian's own look" and the review says so).

Look A args: `-sidebar_style rail -rail_visibility hidden -rail_position corner -rail_labels shown -rail_style floating -home_layout stage -ui_font system -accent_focus_ring YES -focus_ring_poster_color YES -depth_rail_poster_color YES -no_zoom_on_focus NO -row_edge_fade off -show_catalog_details_in_headings YES -settings_style default -detail_action_icons_only NO -detail_trailer_autoplay NO -detail_trailer_background NO -detail_layout cinematic`

**Rig rules in force:** `ready.sh` first; Test 2 only (the Release build auto-enters the remembered profile = Test 2 after the tear-down; confirm by the Lizzie Borden hero before any press); a screenshot before every press; `console.sh stop` kills the app (relaunch with `console.sh start` for each variant, which also terminates the previous instance); no Add-ons pane, no key values on screen; delete any shot that carries a URL or key; nothing 4K; leave Test 2 in Steven's config.

## Surfaces and shots

| # | Surface | Look | Route | Shots |
|---|---|---|---|---|
| 1 | Home, Stage | A | launch → rest; Down ×3 | `a01-home-stage-rest`, `a02-home-stage-row3` |
| 2 | Home, Classic | A (`-home_layout classic`) | launch → rest; Down ×3 | `a03-home-classic-rest`, `a04-home-classic-row3` |
| 3 | Rail, Corner Floating Labels | A | Left from the first card → open | `a05-rail-corner-float-labels` |
| 4 | Rail, Corner Floating Icons | A + `-rail_labels hidden` | same | `a06-rail-corner-float-icons` |
| 5 | Rail, Corner Edge Labels | A + `-rail_style edge` | same | `a07-rail-corner-edge-labels` |
| 6 | Rail, Centre Floating Labels | A + `-rail_position centre` | same | `a08-rail-centre-float-labels` |
| 7 | Rail, Centre Edge Icons | A + `-rail_position centre -rail_style edge -rail_labels hidden` | same | `a09-rail-centre-edge-icons` |
| 8 | Rail at rest, visible | A + `-rail_visibility visible` | launch → rest | `a10-rail-visible-rest` |
| 9 | Search | A | rail → Search; before typing; after `text=animals` | `a11-search-cold`, `a12-search-results` |
| 10 | Detail, film, Cinematic | A | top result → Select | `a13-detail-film-cinematic`, `a14-detail-film-down1` |
| 11 | Detail, film, Classic layout | A + `-detail_layout classic` | same route | `a15-detail-film-classic` |
| 12 | Detail, series | A | search `simpsons` → top result | `a16-detail-series`, `a17-detail-series-seasons` |
| 13 | Player panel | A | Play on Animals (native) → one Up for the app-drawn panel; skip if the panel does not open on Up | `a18-player-panel` |
| 14 | Settings root + Appearance + Subtitles & Audio | A | rail → Settings; Right into the pane; Down ×2 | `a19-settings-root`, `a20-settings-appearance`, `a21-settings-subtitles` |
| 15 | Home + Rail + Detail + Settings | B | the stored look, same routes | `b01-home`, `b02-rail`, `b03-detail-film`, `b04-settings-root` |

Square corners and Icons Only are synced settings: covered on the simulator by the Batch B / Wave 3 UI legs (`DetailActionSquareUITests`), not re-set on the box here.

## Review method

One read-only critique per surface against `docs/design/hig-hybrid-contract.md` and the chrome rule (glass hugs content, never a corner box; bare glyph at rest), each finding with a severity (P1 blocks the public build, P2 Wave 4, P3 next cycle) and the smallest fix. Findings go to `docs/design-review-2026-10-22.md`; P1 / P2 rows are filed in the tracker as the sweep's convention (UX- / BUG- ids), P3s listed in the review only.

## Log

(filled as the session runs)
