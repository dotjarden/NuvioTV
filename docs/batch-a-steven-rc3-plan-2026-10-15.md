# Batch A: Steven's rc3 verdict + follow-ups (2026-10-15)

**Status: MERGED 2026-10-15 on Christian's go: `tvos-shared-extraction` fast-forwarded `b768e6339` → `943030ea4` (7 commits), pushed, branch deleted locally and on `origin`, outer pointer `1e94fc0`. CUT 2026-10-15 as beta.19-rc4: build 136 `975a7010`, tag pushed, outer `df54aa1`, IPA on filebin (until 10-22) + gofile; Steven's DM drafted at `docs/comms-dm-drafts-2026-10-15-beta19-rc4.md` (5/5), not sent.** Master plan `docs/master-plan-2026-10-14.md` §4.1, decisions D1/D2/D9. Fix shapes from
`docs/post-player-revamp-batch-plan-2026-10-08.md` (Batch A table) and the rc3 record
`docs/steven-beta19-rc3-verdict-2026-10-06.md`. Clone `~/Claude/Projects/NuvioMobile-rc3-a`, branch
`claude/steven-rc3-a` off `b768e6339` (`tvos-shared-extraction` after P3 + fix-ups). Not merged, not cut: rc4
(build 136) is cut on Christian's go after the merge.

## Scope

| # | Item | Tracker | Agent |
|---|---|---|---|
| A1 | Detail logo slot shows the title text while the logo loads | BUG-152 P2 | α |
| A2 | In-row trailer tile logo through `TitleLogoStore` | BUG-149 P3 | α |
| A3 | Folder pages immersive (`pushImmersive`/`popImmersive` on `FolderDetailView`) | BUG-148, BUG-144, UX-16 (3), BUG-161 | β |
| A4 | Stage heading-to-shelf gap | BUG-146 P3 | β |
| A5 | "Genres · N sources" under the hero-ON CTA | BUG-159 P3 (was BUG-154) | γ |
| A6 | Rail Hidden mode (third `RailVisibility`) | FEAT-62 P3 | δ |
| A7 | Home position restored after a folder, both layouts | BUG-156 P2 | γ |
| A8 | One ring on the playing trailer card + D9 poster-colour still ring | BUG-158 P2 | α |
| A9 | Per-row landscape from the add-on's `posterShape` | BUG-157 P3 | β |
| A10 | Remember Last Profile (You › "Open Last Profile at Launch", off) | FEAT-65 P3 | δ |
| A11 | Search: measure, then (a) cancel the inflight fetch + (c) debounced query into `SearchContent` | BUG-155 P2 | ε |
| A12 | Strings ×6, tracker rows → BUILT | | main |

## Method

Wave 1 (α Sonnet, β Opus, γ Opus; disjoint files) → build + commit → Wave 2 (δ Opus, ε Opus) → gates → two Opus
read-only review rounds → device pass (rig, Test profile) → OUTCOME.

## OUTCOME

### Build (2026-10-15, one session, ~2.5 h wall)

Commits on `claude/steven-rc3-a` (clone `~/Claude/Projects/NuvioMobile-rc3-a`, MPVKit symlinked over the
gitlink, staged by explicit path):

| Commit | What |
|---|---|
| `a640af9c2` | Wave 1 (α Sonnet: A1 A2 A8; β Opus: A3 A4 A9; γ Opus: A5 A7) + the main session's cross-file halves (the A8 row/button-style wiring, β's HomeView floor + `landscapeArtworkURL` diffs, the CW / Upcoming / Discover shelf padding, SagaCard's D9 line) |
| `b68b22689` | Wave 2 (δ Opus: A6 A10; ε Opus: A11) |
| `b40023eac` | Review r1 fixes (see below) |
| `e471d2d5e` | Review r2 fixes (see below) |
| `ade7baab4` | Device pass: the Stage pop restore re-grabs once when the engine's late restoration pages the strip away; the search leg's cancel assertion is latency-aware |
| `943030ea4` | Device pass: the Classic pop restore re-grabs the origin card (up to 3×, 1.5 s) when the engine's late restoration lands on the hero CTA with no Up input |

