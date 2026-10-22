# GitHub #9 and #10 "landed" comments (2026-10-22) — NOT POSTED

**Status: NOT POSTED.** The addendum (`docs/wave3-github-9-10-plan-2026-10-21.md` § Comms after it lands) owes erdist one comment per issue once Phase 1b is on `tvos-shared-extraction`. It is: `fccfabb3b`, merged 2026-10-22 16:05Z, not cut. Post only on Christian's go: `gh issue comment <n> --repo youngchris29-art/NuvioTV --body-file <file>`, then verify through `gh issue view`. Close neither issue yet (the plan closes them at the public build).

Facts behind the drafts (all device-passed in Test 2 on 2026-10-22 unless noted):
- #9 BUG-200: the symptom lived in the default cell only (ring off, zoom on). `CastCard` / `CompanyChip` resolve to the system lift there with the caption dropping, not a whole-tile scale, which brought BUG-54 / BUG-36 back. Avatar ×1.32 and chip ×1.118 measured on the sim. The ring path was already whole.
- #9 BUG-201: `SubtitleColorSwatch` carries the Appearance ring + `SwatchFocusLift`. The four swatches are four focus targets.
- #9 FEAT-83: `.contextMenu` on episode cards, season posters and season chips. Entries: Mark Episode Watched / Unwatched, Mark Previous Episodes Watched / Unwatched, Mark Season Watched / Unwatched. `heldEpisodeId` keeps focus on the acted-on card.
- #10 BUG-213: field and Save are separate rows for the TMDB / MDBList keys, the plugin repository URL + Install row and the badge pack URL + Import row (per-pack row + Delete Badge Pack). Focus hand-off Save → Remove, Remove → field. **Simulator only:** Test 2 has keys saved, so the box's rows showed Remove. Hardware unverified, and the comment says so.
- #10 BUG-214: Add-ons draws the app background. The new language pages and the MDBList lists page had the same gap and got it.
- #10 BUG-215: not reproduced on the sim (Default / Minimal, root / pane) nor on the box.
- #10 FEAT-84: the shared code list (77 codes) labelled by locale name, A–Z, sentinels pinned. Pushed list pages replaced the `Menu` because a tvOS `Menu { Picker }` opens on its first entry, not the checked one. Fallback Audio Language = None and Fallback Subtitle Language = None. The subtitle fallback row is hidden while Subtitles is Off, and `SubtitleFallbackGuard.isOff` keeps the player from applying it.
- README documents `local.properties` (BUG-218, erdist builds from source).
- No build named, no date. The public beta closes the issues.

Lint: see the bottom of this file.

## #9 — body

```
All three are in on the tvos-shared-extraction tip (fccfabb3b), if you want to build it ahead of the next beta.

Production and Cast rows. The caption now drops with the picture on both rows in the cell you were on (Accent Focus Ring off, No Zoom on Focus off), so the tile moves as one piece. The ring path was already whole. Measured, the avatar grows by about a third and the studio chip by about a tenth, which is where the system lift puts them.

Text Color swatches. Each swatch is its own focus target now, with the Appearance ring and lift, so you can see which one you are on before you pick it.

Hold menu on covers. Hold on an episode card for Mark Episode Watched or Unwatched and Mark Previous Episodes Watched or Unwatched. Hold on a season poster or a season chip for Mark Season Watched or Unwatched. Focus stays on the cover you acted on.

If you build from source: the README now has the local.properties step a fresh clone needs before sign-in works.
```

## #10 — body

```
All four are in on the tvos-shared-extraction tip (fccfabb3b).

1. API key fields. The field and Save are separate rows now, for the TMDB and MDBList keys, the plugin repository URL and Install, and the badge pack URL and Import. After Save, focus lands on Remove; after Remove, on the field. I could only exercise this on the simulator, because my Apple TV profile already has keys saved and its rows show Remove only. If the field still refuses focus on your hardware, tell me and I will look at the row again.

2. OLED on Add-ons. Add-ons draws the app background now. The new language pages and the MDBList lists page had the same gap and got the same line.

3. Clipped focused row. I could not reproduce it. On the simulator and on the Apple TV the focused row's platter overhangs the list edge uncut, in Default and in Minimal style, root list and panes. A screenshot with the pane name would let me find it.

4. Languages. The pickers show the full shared list, sorted A to Z by name, on a page of their own with the current choice scrolled into view, since a menu that long opens at its first entry rather than the current one. Fallback Audio Language and Fallback Subtitle Language sit under the first-choice pickers, both None by default. Off stays Off: the subtitle fallback row is hidden while Subtitles is Off, and the player ignores it then.

If you build from source: the README now has the local.properties step a fresh clone needs before sign-in works.
```
