# Orivio v0.13, as Steven pointed to it (2026-10-15)

Source: Steven's DMs 2026-10-15 07:28Z (release link + Smash video https://fromsmash.com/7Uba5a_5hZ-ct, which expires after 7 days).
Release: https://github.com/prehakanson-art/OrivioTVAppleTV/releases/tag/v0.13 (published 2026-10-15 05:12Z; prehakanson-art, the same author as the app compared in `docs/orivio-feature-comparison-2026-10-01.md`).

## Video (IMG_8958.mov, 22 s, a phone filming an Apple TV; pulled 2026-10-15 on Christian's go, file in ~/Downloads, not in the repo)
Frames (TV area cropped): `01-home-row-detail-hero.jpg`, `02-flip-slide-between-titles.jpg`, `03-detail-page-housemaid.jpg`, `04-detail-page-at-rest.jpg`, `05-scrolled-compact-logo-header.jpg`.
What it shows, in order:
1. A title page ("Doing Life") open full screen with a "< Home" pill top-left. Under the hero a shelf of posters ("Dramas to Watch After Midsommar", more shelves below) is the set you flip through.
2. Pressing Left/Right moves to the neighbouring title: the whole page slides sideways as a rounded full-screen card, the next page entering beside it with a thin gap and the old one leaving (frame 02, two pages on screen at once). No return to the shelf between titles. The ambient colour behind the screen follows each poster.
3. Each page has the same layout: the title (logo art when there is one, big yellow "THE HOUSEMAID"; a serif text title "The Invite." when there is not) at the lower left; under it a meta line, a 3-line synopsis, a badge line (year, runtime, star rating, 4K, Dolby Vision, Dolby Atmos); then Play + three round icon buttons; cast and director set right-aligned at the lower right; a "Trailers" row peeking at the bottom edge.
4. Down scrolls the page to Trailers, Cast & Crew and info tiles; Up returns it to the full-screen hero.
So the "full-screen poster browse view" is a Detail page you can page sideways through, seeded by the row you opened it from. It is not a separate poster grid.

## Which "title changes" Steven means (re-read against the Detail pass, 2026-10-15)
Frame `05-scrolled-compact-logo-header.jpg` (about 18.4 s): when the Detail page scrolls down from the hero, the title logo cross-fades into a **compact centred logo at the top of the scrolled page**, with Trailers, Cast & Crew and Sources below on a blurred, tinted copy of the artwork. That is his FEAT-60 ask (the Apple TV app / Fusion logo that fades in on the first scroll; `docs/steven-beta19-rc3-verdict-2026-10-06.md` line 57 and 112) plus the "blur effect" and darker-area asks. So the likeliest meaning of "titles" is FEAT-60, not the hero layout. It is also a second data point that the release notes do not mention it.
Home row headings (frame 01): plain, small, directly under the hero ("Dramas to Watch After Midsommar"), with no add-on name and no source count. That matches his FEAT-67 / BUG-146 asks; he may mean this too.
Our current hero (logo slot lower left, meta line, 4-line teaser, Play + icon buttons, cast right) already resembles the hero in frames 03/04. The gap is the scrolled state and the sideways flip.

## What the release notes say (read in full)
- A full rebuild, aimed at fast scrolling on older Apple TVs (HD, first 4K): smooth Home rows, lighter row-to-row moves, startup faster.
- **"Flipping between movies and shows on a Detail page is smooth. The titles either side are prepared in the background, so a flip just slides the next page in."** This is the only line that describes the browse-from-one-title-to-the-next behaviour Steven calls "opens full screen and you can browse from one movie to another, like the Apple TV app". It describes a Detail page you flip sideways through neighbours from the row you came from. Not confirmed against the video.
- A new side menu: tabs stay put when it opens, more solid, **Settings > Appearance > "Hide side rail when closed"** (Left at the edge or Back brings it up). It stops opening by itself on title open, Play, link list. Three styles: side rail, sidebar, top bar.
- Live TV guide (EPG), catch-up, live channels on Home.
- Link list: real resolutions, a "Full stream names" setting, link badge packs (Badger).
- Trailers fixed through a backup lookup; auto-play trailer delay honoured; black-bar trailers and backdrops zoomed to fill.
- Match Content: waits for the TV's mode switch to finish; .mp4 now switches too.
- Install note: the "Sideloadly" IPA keeps the historical bundle id and replaces an existing Orivio; the "Sideload" IPA installs alongside.

## Earlier reading (before the video)
The notes never mention title styling, hero titles or heading position. His message says it "includes what I asked you for in the description regarding titles". Closest matches, none certain:
1. "Hide side rail when closed" (his hidden-sidebar ask, FEAT-62 here), though that is not about titles.
2. "Full stream names" (the link list, not Home).
3. The video may show the title treatment. Ask him or read the video before replying specifically.

## Why it matters here
- FEAT-69 (full-screen poster browse view): a product call, parked "later".
- FEAT-62 (rail Hidden mode) is already in Batch A and matches the Orivio setting.
- Orivio also gives a data point for the reinstall question: it is another fork distributed through Sideloadly; whether our bundle id collides with it is unknown.
