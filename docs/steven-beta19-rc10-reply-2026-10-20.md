# Steven's reply to the rc10 answer, 2026-10-20 (video + photo)

Source: Reddit chat with u/mrStevenx3, read 2026-10-20 21:10Z in the interactive session (`fetch-dms.sh --since 2026-10-20T19:40:02.013Z`). It answers the rc10 reply DM sent at 19:40Z (`docs/comms-dm-drafts-2026-10-20-rc10-reply.md`).
- 20:34:47Z: one message (French, translated by him), with a Smash link.
- 20:34:51Z: one photo (`mxc://reddit.com/skfowl8inowh1`, 1280 × 960 from `i.redd.it`).
New DM watermark: `2026-10-20T20:34:51.446Z`.

Media, kept out of the repo: `~/Downloads/steven-reply-smash-2026-10-20/IMG_9057.mov` (Smash `3~hIedqQz6-ct`, 1 file, 510.98 MB, expires ~2026-10-27; 3:11, 4K30, portrait phone video, downloaded through ego-browser space `reddit dm sweep`, script `~/Library/Logs/NuvioDM/steven-reply-smash.js`) and the photo. Named frames, the pacing scripts and the photo are in `docs/research/steven-beta19-rc10-reply-2026-10-20/`.

## What he says, point by point

