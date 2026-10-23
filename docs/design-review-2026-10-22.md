# Design review pass — 2026-10-22, `tvos-shared-extraction` `7239c706c` (Wave 3 + BUG-221 hotfix)

Public beta plan §6: one read-only critique per surface against `docs/design/hig-hybrid-contract.md` and the chrome rule (glass hugs content, never a corner box; bare glyph at rest), with the rig's screenshots as input. Christian's own eye on the TV is the second half and is still owed. Shots: `docs/research/design-review-2026-10-22/` (the cited ones committed; `PLAN.md` there has the routes and the log).

**Looks.** A = Steven's (device-local settings as launch args, numeric Bools; synced ones as stored in Test 2: accent White, Card Depth Subtle / Soft / Full, Medium+, Rounded, Hide Titles, OLED). B = Test 2 as stored, no args (the daily-use "Chris" profile is off limits to the rig, so B stands in for Christian's own look). Both on the Release build of `7239c706` in Test 2.

**Not captured:** the player panel (needs a stream; the P5 device pass covered the native and mpv panels on 10-20), Square corners and Icons Only (synced settings; the Batch B / Wave 3 UI legs cover them on the simulator), Tabs mode (soak).

Severity: P1 blocks the public build, P2 Wave 4, P3 next cycle. Only P1 / P2 get tracker rows.

## Findings

