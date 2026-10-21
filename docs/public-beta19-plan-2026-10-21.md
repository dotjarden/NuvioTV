# Public beta.19 plan (2026-10-21) — APPROVED by Christian 2026-10-21 ("Phase 0 is Steven's rc11 verdict; start Wave 3 when it is in")

**Goal.** Ship `tvos-v0.3.0-beta.19` publicly: the first public build since beta.18 (build 132, 2026-10-01). Everything between is eleven rc builds that only Steven has had. The release goes out only when the gate below passes; there is no date. Distribution stays the sideloaded IPA on GitHub (both repos), as beta.18 did.

**Christian's answers (2026-10-21):** scope = rc11 + Steven's promised items + the two reopened P1s; gate = his own soak and surface walkthrough plus a design review pass; channel = sideload IPA on GitHub; timing = when the gate passes.

## 1. What beta.19 carries (already in rc11, build 143)

Over beta.18: Stage Home + strip, Search & Discover on the Stage, Library L1, the Detail and Settings revamps, native player P1–P5 (remux, Dolby Vision P5 MP4, Sync Line, Boost/Dialogue, speed memory, post-play More Like This), SenPlayer and the upstream ports of Batch D, Rail Centre / Corner / Floating / Edge, Card Depth, Plugins per provider, five languages complete, and Steven's rc1–rc10 verdict batches (A–P). The full list comes from `git log tvos-v0.3.0-beta.18..tvos-v0.3.0-beta.19-rc11` at release time, scrubbed as `docs/comms-beta18-highlights.md` was.

## 2. Scope before the public build