**Fixture note.** The FA87 fixture's data containers were all re-created at 12:55 ET today (before this
session: every `Containers/Data/Application/*` dir has that mtime), so the seeded guest "Chris" profile,
collections and add-ons were gone and every UI leg failed at the picker ("profile picker never
appeared"). Re-seeded the 10-02 way: `profile_payload` (one non-PIN profile "Chris", `profile_index` 1,
bound to the container's `anonymous_user_id`, `hasEverSelectedProfile` true, `rememberLastProfileEnabled`
false) written with `plutil -replace` into the container plist with the app terminated; backup at
`/tmp/fa87-prefs-backup-2026-10-15.plist`. Collections and add-ons are not restored (the legs seed their
own through `-debug.collectionsSeedJsonB64` / the stub server); Cinemeta is the guest default.

### Per item: what was built and the facts found

- **A1 BUG-152.** `CachedAsyncImage` gains `loading:` overloads on both inits (type-erased loading view,
  default shimmer everywhere else); `DetailCinematicHero.logoSlot` and the Classic header pass the title
  text. r1 P3-7 / r2 P3-9: a memory-cached head or placeholder draws nothing for the one body before the
  loader seeds it, so a cached logo never flashes the text.
- **A2 BUG-149.** `InlineTrailerTitleOverlay` observes `TitleLogoStore.shared`, calls `lookupIfNeeded`
  once per key (only for `isLookupCandidate` logos), resolves store → `heroLogoURL` → text
  (`resolvedLogoURL`, unit-tested).
- **A3 BUG-148 / BUG-144 / BUG-161 / UX-16 (3).** `FolderDetailView` pushes/pops the immersive tab-bar
  state exactly as Detail does (one pair covers Rows and Grid; the Rows ↔ Grid switch swaps only the
  child). Only Home pushes `FolderDetailView`. The rail's Hide While Browsing rule hides on `immersive`,
  which is BUG-161. r1 P3-5 / r2 P3-7: `popImmersive` defers the drop-to-zero publish one runloop turn
  and drops it when a push lands in between (folder → Detail no longer crosses 1 → 0 → 1 visibly); the
  probes record the pop only when it is published.
- **A4 BUG-146.** `StripGeometry.shelfTopPadding` = 12 (`sm`) inside the strip through
  `.stripShelfPadding()` (keyed on `\.stripFocusMemory`, which only `StripPager` sets); Classic keeps
  `lg`. `catalogRowHeight` = heading + 16 + 12 + art + caption chrome + 24; titles-on regimes are 12 pt
  shorter (Large titles-on gets 5 synopsis lines); fit boundary 164/165 → 168/169 dp. Heading-to-poster
  gap 28 pt; the 20 pt zoom lift clears it by 8 (4 with the accent ring). CW, Upcoming and Discover
  shelves use the same modifier (Classic unchanged).