| # | Surface | Sev | Finding | Smallest fix | Shots |
|---|---|---|---|---|---|
| D-1 | Detail, Cinematic (film + series) | **P2** → **UX-18** | The metadata line (year · runtime · genres · rating) and the ratings line have no contrast floor over a bright backdrop: over The Simpsons' yellow key art and over the Animals trailer's white graffiti wall both lines all but vanish; the synopsis survives because it is longer and sits lower in the scrim. | A readability floor for the left text column: extend the existing left-to-right scrim upward to cover the two lines (same gradient, taller), not a box or a text shadow. | `a16-detail-series`, `s24-detail-6s-after-menu` |
| D-2 | Settings, pushed pages | **P2** (BUG-219, now CONFIRMED on this tip) | Menu from a pushed language page lands on the first realised row of the pane (Bold), not the Audio row that pushed it. Every language / fallback row pays it. | `ClaimsFocusAfterSwap` rule on `SettingsListPickerRow` + `SettingsLinkRow` (code read in `docs/research/bug219-220-code-read-2026-10-22.md`). | `a21c-audio-language-page`, `a21d-after-menu-bug219` |
| D-3 | Detail, Cinematic, scrolled | P3 | FEAT-60's compact logo band overlaps the Parental Guide chips while they pass under it (Animals over "Frightening Scenes Moderate", The Simpsons over "Alcohol & Drugs / Frightening Scenes"). | Fade the compact logo to ~0 while any row's top edge is inside the band, or inset the scroll content by the band height while the logo shows. | `a14b-detail-film-down3`, `a17-detail-series-down3` |
| D-4 | Detail, trailer close | P3 | After the auto-played full-screen trailer closes on Menu the hero area is black for 2–6 s until the background trailer resumes (look B: both trailer settings on). | Keep the still backdrop visible until the background player reports its first frame. | `s24-detail-6s-after-menu` (the 2 s shot showed the black hero and was not kept) |
| D-5 | Detail, Classic layout | P3 | The Details block's Ratings line truncates ("… letterboxd 2.2 au…") and names providers in lowercase ("imdb", "tomatoes"), unlike Cinematic's "IMDb / Rotten Tomatoes / Metacritic / Trakt / Letterboxd". | Same labels as Cinematic, wrap to two lines. | `a15-detail-film-classic` |
| D-6 | Home, Stage hero | **P2** (raised 20:50Z) | While the hero trailer plays the logo lockup is replaced by a plain text title ("Lizzie Borden Took an Ax"); at rest the same title shows its logo. On one launch (D9 walk `d1-leg0`, 17:49Z) that text was the raw id **"tt3118958"**: the fallback resolved before the title did. | Keep the logo over the trailer (dimmed if the video needs the room); text only when there is no logo, and never an id (hold the last good title until the new one resolves). | `a01-home-stage-rest` vs `b01-home`; `docs/research/d9-walks-2026-10-22/launch-d1-leg0.small.png` |
| D-7 | Home, Classic, folder hero | P3 | The folder hero repeats the name: title "Test Folder", meta "Test Folder · 2 sources". | Meta line = "2 sources" (the BUG-211 rule, applied to the hero). | `a04-home-classic-row3` |
| D-8 | Appearance › Theme | P3 (verify by eye) | With White selected, the focused swatch and the selected swatch look alike at TV distance (the selection is the white label, the focus a thin ring). | The W3-5 subtitle-swatch focus treatment (ring + lift) on the theme swatches. | `a20-settings-appearance` |
| D-9 | Search, recents | P3 | The Recent Searches row runs under the right edge with no fade (Row Edge Fade = Off in Steven's config, so by setting; with the fade on it is fine). | None; note that Search follows the Home setting. | `a11-search-cold` |

**Seen once, not reproduced:** a Menu press after several Downs during a full-screen trailer popped the whole Detail page and landed on Search's keyboard (look A, 18:49Z). The controlled run in look B (open, wait for the autoplay, one Menu) returned to Detail as it should. Left out of the tracker until it repeats.

## What holds up (per surface)

- **Rail, all six variants (`a05`–`a10`, `b02`):** Corner Floating and Corner Edge sit flush top-left and open downward; Centre Floating is the pill off the edge, Centre Edge flat against it; Icons Only keeps the same column; Always Visible rests as the bare Home glyph with a soft shadow (the chrome rule); the focused item is the system white capsule inside the glass. The avatar sits inside the pill in every variant. Nothing to change.
- **Home, Stage (`a01`, `a01b`, `a02`, `a10b`):** logo lockup, "1h 29m left", synopsis, Continue Watching with the poster-colour ring on the focused card, the engine lift. Heading sizes match.
- **Home, Classic (`a03`, `a04`, `a04b`):** hero with "Go to Show" and page dots; rows with the ring; the badge chips ("#4 Today", Dolby, 4K) are dense but consistent.
- **Search (`a11`, `a12`):** field, inline keyboard, dictation hint and the recents at once (the BUG-195 placeholder is the magnifier only); results = suggestion chips, Top result, Movies · N.
- **Detail, Cinematic at rest (`a13`, `b03`):** logo, metadata, ratings, synopsis, the action row (Play + three icon buttons at one optical size, FEAT-82), studio chips, Parental Guide, credits right-aligned with the action row. The cast row lifts avatar + caption as one tile (BUG-200). Seasons / episodes / "13 aired unwatched" / spoiler blur on the series page.
- **Settings (`a19`–`a21b`, `b04`):** root list with the explainer column, white focused platters, the subtitle preview + four swatches with the focus ring (BUG-201), the Audio / Fallback Audio Language / Subtitles rows with the fallback subtitle row hidden while Subtitles is Off (FEAT-84).

## D9 (still Christian's call)

The Cinematic action row is Liquid Glass (`a13`): on the box it is the larger half of BUG-206's cost (98 → 51 hitches without the glass container; the tile-lift shadow is the other third). The contract allows `.glass` for actions over media, so keeping it is within the rules; dropping it to `.bordered` is the cheaper page. Nothing in this review changes that trade.

## Method notes

- Every surface was captured on the Release build after BUG-221's fix; the first Release of `fccfabb3b` crashed on Home (see the tracker).
- `@AppStorage<Bool>` ignores `YES` / `NO` launch arguments and honours `1` / `0` (`scripts/device` note in memory `rig-lessons-2026-10-21`). The first half of the session ran the Bool settings at Test 2's stored values; the cited shots are from the numeric-arg launches except the rail set (String args, unaffected).
- The critique is the session's own read (Opus-class), not a separate agent's; Christian's walkthrough on the TV is the second eye the plan asks for.


**Status 2026-10-23 ~00:30Z (Wave 4 held until the watch ends):** D-5, D-7 and D-8 are fixed on the parked `claude/wave4` (`f2b6c5c0b`, `09ab38b69`, `a86d7caab`; gate green, not merged). D-4 is diagnosed (the hero surface is revealed on the resume remount before its first frame; gate the reveal on `isReadyForDisplay`, device-verified) and D-3 needs per-row geometry near the band or a scroll inset; both wait for Wave 4. D-6 (raised to P2, filed as UX-19) shipped in beta.19 (`8bb6e3916` + `7acd8c008`); D-9 is by setting, no change.

**Status 2026-10-23 ~16:45Z:** D-5, D-7, D-8 MERGED (`769e2c55e`, not cut) and device-checked in Test 2 (`docs/research/wave4-device-2026-10-23/README.md`). D-3 and D-4 still open.

**Status 2026-10-23 ~19:35Z:** D-4 not reproduced on the Wave 4 tip in Test 2 (still up after the cover, no resume gap; `docs/research/wave4-device-2026-10-23/README.md`); stays P3 on the D9 shots. D-3 in progress (agent).