1. **The focus ring (BUG-153).** "I thought you had already turned it off for trailers, episodes and seasons after my last feedback?" He ran the A/B we asked for: the accent ring on or off "made no difference to how it feels. The previous version was smoother. Now the first scroll is too abrupt." So the ring is not the cause on his box; Batch M's ring measurement does not explain his lag. The page is.
2. **The side menu (FEAT-80).** Our proposal (today's pill by default, the flush rail as an option) is "good too". The Centre position "works well in the middle as it is now, but less well in the top left the way I've set it up" (his config is Corner). In Icons Only the transparency "works fine on the Detail page"; on Home "it just shows a grey shape, because it sits on a black background". A "darkening effect kicks in after about a second in icons-only mode". The side menu animation "is much smoother in Settings than on Home".
3. **The video.** He had already planned to film "the current state of Home and the overall smoothness of the app". His caveat, which the analysis below confirms: "my phone seems to smooth things out, so they look more fluid than they really are. Picture the animations you see, but with micro-stutters on everything: the side menu opening and closing, the menu for removing films from the watchlist, the synopsis scrolling, going back from a collection to Home… You can only really spot the stutters in the clips at the moments where it properly freezes."
4. **The "title in the centre" photo (BUG-190).** Taken earlier, forgotten; sent now.

Nothing new on the player, FEAT-82, FEAT-61, BUG-193, BUG-194, FEAT-66.

## The photo (BUG-190)

`photo-classic-collection-logo-centred-skfowl8inowh1.jpeg`: the Classic rows page inside the **Netflix** folder, second row ("Top 10 des films (Films)") focused on *Sacrifice*. The left column shows the title logo, "2026" and three lines of synopsis as one block that starts about 45 % down the header panel, with nothing above it: no Netflix folder logo. That block is the "logo in the centre". Compare the Prime Video photo from 17:40Z (`steven-beta19-rc10-photos-2026-10-20/photo-6-wicegpcesnwh1.jpeg`, first row focused): the folder logo sits top-left with the title block right under it, which reads as top-aligned.

The video shows the same Netflix folder at 3:01–3:11 (`v-183s-…`, `v-187s-…`): there the NETFLIX folder logo is present, risen above the title block (`FolderStageLogoLayer`, `Screens/FolderRowsPage.swift` §2.5), and the stack logo + title + meta + synopsis spans roughly 24–78 % of the panel. So the block's top (`stageBlockTop`) is well below the panel's top edge in both cases; with the folder logo above it the page still looks anchored, without it the title logo floats mid-panel. Two things to check in the fix: (a) why the folder logo was missing in his photo (not loaded yet, or the risen layer hidden on that path), and (b) whether the stage block should pin to the panel's top on the Classic collection page the way the Classic Home hero-OFF panel does, instead of keeping the Stage block's vertical position. Scheduled as Batch P P8.

## The video: what is in it (`IMG_9057.mov`, 3:11)

| Time | Screen |
|---|---|
| 0:00–0:02 | "Chargement des catalogues…" (cold start, recording began mid-load); Stage Home (Spider-Man) up at 0:02. |
| 0:02–0:20 | Stage Home walk down the rows (Continue Watching, Top 10 séries, Crystal Lake, Midsommar, Friends, Netflix row, Clayface) and back up. |
| 0:20–0:22 | The Corner rail opens in Icons Only over the Clayface / Spider-Man hero (`v-020s-home-rail-icons-only-grey-slab.jpg`), then Settings. |
| 0:22–0:41 | Settings, camera zoomed on the rail: the rail opened and closed repeatedly in Icons Only (`v-024-040s-settings-rail-1fps-sheet.jpg`). |
| 0:41–1:30 | Settings › Appearance, scrolled top to bottom: his full configuration (table below). At 1:07 he opens the Rail Labels menu and switches Icons Only → Shown. |
| 1:30–2:00 | Home again: Spider-Man, Crystal Lake row → Crystal Lake Detail (Episodes, Casting) → Back → The Trap. |
| 2:00–2:02 | Home → Search: **0.9 s of black** between the Home dim and the Search page (`v-120-123s-search-open-10fps-strip.jpg`). |
| 2:02–2:22 | Search "Buffy contre les vampires" → Buffy Detail (Episodes, Casting) → Back to Search → Home. |
| 2:22–2:45 | Home: Will & Grace, Hope, the Streaming services row (Netflix, Disney+, Universal), the Genres row (Action…), Seinfeld Detail, back. |
| 2:45–2:58 | Home on Clayface with the rail now showing labels (Rechercher, Bibliothèque, Addons, Paramètres, Steven), opened and closed several times (`v-170s-home-rail-labels-shown.jpg`). |
| 3:00–3:11 | Streaming services → the Netflix folder, Classic rows page (`v-183s`, `v-187s`), rows walked. |

Not in the clip: the watchlist hold menu, a long synopsis scroll, an actor page (BUG-194), a collection → Home return (BUG-188), the player.

## The video: measurements

Method: per-frame scene-change score on a 320-px copy (`ffmpeg select=gte(scene,0)`), then (a) holds of identical frames with motion on both sides, (b) the frame-to-frame pacing inside each animation burst, run on this clip and on his rc9 clip (`IMG_9025.mov`, 10-19) with the same thresholds (`pacing-compare.py`, `pacing-bursts.py`).

| Measure | rc10 clip (today) | rc9 clip (10-19) |
|---|---|---|
| Short animation bursts (4–15 frames) | 192 | 201 |
| Bursts with a duplicated frame inside (a 33 ms hold) | 56 (29 %) | 50 (25 %) |
| Bursts that re-accelerate after their peak (step > 2× the previous) | 61 (32 %) | 77 (38 %) |
| Median share of the biggest step in a burst | 0.39 | 0.37 |
| Holds ≥ 3 frames (≥ 100 ms) with animation on both sides | 0 | – |

- **The two clips pace the same.** Whatever makes rc10 feel like "20 fps" to him is below what a 30 fps phone recording of a 60 Hz panel can show, exactly as he warns. The 77 "holds" the loose filter found are all rest states between presses (checked frame by frame at 0:21, 1:32, 1:43, 1:50, 2:09, 2:18, 2:45, 2:53). This video cannot rank rc9 against rc10; only the rig can (Batch P Wave 0, D6).
- **One real freeze: Search.** From Home (The Trap) to the Search page the screen is black from 2:00.8 to 2:01.7 (TV luma 20 against 46 for the Search page, 99 for Home), after a one-frame white flash at 2:00.6. Filed as **BUG-195**.
- **The rail tint changes.** In the Settings close-up the Icons Only pill alternates between a lighter and a darker tint across its opens (`v-027s-settings-rail-dark-tint.jpg` vs `v-028s-settings-rail-light-tint.jpg`), which matches his "darkening after about a second". Filed as **BUG-196**; it may be the same material question as FEAT-80 (b) / Batch P D3.
- **The grey slab on Home.** At 0:20 the Icons Only pill over the dark Clayface hero is a flat light-grey rounded rectangle; over the bright Spider-Man hero a second later it reads as glass. His "grey shape on a black background" is reproduced on camera; it is the FEAT-80 (b) item (Batch P P3), now with a frame.
- **Cold start.** The clip starts mid-load; Home is up 2.0 s into the recording. No item.

## His Appearance settings (from 0:41–1:30, for Wave 0 / D6)

| Setting | Value |
|---|---|
| Theme accent | Blanc (White) |
| Anneau de focus couleur d'accent (accent focus ring) | ON (he toggled it for the A/B; ON when filmed) |
| L'anneau prend la couleur de l'affiche (ring takes the poster colour) | ON |
| La profondeur prend la couleur de l'affiche (depth takes the poster colour) | ON |
| Pas de zoom au focus (No Zoom) | OFF |
| Fondu de bord de rangée (row edge fade) | OFF |
| Afficher les détails du catalogue dans les titres | ON |
| Noir profond OLED (deep black) | ON |
| Style des paramètres | Par défaut |
| Navigation | Barre latérale (rail) |
| Barre latérale | Masquée (hidden at rest) |
| Position de la barre latérale | Coin (Corner) |
| Libellés de la barre latérale | Icônes seules at the start; switched to Affichés at 1:07 and left there |
| Découvrir | Désactivé |
| Police | Système |
| Taille | Moyen+ |
| Coins | Arrondi (Rounded; his rc10 photo 4 was taken in Square) |
| Masquer les titres (Hide titles) | ON |
| Lignes au format paysage | OFF |
| Affiches personnalisées | not opened |
| Profondeur des cartes (card depth) | ON; Bord Subtil, Brillance Doux, Couverture du bord Complet |
| Home look | Stage (hero + rows), Continue Watching first |

The Batch P plan's D6 assumption "Rail Corner + Labels Shown" holds (he now runs Shown); add Hidden-at-rest, Deep Black, ring takes poster colour, depth takes poster colour, Rounded corners, Discover off.

## Row changes

- **BUG-153:** ring A/B negative on his box ("no difference"; "the first scroll is too abrupt"; "the previous version was smoother"). The cause is the Detail page, not the ring. Stays with UX-16 in Wave 0.
- **UX-16:** the video cannot show the regression (pacing identical to rc9 on camera); his list of where it stutters: rail open/close, the watchlist hold menu, synopsis scrolling, collection → Home; "smoother in Settings than on Home". Wave 0 config confirmed from his settings.
- **FEAT-80:** his verdict on the proposal: good; Centre works well as is, Corner (his setup) less well; Icons Only is fine on Detail, a grey slab on Home (frame at 0:20). Batch P D3 stands, Home-specific.
- **BUG-190:** the photo arrived (Netflix folder, row 2, Sacrifice): the title block floats ~45 % down the panel with no folder logo above it. Batch P P8 can start.
- **BUG-195 (new, P3):** Search opens on ~0.9 s of black from Home.
- **BUG-196 (new, P4):** the Icons Only rail pill darkens about a second after it opens (Settings close-up; his report).
- **BUG-188:** "going back from a collection to Home" is in his stutter list; not in the clip.

## Reply owed (not drafted)

Points to answer when Christian wants a reply: thanks for the video and settings; the ring result changes where we look (the page, not the ring); the Search black screen is filed; the grey rail on Home is understood and in the batch; the "title in the centre" photo is understood (Netflix folder, row 2) and in the batch; no numbers or date promised until Wave 0 has run on his configuration. Note the mismatch to clear: he believed the ring had already been turned off on trailers, episodes and seasons after his earlier feedback; it was kept after Batch M's measurement.