| # | Item | Why it is in | Size | Owner |
|---|---|---|---|---|
| S1 | **Corner rail per Steven's reference** (FEAT-80): the official app's column, flush to the panel edge, vertically centred, logo top-left. rc11's Edge style already makes the pill flush in Centre and Corner; his rc11 verdict says what Corner still misses. Promised in the rc11 DM. | Wait for the verdict, then S–M | Wave 3 |
| S2 | **Card Depth made cheap** (UX-16 / BUG-153 remainder): the rig measured Card Depth as the one remaining Home cost (off = 120 hitches / 3.89 s / 1 long stall vs 146 / 4.76 s / 11). Steven runs it on, so the fix is a cheaper edge + sheen (pre-rendered per card size, or one layer), not a default change. Promised in the rc11 DM. Measure with `walk-home.sh` against the Wave 2 baseline. | M | Wave 3 |
| S3 | **Home Up-skip root cause** (`claude/folder-return-up-skip`, nine commits, base 98 behind, HomeView +293): rebase onto the tip, one Opus review round, the Stage and Classic Home UI legs, device pass. The intermittent Up-skip after a folder pop is a public-beta-grade annoyance. | M | Wave 3 |
| S4 | **BUG-165 (P1): a short Back tap ejects the app from the player.** His case was a DV P5 MP4 on mpv (Animals). Since P5 that file plays natively, so first re-test the exact case on rc11: if the eject is gone with the native path, close with that note; if mpv still ejects on a short Back, fix the Menu handling on the mpv exit (`[MenuProbe]` on, 100 ms Menu from the rig). | S to re-test, M if real | Wave 3 |
| S5 | **BUG-66 (P1): the tab bar stops auto-minimising.** Only Tabs mode; the T1 knobs from the rc1 batch were never device-checked. Re-verify on rc11 in Tabs mode over a long session; keep whichever candidate fix the check favours, or close as not reproducible on current builds with the probe numbers. | S | Wave 3 |
| S6 | **Knobs and leftovers:** delete the page-opacity and edge-mask knobs; the destructive row's label contrast on the white focus platter; focus after Remove Repository; the "Installed …" status line after removal; the Search placeholder's look on a real TV (Christian's eyes). | S | Wave 3 |
| S7 | **Whatever rc11's verdict, the soak and the design review surface** at P1 / P2. | — | Wave 4 |
| S8 | **BUG-199 (new, 2026-10-21): the native remux fails mid-play on a Netflix WEB-DL DV MP4** (`pts < dts` at segment 7 on packets with no pts) and hands over to mpv, so the film restarts seconds in. Fix the remux's pts/dts handling for these packets, or route the class to mpv from the probe. S4's re-test found it; S4 itself is done (four short presses on mpv, no eject). | M | Wave 3 |

Not in beta.19 (next cycle): FEAT-66 collection logo on the right, FEAT-81 Detail redesign, FEAT-73 one Discover catalog, BUG-181 Animals thumbnails / Atmos, BUG-180 menu animation, BUG-178 the shadow, FEAT-3 TestFlight, Watch Party (upstream, deferred).

## 3. The gate (all must hold on the build that ships)

1. **Steven:** his verdict on the final rc has no open P1 / P2 and nothing new of weight.
2. **Soak:** Christian runs the final rc's Release build daily in his own profile for at least five days: no crash, no eject, no stuck focus, no stall that makes him reach for the remote twice. Findings go to the tracker as they come.
3. **Walkthrough:** every row of the checklist in §5 marked PASS by Christian on the TV, with the rig's screenshots beside each.
4. **Design review:** the pass in §6 leaves no P1 / P2 finding open.
5. **Engineering:** Kotlin + 2,000-odd unit tests + Debug and Release sim green on the tip; **the UI legs run once in full** (they have only compiled since Batch M); a rig device pass of the final rc in Test 2 in Steven's look; crash logs pulled from the box clean.
6. **Catalog and docs:** no untranslated user-facing entry (true today); README features and screenshots updated; release notes through SlopMonster at 5/5; tracker and items JSON reconciled with the final rc.

## 4. Order of work

| Phase | What | Exit |
|---|---|---|
| 0 | **Steven's rc11 verdict** (owed): triage; fold his points into Wave 3 as S7 if small, or into Wave 4. | Triage record + tracker |
| 1 | **Wave 3** (S1–S6): a clone off the tip; S1–S3 as three agents on disjoint files (S3 is its own rebase clone first), S4 / S5 on the rig by the main session; Opus critique, two review rounds, gate, device pass in Test 2. Fast-forward. | Merged, not cut |
| 2 | **rc12**: cut, DM to Steven, and the **soak starts** (Christian installs rc12's Release build in his profile). While it runs: the **walkthrough** (§5) and the **design review** (§6). | Findings list |
| 3 | **Wave 4**: the findings from rc12 (Steven, soak, walkthrough, design review). Same loop. **rc13** if anything shipped; the soak clock restarts on the new build only for the areas it touched. | Gate §3 all green |
| 4 | **Release**: README + screenshots, highlights file (SlopMonster 5/5), detached Release build stamped with the tag, `scripts/release-beta.sh --skip-build --tag tvos-v0.3.0-beta.19 --prev-tag tvos-v0.3.0-beta.18 --changelog docs/comms-beta19-highlights.md`, strip the generated commit list from the notes on both repos, Reddit block + comment and the Steven DM on Christian's go, GitHub #5 reply posted and #7 / #8 closed with the build. | Public |
| 5 | **First 72 hours**: the sweep at its normal cadence plus a daily interactive read; anything P1 gets a point release (beta.19.1), as beta.13.5 did. | — |

Optional, when the Codex quota returns on 10-29: a Codex review of the whole beta.18 → beta.19 diff, run after Wave 4 and before the release build. Christian did not ask for it; it is cheap insurance on a diff this size.

## 5. Walkthrough checklist (Christian on the TV, rig screenshots beside)

Run twice: once in Steven's look (Stage, Medium+, Hide Titles, Card Depth, Rail Corner), once in Christian's own. Each row PASS / note.

- **Launch:** cold start to Home under 4 s on the box; the loading titles in the device language; the last profile remembered.
- **Home, Stage:** 20-row walk down and up without a stall that reads as a stutter; hero follows focus; trailers play and stop where expected; Continue Watching, Upcoming, collection folders and their pages; Menu to top; Back from a folder lands where you left (the Up-skip after S3).
- **Home, Classic:** the same walk; row headings; the Rows collections look; long synopsis lines.
- **Rail:** Centre and Corner, Floating and Edge, Labels Shown and Icons Only, Hidden at rest; open / close feel; the pill over a dark and a bright hero; Tabs mode once.
- **Search:** opens with its field visible at once; typing from the remote and from an iPhone; results grouped and per add-on; Discover entry; a Detail push and pop lands back on the card.
- **Discover and Library:** the Stage Discover page; Library grid and the Trakt / Simkl / MDBList lists in the device language.
- **Detail:** film and series, Rounded and Square corners, Icons Only and labels; synopsis teaser and the full screen; cast → biography → Back in one move; studios, seasons, episodes, trailers; a big page (Monstre) first scroll with the ring on.
- **Player, native:** a DV P5 MP4, a DV P8 MKV, a 1080p file; first frame time; the top panel; subtitles, Sync Line, audio delay; Boost / Dialogue; speed memory on a series; post-play screen and More Like This; exit on a short Back and on a hold (BUG-165).
- **Player, mpv:** the same file set; the HDR mode switch; exit paths.
- **External players:** Infuse, VidHub, SenPlayer handoff and the return.
- **Settings:** every pane once, each row's description, the destructive rows (Remove API Key, Remove Repository, Sign Out in Account & Profiles is read only), Plugins with a repository installed, the Appearance options round-trip.
- **Languages:** one full pass in French; spot checks in German and Vietnamese (Settings, Player panel, Plugins).
- **Long session:** the app left open for a day in Tabs mode (BUG-66) and in Rail mode; memory from the crash logs.

## 6. Design review pass

A structured critique against `docs/design/hig-hybrid-contract.md` and the chrome rule (glass hugs content, never a corner box), one Opus read-only pass per surface with the rig's screenshots as input, plus Christian's own eye on the TV: Home Stage, Home Classic, Rail (all variants), Search, Detail (film / series, both corner styles), Player panel, Settings. Each finding carries a severity and a smallest fix; P1 / P2 go to Wave 4, P3s are listed for the next cycle. The `design-council` skill is available for the critique if Christian wants a second voice on the aesthetics.

## 7. Risks and what we do about them

- **Scope creep from the verdicts.** Steven's rc11 and rc12 verdicts will bring new asks; only P1 / P2 on shipped behaviour enter Wave 4, the rest is filed for the next cycle and told to him as such.
- **The soak finds something only Christian's profile shows** (synced settings, real add-ons, debrid): the rig cannot reproduce it in Test 2; the fix gets its device check in Test 2 with the same add-on installed as a tester payload, then Christian confirms in his profile.
- **A big release diff and no Codex until 10-29:** two Opus review rounds per wave stand in, as they have since 10-01; the optional Codex pass above covers the whole diff once.
- **Corner rail design conflict** (Christian's chrome rule vs Steven's flush column): resolved by S1 as a Corner-specific layout matching the official app's reference, with Centre untouched; Christian decides from the rig's screenshots before the rc.
- **Sideloading friction** (FEAT-3): unchanged for beta.19; the README's install section stays as it is.

## 8. Records

Plan: this file. Waves: `docs/batch-p-steven-rc10-plan-2026-10-20.md` continues as Wave 3 / 4 sections, or a `docs/wave3-plan-<date>.md` if it grows. Soak and walkthrough findings: the tracker (new rows) and `docs/research/beta19-walkthrough-<date>/`. Release: `docs/comms-beta19-highlights.md`, `docs/comms-reddit-beta19-*.md`, `docs/comms-dm-drafts-<date>-beta19.md`.
