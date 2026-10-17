# NuvioTV master plan, 2026-10-14: every open bug and planned feature, sequenced

**Status: PLAN, awaiting Christian's go. Nothing built this session.** Written from a full read of the three feedback
sources (Steven's DMs through 2026-10-10, the r/NuvioForks thread, GitHub #3/#4/#5), the upstream checks 10-08 → 10-14,
the player revamp plan, the drafted post-player-revamp plan (`docs/post-player-revamp-batch-plan-2026-10-08.md`, now on
`main`), and three read-only code surveys of `tvos-shared-extraction` at `11944d02e` plus upstream `cmp-rewrite` at
`779c145a5`. Evidence pulled today: Steven's three unread photos and u/an_angry_Moose's BUG-128 glitch video (both
analyzed below).

This plan supersedes the 10-08 draft's sequencing; its per-item fix shapes still hold and are referenced, not repeated.

---

## 0. Where we are

| | |
|---|---|
| Public build | beta.18 (build 132, 10-01). Testers' rc: beta.19-rc3 (build 135, 10-05; litterbox link expired 10-08). Steven is on rc3, Classic + Rail. |
| `tvos-shared-extraction` tip | `11944d02e` = rc3 + Search & Discover (uncut) + player P1 + P2. |
| Player P3 | BUILT + reviewed (`claude/player-p3`, 25 commits, tip `0673f73c2`, backed up on `origin`), **device pass OWED**. The free-team provisioning profile expired **2026-10-14 12:07Z**: the dev build must be re-signed (`-allowProvisioningUpdates`, delete the stale `youngchris29` profiles) before the pass. |
| Checkpoint rule (10-06) | "If P3 has not merged within ten days of P1 starting (10-06), cut an interim rc with Search & Discover + P1 + P2." That date is **10-16**. |
| P4 / P5 | Not started. P5's B19 (automatic subtitle sync) collides with the 10-13 upstream finding (see D3). |
| Comms owed | ~~Steven's reply DM for his 10-08/09 reports~~ **SENT 10-14 19:55Z** (with the FEAT-63 decline to u/marcomez18). Steven answered 20:24Z (BUG-155/156/158 corrected, five new asks BUG-160/161, FEAT-66/67/68, his add-on URL in confidence, **he no longer has the app installed**: another fork overwrote it, so rc4 is also his reinstall). **Reply 2 drafted, NOT SENT:** `docs/comms-dm-drafts-2026-10-14-steven-reply2.md`. u/marcomez18 FEAT-63 answer once there is a decision. GitHub #4 (`mikeyunk`) and #5 (`4rtz1z`) wait on the reporters. Public promises: BUG-130 ("I'll look at carrying the position across"), FEAT-56 SenPlayer ("in a coming build"). |
| Reddit thread | Quiet since 10-02 (`pdgfqap`). DMs: **Steven's rc4 verdict 10-16 20:09Z** (§1e); reply **SENT 21:06Z** (`docs/comms-dm-drafts-2026-10-16-rc4-reply.md`); his answers owed on BUG-165 (engine + press), rail mode, wide-row photo. **rc5 verdict 10-17 03:05Z** (§1f, record `docs/steven-beta19-rc5-verdict-2026-10-17.md`); reply `docs/comms-dm-drafts-2026-10-17-rc5-reply.md` SENT 06:08Z; owed from him: which player for the late HDR (BUG-170). |
| Upstream | `779c145a5` (0.5.10-beta). Open ports: CW dismissed-restore (#2244, small), TorBox mylist pagination (10-10, medium), MDBList release-date sort (10-08, medium), ytId streams (10-08, low-med). Declined/parked: subtitle AutoSync (10-13, HIGH), Jellyfin/Emby (10-08, product call), iOS PiP (N/A). |
| Review | Codex quota resets 10-29; Opus read-only rounds until then. |
| Repo hygiene | Untracked on `main`: `docs/upstream-port-plan-2026-10-13/14.md`, the CLAUDE.md status lines, the 10-08 draft plan (taken from `origin/claude/sweet-hopper-47y3l2`), today's evidence dirs. Committed with this plan. The tracker's dashboard ITEMS array lags BUG-131+ (reconciliation still owed). |

---

## 1. Evidence read today

### 1a. Steven's photos (`docs/research/steven-beta19-rc3-photos-2026-10-09/`)

| File | What it is | What it settles |
|---|---|---|
| `2026-10-08-feat64-watched-home.jpg` | **Official Nuvio** Home (Obsession hero, "Films recommandés pour vous" row): watched posters carry a **blue circle with a white check, top-right, inset inside the poster** (Obsession, Heretic). | FEAT-64's reference is the badge, not hiding. Upstream has no hide-watched setting at all (survey §4); the badge is `NuvioPosterWatchedOverlay`, accent circle + check, top-end. tvOS already has the same shape in `PosterCard.watchBadge` (Library L1 only). |
| `2026-10-09-bug158-white-box-1.jpg` | NuvioTV Classic Home, "Top 10 des films" row, first card = the **in-row trailer card morphed to landscape** (Doing Life, playing). A **thin white rounded outline** around the playing card, with a second lighter inner edge (a double outline). | The "white box" surface is the **inline trailer card in its expanded state**, not a plain poster. |
| `2026-10-09-bug158-white-box-2.jpg` | Same row, same card, a **thick bright white rounded outline**, card slightly lifted. | Two different strokes across the two states. |

Reading against the code survey (§3 of the Home survey): no view draws a stroke on an unfocused card, so "all the time"
means "on every focused card, always", which is exactly what **No Zoom on Focus ON** does: `CardFocusTreatment.still`
draws a 4 pt `Color.white.opacity(0.85)` stroke on the focused card whenever the accent ring is off (`PosterCard.swift:616-633`),
and the expanded trailer card adds its own focus ring (`InlineTrailerCard.swift:1823-1830`), hence the double outline. With
No Zoom OFF and the ring off, the card gets `.systemLift` (`hoverEffect(.highlight)`) and no stroke, which is his "nothing
appears". **Corrected by his 4:24 PM ET answer (same day):** photo 1 = **Zoom ENABLED** (No Zoom on Focus OFF) *with* the
outline, photo 2 = no outline. So the box belongs to the zoom state: with No Zoom off and the ring off the card is
`.borderless` + `hoverEffect(.highlight)` (`.systemLift`, `PosterCard.swift:782-788`), and the BUG-54 note already records
that system effect drawing a standing platter edge, focused or not; on the expanded trailer card it reads as the thin
doubled outline. Fix shape (A8): `.focusEffectDisabled()` or `RingCardButtonStyle` on the systemLift branch of the
morphed trailer card, verified in both states on the device before the DM claims it.

### 1b. u/an_angry_Moose's BUG-128 video (`docs/research/bug128-moose-glitch-video-2026-10-02/`)

Pulled from `v.redd.it/ptm5pgnhe3th1` (HLS; the DASH mp4s are 403 unauthenticated), 24.8 s phone recording of the TV,
*Pinocchio* (2022) trailer on the **default Detail full-screen trailer** (`FullScreenTrailerPlayer`, health surface
`detail-full`), beta.18. Frame by frame (one per second):

- 0–6 s: five distinct shots play in order (A Geppetto, B square, C courtyard, D legs).
- 7–12 s: **the same five shots again, frame-accurate** (the player seeks back ~6 s and replays).
- 13–16 s: new content (Jiminy, seagull, Pinocchio's face).
- 17–24 s: **one frame held for 8 s** (the hang).

Read: a seek within the same media (not a reload), then a stall. Two mechanisms fit: the HLS byte-range repack
(`TrailerLocalHLS`, memory `trailer-sabr-hls-repack`) publishing segment timing that does not match the fragment for
this itag, so AVPlayer re-requests an earlier segment and then starves; or the full-screen cover's fresh `AVPlayer` racing
the still-live `detail-bg` looper on the same loopback token. The shipped rc1 probe (`TrailerHealthProbe`, About › Trailer
Diagnostics, `[TrailerRepack] serving … fps= itag=`) exists for exactly this; the reporter was asked to photograph it on
the next public build. **Repro recipe for Batch C:** FA87 sim, `-debug.trailerSmokeVideoId <id>` for both *Pinocchio*
trailers (2022 Disney, 2022 del Toro; get the ids from the Detail page's trailer list), Detail full-screen, read the
`[TrailerHealth]` end summary; then the A/B knobs `-debug.trailerMaxFps 30` and `-debug.trailerBufferSeconds 10`.
BUG-130 (restart on going full screen) is the same seam: the cover builds a new player from the URL
(`TrailerHeroPlayerView.swift:489`), nothing carries the background copy's time. Fix both in one pass (C5).

### 1c. DMs, thread, GitHub

- `scripts/reddit/fetch-dms.sh --since 2026-10-08T15:24:08Z --summary`: 8 rooms, nothing newer than the
  2026-10-10T02:06:40.899Z watermark (Steven's second BUG-158 photo). Inbox: 0. Watermark unchanged.
- r/NuvioForks `1wtmutc`: last tester comment `pdgfqap` 10-02 (14 consecutive quiet sweeps). Our BUG-130 answer `pe7y533` 10-06 is the newest entry.
- GitHub: #3 (BUG-114, fixed in rc13; Menu question open to `dotjarden`), #4 (BUG-120 Xperience; `mikeyunk` promised data 10-01), #5 (FEAT-56 SenPlayer; answered 10-06, version asked). No new activity.

### 1d. FEAT-56 SenPlayer research (web; no IPA on this Mac, so no binary read)

- App Store: iPhone/iPad/Mac/Apple TV, **tvOS 17.0+**, developer 军 王 / Hangzhou Yuesen Vision, free with Lifetime Pro (AppleTV) $9.99.
- Version history facts that matter: **5.9.1** "External subtitle support for URL Scheme playback", "URL Scheme support for setting UA and name during download/playback"; **6.1.1** "support for passing in playback time when playing via URLScheme; returning current playback time when exiting playback", "option to save URL to playlist when playing via URLScheme (configurable via parameters)"; **6.1.3** "Fixed an issue on TV where playback launched via URLScheme could not return".
- Third-party integrations treat SenPlayer like Outplayer: `senplayer://x-callback-url/play?url=<encoded>` (plex-outplayer-tamper). The exact parameter names for position / subtitle / name / UA / `x-success` are **not published** anywhere I could find; the developer's docs are a QQ doc.
- Plan: spec the entry with the Outplayer/VidHub shape (`url`, `position`, `sub`, `filename`/`name`, `x-success`), then **verify on the device** with SenPlayer installed in the Test profile (hand-off, start position, subtitle, return position). If `x-success` does not carry a position, the app records nothing on return (VidHub precedent) and the GitHub reply says so. A binary read of the SenPlayer tvOS IPA (REA `open_binary` → strings `x-callback-url`, URL-type plist) would settle the parameter names before building; it needs the IPA, which is Christian's call to supply.

---

### 1e. Steven's beta.19-rc4 verdict (added 2026-10-16)

Read 2026-10-16 20:09Z (record `docs/steven-beta19-rc4-verdict-2026-10-16.md`, frames
`docs/research/steven-beta19-rc4-video-2026-10-16/`; two videos, 8:34 + 1:39). He runs the Stage Home,
Rail = Hide While Browsing (and now Hidden), Medium+, No Zoom ON, native player ON, Enhanced Video Renderer OFF.

- **Confirmed:** BUG-152, BUG-149, BUG-161 (folder half), FEAT-62, FEAT-65, BUG-155 (a)+(c).
- **No-go:** BUG-159's hero-ON line was the wrong fix. He wants the genre + source count and the add-on name
  OFF both Homes (BUG-145 + FEAT-67). Revert under one toggle, first thing in Batch B.
- **Failed for him:** BUG-156 on the Stage, both Home ← folder (re-grab window on his box) and folder ← Detail
  (never wired: `FolderRowsPage` relies on the engine). BUG-146 still slightly high.
- **New rows:** BUG-162 landscape cards too small + heading floats (360×203 constant ignores Poster Size, row
  planned at portrait height), BUG-163 trailer audio-only on per-row landscape cards (single landscape path
  never reveals), BUG-164 far-left card clipped / left-edge glitch with No Zoom ON (`leadingEdgeAllowance`
  drops to ring + shadow when `liftScale` is 1, the Stage overlay tile is cut), **BUG-165 (P1) exit from the
  mpv player suspends the app to the tvOS home screen on a real remote** (on video at 6:18–6:28; play came
  from the Continue Watching hold menu with Home underneath; P3-F8 was NOT rig-only), BUG-166 DV profile 5
  on mpv plays green/magenta (router sends P5-in-MP4 and any native failure to mpv; mpv's `gpu` VO has no
  RPU processing; Enhanced Video Renderer OFF), BUG-167 ~12–14 s to first frame (probe + remux attempt +
  mpv cold start), BUG-168 thumbnails green on DV / sparse on SDR; FEAT-70 folder opens on the first item
  (not the folder intro), FEAT-71 folder Layout Rows/Grid out of the page's top band into Settings, FEAT-72
  Best Result = title / year / type only, FEAT-73 Discover as a type + genre grid over one default
  "Popular" catalog.
- **Disowned:** BUG-158 (the white box; fixed anyway). **By design:** rail on Home row 0 in Hide While
  Browsing (he uses Hidden now), zoom-mode focus edge.
- **Player facts for his setup:** rc4 = P1–P3 only; P4 merged after the cut. The DV source that went wrong is
  a "DV"-only WEB-DL (P5); the "DV · HDR10" (P8) ones beside it would have played native.

### 1f. Steven's beta.19-rc5 verdict (added 2026-10-17)

Read 2026-10-17 (DM 03:05Z + 3 photos + a 03:15Z add-on; record `docs/steven-beta19-rc5-verdict-2026-10-17.md`,
photos `docs/research/steven-beta19-rc5-photos-2026-10-17/`). He runs the Stage Home, Medium+, Hide Titles ON,
No Zoom OFF with Card Depth ON, Collections Layout Rows, Infuse Pro as external player. "Things are moving in the
right direction."

- **Confirmed:** BUG-145 / BUG-159 / FEAT-67 (heading details gone), FEAT-70 (folder opens on the first film),
  FEAT-71 (Collections Layout), FEAT-72 (Best Result "perfect"), BUG-164 (No Zoom far-left), BUG-166 (no green
  picture), BUG-158 (the white outline with Card Depth ON is gone, cause unverified).
- **Still open:** BUG-146 (B6 moved the heading 4 pt; "no difference", much too high on landscape rows),
  BUG-162 (B4's 624 × 351 is now "much too large"; he wants the collection-poster size at rest and the big size
  only while the trailer plays), BUG-156 (both returns land right but after a visible glide to the engine's
  default and back), BUG-168 (mpv none on Animals; native shows a transparent box = P3's AVKit limit), BUG-170
  (HDR ~10 s in), FEAT-64 (watched tick: he thought it shipped; it did not).
- **New:** BUG-173 collection title twice on Home (the folder's stage meta line is `collection.title`, the row
  heading below is the same; B1 gated only the synopsis), FEAT-76 per-collection Rows / Grid (D17), FEAT-77
  Nuvio/Stremio pulsing-title loading animation (D18).
- **Not his:** BUG-143 (rc5's player notes listed it; it came from a device session). **No tester:** FEAT-56
  SenPlayer (neither he nor Christian has it).

## 2. Inventory: everything open, by area

Sizes: S ≤ ½ day, M 1–2 days, L more. "Shape" cites the survey facts; the 10-08 draft has the longer version for its items.

### 2a. Home, folders, focus (Steven, rc3 + follow-ups)

| ID | Pri | Item | Shape | Size | Batch |
|---|---|---|---|---|---|
| BUG-152 | P2 | Detail "black square" (shimmer in the 600×180 logo slot) | `CachedAsyncImage` gets a `loading:` builder; Cinematic + Classic logo slots pass the title text. Only from collections / search (Home cards arrive with the logo cached). | S | A |
| BUG-149 | P3 | Trailer tile shows text, not the logo, on TMDB-id items | `InlineTrailerTitleOverlay` through `TitleLogoStore` with `lookupIfNeeded`. | S | A |
| BUG-148 | P3 | Stage folder page: tab bar never hides with one row | `FolderRowsPage` + `FolderDetailView` call `tabBarVisibility.pushImmersive()/popImmersive()` like `DetailView.swift:1201-1204` does; today only Detail does. Also removes the folder-logo/bar collision (UX-16 (3)). | S | A |
| BUG-144 | P3 | Classic folder grid: tab bar drawn over the grid after Back | Same immersive pair on `FolderDetailView` (`CollectionsUI.swift:1271-1367`). Fallback: re-link the grid's scroll view on reappear. | S | A |
| BUG-146 | P3 | Stage row headings too high | `StripGeometry.catalogRowHeight`: heading + md + sm; test + probe sweep. | S | A |
| BUG-156 | P2 | **Home position not restored after leaving a folder (Stage and Classic)** | Both layouts rely on native focus restoration only. Stage: in `StageStripHome.syncCover` on pushed → false, call `stage.requestFocus(rowKey: stage.currentRowKey, itemId: stage.memory.itemId(for:))` (the rail route already does this). Classic: it keeps no focused-card id; record it in the focus `onChange` (or install `StripFocusMemory`) and on `homePath.count → 0` issue `PinnedRowFocusRequest(rowKey: upInput.lastOwnedRowKey, itemId:)`; also check `PinnedRowSettle.setCovered(false)`'s re-armed `scrollTo` is not undoing the landing. Clarify with him whether "also in old home page" means Home or the folder page after Back from Detail (UX-14). | M | A |
| BUG-158 | P2 | White outline on the playing trailer card with **Zoom ON** (his 4:24 PM answer), none with No Zoom | The system `.borderless` + `hoverEffect(.highlight)` branch (`.systemLift`, `PosterCard.swift:782-788`) draws a standing edge on the expanded trailer card (BUG-54 class), stacked on the card's own ring (`InlineTrailerCard.swift:1823`). Fix: `.focusEffectDisabled()` / `RingCardButtonStyle` on that branch for the morphed card; one outline. Device-verify both states. | S | A |
| BUG-157 | P3 | Add-on catalog with `posterShape: "landscape"` draws portrait cards | Shared parses it per item (`HomeCatalogParser.kt:54`), no Swift reader. Upstream: per item, width = base × 180/110, image stays `item.poster`. tvOS: derive a per-section flag (majority / first item landscape) and apply `.environment(\.posterStyle, style.withLandscapeRows(true))` on that `CatalogRowView` so metrics + `baseCard` follow (Classic, Stage, Discover, folder Rows, Search all route through `CatalogRowView`). Ask him for the add-on so a fixture carries it. | S–M | A |
| BUG-154 (Classic hero-ON folder line) → **renumber BUG-159** | P3 | Classic Show Hero ON: no "Genres · N sources" line on folders, 1–2 synopsis lines | `folderHeroDescription` under the CTA in the hero-ON panel (`HomeView.swift:6442`), 1 line; the synopsis budget stays (rt4). The number BUG-154 is taken by the P2 arbiter fix; BUG-155 is now Search, so this becomes **BUG-159**. | S | A |
| FEAT-62 | P3 | Rail Hidden mode (reveal on Left from the first card / Menu) | `RailVisibility.hidden`; rule table + Appearance row; default stays Always Visible. | S | A |
| FEAT-65 | P3 | Open straight into a profile at launch | **Shared already has it**: `StoredProfilePayload.rememberLastProfileEnabled` + `activeProfileIndex` + `hasEverSelectedProfile` (`ProfileRepository.kt:33-59`), upstream's "Remember Last Profile" (default off, PIN profiles never auto-entered, single non-PIN profile auto-enters regardless). tvOS never reads it. Add: Settings › You row calling `setRememberLastProfileEnabled`; in `ContentView` on first `.main`, after `loadCachedProfiles()`, if remember + everSelected + target has no PIN → `select`, `reseedNow`, `entered = true`, once per cold launch; Switch Profile keeps the picker. | S | A |
| BUG-160 | P3 | App opens on the Streaming Services row (new, 10-14 PM) | **10-15: cold launch only, ~85 %.** Repro first on a fully closed app. BUG-156/113 class. | S | A if reproduced |
| BUG-161 | P3 | Rail stays visible at launch / entering a collection (new, 10-14 PM) | **10-15: his mode is Hide While Browsing, so a confirmed bug.** Always Visible → by design, FEAT-62 answers it; Hide While Browsing → A3 immersive folders + first-move hide. | S | A |
| FEAT-66 | P3 | Collection title top-right (new, 10-14 PM) | Placement call (the 10-08 draft kept top-left); no date promised. | S | B or later |
| FEAT-67 | P3 | Hide source counts on headings as well as add-on names (new, 10-14 PM) | One "Show catalog details" switch covering BUG-145's suffix and BUG-159's folder line, or two toggles. | S | B |
| FEAT-68 | P3 | "Netflix-style detail scrolling" (new, 10-14 PM, unclear) | **10-15: resolved to the Home Wako fixed-slot row (his Arvio link), not Detail.** Rides the Home rework. | — | — |
| FEAT-69 | P3 | Full-screen poster browse view (Orivio v0.13 / Apple TV app; new, 10-15) | Steven's suggestion; video + release in `docs/research/orivio-v0.13-steven-2026-10-15/`. | — | later / product call |
| BUG-145 | P3 | Add-on name on every Stage heading | Gate `StageCopy.headingAddon` on "Show catalog type in title" (D2 in the 10-08 draft, promised in the DM). | S | B |
| UX-16 (1) | P3 | Stage feels slow | Device A/B on the knobs (`-debug.stripPageSeconds 0.35`, `-debug.stageSwapPause 0.3`), then defaults. | S | B |
| UX-16 (2) | P3 | Ambient wash too foggy at the sides | Mask below the stage art + opacity A/B (new knob `-debug.washBelowArt`). | S–M | B |
| BUG-147 | P3 | OLED: wash darkens late after the swap (his video 3:00+) | Repro with OLED on + the probe (`late=`); fade the outgoing wash on the stage commit. | S–M | B |
| BUG-150 | P3 | Folder stage art blurry on 4K | Confirm `FolderRowsPlan` art source + decode size vs Home's `StageArtLayer`; photo at rest still asked. | S | B |
| BUG-151 | P3 | Stage/Classic hero print English copy for English-metadata catalogs | `TitleLogoStore` already fetches `TmdbPreviewEnrichment` (localizedTitle + description) for logo-less items; add a "copy wanted" gate, keep both fields, `StageCopy` + Classic hero prefer them. TMDB-on only. | M | B |
| weekend | P3 | Portrait poster goes black after the in-row trailer fade (Top 10 slot 3) | Repro with `-debug.trailerMorphAbortAfterWideMs`; suspects: image-cache eviction after I1 decodes, morph abort leaving `.none`. | M | B |
| FEAT-61 | P3 | Classic: longer synopsis, Rows folders under Classic, no bounce | (a) BUG-159 line; (b) "Collections Layout: Follow Home / Rows / Grid" setting; (c) no-bounce: no (strip structure). Keep Classic alive until the Stage has two public builds of feedback. | M | B |
| FEAT-64 | P3 | Badge or hide watched titles on Home | **Badge first** (parity, his photo): pass `watchBadge` through `PosterCardView` / `LandscapeCard` from `InlineTrailerCard.baseCard` using Library's `isWatched` logic (`WatchedRepository.isWatched` + `fullyWatchedSeriesKeys`); Continue Watching excluded (upstream has no badge there). **Hide** as a second, off-by-default toggle `hideWatchedContent` next to `hideUnreleasedContent` filtering in `rebuildRows` (our own addition; upstream has none). | S + S | B |
| BUG-153 | P3 | Detail first scroll stutters on heavy pages (Monstre) | Profile on FA87 with `debug.detailScrollProbe`; mount the heavy rows after the hero exit lands. | M | B |
| BUG-113 | P3 | Collection forgot its place after a long session (rc10, not seen since) | Watch; BUG-156's fix covers the likely mechanism. Close if his rc4 verdict is clean. | — | — |
| BUG-104 | P3 | Zoom-on + ring-on gap on four `TileFocusLift` labels | Needs the `manualScale` architecture; unprompted by testers. Backlog. | M | later |
| FEAT-36 / FEAT-41 / FEAT-33 / FEAT-16 | P3 | Apple-TV-app collection browsing; depth sliders; 60 fps probe; font picker | Product calls, unchanged. FEAT-33 needs a hardware frame probe first. | — | later |

### 2b. Search (Steven, rc3)

| ID | Pri | Item | Shape | Size | Batch |
|---|---|---|---|---|---|
| BUG-155 | P2 | **10-15: both halves real.** Search-as-you-type: **the cursor sits on B while A is displayed** (a visual offset, his 4:24 PM answer) and results are slow | Survey §1: a 350 ms Swift debounce exists, but **a superseded query never cancels its HTTP calls** (`deduplicatedHttpGetText` launches in `inflightRequestScope`, `CatalogData.kt:33-63`, 60 s timeout), one request per search-capable catalog with no cap or per-request timeout, `isLoading` waits for the slowest, `buildSearchResultsSnapshot` rebuilds everything on every arrival (O(N²)), and `SearchContent` re-evaluates its whole body on every keystroke because it binds `query` directly. Fix: (a) ref-count + cancel the inflight fetch when the last waiter leaves (or bypass the dedupe for search); (b) `withTimeoutOrNull(8–10 s)` per catalog → Failed/Empty; (c) hand `SearchContent` the debounced query, not the live binding; (d) debounce 450 ms and skip 1-char queries. Measure main-thread time per keystroke on FA87 with his add-on count before and after. | M | B (or A if the DM promises it) |

### 2c. Detail and trailers

| ID | Pri | Item | Shape | Size | Batch |
|---|---|---|---|---|---|
| FEAT-60 | P3 | Compact logo header fades in on the first Down (Apple TV app / Fusion) | Pinned `TitleLogoHeader` compact variant on `DetailRowAnchor.heroExit`, 0.25 s; Cinematic only. | M | C |
| weekend | P3 | Darker area behind the synopsis + poster bottom; full-synopsis affordance | `DetailScrim` cinematic values or a local panel; "More" glyph on the truncated teaser. | S–M | C |
| BUG-130 | P3 | Full-screen trailer restarts instead of continuing from the background copy (public promise) | Seek the cover player to the `detail-bg` copy's time, or hand the player across. | S–M | C |
| BUG-128 | P2 | Trailer replays a few seconds then hangs on some trailers (video above) | Repro with the two *Pinocchio* ids + the health probe; then fix at the repack/looper seam. | M (repro first) | C |
| U5 | — | "Intro skipped to M:SS" toast on auto-skip (upstream #2137) | 1.4 s toast on the `.auto` seek paths, both engines. Optional. | S | C |

### 2d. Player revamp (planned features, `docs/player-revamp-plan-2026-10-06.md`)

| Batch | State | What is left |
|---|---|---|
| P3 seek-preview frames | built + 3 Opus rounds CLEAN, **device pass owed** (12 steps, ★ items hardware-only: 4K decode timing, no stall, host connections, HDR/DV, memory, exit mid-decode) | re-sign the dev build, run the 12 steps in Test, merge on go. Carried: baked-bar aspect no-op, 1080p harvest timing. |
| P4 native-engine parity | not started | A8 Playback tab on native (`customInfoViewControllers`, `speeds`, `transportBarCustomMenuItems`), A9 `AVTextStyleRule`, B16 pause card, B17 late subtitles, A6 chapters from MKV, B24 loading overlay both engines. 3 agents, 2 rounds, 6-step pass. |
| P5 | not started; **rescoped by D3** | B20 amplification + Dialogue/Night mode (mpv), B22 post-play More Like This both engines, B23 per-show speed, **B19 reduced to "Sync Line"** (manual anchor) unless D3 says otherwise. |
| BUG-129 | P3 | mpv Sources tab vs the up-next search: `loadSources()` clears the shared flow while `beginSearch`'s watcher has no generation check (`NextEpisodeAutoPlay.swift:256-287`, `:539-559`). Fix: early-return/busy when `streamsWatcher != nil`, or a `searchGeneration` the watcher guards on. Rides P4. | S |
| BUG-143 | P3 | Rejected-link memory remembers network failures for 8 h | Classify first: remember HTTP errors + decode failures only, never host-unreachable / DNS / timeout / offline. Changes failover policy: Christian's call (D6). Rides P4 if yes. | S |

### 2e. Upstream ports (10-08 → 10-14 checks)

| # | Upstream | What | tvOS state (survey §3) | Size | Batch |
|---|---|---|---|---|---|
| U6 | `6fefbcdab` #2244 | Restore dismissed Continue Watching shows when marking episodes watched | `WatchedRepository.markWatched(items)` (`:767-769`) never touches `ContinueWatchingPreferencesRepository`; `removeDismissedNextUpKeysForContent` (`:168-177`) matches only the `"id|"` prefix. Port both hunks (filter `isEpisode`, also match the bare id) + tests; the tvOS hold-menu "Mark Episode Watched" and `WatchingActions.markWatched(seriesItems)` go through this overload. | S | D |
| U7 | `be81802c8` #2215 | TorBox cloud `mylist` pagination | `DebridApiClients.kt:123-145`: three single unpaged GETs under a 16 MB cap. Port `listCloudItems` + `fetchTorboxCloudPages` (offset/limit 100, halve on `...[truncated]`). ⚠️ `TorboxCloudLibraryProviderApiTest` lives in **composeApp**'s commonTest, not shared's: add the tests beside it or move the fixture. | M | D |
| U1 | `d8ce7258` | MDBList Recently / Oldest released sorts + owner's saved order as DEFAULT | `LibrarySortOption` has no `RELEASED_*`; Library L1's Sort pill picks the new options up from `availableLibrarySortOptions`. Diff line by line against batch 11's newest-first port. Needs MDBList in the Test profile for the pass (D7). | M | D |
| U2 | `94976222` | ytId-only add-on streams | Parser drops them (`StreamParser.kt:27-33`); resolve on device through the trailer extractor's HLS master, session-only URL, auto-play excluded by construction. | LOW–MED | D |
| FEAT-56 | GitHub #5 | SenPlayer as an external player (public promise) | New `IosExternalPlayerSpec` in `ExternalPlayerPlatform.apple.kt:16-123` (Outplayer/VidHub shape), `senplayer` in `Info.plist` `LSApplicationQueriesSchemes` (`:24-31`) and the `ContentView.swift:181` probe list; device test decides position/subtitle/return. See §1d. | S + device | D |
| U8 | `c27c92fa2` | Next-episode preload timing + heuristic post-credits | Survey: tvOS preload already fires `max(timeout, 30) s` **before** the card (`NextEpisodeAutoPlay.swift:403-412`), and the fork deliberately removed the invented tail scene (`PostCreditsHold.kt:47-52`); no "heuristic" provider exists here. **Nothing to port**; close in the next upstream check. | — | — |
| U9 | `bdbe5388c` | `CustomPosterUrlResolver` single-pass rewrite | Only if poster rows stutter; keep the fork's null-on-no-placeholder rule. Decline for now. | — | — |
| U10 | `4ff0deb02..885cb2f30` | Localize "Episode N" titles | tvOS is English-only in the UI; skip. | — | — |
| U11 | PR #2143 | Subtitle AutoSync (Android ExoPlayer only) | **Do not port** (10-13 doc): the embedded-cue reference source does not exist for AVPlayer/mpv. See D3 for what it means for P5. | — | — |
| U3 | PR #2081 | Jellyfin / Emby media servers | Park (10-08 draft D1); a separate project if wanted. | — | — |

### 2f. Comms and hygiene

| Item | Owed | Batch |
|---|---|---|
| Steven reply DM (10-08 PM + 10-09 reports) | now; see §5 | 0 |
| u/marcomez18 FEAT-63 (play without debrid) | after D5 | 0 |
| GitHub #5 answer with the SenPlayer verdict | after D's device test | E |
| Upstream-report queue (batch 10's nine, S&D's two, BUG-141/142, 08-30's four) | a quiet day | E |
| Tracker: BUG-154 duplicate → BUG-159; photos marked read; BUG-128 video triaged; dashboard ITEMS reconciliation | this session (rows) / E (dashboard) | — |
| Translation pass (~30 L1 strings + plurals) before a public cut | E | — |

---

## 3. Decisions for Christian

| # | Question | Recommendation |
|---|---|---|
| **D1** | Fire the 10-16 checkpoint: cut **rc4** with Search & Discover + P1 + P2 + P3 + Batch A, before P4/P5? | **Yes.** Steven has had no build since 10-05, the 10-08 DM promised "next build" for the Batch A items, and his 10-08/09 reports (BUG-155–158) are rc3 findings he will want to re-check. P4/P5 go into rc5. |
| **D2** | Batch A scope: the 10-08 draft's A1–A8 plus the new rc3 follow-ups (BUG-156, BUG-157, BUG-158, FEAT-65)? | **Yes, all.** They are S–M each and the DM can then say "in rc4" for every item he reported. BUG-155 (search) is M and needs a measurement first: put it in Batch A only if the fix is (a)+(c) alone; otherwise B. |
| **D3** | P5's B19 "automatic subtitle sync" vs upstream's AutoSync verdict (not portable without an embedded-cue source). | **Rescope B19 to Sync Line** (pick a cue, press when you hear it) and drop the automatic half until a tvOS reference source exists. The 10-13 doc's phased route is the only way to the automatic half and it is HIGH. |
| **D4** | FEAT-64: badge only, or badge + hide? | **Badge now** (parity, his photo, S). Hide as an off-by-default toggle in the same batch only because it is also S; CW excluded either way. |
| **D5** | FEAT-63 (u/marcomez18): sources without a debrid account (torrent streaming, Stremio/SceneBox style). | **Decline for the App-Store-shaped build; say so.** Upstream's P2P engine is composeApp-only; tvOS has no engine; a sideload-only torrent client is a different product and a pull-risk for any TestFlight path (FEAT-3). Reply owed with that answer. |
| **D6** | BUG-143 network-aware rejected-link memory. | **Yes**, in P4: remember HTTP errors + decode failures; never host-unreachable / DNS / timeout / offline. |
| **D7** | MDBList in the Test profile for U1's device pass. | Connect it for one session (the L1 pass skipped MDBList for this reason). |
| **D8** | SenPlayer parameter names: build on the Outplayer/VidHub shape and verify on device, or get the IPA for a binary read first? | **Build + device-verify** (half a day). If Christian has SenPlayer installed on the Living Room ATV already, the device test is the whole answer. |
| **D9** | BUG-158 still-mode stroke: drop the flat white stroke on the morphed trailer card only, or move still mode to the FEAT-46 poster-colour ring everywhere? | **Both**: one ring on the playing card (bug), poster-colour ring in still mode (taste, matches rc2's ring mode). |
| **D10** | Keep the Stage plan's "delete Classic after one or two betas" step on hold while Steven prefers Classic? | **Hold** (10-08 draft D6). Decide after rc5's verdicts. |
| **D11** | FEAT-73 Discover shape (rc4 verdict): keep the per-genre Stage rows, or rebuild as the official app's grid (Type + Genre pills, one default general catalog, the catalog pill secondary)? | **Grid-first behind the existing placement setting**: Type + Genre over the grid, default catalog = the first that serves the selected type's genre list (Cinemeta / TMDB "Popular"), rows kept as "Browse" under it. His 30-catalog setup makes the catalog pill noise; the genre walk is the blocker. M. |
| **D12** | FEAT-72 Best Result card fields: title / year / type only (drop "Found in" and the rating)? | **Yes.** The row footnote keeps "Found in"; print the type always ("Film · 2009"). S. |
| **D13** | Heading details toggle (BUG-145 + BUG-159 revert + FEAT-67): one Appearance switch "Show catalog details in headings" covering the Stage heading's add-on name AND the folder line on both Homes. Default? | **One toggle, default OFF** (his no-go; the add-on name never helped a viewer). The hero-ON line A5 added goes under it, so the rc4 behaviour is reachable. S. |
| **D14** | FEAT-70: seed the Stage folder page with the first item's art + synopsis on open, or keep the folder intro (logo, "Netflix · 6 sources", cover)? | **First item once row 0 lands**, folder logo stays docked; the intro only until the row arrives. S. |
| **D15** | BUG-165 exit eject: hotfix rc (rc4.1) or ride rc5? | **Repro first** (Test profile, CW hold menu → play → pause card → scrub → Menu once, both engines). If it reproduces, fix it at the head of Batch B and cut rc5 as soon as B's mechanical half is in; no separate hotfix build unless rc5 slips past 10-24. |
| **D16** | BUG-162 landscape rest size (rc5 verdict: 624 × 351 "much too large", rc4's 360 × 203 "much too small"). | **Rest at the landscape folder tile's size, `width × 16/9` × `width` (416 × 234 at Medium+), morph to `height × 16/9` × `height` (624 × 351) when the trailer reveals**, the portrait row's morph. His words: "the same size as the collection posters normally, and only enlarge them when the trailer starts". Heading right above the 234 pt card; the page keeps the portrait height so the tile can grow. M. |
| **D17** | FEAT-76 per-collection layout (Genres as a grid, the rest as rows). | **Yes, as an override on the collection**: Default / Rows / Grid in the folder's hold menu, stored and synced with the collection, Default = Settings › Collections Layout. Not the pre-B7 device-local store (nothing could undo it). S–M, after Batch B's first group. |
| **D18** | FEAT-77 loading animation: the official apps' centred title pulse. | **Yes, as the loading overlay's look** (title logo centred, slow 1.0 ↔ 1.08 scale loop, stage text under it), no setting; with P5's start-time work (BUG-167/170). S. |

The 10-08 draft's D2 (gate the heading suffix on "Show catalog type in title"), D3/D4 (wash and speed A/Bs), D5 (collision only), D7 (localized copy on both surfaces), D8 (rail Hidden mode, default Always Visible), D9 (Detail pass Cinematic only), D11 (toast in C), D12 (ytId port) stand as recommended there.

---

## 4. Sequence

```
10-14/15  Batch 0   P3 device pass (re-signed dev build, Test profile) → merge P3 on go.
                    Send Steven's reply DM (§5). Send the FEAT-63 answer (D5).
10-15→17  Batch A   Steven's mechanical + rc3 follow-ups (one clone, 3 agents, 2 Opus rounds, 1 device pass).
10-17     rc4       build 136, tag beta.19-rc4: S&D + P1 + P2 + P3 + A. Regression pass (§4.6). DM.
10-17→21  P4 ∥ D    native parity (player clone) ∥ upstream ports + SenPlayer (shared clone; disjoint files).
10-17→22  Batch B   rc4 verdict first: heading toggle (his no-go), BUG-165 repro/fix, No Zoom clip, landscape rows, folder-page restore; then Stage polish + localized copy + search perf + watched badge.
10-22→28  Batch C ∥ P5   Detail pass + trailer seam (BUG-128/130) ∥ P5 + BUG-166 P5-on-mpv routing, BUG-167 start time, BUG-168 thumbnails, audio, post-play, per-show speed, Sync Line.
10-29     Codex is back: one Codex round over everything since rc4.
≈10-30    rc5       build 137. Full regression pass. DM. Translation pass before any public beta.19.
```

Two clones at most at a time, one build at a time (the agent playbook). Each batch: branch off the `tvos-shared-extraction`
tip, Opus rounds until CLEAN, gates (jvm / K/N / composeApp / NuvioTVTests / Debug + Release sim, `-collect-test-diagnostics never`
on UI runs), dev-build device pass in **Test**, fast-forward on Christian's go, outer pointer bump + record, tracker + CLAUDE.md + memory.

### 4.0 Batch 0 (now)

1. `xcodebuild … -allowProvisioningUpdates` after deleting the stale `youngchris29` tvOS profiles; install the P3 dev build from `0673f73c2`.
2. Run the P3 12-step checklist (plan OUTCOME "P3 device pass"); Harvest + Decode for steps 1–7 and 10; console attached for ★ steps. Record in the plan's OUTCOME; new BUG rows for findings.
3. On go: fast-forward `claude/player-p3` into `tvos-shared-extraction`, delete the branch locally + on `origin`, bump the outer pointer.
4. Steven DM + FEAT-63 answer (both through SlopMonster, 5/5 shown).

### 4.1 Batch A: Steven's rc3 items + follow-ups (branch `claude/steven-rc3-a`)

| # | Item | Files (survey facts) |
|---|---|---|
| A1 | BUG-152 logo loading = title text | `DesignSystem/CachedAsyncImage.swift` (`loading:`), `Screens/Detail/DetailCinematicHero.swift` `logoSlot`, `Screens/DetailView.swift:1751` |
| A2 | BUG-149 tile logo via `TitleLogoStore` | `Screens/InlineTrailerCard.swift` (`InlineTrailerTitleOverlay`) |
| A3 | BUG-148 + BUG-144 + UX-16 (3): folder pages immersive | `Screens/FolderRowsPage.swift:112-126`, `Screens/CollectionsUI.swift:1271-1367` (`pushImmersive`/`popImmersive` pair as in `DetailView.swift:1201-1204`), `DesignSystem/TabBarVisibility.swift` unchanged |
| A4 | BUG-146 heading gap | `Screens/Home/StripGeometry.swift:177-183`, `StripGeometryTests`, `StageStripProbe` |
| A5 | BUG-159 folder line under the hero-ON CTA | `Screens/HomeView.swift:6442` |
| A6 | FEAT-62 rail Hidden mode | `DesignSystem/NavigationChrome.swift:36,261-271`, `NavigationRail.swift`, `AppearanceSettingsPane.swift`, xcstrings ×6 |
| A7 | **BUG-156 folder-return position, both layouts** | `Screens/Home/StageStripHome.swift:428-436` (`syncCover` → `requestFocus` on uncover), `Screens/HomeView.swift:1291-1294,1977,2000,2297` + a focus memory for Classic, `BrowseComponents.swift:3514-3537` (settle re-arm check); UI legs: open a folder from row 3, Menu, assert the row + card; both layouts |
| A8 | **BUG-158 one ring on the playing trailer card** (+ D9 poster-colour still ring) | `DesignSystem/PosterCard.swift:616-633,670-712`, `Screens/InlineTrailerCard.swift:1823-1830` |
| A9 | **BUG-157 per-row landscape from `posterShape`** | `Screens/BrowseComponents.swift` (`CatalogRowView` section flag → `.environment(\.posterStyle, …withLandscapeRows)`), `HomeModels.kt` only if a section-level field is cleaner; fixture add-on with landscape previews for a UI leg |
| A10 | **FEAT-65 Remember Last Profile** | `Screens/Settings/*` (You › "Open Last Profile at Launch", off), `ContentView.swift:32,137` (auto-enter once per cold launch, PIN → picker), `ProfilesViewModel.start()`; shared flag already exists |
| A11 | BUG-155 search (a)+(c) if the measurement says they are enough | `shared/.../catalog/CatalogData.kt:33-63` (cancel the inflight fetch when the last waiter leaves), `Screens/SearchView.swift:132` (debounced query into `SearchContent`), `SearchViewModel.swift:410-444` |
| A12 | Strings ×6, tracker rows → BUILT, BUG-154 → BUG-159 |  |

Device pass (Test profile, dev build): the 10-08 draft's 7 steps + 8. Open a folder from row 3 (Stage, then Classic), Menu: same row and card focused. 9. No Zoom ON: one ring on the playing trailer card; No Zoom OFF: zoom, no box. 10. A landscape-shape catalog (his add-on or the fixture) draws a 16:9 row; the global Landscape Posters toggle still overrides. 11. Remember Last Profile ON: cold launch lands in the profile; PIN profile → picker; Switch Profile → picker. 12. Search: type a 10-letter title with his add-on count; the cursor keeps up; results land within ~2 s of the last letter.

### 4.2 rc4 (build 136)

`scripts/cut-rc.sh` after the A merge; tag `tvos-v0.3.0-beta.19-rc4`; IPA on litterbox + filebin + gofile, size verified. Release notes with `--prev-tag tvos-v0.3.0-beta.19-rc3`: Search & Discover (its drafted notes), player P1/P2/P3 (Developer "Seek Preview Frames" default Harvest Only), Batch A by item, every new setting with its default (Rail Hidden available / default Always Visible; Remember Last Profile off; Discover placement Own Tab). Regression checklist = the player plan's post-P5 list minus P4/P5 rows.

### 4.3 P4 ∥ Batch D (two clones)

P4 per the player plan (W0 spec + critique, 2 agents + 1, 2 Opus rounds, 6-step pass) plus BUG-129 and BUG-143 (D6).
Batch D = U6 (CW restore, with tests), U7 (TorBox pagination, tests beside composeApp's), U1 (MDBList sorts; D7 pass), U2 (ytId), FEAT-56 SenPlayer (D8 device test), then the GitHub #5 answer. Upstream diffs are the spec; 2 agents; 2 Opus rounds.

### 4.4 Batch B (re-sequenced 2026-10-16 from his rc4 verdict)

Order is his: the no-go first, then what Batch A missed on his box, then the polish.

| # | Item | Shape / files |
|---|---|---|
| B1 | **BUG-145 + BUG-159 revert + FEAT-67: "Show catalog details in headings" toggle, default OFF (D13)** | `StageCopy.headingAddon` gated; `HomeView.folderBox` (A5's line) and the hero-OFF panel's `folderHeroDescription` gated; `DiscoverRowsPlan` heading rule; Appearance row + 6 strings. |
| B2 | **BUG-165 exit eject (D15)** | Repro in Test (CW hold menu → play → pause card → scrub → Menu, both engines, console on `[MenuProbe]`/`gateCoverMenuTap`); fix in `MPVPlayerView` (cover Menu tap re-enable timing) or the cover host; UI leg: Menu from a Home-underneath play never leaves the app. |
| B3 | **BUG-164 No Zoom leading-edge clip** | `BrowseComponents.leadingEdgeAllowance`: No Zoom branch gets the overlay tile's leading growth + ring band; `RowLeadingEdgeClipTests`. |
| B4 | **BUG-162 + BUG-163 per-row landscape rows** | Card size from Poster Size (poster height × 16/9), strip row height from the row's card size (`StripGeometry`/`StripRowsPlan`), heading gap as portrait rows; `InlineTrailerCard` landscape path reveals for per-row landscape (sim repro with the BUG-157 fixture first). |
| B5 | **BUG-156 (b) folder ← Detail restore + (a) Home re-grab on his box** | `FolderRowsPage`: push/pop capture + `restoreAfterUncover` on its own `StageController` (mirror `StageStripHome.syncCover`); Home: re-grab on the first non-target row change regardless of age, keep the remembered card through a trailer collapse; ask Steven for `[StageStrip] restore` lines if it still jumps. |
| B6 | BUG-146 second trim | One constant on the strip (heading→shelf `md` → `sm`, or shelf 12 → 4), his call on the number. |
| B7 | FEAT-71 Layout out of the folder page's top band | Settings › Home Screen › Collections Layout (FEAT-61 (b)); Edit Filters stays as a hold action / hidden at rest. |
| B8 | FEAT-72 Best Result fields (D12) | `SearchTopResultCard`: drop `foundIn` + rating, type always. |
| B9 | FEAT-70 folder seed = first item (D14) | `FolderRowsPage.seedStage` / `FolderStageInput.step`. |
| B10 | BUG-166 quick half: force gpu-next for a DV P5 the router sends to mpv + picker note | `PlayerEngineRouter` reason → `MPVPlayerView` `videoOutput`; the real P5-MP4 native path stays in P5. |
| B11 | UX-16 (1) Stage + Discover speed (the device A/B session: glide 0.5 vs 0.35, swap pause 0.45 vs 0.30) | As before. |
| B12 | FEAT-73 Discover grid-first (D11) | `DiscoverTabRoot` / `DiscoverPillBand`: Type + Genre pills over the grid, default catalog rule, rows as "Browse". M. |
| B13 | BUG-155 (b)+(d) search fan-out | As before. |
| B14 | The rest of the old B list: wash (B2 old), BUG-147, BUG-151 localized copy (lower: his add-ons ship French), BUG-150, black poster, FEAT-61 (b), BUG-153, FEAT-64 watched badge (+ hide toggle, D4) | As before. |

3 agents, 2–3 Opus rounds, device pass in Test: the old 11 steps + heading toggle both Homes + No Zoom far-left
card at rest and with the trailer + his landscape fixture row at Medium+ + folder ← Detail restore + the
BUG-165 repro leg + Best Result card. Release notes must say the heading details are OFF by default and that
rc4's hero-ON line is the toggle's ON state.

#### 4.4b Batch B second half (re-sequenced 2026-10-17 from his rc5 verdict)

The items the rc5 reply promised (B11 P1+P2, B12, B14, B15) have their own build plan: `docs/rc5-reply-promises-plan-2026-10-17.md`.

B1–B10 shipped in rc5 (build 137). What is left, his rc5 items first:

| # | Item | Shape / files |
|---|---|---|
| B11 | **BUG-162 landscape rest size (D16) + BUG-146 heading → art** | `PosterStyle.cardWidth/cardHeight` (shape-landscape rest = folder-tile size), `InlineTrailerCard` portrait morph stages for shape-landscape rows; `StripShelfPadding` top 12 → 0 on the strip, `StripGeometryTests` re-derived (clearance against the heading glyphs, not its line box). Rig check in HIS config (Medium+, Hide Titles ON, No Zoom OFF, Card Depth ON, his landscape add-on or `scripts/device/fixtures/landscape-addon.py`), a measured frame before the reply claims it. |
| B12 | **BUG-173 title once on Home** | `StageCopy.make` / `HomeRowPreviews.swift:55`: on Home's strip a folder preview's stage copy drops the collection title; `StageCopyTests`. S. |
| B13 | **BUG-156 hold the engine's first move** | `StripPager`: while an uncover restore is pending a non-target row change does not move `positionId`; the remembered card is the only default candidate during the window (`StageController`, `FolderRowsPage`, `StageStripHome`). Fix the `retired why=expired` logging gap. UI legs + rig with his flags. M. |
| B14 | **FEAT-64 watched tick on Home + folder rows** | `PosterCard.watchBadge` (Library today) on catalog rows, CW excluded; hide toggle (D4) later. S–M. |
| B15 | BUG-168 native half: no empty preview frame on AVPlayer | Native transport: time card only when the engine cannot give a frame. S. mpv half waits for the BUG-165/168 repro card. |
| B16 | UX-16 (1) Stage + Discover speed A/B | Was B11. |
| B17 | FEAT-73 Discover grid-first (D11) | Was B12. |
| B18 | BUG-155 (b)+(d) search fan-out | Was B13. |
| B19 | Wash, BUG-147, BUG-151, BUG-150, black poster, FEAT-61 (b), BUG-153 | Was B14 minus FEAT-64. |
| B20 | FEAT-76 per-collection layout (D17) | After B11–B15. |

BUG-170 (HDR before the first frame), BUG-167 (start time) and FEAT-77 (D18) go to P5. The device pass adds: his
config's heading measurement, a landscape row at rest + with the trailer, Home ← folder and folder ← Detail with
no visible detour, a watched film's tick on Home.

### 4.5 Batch C ∥ P5

C1 FEAT-60 header logo, C2 scrim, C3 synopsis affordance, C4 U5 toast, **C5 BUG-130 + BUG-128 trailer seam** (repro with the *Pinocchio* ids and the health probe first; carry the `detail-bg` time into the cover; fix the replay/stall at the repack or looper seam the probe names). P5 per the plan with B19 rescoped (D3), plus the rc4-verdict player items: BUG-166 real fix (P5 in MP4 on native, the P4-owed path), BUG-167 start time (skip the native probe when the picker's tags already say P5/MP4, open mpv in parallel), BUG-168 thumbnails (colour follows BUG-166; cadence/stride). Codex round on 10-29 over `rc4..tip`.

### 4.6 rc5 + comms

Full regression pass (the player plan's list + every batch's device list), build 137, notes per batch with every default, Steven's DM split by area with asks (collection-page photo at rest, OLED walk, Stage at the new speed, rail Hidden, Detail header, French copy on his Netflix rows, SenPlayer hand-off if he has it). Translation pass before any public beta.19. Tracker rows → SHIPPED; dashboard ITEMS reconciliation; CLAUDE.md + memory.

---

## 5. Steven's reply DM (SENT 2026-10-14 19:55Z as drafted; reply 2 to his answers is drafted and waits for the go)

One message, bubbles by area, no new build yet:

- Thanks for the four follow-ups and the photos; all read.
- **Search**: the delay is the search itself, not the keyboard: a new letter does not stop the previous search's add-on requests, so they pile up; also the results screen redraws on every letter. Both fixed next build; ask whether the cursor lag is there before any result arrives.
- **Collections / back**: confirmed in the code, both Homes; next build restores the row and the card. Ask: does "also in old home page" mean Home after leaving a collection, or the collection page after Back from a film?
- **Black square**: confirmed why it is only from collections and search (Home cards arrive with the logo already cached); next build.
- **Landscape catalog**: the app reads the add-on's poster shape but never uses it; next build draws such catalogs as wide cards. Ask for the add-on's manifest URL so it can be tested.
- **White box**: it is the still-focus outline that "No Zoom on Focus" draws, doubled on the playing trailer card; next build draws one outline there, and the outline takes the poster's colour. Ask which photo is which setting.
- **Watched titles**: the check badge from the official app comes next build on Home rows; a hide option follows.
- **Profile at launch**: a "Remember Last Profile" setting next build; PIN profiles still ask.
- **OLED video at 3:00**: seen; on the list with the collection page sharpness.
- Build: rc4 within the week; it also carries the new Search & Discover and the new player (thumbnails while scrubbing, swipe scrub, chapters), so the DM for it will be long.

Lint `python3 scripts/deslop/deslop.py`, Codex cleanse skipped (quota) or run if `codex login` works, show at 5/5, send only on his go via the ego-browser recipe (memory `reddit-chat-smash-fetch`); move the DM watermark.

---

## 6. Risks

- **rc4 is a seven-area pile** (S&D, P1–P3, Batch A) on a tester who prefers Classic; the DM must be split by area and each batch's device record kept so a "feels wrong" note is bisectable.
- **P3's ★ steps are hardware-only** (4K decode on a debrid link, host connection count, DV profiles, memory, exit mid-decode). If any fails, P3 ships Harvest Only (the default) with Decode behind the Developer toggle, which is already the shipped shape.
- **A3's immersive folder pages** change Tabs-mode behaviour Steven did not ask about (bar gone until pop); matches official Nuvio; the fallback (re-link the grid's scroll view) stays in the spec.
- **BUG-156's Classic half** touches `PinnedRowSettle`, the most regression-prone Home code (BUG-87/89/112 history). UI legs both layouts, device pass both layouts.
- **BUG-155's cancel change** touches `deduplicatedHttpGetText`, which Home and Discover share; a ref-count bug would cancel a live Home fetch. Unit test the waiter count; smoke Home after.
- **U1 changes MDBList DEFAULT order** (owner's saved order instead of newest-first); say it in the notes.
- **SenPlayer parameters are unverified**; the GitHub answer waits for the device test.
- **Codex is out until 10-29**; Opus rounds are the record until the rc5 round.
- **Provisioning**: the free-team profile lasts 7 days; every device pass after 10-21 needs another re-sign.
