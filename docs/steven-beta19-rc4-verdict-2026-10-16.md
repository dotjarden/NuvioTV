# Steven's beta.19-rc4 verdict — DM 2026-10-16 + two videos

Read 2026-10-16 ~16:20 ET from the Reddit chat room (`scripts/reddit/fetch-dms.sh --since 2026-10-15T22:10:27Z
--summary`; the DM landed 20:09Z, 22 h after the rc4 DM). One Smash link
(https://fromsmash.com/vX7Se6azRY-ct, expires ~10-23) carrying two videos, downloaded through ego-browser
(space `reddit dm sweep`, the "Click to download your files" leaf; `~/Downloads/Smash.zip`, 1.3 GB) and
unzipped to `~/Downloads/steven-rc4-smash/` (`IMG_8966.mov` 8:34, `IMG_8967.mov` 1:39, both 4K30), kept
OUT of the repo. Named frames (1600 px wide, file names carry the video and the second) in
`docs/research/steven-beta19-rc4-video-2026-10-16/`; contact sheets at 1 frame / 2 s read for the timeline.

Build under test: **beta.19-rc4, build 136 (`975a7010`)**: Search & Discover, player P1–P3 (transport bar,
swipe scrub, chapters, seek-preview thumbnails), Batch A (his rc3 items A1–A12). **Not in rc4:** P4
(native-engine parity, BUG-129, BUG-143) and Batch D, both merged 10-16 after the cut (`8e8090806`).

His setup, read off the video: Stage Home (the "new" Home, 0:00–6:30 and both Discover walks), Rail =
**Hide While Browsing** (Appearance pane at 3:27), Poster Size **Medium+**, Hide Titles ON, Landscape
Catalog Rows OFF, Ambient Background ON, Trailers in the row, Discover = Own Tab; Player: **Native player
(Dolby Vision & HDR) ON**, Keep Profile 7 FEL on mpv OFF, **Enhanced Video Renderer OFF** (3:42–3:46),
buffers Default; tvOS Match Content → Dynamic Range ON (his 10-05 DM; the TV's "HDR 10 / 3840x2160@24Hz"
badge at 5:44 confirms the display switched). He turned **No Zoom on Focus ON** at 2:06 and **Depth Takes
Poster Color ON** at 2:12 during the walk.

## His DM, verbatim (2026-10-16 20:09Z)

> Hi Chris, Here's my feedback on this version. There's quite a lot to cover, so I'll try to structure
> everything as clearly as possible, separating the fixes, the areas that still need improvement, and my
> personal observations.
>
> 1. Feedback on the fixes and new features
> * Black square on the description page: This is fixed, and the result is much better. I even get the
>   impression that titles load faster than before.
> * Trailer thumbnails in rows: This is working too. I now get French trailers in collections whenever they
>   are available, which is great.
> * Collections and sidebar: The sidebar now hides correctly when opening a collection. However, it still
>   remains permanently visible on the first row of my Home screen. On the other hand, the new "Hidden"
>   option works as expected: the sidebar stays hidden and only appears when I press Left. So this part is
>   good for me.
> * Row headings on the new Home screen: This is better, but the headings are still slightly too high. You
>   could move them down a little further to bring them closer to the posters.
> * Old Home screen with the hero enabled: I have to admit that I don't really understand this change. My
>   request was specifically to remove the genre and source count displayed next to the title. I asked you
>   to hide this information on the new Home screen, and you've added it to the old one instead, lol. This
>   is definitely a no-go for me. I'd prefer not to have this information displayed on either Home screen.
> * Returning from a collection or a movie: This still doesn't work properly for me, at least on the new
>   Home screen. Whenever I leave a collection, the view still jumps back up. The same thing happens when I
>   open a movie inside a collection and then go back. My position isn't preserved correctly, so this issue
>   isn't fixed on my end yet.
> * White box on the trailer card when zoom is enabled: I'm not sure what you're referring to here, as this
>   isn't a bug I reported. So I don't really have any feedback on this particular point.
> * My add-on with landscape posters: The format detection works correctly, and my add-on now displays
>   landscape posters properly. However, these posters are generally much too small, both for collections
>   and movies. They need to be larger. The title is also still positioned too high on these posters, just
>   as it was before. There's another issue: trailers don't display on landscape posters. I can only hear
>   the trailer audio playing in the background, without seeing the video.
> * Sidebar: As mentioned above, the "Hidden" option works well and does exactly what I'm looking for.
> * Profile at launch: This works correctly.
> * Search: The cursor offset issue is gone, so that's perfect. Search results also appear faster than
>   before, although I still find the process a little slow. There's definitely been an improvement, but the
>   responsiveness could still be optimized further. I also noticed that you've added a "Best Result"
>   option. It works well, and I think it's an excellent idea. To make the presentation even cleaner, I
>   would only display the title, year, and content type (movie or series) in the "Best Result" section.
>   There's no need to show which catalog or source the result was found in, or to display its rating. This
>   would make the interface cleaner and easier to read.
> * Discover tab: Personally, I don't find this feature particularly useful in its current form. The
>   interface is also very slow, although I assume this will improve once you've optimized the performance
>   and responsiveness of the new Home screen. Being able to choose from all available catalogs doesn't seem
>   particularly useful to me either. This is actually one of the reasons I don't use this feature in the
>   official version of Nuvio. The grid layout also has an issue: you have to scroll through every movie in
>   one genre before reaching the next genre. That's not very practical. If you want to make this feature
>   really polished, I think you could follow the same approach as Nuvio, with a grid where you can select
>   the content type (movies or series) and the genre. As for the catalog to use, I think there should be a
>   default general catalog. The "Popular" catalog seems like the best choice to me. I have around 30
>   catalogs, including some that only show the daily top 10. I don't need all these catalogs to appear in
>   a selection list for Discover. It would be better to use a general catalog rather than asking users to
>   choose from all their sources.
> * Video player: I'll need your help with this one because I exclusively use Infuse normally. I wanted to
>   give your player a chance, but so far, the experience hasn't been great. Here are the issues I've
>   encountered:
>   * Dolby Vision content doesn't display the correct colors.
>   * Movies take quite a long time to start playing.
>   * Preview thumbnails while scrubbing don't work with Dolby Vision and work poorly with non-Dolby Vision
>     movies.
>   * When I start playing a movie and then exit playback, the app closes completely or takes me out of the
>     app.
>   Could you recommend which player settings I should enable or disable in the app? I'd genuinely like to
>   be able to use your player properly, but at the moment, the results are far from satisfactory. It's
>   possible that I simply don't have the right settings enabled, so I'd like to get your recommendations
>   before drawing any final conclusions.
>
> 2. My personal feedback on the old and new Home screens
>
> Old Home screen
> * The scrolling bounce issue is still present.
> * Adding the source count and add-on names next to the headings is something I really don't like. As
>   explained above, I don't want this information displayed.
>
> New Home screen
> I'm not going to repeat the points you've already told me haven't been fixed yet. Instead, here are some
> additional observations from using this version.
> * Catalog translations: All my catalog text is now displayed in French. That's great. This might be
>   because I integrated TMDB directly in French into the add-ons I created, but either way, the result is
>   good.
> * Trailer display when a poster is focused: I noticed that you've changed how trailers are displayed. The
>   trailer now overlays the other posters. I really like this effect! I think it looks great. However, I
>   initially encountered a small issue: the poster on the far left was partially cut off along its left
>   edge. The problem eventually disappeared on its own after a while, but I wanted to mention it in case
>   it's relevant.
> * Opening a collection: When I enter a collection, the synopsis and the first movie's artwork aren't
>   displayed immediately. I have to start moving through the collection before this information appears.
>   Ideally, these details should be visible as soon as the collection opens.
> * Collection display options: The option to switch between grid and row layouts inside collections
>   shouldn't remain visible on the first row of the Home screen, as it breaks the immersive feel of the
>   interface. It would be better to move this option into the settings instead, so the Home screen stays
>   clean and immersive.
> * Visual glitch during trailer playback: I still get a visual glitch on the left side of the screen when
>   the trailer for the poster on the far left is playing.
> * Poster outlines with Zoom mode enabled: The outlines around posters are still visible when I enable
>   Zoom mode, whereas they disappear when I disable it. This is particularly noticeable in the top 10
>   sections of my add-ons. However, I don't think this is necessarily a bug. I suspect it's simply how this
>   mode is designed to look on Apple TV. I'm mentioning it so you're aware of it.
>
> EDIT I tried recording a second video to show you the Discover tab, and the issue with the poster being
> cut off on the left returned. I also figured out which setting causes it: the bug occurs when I enable
> "No Zoom on Focus".
>
> That's all my feedback for this version! Overall, there are several positive improvements, particularly
> with search, trailer display, and support for my landscape posters. However, some issues still persist and
> there are a few aspects of the interface that I think need further refinement. Thanks for all your work
> and for the fixes you've made so far! Vidéo link : https://fromsmash.com/vX7Se6azRY-ct

## Video 1 (IMG_8966, 8:34) — what he shows, by second

| From | What is on screen |
|---|---|
| 0–38 | Stage Home: "Nouveaux films ! · The Movie Database Addon" (heading suffix, `v1-002`), Masterplan / Hope / The Trap / Friends, Studios row, Netflix folder → Top 10 row with the in-row trailer card overlaying its neighbours (ANIMALS, `v1-020`). |
| 40–78 | Netflix folder (Stage Rows): Animals, Le Retour du Roi, Chihiro; back out through the Studios row; prime video folder; Lovesick. |
| 80–118 | Tyson Detail (Episodes), The Trap Detail; Interstellar; Masterplan trailer tile; Settings › Apparence. |
| 120–138 | Apparence: **"Pas de zoom au focus" turned ON** (`v1-126`), "La profondeur prend la couleur de l'affiche" ON. |
| 140–158 | Netflix folder in Rows with No Zoom: first card focused with the still ring, **"Modifier" pill at the top-right of the folder's first row** (`v1-140`, his "grid/row option on the first row"). Anneau de focus couleur d'accent, Noir profond OLED, Police, Masquer les titres ON, Lignes au format paysage OFF. |
| 160–198 | Netflix Top 10 row cards 1–7 (`v1-170`, `v1-172`); **prime video folder with his landscape add-on: "Top 10 des films (Films)" as 16:9 cards with the rank numeral baked into the art, heading ~120 pt above the cards, cards 360×203** (`v1-186`, `v1-190`, `v1-196`); the focused landscape card never shows a trailer. |
| 200–238 | Whalefall / Chihiro with the rail open (Hide While Browsing, rail shown on row 0, `v1-207`); Apparence › Barre latérale = "Masquer pendant la navigation"; Settings › Lecteur: Lecteur par défaut, auto-skips, Fiche d'info en pause, Hold Left/Right, Left/Right Click; **Rendu vidéo amélioré OFF, Lecteur natif (Dolby Vision et HDR) ON, Garder Profile 7 FEL sur mpv OFF** (`v1-222`, `v1-224`). |
| 240–278 | Continue Watching hold menu on Chihiro → Lire manuellement → source list (`v1-241`, Lumio · Salon) → "Préparation de la lecture…" ~8 s (`v1-246`) → black ~4 s → plays (SDR, correct colours; TV badge "Apple TV 3840x2160@24Hz", `v1-256`); scrubbing on the P1 bar (`v1-266`). |
| 280–318 | Exit: black ~6 s (`v1-296`), then **the source list again** (`v1-300`): a clean exit to the picker. Animals Detail + CW hold menu. |
| 320–358 | Animals source list (`v1-320`: Lumio 14.4 Go "4K · WEB-DL · DV · 19 Mb/s · HEVC 10bit · Atmos EAC3 5.1"; the next two say "DV · HDR10") → **"Préparation de Dolby Vision…" ~8 s** (`v1-326`) → the mpv loading overlay with the P1 bar (`v1-332`, "Animals · [AD] Lumio · Lumio · Salon · -1:48:11") → **playback with green/magenta colours** (`v1-336`), TV badge **"HDR 10 / 3840x2160@24Hz / HDR10 PQ16"** (`v1-344`). |
| 360–398 | Scrub with thumbnails (green too, `v1-366`), pause card (`v1-372`), **exit → black ~6 s (`v1-378`) → the tvOS home screen (`v1-384`)**; he reopens NuvioTV at 388 and **the Animals source list is still there** (`v1-388`): the app was suspended, not killed. |
| 400–438 | Search "Avatar": **Best Result card = poster, "Avatar", "2009 · IMDb 7.9", "Trouvé dans The Movie Database Addon"** (`v1-408`). |
| 440–514 | Search "the 100": People row first, "Recherche…" for several seconds, Best Result with a placeholder poster, Films · 35 / Séries · 20; The 100 Detail; "les 100": **"Recherche…" for ~12 s** before the first row (`v1-490`, `v1-498`). |

## Video 2 (IMG_8967, 1:39) — Discover, and the far-left cut

| From | What is on screen |
|---|---|
| 0–4 | Stage Home with the far-left trailer card (Whalefall) playing and the rail open (`v2-000`, `v2-002`). |
| 4–60 | Discover tab: Unabomber, rows "Crime · Cinemeta", "Documentary · Cinemeta", Whisper Man, Spider-Man "Action · Cinemeta", Love Hypothesis "Comedy · Cinemeta" (`v2-006`, `v2-014`). Each row is a genre; he walks a whole row to reach the next genre. |
| 60–76 | The Grid pill → the Action grid with shimmer placeholders filling in (`v2-060`, `v2-064`). |
| 78–88 | **App switcher → force quit** (`v2-079`), tvOS home, Divers folder, relaunch: "Chargement des catalogues…". |
| 88–99 | Home back with Whalefall; the far-left card with the rail at rest (`v2-092`, `v2-094`). |

The cut itself is a few pixels on a phone video and does not read on the frames; his EDIT names the setting
(No Zoom on Focus) and the code says why (BUG-164 below).

## Triage

Code read at `8e8090806` (`tvos-shared-extraction`, rc4 + Batch D + P4). "Verified" = the frame shows it and
the code says why. Rows are the tracker's.

### His points in order

| # | His point | Row | Status | Where / why | Shape |
|---|---|---|---|---|---|
| 1 | Black square gone, titles load faster | BUG-152 | **CONFIRMED** | A1 | Close. |
| 2 | Trailer tile logos work, French trailers in collections | BUG-149 | **CONFIRMED** | A2 | Close. |
| 3a | Sidebar hides on entering a collection | BUG-161 | **CONFIRMED** (folder half) | A3 | — |
| 3b | Sidebar still visible on Home row 1 in his mode | BUG-161 | **BY DESIGN** of Hide While Browsing | `RailVisibilityRule.shown`: `.whileBrowsing` hides on immersive / Search / scrolled-down and **shows at the top of Home** (R7). The mode he asked for on 10-08 ("hide it on the first line, show it on Left/Back") is FEAT-62 Hidden, which he confirms works. | Close BUG-161; the answer is Hidden (he is using it). |
| 4 | Row headings still slightly high (Stage) | BUG-146 | **OPEN, second trim** | A4 took `StripGeometry.shelfTopPadding` to 12 (the loaded, loading and message rows). What is left above the shelf: the heading's own line box + `Theme.Spacing.md` + the 12. `v2-006` (Crime · Cinemeta) reads ~10 px at 1600 wide; `v1-002` reads larger on Home. | Trim `Theme.Spacing.md` → `sm` between heading and shelf on the strip, or 12 → 4 on the shelf; one constant, StripGeometryTests. His call on the number. |
| 5 | Classic hero-ON folder line "Genre · N sources" = **no-go**; wants it off BOTH Homes | BUG-159 + BUG-145 + FEAT-67 | **MISREAD, revert** | A5 added `folderHeroDescription` to the hero-ON folder box (`HomeView.folderBox`) because his 10-08 photos showed hero-OFF printing it and hero-ON not; his 10-08 words were about the Stage heading's add-on name (BUG-145) and the 10-14 FEAT-67 said "hide the source count as well as the add-on names". The plan read the photo pair as a missing line. | **B1 first:** one Appearance toggle "Show catalog details in headings" (default OFF) covering the Stage heading suffix (`StageCopy.headingAddon`) and the folder line on BOTH Homes (hero-ON box and hero-OFF panel). Revert A5's hero-ON line under the toggle. |
| 6 | Return from a collection / from a movie inside a collection still jumps (Stage) | BUG-156 | **FAILED for him, two gaps** | (a) Home ← folder: A7 wired `StageStripHome.syncCover` → `StageController.restoreAfterUncover` with a 1.2 s re-grab window after the device pass found the engine's own restoration landing 0.55–0.98 s late on Christian's box. His box runs No Zoom + in-row trailers at Medium+; a morphed trailer card collapsing under the cover replaces the focused view, and a restoration later than 1.2 s is the viewer's. (b) **Folder ← Detail is not covered at all:** `FolderRowsPage.onAppear` only runs `stage.setCovered(false, restoresFocus: true)` and relies on the engine; nothing re-requests the folder strip's remembered row/card, so the pop lands on row 0's default candidate: "the view jumps back up". | (b) is mechanical: the same push/pop capture + `restoreAfterUncover` on the folder page's own `StageController`. (a) needs his probe lines: `[StageStrip] restore …` / `restore regrab …` with `age=`; widen the window or re-grab on the first non-target row change regardless of age, and keep the remembered card through the trailer collapse. |
| 7 | White box on the trailer card: not his report | BUG-158 | **Disowned**; fixed anyway | The 10-09 photo was his, the triage read it as a report. Keep A8 (one ring), close the row. His separate note "outlines visible with Zoom ON" is the system focus edge in zoom mode, by design on tvOS; he says so himself. | Close. |
| 8a | Landscape cards from his add-on much too small | **BUG-162** (new) | **VERIFIED, root-caused** | A9 draws `LandscapeCard` at `Theme.Size.landscapeWidth` 360 × 203, a constant that ignores Poster Size (he runs Medium+; a Medium+ portrait card has a taller footprint) and is the size rc7's saga cards were called "too small" at (FEAT-34 went to 500×281). `v1-190`. | Scale the per-row landscape card off the poster height (`posterStyle.height × 16/9` wide, the morph tile's own rule) or a landscape size table per Poster Size; the Continue Watching row keeps 360. |
| 8b | Title still too high on these cards | BUG-162 | **VERIFIED on video** | Titles are hidden (Masquer les titres ON), so "the title" is the row heading: it floats ~120 pt above the 16:9 cards because the strip plans the row at the portrait height and the shorter card sits at the bottom of that slot (`v1-190`). | Plan the row height from the row's card size (landscape rows are shorter), heading then sits at the same gap as portrait rows. Same fix as 8a. |
| 8c | Trailers on landscape cards: audio only | **BUG-163** (new) | **VERIFIED on video, candidate cause** | `InlineTrailerCard` has one landscape path, keyed on `posterStyle.landscapeCatalogRows` ("already the target geometry — no morph there, the trailer just fades in"); A9 feeds the row a per-row style, so the card takes that path. The audio starts (the player is created and plays), the picture never shows: the reveal is tied to the morph stage machine (P-1b: the card "becomes visible as a landscape tile" at the expand), and with no expand the tile stays at opacity 0, or the tile's `InlineTileArtSource.tileSize` (360×203) never matches the drawn card. | Sim repro with the BUG-157 fixture add-on (`scripts/device/fixtures/`), then make the landscape fade-in path the reveal for per-row landscape too; mute until revealed. |
| 9 | Hidden rail works | FEAT-62 | **CONFIRMED** | A6 | Close. |
| 10 | Profile at launch works | FEAT-65 | **CONFIRMED** | A10 | Close. |
| 11a | Cursor offset gone; results faster but still slow | BUG-155 | (a)+(c) **CONFIRMED**; (b)+(d) OPEN | "les 100" shows "Recherche…" ~12 s (`v1-490`→`v1-498`); People arrive first; the Best Result poster is a placeholder for a while. With ~30 catalogs every letter fans out to every add-on. | B11 as planned: (b) per-add-on timeouts / early emission of the first rows, (d) the catalog fan-out cap. |
| 11b | Best Result: title, year, type only; drop "found in" and the rating | **FEAT-72** (new) | Product call | `SearchTopResultCard` prints name, `metaLine` ("Series · 2021 · IMDb 8.0": type only when not a movie) and `foundIn`. `v1-408`. | **D12.** If yes: drop `foundIn` and the rating from the card, print the type always ("Film · 2009"); the row footnote keeps "Found in". Small. |
| 12 | Discover: not useful as is, slow, catalog picker pointless over 30 catalogs, genre rows force a full walk; wants Nuvio's grid with type + genre over a default "Popular" catalog | UX-16 (speed) + **FEAT-73** (new) | Product call | Stage Discover = one strip row per genre of the selected catalog, the Grid pill opens the focused row's grid. His ask is the official app's shape: a grid, Type + Genre pickers, one general catalog. The speed is the Stage's (UX-16 (1)); the Grid page fills with shimmer per cell (`v2-064`). | **D11.** Options: (1) a "Grid first" Discover: Type + Genre pills over the grid, the default catalog = the first catalog that serves the genre list of the selected type (Cinemeta "Popular" / TMDB "Popular"), the catalog pill kept but secondary; (2) keep the rows and add Up/Down genre paging; (3) both behind the existing Discover placement setting. |
| 13a | DV colours wrong | **BUG-166** (new) | **VERIFIED, root-caused** | The Animals source is "4K · WEB-DL · DV" (no HDR10 tag = profile 5, usually MP4). "Préparation de Dolby Vision…" ran (the probe/remux step), then the **mpv** bar appeared and the TV switched to **HDR10**: the title did not play native. `PlayerEngineRouter.route`: P5 in MP4/MOV → mpv (P3-F7); any native failure also fails over to mpv. mpv's default `gpu` VO has no DV RPU processing, so a P5 (IPTPQc2) stream renders as BT.2020 PQ: the green/magenta picture (`v1-336`, `v1-344`). The **Enhanced Video Renderer** (gpu-next / libplacebo, `MPVPlayerView` line 840) is OFF on his box. | Immediate: Enhanced Video Renderer ON (his DM). Fix: force gpu-next for any DV P5 the router sends to mpv (and tell the picker), plus the P4-owed real P5-MP4 native path. Keep "DV · HDR10" (P8) MKVs on native. |
| 13b | Slow starts | **BUG-167** (new) | **VERIFIED on video** | Chihiro: ~8 s "Préparation de la lecture…" + ~4 s black; Animals: ~8 s "Préparation de Dolby Vision…" + ~6 s loading overlay = 14 s to the first frame. The native path probes the stream, starts the remux, and on the DV P5 source gives up and hands mpv a cold start; the mpv path then opens, demuxes and fills its buffer. P4's loading overlay now prints the stage; nothing shortens it. | Measure the stages on his two sources (`[Loading]`/`[Remux]` lines), skip the native probe when the picker's own tags already say P5/MP4, start mpv's open in parallel with the probe. P5. |
| 13c | Scrub thumbnails broken on DV, poor otherwise | **BUG-168** (new) | **VERIFIED on video** | On the green mpv session the harvested frames are green too (`v1-366`): `screenshot-raw` captures the VO's output, so a wrong-colour playback gives wrong-colour thumbnails, and the FFmpeg `KeyframeThumbnailer` has no DV handling (`HDRThumbnailToneMap` maps PQ). "Poorly" on SDR = sparse (10 s harvest cadence, keyframe stride) and the first frames late. | Follows BUG-166 for colour; cadence/stride tuning in P5. |
| 13d | **Exit closes the app / leaves the app** | **BUG-165** (new, P1) | **VERIFIED on video, on a real remote — P3-F8 is real** | 6:18–6:24: the mpv player (the P1 bar, Animals) exits to black, then **the tvOS home screen**; at 6:28 NuvioTV reopens on the Animals source list (suspended, not crashed: a crash relaunch shows "Chargement des catalogues…", as his own force-quit at v2 1:28 does). The Chihiro exit 40 s earlier went cleanly to the picker. Both plays came from the Continue Watching hold menu (Lire manuellement), so the player cover sat over Home with no Detail under it: one Menu that reaches Home's root is an eject. Candidates: the press delivered twice (the `UITransitionView` Menu tap recogniser that `gateCoverMenuTap` switches off while the controller is up, re-enabled at dismissal start, and the responder chain), or a Menu that lands after the controller's `isLeavingPlayer` with nothing focusable under it. P3 round 5's "rig-only" verdict rested on five remote exits over a Detail page. | **Hotfix candidate for rc5.** Repro: play from the CW hold menu (Home underneath), pause until the pause card, scrub, Menu once. Ask Steven which engine (the bar = mpv) and the exact press. |
| 14 | Old Home bounce still there; the heading info unwanted | FEAT-61 / BUG-159 | known / item 5 | The bounce is BUG-87/89's class on Classic; FEAT-61's note stands. | — |
| 15 | Catalog translations now French | BUG-151 | **His add-ons ship French**; the Stage prints what the catalog sends | Nothing changed in rc4 for this. English catalogs (his Netflix one on 10-06) still print English. | Keep B5 at lower priority. |
| 16 | Trailer overlays the neighbours: likes it | — | positive | The Stage morph (rc4) | — |
| 17 | Far-left poster cut on its left edge, keyed to **No Zoom on Focus**; left-edge glitch during the far-left trailer | **BUG-164** (new) | **root-caused from code** | `CatalogRowView` (the Stage strip reuses it) clips the row's leading edge with `RowLeadingEdgeClip` at `leadingEdgeAllowance` = `ceil(posterWidth × (liftScale − 1) / 2) + ring + shadow`. With No Zoom ON `liftScale` is 1, so the opening shrinks from ≈36 pt (lift) to the ring + shadow only; anything the first card draws past its frame on the left, the still ring band and the overlay trailer tile the Stage now grows over the neighbours, is cut: the still-mode "cut" at rest, the hard edge while the far-left trailer plays. BUG-92's original report was this exact pair (No Zoom ON, first card, inline trailer). "Disappeared on its own" = he turned No Zoom off at some point, then back on for video 2. | Give the No Zoom branch the tile's growth (`max(restingWidth, height×16/9) − restingWidth` on the leading side when the Stage overlay tile is anchored left) + the ring band; or clip only when zoom lifts. One function, `RowLeadingEdgeClipTests`. |
| 18 | Collection opens without the first movie's art + synopsis until the first move | **FEAT-70** (new) | **BY DESIGN**, product call | `FolderRowsPage.seedStage` seeds the stage with the folder (name, "Netflix · 6 sources", cover mosaic) and `FolderStageInput.step` keeps it until the first move (Q1). He wants the first item at once. | **D14.** Seed with row 0's first item once the row lands (the folder logo stays docked), or keep the folder intro. Small either way. |
| 19 | Grid/Rows option visible on "the first row of the Home screen" | **FEAT-71** (new) | **VERIFIED on video**: it is the folder page's Edit band | `FolderEditMenuBand` (Layout › Rows / Grid + Edit Filters) is active at the top of the Stage folder page and shows the "Modifier" pill top-right while row 0 holds focus (`v1-140`). | Move Layout to Settings › Home Screen › Collections Layout (FEAT-61 (b) already plans it) and keep Edit Filters as a hold action or a hidden-at-rest control. |
| 20 | Poster outlines with zoom on: not a bug | — | by design | The system focus edge on `.systemLift`. | Answer only. |

