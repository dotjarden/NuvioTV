# Steven's beta.19-rc7 verdict, 2026-10-18

Source: Reddit chat with u/mrStevenx3, read 2026-10-18 23:42Z by the local task `nuviotv-reddit-dm-check` (`fetch-dms.sh --since 2026-10-18T21:34:10.534Z`). Messages 22:53Z-23:37Z; 4 photos (22:53Z) unread. New DM watermark `2026-10-18T23:37:01.151Z`.

## Confirmed working
HDR on from the start of the film; subtitles (two films); progress bar (had it already); landscape row gap fine; New Home speed Intermediate and Standard both fine (slight preference Standard); Rows/Grid for collections; Detail pages much smoother; Search no issues; loading screen with pulsing logo "very clean". Native Player limits understood.

## New items
- **BUG-174** (P2): Going back from a player (external or built-in) returns to the stream selection instead of the app's Home/Detail he came from.
- **BUG-175** (P3): Wide poster on top (landscape card + trailer) works in his collection but not in the Continue Watching section.
- **BUG-176** (P3): Going back from a collection to Home takes two moves on the new Home (Classic is fine).
- **BUG-177** (P3): Detail page: depth effect and focus ring don't apply to trailers, episodes or season posters.
- **BUG-178** (P3): Detail page: scrolling back up, the shadow that appears going down moves up with the content (video offered).
- **BUG-179** (P3): Actor biography stays cut off, even after clicking it; the full text can't be read.
- **BUG-180** (P2): While menus are open during playback the film behind plays at ~10 fps, very choppy (on top of the menu stutter already reported).
- **BUG-181** (P3): Animals (mpv): thumbnails still not real time, a transparent image until they load; Dolby Atmos still not decoded (see FEAT-75). HDR from the first frame and subtitles are confirmed fixed.
- **BUG-182** (P4): Pulsing-logo loading screen: the title disappears and restarts its animation at each loading step instead of pulsing continuously; he'd drop the text under the title (FEAT-77).
- **BUG-183** (P3): With automatic stream selection the stream list still shows for about a second; Play should go straight to the loading animation.
- **FEAT-79** (P3): Use the Classic interface inside collections when Classic is selected (collections show the new Home's look; Rows/Grid choice itself works well).
- **FEAT-80** (P4): Sidebar placed top-left instead of middle-left, plus an icons-only option (no text).

## Reinforced
- Landscape trailer enlargement: keep the Apple TV default focus size and play the trailer inside it (same as his 19:47Z rc6 follow-up).
- Home still less smooth than Classic (varies, stutters sometimes): UX-16 / B16.

## Question owed
Do the subtitle and language preferences set in the app apply to films played in an external player?
