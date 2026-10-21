# Open items to public beta.19 — consolidated plan (2026-10-21 evening) — APPROVED 2026-10-21 (Christian: "complete the plan"; D1 yes, D2 after beta.19, D3 keep Square, D5 magnifier only; D4, D6, D7, D8 at their defaults)

One plan over everything still open: the Wave 3 work waiting on the box, Steven's rc11 verdict, the GitHub #9 / #10 addendum drafted in the other session (`docs/wave3-github-9-10-plan-2026-10-21.md`, NOT APPROVED there either), the older GitHub issues, and the public beta gate. It replaces nothing: the public beta plan (`docs/public-beta19-plan-2026-10-21.md`, APPROVED) stays the frame; this file is the work order inside it.

## 0. Where things stand

| Thing | State |
|---|---|
| `tvos-shared-extraction` | `6baddab46` = rc11 (build 143). Outer `main` pushed through `eaaa12b`. |
| `claude/wave3` (`~/Claude/Projects/NuvioMobile-wave3`) | `823450355`: BUG-199 remux fix (device PASS), BUG-199b dts-index seek fix (unit-proven, live seek owed), S6 leftovers (device PASS), BUG-208 Search fix (gate 2120/0, box probe owed). Reviews r1 / r2 CLEAN. **Not merged.** |
| `claude/up-skip-rebased` (`~/Claude/Projects/NuvioMobile-upskip`) | `0c05b6ab2`, nine commits replayed on rc11, gate green, net patch identical to the thrice-reviewed branch. **Device walk not run, not merged.** |
| The box | Last `ready.sh` REFUSED after the fourth Wi-Fi drop of the day (each after a 4K stream). Nothing on the box can move until it passes. |
| Steven | rc11 reply SENT 18:42Z. Owed from him: mpv at once or after seconds + one stream name (BUG-166 / 199); Search empty while typing or after a pause (BUG-208). Owed to him: the striped-tile correction line (next DM). |
| GitHub | #9 and #10 answered 18:58Z with promises (below). #7 / #8 fixed in rc11, "shipped" comment waits for a public build. #4 waits on mikeyunk. #3, #5, #6 have our comment last. |
| Tracker | 41 open rows (items JSON 12:10Z) + BUG-213 / 214 / 215 / FEAT-84 filed by hand this evening. P1: BUG-165 (close proposed), BUG-66 (Christian's soak), BUG-97 (reporter silent since 09-05). |

## 1. Decisions that gate work (Christian)

Each one blocks a line below; the plan assumes the default in brackets until told otherwise.

| # | Decision | Blocks | Default assumed |
|---|---|---|---|
| D1 | **Corner rail (S1):** build Steven's flush spec (top and left edges, opens downward) as a Corner-only layout, keeping Centre on the glass-hugs-content rule? | W3-11 | Yes: Corner follows the official app's column, Centre untouched (the public beta plan's §7 resolution). |
| D2 | **Redesigns (FEAT-81 Fusion Detail, UX-17 Wako / Netflix Home):** before beta.19 or after? | Wave 4 scope, the DM wording | After: beta.19 ships the current surfaces polished; the redesigns open the next cycle. Steven is told that plainly in the rc12 DM. |
| D3 | **Square button style:** keep, or drop it as he asks? | W3-12 | Keep; fix FEAT-82 in his config first, decide on the rig's screenshots. |
| D4 | **Icons Only tint:** darker than rc11's white 0.12? | S6 follow-up | Leave as shipped (he called it "fixed, prefer darker"); revisit in the design review. |
| D5 | **Search cold-start placeholder:** quieter (magnifier only, no prompt text) for the 1.1 s keyboard mount? | W3-13 | Yes, magnifier only on a cold start; XS. |
| D6 | **GitHub #9 / #10 addendum (W3-4..W3-10):** approve as drafted inside Wave 3, with its four defaults? | Phase 1b | Yes, as drafted (the other session's answers: scope = #9 + #10 only, inside Wave 3, no waiting on erdist). |
| D7 | **BUG-165:** close on the rc11 re-test (four short presses, native and mpv, no eject) with a note to Steven? | Tracker, DM | Yes; one line in the rc12 DM asking him to confirm on his remote. |
| D8 | **BUG-97 / BUG-62 / BUG-120:** reporters silent 6 / 8 / 3 weeks. Close as "no response" at the public release, or carry? | Release notes, tracker | Close at release with a note; reopen on any reply. |

## 2. Phase 1a — finish Wave 3 on the box (when `ready.sh` passes)

All in Test 2. One `ready.sh`; stop if refused. Shoot 4K / debrid items **last** in the session (the box drops off Wi-Fi after them).

| Step | Build | Check | Record |
|---|---|---|---|
| 1a-1 | `claude/up-skip-rebased` Debug (product exists at `iosApp/build/DerivedDataDevice`) | Folder pop → Up on Stage and on Classic Home, five tries each, no skip; the `[HomeUp]` probe lines. | `docs/research/wave3-device-pass-2026-10-21/README.md` |
| 1a-2 | `claude/wave3` `823450355` Debug | Search retry probe: an uncached query, `[SearchPerf] catalog … retry=ok`, the failure + Retry row above People when the add-on 504s. | same |
| 1a-3 | same | BUG-199b live seek: Animals Comet NF DV MP4, three repositions (forward, back, resume), landing on the boundary, no "two frames late" abort; `[Remux]` lines. Last, because it is a 4K debrid stream. | same |
| 1a-4 | — | Merge: `git fetch ~/Claude/Projects/NuvioMobile-wave3 claude/wave3:claude/wave3`, fast-forward into `tvos-shared-extraction`; then `claude/up-skip-rebased` on top (fast-forward; it was rebased on rc11, so it needs one rebase onto the wave3 tip first, in its clone, gate re-run). Push, delete both branches and clones, bump the outer pointer, push outer `main`. **No cut.** | tracker, memory |

Exit: `tvos-shared-extraction` = rc11 + Wave 3 code-only pieces + up-skip. Size: one rig session (~2 h) + the merge.

## 3. Phase 1b — the GitHub #9 / #10 addendum (W3-4..W3-10), from the other session

Included as written in `docs/wave3-github-9-10-plan-2026-10-21.md`; the summary here is the work order, that file is the spec. Lands on `claude/wave3` **after 1a-4** in a fresh clone off the merged tip (the wave3 clone is deleted at the merge), branch `claude/wave3b`, so the addendum's device pass is its own session and the already-passed Wave 3 pieces do not wait on it.

| # | Item | Promise on GitHub | Owner, size |
|---|---|---|---|
| W3-4 | BUG-200 Detail Production and Cast rows lift the whole tile, both ring settings | Yes, both rows, both settings | Opus, M (`DetailView.swift` only) |
| W3-5 | BUG-201 subtitle colour swatches get the Appearance focus treatment | Yes | Sonnet, S |
| W3-6 | FEAT-83 hold menu on season and episode covers (Mark Season / Episode Watched or Unwatched, Mark Previous Episodes Watched) | "a coming build" | Opus, M |
| W3-7 | BUG-213 API key field and Save as two rows (plus the Plugins repository URL + Install row and the badge-pack import row); **step 0 on the box: does Select on the TMDB key row open the keyboard today?** | Yes | Sonnet, M |
| W3-8 | BUG-214 OLED True Black on Add-ons | Yes | Sonnet, XS |
| W3-9 | BUG-215 focused pane row clipped at the List's left edge; step 0 = sim + box screenshots in Default and Minimal | "a pane check on sim and device" | Sonnet, S |
| W3-10 | FEAT-84 languages A–Z (74 codes), Fallback Audio Language = None, Fallback Subtitle Language = None, Off stays Off | Yes, all four | Sonnet, M |

Waves as the addendum sets them: A1 (W3-4 + W3-6, Opus) beside A2 (W3-5, W3-8, W3-9, the plugin-row and badge-row halves of W3-7, Sonnet); then B (the `DebridKeyEntryRow` split + W3-10, one Sonnet). Opus critique first, r1 / r2 reviews to CLEAN, gate (Kotlin, 2,100-odd tests, Debug + Release sim, UI legs compile), then the device pass listed in the addendum's gate 4, in Test 2, plus W3-7 step 0 **before** the build. Fast-forward, no cut.

The four defaults the other session took stand unless D6 says otherwise: Mark Previous Episodes Watched included; the 76-entry language picker stays a Menu unless the sim scrolls it badly; BUG-200 = the whole tile scales together, ring on the artwork; the shared NONE + secondary behaviour is guarded on tvOS and noted for an upstream report.

Size: two agent waves + one Sonnet wave, ~1 day of agent time, one rig session.

## 4. Phase 1c — Steven's rc11 items (same cycle, before rc12)

These are what the rc11 DM and the public beta plan already promised him, plus his new P2 / P3s that are cheap enough to carry. They run **beside** Phase 1b where the files are disjoint (rail / Home / Detail-config checks do not touch the addendum's Settings and Detail-row files; W3-12 and W3-4 both touch `DetailView.swift`, so W3-12 waits for W3-4).

| # | Item | What | Owner, size | Gate |
|---|---|---|---|---|
| W3-11 | **S1 Corner rail per Steven's spec** (FEAT-80) | Corner layout: pill flush to the top and left edges, the rail expands downward; Centre and Edge untouched; Labels Shown and Icons Only both. Opus critique on the layout before code (the glass rule vs his flush column = D1). | Opus, M (`Rail*` files only) | sim A/B shots in both styles; rig shots over a dark and a bright hero |
| W3-12 | **Re-test the Cinematic Detail trio in HIS config** (FEAT-82 icon sizes, BUG-194 two moves back from an actor, BUG-206 choppier Cinematic Detail) | Install his Appearance table (`docs/steven-beta19-rc10-reply-2026-10-20.md`) + Open Sans + Icons Only + Square + Cinematic in Test 2 on the merged tip; walk cast → biography → Back with `moves=`; measure the Detail open and first scroll with `xctrace` Animation Hitches against the Wave 2 numbers; screenshot the button row. **Then** code: whatever differs. | Main session on the rig (S); fixes Opus (S–M each) | the re-test record first; no code before it |
| W3-13 | **S2 Card Depth made cheap** (UX-16 / BUG-153 remainder) | Pre-rendered edge + sheen per card size, or one layer; measure with `walk-home.sh` against the Wave 2 baseline (off = 120 hitches / 3.89 s; on = 146 / 4.76 s / 11 long stalls). Default stays on. | Opus, M (`CardDepthStyle.swift`, `StripPager.swift`) | `walk-home.sh` + `compare.py`, Release build |
| W3-14 | **Classic Home trio** (BUG-209 heading lands high and drops a notch; BUG-210 previous title's logo and synopsis linger ~0.7 s under a collection's logo; BUG-211 catalog name twice on a collection tile) | BUG-209: the pinned-row heading landing above its rest (the BUG-61 / rest-law class); first suspect = Wave 1's FEAT-61 pinned geometry on Classic with Hide Titles. BUG-210: the hero's text swap is keyed late for folder tiles; clear it with the logo. BUG-211: drop the name line under the logo when the row heading already shows it, larger logo (his ask). | Opus, M (Classic Home hero + pinned row files; not `HomeView.swift` without a critique) | sim screenshots; rig walk in his Classic config with the 4 fps sheet |
| W3-15 | **BUG-153 first Down too abrupt** | Ease the first press on Home (and Detail) to match presses 2–3. | Sonnet, S | rig: his video's cadence |
| W3-16 | **BUG-207 stream picker scroll** | Measure the picker with Animals' 40-row list (`xctrace`); likely the tall multi-line rows with flags re-laid per focus move; cache the row layout. | Sonnet, S–M | hitch numbers before / after |
| W3-17 | **BUG-205 Watched icon colour lag** | The Watched button's tint animates on a longer curve than its neighbours; match it. | Sonnet, XS | sim |
| W3-18 | **BUG-195 quieter cold-start placeholder** (D5) | Magnifier only until the UIKit field mounts; no prompt text on a cold start. | Sonnet, XS | sim + rig cold start |
| W3-19 | **Probe cap finding** (BUG-166 / 167): the stream probe hit its 4 s cap once in four opens on a debrid link and routed to mpv silently | Log the cap hit as its own `[Router]` line, and raise the question with Steven (his stream name decides whether his films hit the cap or BUG-199's handover). Code change only if his answer says the cap: then a longer cap on a confirmed-reachable host, or a visible "Apple TV player unavailable for this stream" toast. | Main session, XS now; M if the cap | his answer |

W3-15..18 are small enough to ride in Phase 1b's Sonnet wave B if the files are free; W3-11, 13, 14 are their own Opus agents. Critique → agents → gate → r1 / r2 → device pass in Test 2 in **Steven's config** (the rc11 lesson: the rig passed three items his box did not, because the config differed).

## 5. Phase 2 — rc12, DM, soak, walkthrough, design review

1. **Cut rc12** on Christian's go only: `scripts/cut-rc.sh beta.19-rc12` after `--preflight`; translation pass first if any new catalog entry is untranslated (W3-6 labels, W3-10's two rows and explainers).
2. **DM to Steven** (SlopMonster 5/5, NOT SENT until his go), carrying: the striped-tile correction (one line); Corner rail done per his spec; the Detail trio re-tested in his config and what changed; Card Depth; the Classic Home trio; the native player fix (BUG-199) and the probe question if still unanswered; the new settings with defaults (Fallback Audio Language = None, Fallback Subtitle Language = None; the A–Z list; hold menus); BUG-165 asked to confirm (D7); the redesign answer (D2).
3. **Soak starts** (Christian, his own profile, five days on rc12's Release build; BUG-66 Tabs long session included).
4. **Walkthrough** (public beta plan §5, both looks) and **design review** (§6, Opus per surface + Christian's eye; `design-council` optional).
5. **UI legs run in full once** (they have only compiled since Batch M).

## 6. GitHub issues — what closes each

| Issue | Tracker | State | Closes when |
|---|---|---|---|
| #3 pinned hero leaves the tab bar offscreen | BUG-66 class | our comment last | the soak's Tabs long session is clean → close with the beta.19 build |
| #4 Xperience add-on | BUG-120 | waiting on mikeyunk since 10-01 | his data, or D8 at release |
| #5 SenPlayer | FEAT-56 | shipped in rc11's Batch D; held refresh in `docs/comms-github-issue5-reply-2026-10-21.md` | post the refresh with the public build; close |
| #6 streaming jitter | BUG-172 | lead: movenc rewrites fragment keyframe pts (Wave 3 critique); Wave 3's grid rewrite changes the boundary; unverified against his files | after 1a-3 and his files: a rig measure on a 23.976 MP4, then a comment asking him to try the public build |
| #7 Plugins per provider | BUG-197 | fixed in rc11 (erdist's patch, credited) | "shipped" comment at the public build; close |
| #8 trailer on Play | BUG-198 | fixed in rc11 | same |
| #9 Detail rows, swatches, hold menu | BUG-200 / 201 / FEAT-83 | answered 18:58Z, W3-4 / 5 / 6 | one comment when Phase 1b lands (he builds from source; the `tvos-shared-extraction` tip is enough), close at the public build |
| #10 Settings focus, OLED, clipping, languages | BUG-213 / 214 / 215 / FEAT-84 | answered 18:58Z, W3-7..10 | same, plus the W3-7 step-0 result if the box differs from the sim |

Every GitHub comment is drafted in `docs/comms-github-*.md`, linted 5/5, posted only on Christian's go.

## 7. Phase 3–5 — Wave 4, release, first 72 hours

Unchanged from the public beta plan: Wave 4 = the findings from rc12 (Steven, soak, walkthrough, design review), P1 / P2 only; rc13 if anything shipped; release per §4 phase 4 (README + screenshots, highlights at 5/5, `release-beta.sh`, Reddit block, Steven DM, GitHub closes); the sweep daily for 72 h. Optional Codex pass on the whole beta.18 → beta.19 diff when the quota returns 10-29.

## 8. Order

| Order | Work | Needs |
|---|---|---|
| 1 | Phase 1a (box) → merge | `ready.sh` |
| 2 | Phase 1b agents (W3-4..10) in a fresh clone; W3-11 (S1) and W3-13 (S2) beside it as their own Opus agents on disjoint files | D1, D6 |
| 3 | W3-12 re-test in Steven's config on the rig (same session as W3-7 step 0 and W3-9 step 0) | box |
| 4 | W3-14..19 as the fixes come; W3-12's code after the re-test | D3, D5 |
| 5 | Gate, r1 / r2, device pass in Steven's config, merge | box |
| 6 | rc12 cut + DM on the go; soak, walkthrough, design review, UI legs | D2, D7 |
| 7 | Wave 4 → rc13 → release | gate §3 |

Parallelism: at most two agents concurrently, builds serialised through `with-lock.sh`; the rig is one session at a time; nothing 4K on the box before the last item of a session.

## 9. Open rows not in beta.19 (next cycle, told to Steven as such)

FEAT-81 Fusion Detail and UX-17 Wako / Netflix Home (D2); FEAT-66 collection logo on the right; FEAT-69 full-screen poster browse; FEAT-74 per-source player choice; FEAT-75 mpv Atmos; FEAT-60 compact logo on scroll; FEAT-36 collections from the Home menu; FEAT-41 depth sliders; FEAT-33 60 fps folder rows; FEAT-16 app font (partly done: Open Sans); FEAT-3 TestFlight; BUG-178 the shadow; BUG-181 Animals thumbnails / Atmos; BUG-180 menu animation; BUG-169 player overlay choppy; BUG-167 12–14 s to first frame (measured, P5 helped); BUG-160 cold-launch focus row; BUG-150 folder stage art; BUG-113, BUG-37, BUG-104, BUG-129, BUG-143 (in-house P3s).

## 10. Records

This file; the addendum `docs/wave3-github-9-10-plan-2026-10-21.md`; the Wave 3 record `docs/wave3-plan-2026-10-21.md`; device passes under `docs/research/wave3-device-pass-2026-10-21/` and a new `docs/research/wave3b-device-pass-<date>/`; the tracker and `docs/beta-feedback-items.json`; comms under `docs/comms-*`.