### What Batch A's merged fixes should have covered for him, and why they did not

- **A7 (BUG-156) covered Home only.** Both Homes re-request the remembered row/card after a pop, with a
  hardware re-grab because the focus engine restores late. The folder page's own strip got nothing: a Detail
  pop inside a collection lands on its default candidate. And his Home case still jumps with No Zoom + in-row
  trailers, so the re-grab window or the trailer-collapse case misses on his box. Both are fixable; the
  first is mechanical.
- **A5 (BUG-159) was the wrong fix.** The 10-08 photo pair (hero-ON folder box without the line, hero-OFF
  panel with it) was read as "add the line to hero-ON"; his words were "hide the add-on names and the source
  count". FEAT-67 (10-14) said it again. The line now has to go behind a toggle on both Homes.
- **A9 (BUG-157) detects the shape and draws the wrong size.** The per-row landscape card reuses the Continue
  Watching card's 360×203 constant and the trailer's single landscape path, so the row reads small, the
  heading floats, and the trailer plays blind.
- **A4 (BUG-146)** moved the heading by the planned amount; he wants more.
- **A3 / A6 (BUG-161, FEAT-62)** did what they said; the "row 1" half was never a bug.
- **A1, A2, A10, A11 (a)+(c)** confirmed.

### Player: what rc4 carries and what his box did

