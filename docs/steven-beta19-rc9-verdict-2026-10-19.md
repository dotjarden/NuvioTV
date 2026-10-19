# Steven's beta.19-rc8 + rc9 verdict, 2026-10-19

Source: Reddit chat with u/mrStevenx3, read 2026-10-19 19:23Z in the interactive session (`fetch-dms.sh --since 2026-10-19T17:30:40.061Z`).
- 17:58:12Z: one long message covering rc8 + rc9, with a Smash link (`https://fromsmash.com/eESiuXid_b-ct`: 4 files, 475.13 MB; `IMG_9025.mov` is 466.09 MB, plus 3 JPEGs).
- 17:58:15Z: 2 photos, saved in `docs/research/steven-beta19-rc9-photos-2026-10-19/`.
- 18:04Z and 18:10Z: two follow-up suggestions.

The video is not downloaded yet; it waits for Christian's go. He tested rc9 (build 141), which carries every rc8 fix.

## Photos
- **Photo 1** (`photo-1-d0v3s8rnqgwh1.jpeg`): the Classic Home's collection page in Rows layout, "Walt Disney" folder. A Studios row (Disney, Pixar, DreamWorks, Ghibli, Marvel, DC); the hero shows only the collection's own backdrop and logo, with no focused title poster or synopsis. This is his FEAT-79 "not right" (BUG-190). The tips of the Genres row show at the bottom edge.
- **Photo 2** (`photo-2-0p9pixrnqgwh1.jpeg`): Home (Stage), Top 10 Séries with the focused landscape card (Link Click). The next row's tips show along the bottom edge: his "no tips of the posters from the row below" (UX-17).

## Confirmed working
- **BUG-174:** back from the built-in and external players lands on Detail ("much more natural").
- **BUG-183:** auto-select goes straight to the loading screen.
- **BUG-182 / FEAT-77:** the pulsing logo with no text, and only the episode line for series ("Don't touch anything!").
- **BUG-180 (film half):** the film behind the menus is smooth.
- **BUG-177:** focus ring and depth on episodes, season posters and trailers.
- **BUG-179:** the biography opens the full text.
- The clickable long synopsis.
- **BUG-175:** the focused Continue Watching card sits on top.
- **BUG-176:** back from a collection no longer scrolls the page.
- Wide posters without enlargement ("much better").
- **BUG-147:** OLED True Black: the toned-down haze is better and the sudden darkening is gone.

## Not fixed, partial, or regressed
- **BUG-153, REGRESSED:** the first Down and scrolling on big Detail pages is less smooth than rc7, which he called perfectly smooth everywhere. Suspect Batch K's deferred trailer mount (`9dbedc482`).
- **BUG-181, NOT FIXED:** Animals thumbnails still don't work; the box is now grey instead of transparent.
- **BUG-180, menu half:** the menu-opening animation itself still isn't smooth.
- **FEAT-60 / Batch C:**
  - He sees no difference in the darker band behind the synopsis and at the bottom.
  - The compact logo on scroll appears only on the second Down and overlaps the text.
  - He proposes a redesign instead (FEAT-81).
- **BUG-178, NOT FIXED:** the shadow still moves up (video). He notes it goes away with FEAT-81.
- **FEAT-79, NOT RIGHT:** collections with Classic Home (Rows) show no poster and no synopsis (photo 1; video).
- **FEAT-61:** Long shows 3 lines, not 4. He asks to drop the setting and make 4 lines the default on Classic; the new Home already shows the maximum.
- **FEAT-80, NOT WHAT HE MEANT:**
  - He pictured a bar along the very top-left of the screen. Top just moves the centred rail up and looks worse there.
  - Icons Only loses the glass and goes flat, though he likes the icons-only look.
- **FEAT-73, PARTIAL:**
  - The tabs are better, but every catalog still shows; he wants a single general catalog.
  - The Browse tab's row layout seems pointless to him, and it is "not smooth at all, even worse than Home".
  - All Discover menus are in English (BUG-189).
- **UX-16:** Home still lacks responsiveness and smoothness; a side-by-side against Nuvio is in the video.

## New items
- **BUG-185** (P4): leaving the built-in player shows the logo for about a second before Detail; leaving an external player shows the loading screen for about a second.
- **BUG-186** (P2): stuck once in the player on the "Info" screen (the top panel's Info tab or the info overlay); only a force-close got out. Seen once.
- **BUG-187** (P3): back from an actor's biography returns to the top of the movie page (on Play) instead of the cast row.
- **BUG-188** (P4): after back from a collection, the logo you land on flickers once (video).
- **BUG-189** (P3): Discover menus are in English.
- **BUG-190** (P3): FEAT-79's Classic rows page shows no title poster or synopsis (photo 1).
- **BUG-191** (P3, regression): the bottom Home rows show collection posters from the row above, only with No Zoom on Focus. "A bug I hadn't seen in a while is back."
- **BUG-192** (P4): the synopsis "more" is in English. He suggests removing it, since the focus already shows it's clickable (18:10Z).
- **FEAT-81** (P2): Detail redesign in the style of Fusion and the Apple TV app:
  - title with the Play buttons and synopsis on the right, over a blur;
  - one Down reveals the title and the rest (trailers, cast, episodes, season posters);
  - Home's ambient blur instead of the darkening poster.
  He'll show it in the video.
- **FEAT-82** (P3): when square posters are selected, square Detail buttons (Play, Trailer…) instead of rounded ones (18:04Z).
- **UX-17** (P2):
  - Home sizes and spacing like Nuvio's (poster size, spacing); the video shows a side-by-side.
  - No poster tips from the row below (photo 2).
  - He's "really looking forward" to the Home redesign with Wako / Netflix-style animations. Check whether an earlier DM promised that before answering.

## Corrections
- **BUG-128 / BUG-130:** he never reported a full-screen trailer freeze. That was u/an_angry_Moose (public thread); the rc8 DM attributed it to him by mistake.
- **Black poster (rc3):** he thinks it was a missing TMDB image, not an app bug. The rc9 change was harmless.
- **BUG-151:** he had already said the Stage text was fine, possibly because his add-ons are all his own (French).

## Effect on the queue
- **Before P5:** BUG-153 (a regression we caused), BUG-186 (stuck player, P2) and BUG-191 (a regression).
- **Goes into P5:** BUG-181 (the DV thumbnail path) and BUG-180's menu half (player chrome).
- **New design batch, owed his video first:** FEAT-81 Detail redesign and UX-17 Home layout.
- **Small fixes:** BUG-185, BUG-187, BUG-188, BUG-189, BUG-190, BUG-192, FEAT-61, FEAT-82, plus the FEAT-80 and FEAT-73 rescope.