- **A5 BUG-159.** The hero-ON FEAT-29 folder box draws `folderHeroDescription` (already carried in the
  folder preview's `description` since rc14, never drawn with the hero on) as one `meta` line in its
  bottom 32 pt (`HeroFolderBoxLayout.split`, fixed total height, dropped below 80 pt). Tests in
  `PinnedRowGeometryTests`.
- **A6 FEAT-62.** `RailVisibility.hidden`: shown only while a rail item holds focus or a reveal is open;
  reserves no width; the Hide While Browsing slide never runs; Left-from-first-card and Menu reveal
  through the existing paths. Appearance › Rail gains "Hidden"; explainer sentence; six languages.
- **A7 BUG-156.** Stage: `syncCover` captures the row on the push edge and, on the pop edge (not the CW
  picker lifting), `StageController.restoreAfterUncover` waits for the pager handle (0.1 s polls, ≤ 1 s)
  then `requestFocus(row, remembered card, reason: "uncover")`; cancelled by a new push and (r2 P3-6) when
  focus leaves the strip. Classic: `HomeRowInputBox.returnFocus` (`HomeReturnFocusMemory`) remembers each
  row's focused card from the row's own `@FocusState` (`noteFocusedItem`), captures the origin on the
  `homePath` 0 → 1 edge (never from the hero CTA), and on the pop issues three rungs (0 / 0.3 / 0.7 s,
  the row's first card on the last) through `PinnedRowFocusRequest`, expiring at 1.0 s. r1 P2-3 / r2
  P2-1..3: a rung that finds the engine restored the right row on the WRONG card re-targets the card with
  `forceCard` (every rung; only when the row still contains the card, `rowContainsItem`; the request is
  cleared on the (row, card) landing, on `landed=1` and on expiry). r1 P2-4 / r2 P2-5: a directional
  press on the rows, an Up swipe or the hero taking focus retires the restore (`retireReturnRestore`).
  Residual, documented: a Down SWIPE inside the 0.7 s rung window cannot be told from the engine's own
  restoration and may be pulled back once. Probes: `[HomeReturn]` (behind `-debug.homeScrollProbe`),
  `debug_homeReturn own= foc= ret=`, Stage `[StageStrip] restore … reason=uncover`.
- **A8 BUG-158 + D9.** The outline: with Zoom ON and the accent ring OFF the card is a bare `.borderless`
  button (the only branch that still wears the SYSTEM focus treatment) and that treatment draws its
  standing platter/specular edge at the LABEL's bounds (the BUG-54 mechanism); under the opaque poster it
  is hidden, but once the portrait card fades out under the landscape tile the edge shows around the tile.
  Fix: `InlineTrailerCard` reports the tile-showing card up through `InlineTrailerTileShowingKey`;
  `CatalogRowView` puts `CardSystemLiftStyle.lift` in that card's environment (portrait rows only) and
  gives it a zIndex; `CardFocusButtonStyle` adds `.focusEffectDisabled(liftStyle == .lift)` on the
  borderless branch (a modifier flag, never a style-type swap, which would drop focus mid-trailer);
  `CardArtworkFocusLift.systemLift` is one value-driven chain (`.hoverEffect(.highlight, isEnabled:)`);
  the TILE draws ring mode's own scale + shadow (`CardArtworkFocusLift.manualScale` at its frame) and its
  overlay title drops with it (`CardCaptionFocusDrop`). Landscape rows keep the system lift (their base
  card never fades). D9: `FocusRingTintSampling.samples` — still mode (No Zoom ON, accent ring OFF)
  samples and wears the poster colour whenever the store has one, independent of
  `focus_ring_poster_color`, on PosterCard / LandscapeCard / SagaCard / the trailer tile
  (`InlineTrailerTileTint.ringSource`: noZoom → `.poster` when a colour exists). `FolderTile` / `CastCard`
  still rings stay white (r2 P3-13 follow-up). **Unproven on the simulator:** whether
  `.focusEffectDisabled(true)` suppresses `.borderless`'s platter on hardware (the 2026-08-30 note);
  device-pass step 9 decides. If the box remains, the fallback is a custom `ButtonStyle` for the
  trailer-capable card in every zoom-on state (a look change for every Home card; Christian's call).
- **A9 BUG-157.** `PosterStyle.landscapeSection` (strictly more than half the items tagged landscape; a
  tie, an empty row or `square` stay portrait), memoised per (count, first id, last id);
  `CatalogRowView` resolves its style per section and republishes it to the cards, the See All card,
  the strip memory widths and the morph math, from every host; a shape-landscape item's `poster` is its
  landscape art; Home floors such a short row like a collection row (BUG-122 class,
  `isLandscapeShapeCatalogRow`). The global Landscape Posters toggle still wins.
- **A10 FEAT-65.** Settings › Account & Profiles › Profiles › "Open Last Profile at Launch" (off) writes
  the shared `rememberLastProfileEnabled`; `ContentView.autoEnterRememberedProfileIfNeeded` runs on the
  first `.main` gate per process (`ProfileAutoEnter.decision`: enabled ∧ everSelected ∧ active profile
  exists ∧ no PIN ∧ not fired), does exactly the picker's tap (`select`, `reseedNow`, `entered`), prints
  `[ProfileSelect] auto-enter profile N`; the latch is also consumed by any Welcome gate, so Switch
  Profile and sign-out → sign-in always show the picker. Deliberately NOT ported: upstream's lone
  non-PIN-profile auto-enter regardless of the flag. r2 P3-8 (a PIN added on another device is read from
  the cache before the pull) matches upstream's rule; not changed.
- **A11 BUG-155.** (a) `CatalogInflightRequests` ref-counts the waiters of a deduplicated catalog fetch
  and cancels the launched job when the last waiter is cancelled (NonCancellable finally blocks under the
  mutex; a joiner after the cancel starts a fresh fetch; Home / Discover sharing the URL keep it alive);
  `CatalogInflightStats` counters. (c) `SearchContent` reads the model's synchronous `queryIsEmpty` edge
  and the debounced `displayQuery`, never the live field text; chips write the text back through
  `setQuery`. DEBUG `SearchPerfProbe` (`[SearchPerf] key / fire / results`, `debug_search_perf`) and
  `-debug.searchLegacy YES` restoring both pre-fix behaviours. **Measurement (FA87, guest Cinemeta only,
  "fight club" typed letter by letter at 0.4 s):** fix `maxBody=1 cancelled=12 first=154 ms last=195 ms`
  (one body on the first letter's empty → non-empty edge, none after; 12 superseded fetches cancelled on 9
  keystrokes); legacy `maxBody=1 cancelled=0 first=44 ms last=53 ms` (one body per keystroke, nothing
  cancelled). The pile-up mechanism is real and now cut; the keystroke body cost is bounded; the single
  guest add-on cannot reproduce the latency or the caret lag Steven sees with his add-on count, so
  `first`/`last` on the sim say nothing about his case. Shipped in A as planned ((a)+(c)); (b) the
  per-catalog 8–10 s timeout and (d) the 450 ms / 1-char debounce stay in Batch B; device-pass step 12
  with his add-on count is the real check.
- **A12.** Strings: "Hidden", the rail explainer, "Open Last Profile at Launch" + its description,
  "Profiles" in en/de/es/fr/it/vi (δ); no other new user-facing strings. Tracker rows: see below.

### Reviews (Opus read-only, the Codex stand-in until 10-29)

- **r1** over `b768e6339..b68b22689` (`docs/research/batch-a-review-r1-2026-10-15.md`): 0 P1 / 4 P2 /
  10 P3. P2s: the playing tile lost its lift and landscape rows showed the base card around it;
  `CardArtworkFocusLift`'s structural switch rebuilt the artwork at both tile edges; the restore stood
  down on the right row / wrong card; a later rung could pull focus off a row the viewer moved to. All
  four fixed in `b40023eac` together with P3-5/7/11/12; declined P3-6/8/9/10/13/14 (reasons in the
  commit message).
- **r2** over `b768e6339..b40023eac` (`docs/research/batch-a-review-r2-2026-10-15.md`): 0 P1 / 5 P2 /
  6 P3. P2-1/2 verified fixed; P2-3/4 partly: new P2s — a forced request never cleared after landing,
  a stale id forced into a focused row (focus-drop class), the forced rung barred on the last rung, the
  tile's overlay title under the lift, swipes never retiring the restore. All five fixed (see A7 / A8
  above) plus P3-6/7/8/9/10; P3-11 (assert immersive cleared right at the pop) not added: no probe
  exposes the depth outside the About pane.

### Gates

| Tip | NuvioTVTests | Debug | Release | Shared | UI legs (FA87, re-seeded fixture) |
|---|---|---|---|---|---|
| `a640af9c2` (wave 1) | 1677 / 0 | green | — | — | — |
| `b68b22689` (wave 2) | 1688 / 0 | green | — | jvm 1444 / K/N 1462 (ε) | — |
| `b40023eac` (r1 fixes) | 1688 / 0 | green | green | — | folder 3 pass + 1 skip, home-return 2, rail/profile 3, search 2 (over three runs) |
| `e471d2d5e` (r2 fixes) | 1688 / 0 | green | green | — | 11 legs: 10 pass, landscape skips (Add-ons field never takes keyboard focus in the harness); the search "fix" leg once failed its cancel count because Cinemeta answered in 48 ms, now latency-aware |
| `ade7baab4` (Stage re-grab) | 1688 / 0 | green | green | — | search legs 2 / 2 |
| hero re-grab, first form | 1688 / 0 | green | green | — | — |
| `943030ea4` (final tip) | see "Final gate" below | | | — | — |

**UI-leg harness notes.** (1) `testStageOneRowFolderHidesTabBar` / `testClassicGridKeepsTabBarHiddenAfterDetail`
first asserted the bar's return right after the pop; Home comes back scrolled to the folder's row, where tvOS
hides the bar by scroll, so they now walk Up to the top first (the immersive clear is what that proves; the rail
leg reads `shown=1` on the same pop). (2) The rail leg likewise walks Up: Hide While Browsing keeps the rail off
below row 0 by design, and BUG-156's restore pages the strip to the folder's row. (3) The landscape leg's blind
Select on the Add-ons list toggled the fixture's Cinemeta OFF once (`installed_manifest_enabled_states_1`
… `false`), which made every later Home leg lose its catalog rows; re-enabled with `plutil`, and the leg now
skips unless the manifest field holds focus and the keyboard's keys exist. (4) The sim wedge rule still holds:
run the legs in small groups.

### Device pass (Living Room Apple TV 4K, tvOS 27.2, Test 2 profile, dev builds from `e471d2d5e` → `ade7baab4` → the hero re-grab tip; rig: `scripts/device/`, console logs `docs/research/batch-a-device-pass-2026-10-15/console*.log`)

Test 2 came up on the Stage layout, Rail = Hide While Browsing, Show Hero ON, Trailers on Focus ON (In Row),
Zoom ON, accent ring OFF, Ring Takes Poster Color ON, OLED True Black ON. Settings changed during the pass (left as
they are; Test 2 is disposable): Rail → Hidden, No Zoom on Focus → ON, Ring Takes Poster Color → OFF, Open Last
Profile at Launch → ON, Home Layout → Classic.

| Step | Item | Result |
|---|---|---|
| 1 | BUG-152 Detail logo text while loading | NOT JUDGEABLE by the rig (a screenshot takes 1.3 s; the window is ~0.8 s). Later screenshots show the logo, no grey block. **Christian:** open a Detail from a collection or Search with a cold logo, Cinematic and Classic. |
| 2 | BUG-149 Stage trailer tile logo on a TMDB-only title | not walked (needs a TMDB-id row with no preview logo; the Test 2 rows carry logos). **Christian**, or trust the resolver change. |
| 3 | BUG-148 Stage one-row folder, no tab bar | Tabs mode only; Test 2 runs the rail. Sim leg passes. **Christian (Tabs mode)** if wanted. |
| 4 | BUG-144 Classic grid → Detail → Back, no bar | same (Tabs). Sim leg passes. |
| 5 | BUG-146 heading gap | **PASS** (`d4`, `g7`: the heading sits just above the posters at Test 2's size, the zoom lift clears it). |
| 6 | BUG-159 hero-ON folder line | **PASS** on Classic (`h9`: wordmark, "Test Folder · 2 sources", Open Folder; the hero's height did not change against a title). |
| 7 | FEAT-62 Rail Hidden | **PASS** (`g4` nothing at rest on Home row 0, `g5` Left from the first card reveals, `g6` Right hides, `g3` Menu at a tab root reveals). The rail pill is gone from every tab root. |
| 8 | BUG-156 Stage | **FAIL on `e471d2d5e`, PASS on `ade7baab4`.** First walk: our rung 2 put focus on row 3 / card 2 at +0.56 s, the engine's own deferred restoration moved it to the row above 35 ms later (`src=vfocus-up`), the strip paged there, nothing answered. With the re-grab (`restore regrab … age=676`, `reason=uncover-regrab`, landed 50 ms later) Home came back on row 3 with Practical Magic 2 focused (`e3`). |
| 8 | BUG-156 Classic | **FAIL on `ade7baab4`, PASS on `943030ea4`.** First walk: rungs 1–2 landed card 2 at +0.55 s, the engine's late restoration then took the hero CTA 15 ms later (and again at +0.98 s on the next walk) and the r2 "hero takes focus" cancel retired the restore (`restore cancelled by hero`, `upFallback … reason=staleInput`: no Up input). With the hero re-grab (no Up input inside 1 s → re-request the origin card, up to three times inside the 1.5 s attempt): push, rungs 1–2, `restore regrab … from=hero n=1` at +0.58 s, rung 3 `landed=1`, settle clean at margin 1; Home came back on row 3 with Practical Magic 2 focused and its trailer playing (`k2-back`). |
| 9a | BUG-158 Zoom ON, ring off: no box on the playing tile | **PASS** (`e3` + the full-res crop `e3-tile-crop`: one clean rounded edge with the shadow, no platter edge). `.focusEffectDisabled` does suppress the `.borderless` platter on tvOS 27.2 hardware in this state. |
| 9b | D9: No Zoom ON, Ring Takes Poster Color OFF | **PASS** (`g7` + crop: one ring in the poster's colour on the playing tile; the CW landscape card wears the poster-colour ring too, `h8`). |
| 10 | BUG-157 landscape-shape catalog | not walked: Steven's add-on URL is out of the repo. **Christian:** install it in Test 2 and read the row. |
| 11 | FEAT-65 Remember Last Profile | **PASS**: cold relaunch landed on Home in Test 2, console `[ProfileSelect] auto-enter profile 3` (`h0`); Switch Profile showed the picker and stayed there (`h2`, the auto-enter line stays at one). PIN profile → picker not walked (no PIN on the fixture profiles). |
| 12 | BUG-155 search | Companion `text=` pastes the whole string (one fire, `keys=0`), so the per-letter caret cannot be judged by the rig. `[SearchPerf] results q="unabomber" first=576 last=2295 ms` with Test 2's add-on set. **Christian:** type a ten-letter title letter by letter; the caret should stay on the last letter and results land ~2 s after it. |

Rig caveats met: the Detail's full-screen trailer takes over a few seconds after a title opens, so a Menu after a Select
lands on the Detail page and a second Menu pops it (a Menu inside ~2.5 s of the Select pops straight to Home); the
console stream is restarted after each install; the Companion `text=` pastes a whole string, so per-letter typing is
not a rig test. Evidence: the screenshots named above as JPEGs plus the five console logs (redacted; no tokens were
found) in `docs/research/batch-a-device-pass-2026-10-15/`.

### Final gate

`943030ea4`: Debug simulator build green, NuvioTVTests 1688 / 0 (5 skipped), Release simulator build green
(`iosApp/build/logs/rc3a-r5fix-*` in the clone). The UI legs were last run in full on `e471d2d5e` (10 pass, 1 skip)
and the search legs on `ade7baab4`; the two device-pass commits touch only `StageController` / `StageStripHome` /
`HomeView`'s restore paths, which the home-return legs exercise on the simulator (the simulator's engine never fired
the late restoration the device did, which is why the legs passed before the device walks failed). Branch pushed to
`origin/claude/steven-rc3-a` at `943030ea4`.

### Left for Christian (feel items the rig cannot judge)

1. BUG-152: open a Detail from a collection or Search on a title whose logo is not cached (Cinematic, then Classic): the
   title text shows while the logo downloads, never a grey block; a cached logo shows no text flash.
2. BUG-155: Search, type a ten-letter title letter by letter with his add-on count: the caret stays on the last letter;
   results land about two seconds after the last letter (the rig saw `first=576 last=2295 ms` for a pasted query in Test 2).
3. BUG-157: install Steven's landscape-shape add-on in Test 2 (his URL, out of the repo): the catalog draws 16:9 cards on
   the Stage, on Classic and inside a folder; the global Landscape Posters toggle still forces landscape; remove it after.
4. BUG-149: a Stage row with a TMDB-id title that ships no preview logo: the in-row trailer tile shows the logo once the
   lookup lands.
5. Tabs mode (optional, Steven runs the rail): BUG-148 one-row Stage folder with no bar, BUG-144 Classic grid → Detail →
   Back with no bar over the grid, Menu → Home with the bar back. The sim legs cover both.
6. BUG-156 feel: no bounce after the return (the settle rested at margin 1 on the Classic walk); a Down swipe inside
   0.7 s of the pop may be pulled back once (documented residual).
7. FEAT-65: a PIN profile still shows the picker (no PIN profile on the fixture); sign-out → sign-in shows the picker.

### State left on the device

Test 2 profile, Classic layout, Rail = Hidden, No Zoom on Focus ON, Ring Takes Poster Color OFF, Open Last Profile at
Launch ON (a cold launch lands in Test 2 until it is switched off in Account & Profiles), OLED True Black ON,
Trailers on Focus ON. Dev build `943030ea4` installed under `com.youngchris29.NuvioTV` (free-team profile until
2026-10-22 04:23Z). Console stream stopped.

### Merge recipe (DONE 2026-10-15 ~17:15 ET, as written)

```
cd "~/Claude/Projects/Nuvio tvOS/NuvioMobile"
git fetch ~/Claude/Projects/NuvioMobile-rc3-a claude/steven-rc3-a:claude/steven-rc3-a   # already at 943030ea4 locally after the backup push
git checkout tvos-shared-extraction && git merge --ff-only claude/steven-rc3-a && git push origin tvos-shared-extraction
git push origin --delete claude/steven-rc3-a && git branch -d claude/steven-rc3-a
cd .. && git add NuvioMobile && git commit -m "Batch A merged: NuvioMobile tvos-shared-extraction b768e6339 → 943030ea4"
```
Then rc4 (build 136) through `scripts/cut-rc.sh`, release notes with every new setting and its default (Rail Hidden
available, default Always Visible; Open Last Profile at Launch off), and Steven's DM (copy rule, 5/5) saying rc4 is
his reinstall. The clone `~/Claude/Projects/NuvioMobile-rc3-a` can be deleted after the merge.

### Follow-ups (not in this batch)

- BUG-155 (b) per-catalog 8–10 s timeout and (d) 450 ms / 1-char debounce: Batch B, after his rc4 verdict.
- r2 P3-13: `FolderTile` / `CastCard` still rings stay white in No Zoom (they use `PlainLabelRing`), while every
  other card wears the poster colour; one more D9 pass if he notices.
- r2 P3-11: a probe for the immersive depth outside the About pane, so a UI leg can assert the clear at the pop.
- The landscape UI leg needs a DEBUG add-on seed launch argument (`-debug.addonManifestUrls`) to stop depending on
  the Add-ons keyboard; today it skips.
- BUG-160 (cold launch on the Streaming Services row): γ's reading of `HomeViewModel.rebuildRows` (collections are
  appended before the catalog sections have loaded, so the first build can start on a collection row and the focus
  engine stays there once the catalogs insert above it) is a plausible mechanism; confirm with the `[HomeHero]`
  row-identity line on a cold launch before building anything.
- The fixture simulator's data containers were reset at 12:55 ET today by something outside this session; the
  re-seed recipe is in this record, and the Cinemeta enabled-state key is the second thing to check when Home
  comes up empty.