rc4 = P1 (transport bar), P2 (swipe scrub, aspect, chapters, harvest thumbnails), P3 (I-frame playlist spike,
FFmpeg keyframe thumbnailer). P4 (native Playback tab, `AVTextStyleRule`, pause card on native, late
subtitles, loading overlay stages, BUG-129, BUG-143) merged after the cut. Nothing in rc4 or P4 changes the
DV P5 → mpv routing or mpv's VO choice, so BUG-166 is a settings answer today (Enhanced Video Renderer ON)
and a routing fix next. BUG-165 contradicts P3 round 5 (`docs/player-revamp-plan-2026-10-06.md`, "P3-F8 did
not reproduce with the Siri Remote"): that pass exited over a Detail page five times; his eject came from a
Home-underneath play. Reopen as a bug, not a rig caveat.

### Not in this verdict

BUG-160 (cold launch on Streaming Services) is not mentioned. Nothing on Library L1, Batch D, FEAT-56.

## Suggested batch order (feeds the master plan's Batch B)

1. **B1** heading details toggle (BUG-145 + BUG-159 revert + FEAT-67) — his no-go, first.
2. BUG-164 leading-edge allowance (No Zoom), BUG-162 + BUG-163 landscape rows (size, row height, trailer
   reveal), BUG-156 (b) folder-page restore + (a) re-grab on his probe lines, BUG-146 second trim, FEAT-71
   Layout to Settings — mechanical.
3. BUG-165 exit eject — hotfix class, repro first (CW hold menu → play → pause card → Menu).
4. BUG-166 P5-on-mpv → gpu-next; FEAT-72 Best Result fields (D12); FEAT-70 folder seed (D14).
5. UX-16 (1) speed + FEAT-73 Discover shape (D11) — the Stage polish pass; BUG-155 (b)+(d).
6. BUG-167 start time, BUG-168 thumbnails → P5.

## Reply DM

Draft: `docs/comms-dm-drafts-2026-10-16-rc4-reply.md` (SlopMonster 5/5; NOT sent). Asks: which player the
eject happened on and the exact press; his rail mode's name; a photo of the landscape row at rest after the
size change; whether Enhanced Video Renderer fixes the colours on his Animals source.
