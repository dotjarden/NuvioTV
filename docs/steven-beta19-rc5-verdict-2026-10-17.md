# Steven's beta.19-rc5 verdict — DM 2026-10-17 + three photos

Read 2026-10-17 ~02:00 ET (`scripts/reddit/fetch-dms.sh --since 2026-10-17T02:14:42.047Z --summary`). The
verdict landed 03:05:26Z (one long message + three photos at 03:05:28–29Z), plus a one-line add-on at
03:15:17Z. DM watermark was already moved to `2026-10-17T03:15:17.266Z` by the 05:52Z DM check (`7d6405b`).
Photos: `docs/research/steven-beta19-rc5-photos-2026-10-17/2026-10-17-rc5-photo-{1,2,3}.jpg`.

Build under test: **beta.19-rc5, build 137 (`eeca35353`)** = rc4 + Batch D (upstream ports, SenPlayer) +
player P4 (native parity) + Batch B's mechanical half B1–B10 (`d5dd6aec1` is an ancestor of `eeca35353`,
checked). Not in rc5: the SwiftUI Pro review fixes (`9ee8597d4`, after the cut).

His setup from the photos and the text: **Stage Home** (stage block on top, one strip row, next heading
peeking), Medium+, Hide Titles ON, **No Zoom OFF** with Card Depth ON (his 03:15Z line), trailers in the row,
Collections Layout = Rows, Infuse Pro as external player (no SenPlayer).

## His DM, verbatim (2026-10-17 03:05Z)

> Hi Chris, yeah, our messages really are crossing each other. It's a complete mess 😂 Here's my feedback on
> RC5:
>
> Regarding the home screen and collections:
> * Section headings and source counts: They're finally gone, thanks! It looks much better now. However, in
>   the collections, the row title appears twice. It would be better to use the same approach as the old
>   home screen, which displayed the poster artwork prominently and showed the title only once.
> * Heading positions: I'm wondering whether the fix to move the headings lower was actually included,
>   because I can't see any difference compared to RC4. The headings are still a little too high on
>   portrait-format collections and much too high on landscape-format collections. They need to be moved
>   further down, especially for landscape posters.
> * Returning to a film and going back to Home: The behaviour when returning to a film from a collection,
>   and when going back to Home from a collection, is partially fixed. The app scrolls back towards the top
>   and then immediately jumps back to its previous position. So the behaviour still isn't quite smooth.
> * Landscape posters from my add-on: It works, but the posters are much too large! It looks as though I've
>   selected MAXI LARGE, even though my setting is Medium+. Their size needs to be reduced so they match the
>   collection posters. Then, when the trailer starts playing, they could expand to the larger featured
>   size. The idea is to keep them the same size as the collection posters normally, and only enlarge them
>   when the trailer starts.
> * Far-left posters with "No Zoom on Focus": They're no longer cut off when this option is enabled.
>   However, we lose the great new effect where the trailer overlays the other posters. That said, I think
>   this is actually a good compromise, as it gives users the choice depending on their preferences.
> * Switching between grid and row layouts for collections: The setting works really well. It's just a
>   shame that we can't configure the layout separately for each collection, like in the official Nuvio
>   app. For example, I'd like to display certain collections, such as "Genres", in a grid while keeping all
>   my other collections in rows.
> * Best search result: This is perfect as it is! The result displayed is always the one I have in mind, so
>   nothing to change here.
> * Opening collections: They now open correctly, immediately displaying the artwork and synopsis of the
>   first film. This part is working well!
>
> Regarding the player:
> * SenPlayer: I don't have SenPlayer installed. I only use Infuse Pro as an external player.
> * Green image in HDR / Dolby Vision: You removed the option I previously had to enable to fix the green
>   image issue. Since then, I haven't had any colour problems with HDR or Dolby Vision content. So this is
>   working perfectly!
> * Preview thumbnails while seeking: On Animals, the mpv player still doesn't display any preview
>   thumbnails. I have exactly the same problem with Spirited Away when using the Apple TV player: I only
>   get a transparent image instead of the expected preview.
> * HDR switching delay: I'm still experiencing the issue where a film starts playing without HDR and only
>   switches to HDR after around 10 seconds. HDR needs to be enabled right from the start of playback,
>   before the first frame of the film appears. This is important to avoid the change in picture rendering
>   partway through playback.
> * Loading screen: The new loading screen is nice, but perhaps you could add the same animation used in
>   Nuvio / Stremio: the title appears in the centre of the screen, grows larger, gets smaller, then grows
>   larger again, and so on. You can look it up online to see exactly what I mean. Otherwise, I can record a
>   video to show you the effect I'm looking for.
>
> One last thing regarding links failing because of network issues: I'm not quite sure what you're
> referring to, as I've never reported this issue to you. I just wanted to clarify that to avoid any
> confusion.
> * Watched indicator on posters: I seem to remember you telling me that you'd added the option to display
>   a checkmark on a poster, like in Nuvio, when a film has already been watched. With all our
>   back-and-forth, maybe I just imagined it lol 😂 But either way, when I mark a film as watched, no
>   checkmark appears on the poster. Is this feature already implemented, or is it still something you're
>   planning to add?
>
> That's my feedback on RC5! Things are moving in the right direction. Thanks for all the work you're
> putting into this 😉

03:15:17Z add-on, verbatim:

> * White outline around posters: One last thing: you also managed to remove the white border I was getting
>   around posters, even with Card Depth enabled and No Zoom disabled. I thought it was related to the Apple
>   TV animation, but apparently not! So that's great, thanks for fixing that too.

## The three photos

| Photo | What it shows |
|---|---|
| 1 | Stage folder page (Netflix collection, Rows): stage = NETFLIX logo, "REPORTING LIVE" title logo, "2026 · Crime · Thriller"; heading "Nouveaux films (Films)" over portrait cards (Stormen, Hoemonal, Money Bank), the focused card morphed into the playing trailer tile (Reporting Live) overlaying its neighbour; "Top 10 des films (Films)" peeking. Heading text bottom → unfocused card tops ≈ 35 photo px ≈ 55–60 pt by the screen's 1.72 pt/px. |
| 2 | Same page, prime video collection: his add-on's landscape row "Nouveaux films (Films)": 16:9 cards (Amazon Original, My Happy End, L'Amour de ta vie focused with the cyan ring), each ~⅓ of the screen wide = the B4 size **624 × 351**. The heading gap reads the same ≈ 44 photo px as photo 1; the cards are what changed (three fill the row where six portraits do). |
| 3 | **Stage Home**, "Services de Streaming" collection row (Netflix / Disney+ / prime video / Universal+ folder tiles, Netflix focused with the red ring): the stage shows the NETFLIX logo with **"Services de Streaming" under it**, and the row heading directly below reads **"Services de Streaming"** again; "Studios" peeks at the bottom. |

## Triage

Code read at `eeca35353` (rc5) / `9ee8597d4` (tip). Rows are the tracker's.

### His points in order

| # | His point | Row | Status | Where / why | Shape |
|---|---|---|---|---|---|
| 1a | Headings + source counts gone, "much better" | BUG-145, BUG-159, FEAT-67 | **CONFIRMED** | B1 `HeadingDetailsSetting` default OFF | Close all three. |
| 1b | **Collection row title appears twice** on Home (photo 3) | **BUG-173** (new) | **VERIFIED, root-caused** | `HomeRowPreviews.swift:55` builds a folder's stage preview with `releaseInfo = collection.title`, and `StageCopy.make` prints `releaseInfo` as the stage meta line (`classicMeta`), so the stage reads "logo / Services de Streaming" right above the strip row whose heading is the same collection title. B1 only gated the synopsis (`folderHeroDescription`); the meta line was left. Classic's folder box shows the logo and no collection line, which is his "old Home" reference. `FolderRowsPlan.swift:255` does the same on the folder page's intro, but there the row headings are the catalogs, not the collection, so no repeat. | On Home's strip, a folder preview's stage copy drops the collection title (meta line empty; the logo or the folder's name carries the slot). Keep it where the heading does not repeat it (folder page intro). One rule in `StageCopy` + `StageCopyTests`. S. |
| 2 | **Heading positions: no difference vs rc4**; still a little high on portrait rows, **much too high on landscape** | BUG-146 | **OPEN; B6 shipped but moved 4 pt** | B6 is in build 137, and it changed heading → shelf from 28 to 24 pt (`StripGeometry.headingGap` `md` → `sm`). Four points is below what a viewer can see at 3 m, so "no difference" is accurate. His photo 1 reads ≈ 55–60 pt from the heading's text to the card tops, the rig's `p2-folder-open` ≈ 30 pt: the extra is the heading's line box (38 pt for ≈ 28 pt glyphs, so ~10 pt of empty box under the baseline) plus photo error; nothing in the strip adds a reach on the Stage (`rowCardTopReach` is set by Classic only). The landscape row's heading gap in photo 2 measures the same as the portrait row's; it reads "much higher" because the 351 pt tall wide cards sit in a page planned for them while the eye compares against the folder tiles. | Two parts. (a) Portrait: shelf top `sm` 12 → 0 on the strip, heading → art 12 pt, and let the zoom lift (20 pt) rise over the heading's empty lower line box (`StripGeometry.headingGap` stays 12; clearance against the glyphs, not the box, re-derived in `StripGeometryTests`). Verify on the rig in HIS config (Medium+, Hide Titles ON, No Zoom OFF, Card Depth ON) with a measured frame before claiming it. (b) Landscape: follows BUG-162's rest size (row 4): a 234 pt tall card top-aligned under the heading. |
| 3 | **Return to a film / to Home: "scrolls back towards the top, then jumps back"** | BUG-156 | **PARTIAL: lands right, two visible moves** | B5 re-grabs AFTER the focus engine's own late restoration has landed on its default candidate (0.55–0.98 s late on hardware, `[StageStrip] restore regrab …`). Each focus change moves the strip's `.scrollPosition(id:)`, so the viewer sees the page glide to the engine's row (towards the top), then our re-grab glides it back. | Hold the engine's first move instead of correcting it: (1) while an uncover restore is pending, a non-target row change does NOT move `positionId` (the pager keeps the remembered page; the re-grab then lands without a glide), and (2) make the remembered card the strip's only default candidate during the window (`.defaultFocus` / `prefersDefaultFocus` on the remembered card in the remembered row, the other rows' focus sections gated as the rail spike did), so the engine's own restoration lands on the target. (1) alone removes the double glide; (2) removes the re-grab. M. Rig repro first with his flags. |
| 4 | **Landscape cards from his add-on "much too large" (look like Maxi Large at Medium+)**; same size as the collection posters at rest, enlarge only when the trailer plays | BUG-162 | **OPEN: B4 overshot** | B4 made a shape-landscape card `posterStyle.height` tall × 16/9 wide = **624 × 351** at Medium+ (photo 2), the trailer tile's size, so the trailer could dissolve in with no morph. rc4's 360 × 203 was "much too small". "The collection posters" = the landscape folder tiles on Home, which `FolderTile` sizes from the width dial: `style.width × 16/9` by `style.width` = **416 × 234 at Medium+** (`CollectionsUI.swift:608–633`). | **Rest at the folder-tile size (416 × 234 at Medium+, `width × 16/9` × `width` at every Poster Size) and morph to 624 × 351 when the trailer reveals**, the portrait row's morph (grow over the neighbours, base card fades). Row: heading right above the 234 pt card, top-aligned; the page keeps the portrait height so the tile has room to grow. D16. The reveal path B4 fixed (base card fades under the tile) stays; the tile now needs the portrait morph stages. M. |
| 5 | Far-left posters with No Zoom: no longer cut; loses the overlay effect, "a good compromise" | BUG-164 | **CONFIRMED** | B3 (`CardSystemLiftStyle.resolve` never takes the tile's manual lift with No Zoom) | Close. |
| 6 | Collections Layout setting "works really well"; wants a per-collection layout (Genres as a grid, the rest as rows) like the official app | FEAT-71 + **FEAT-76** (new) | FEAT-71 **CONFIRMED**; FEAT-76 product call | B7 removed the per-folder Grid store on purpose (r1 P2-1: nothing could undo a stored choice). Upstream keeps a per-collection layout on the collection itself (synced). | D17: a per-collection override (Default / Rows / Grid) in the folder's hold menu or Edit band, stored on the collection, Default = the Settings value. S–M. |
| 7 | Best Result "perfect as it is" | FEAT-72 | **CONFIRMED** | B8 | Close. |
| 8 | Collections open on the first film's art + synopsis | FEAT-70 | **CONFIRMED** | B9 | Close. |
| 9 | SenPlayer: not installed, Infuse Pro only | FEAT-56 | **No tester** | Christian's box does not have it either (Batch D device pass). | Park the hand-off test until someone with SenPlayer reports. |
| 10 | Green picture gone on HDR / DV since the option was removed | BUG-166 | **CONFIRMED** | B10 forces gpu-next for a DV P5 on mpv (the Enhanced Video Renderer is no longer the gate for that case) | Close the quick half; the native P5-MP4 path stays in P5. |
| 11 | **Thumbnails: none on mpv for Animals; a transparent box on native for Spirited Away** | BUG-168 | **mpv half OPEN (repro scheduled); native half = known platform limit** | mpv: the Animals repro (DV P5, gpu-next since B10) is already on the separate BUG-165/168 card. Native: P3's spike found AVKit's paused-scrub preview on tvOS 27 never requests an I-frame (blank boxes in all four runs, `docs/player-revamp-plan-2026-10-06.md` P3 run 4); only FF/RW scan steps pictures. His 02:07Z "pictures, then stopped after a scrub" and today's "transparent box" are that limit. | Native: do not draw an empty preview frame (time card only) when the engine is AVPlayer, so it reads as "no previews" instead of broken; state the limit in the reply. mpv: wait for the repro. |
| 12 | **HDR switches ~10 s after the film starts; wants it before the first frame** | BUG-170 | **OPEN, candidate cause on mpv** | mpv: `applyDisplayCriteriaIfEnabled()` runs at file-loaded and reads `video-params/primaries` + `gamma`, which mpv only fills once the first frame is decoded; at that point they are usually empty, so the criteria ask for the frame rate only and the HDR mode arrives later. Playback is not held while tvOS switches either. Native: `AVPlayerViewController` applies the criteria itself once the item is ready; it does not hold the first frame either. | Build the criteria from what is known before play (the picker's tags / the native probe's format: DV, HDR10, HLG; `video-dec-params` or the track list on mpv), apply them before `loadfile` / before `play()`, and hold playback (mpv `pause=yes`, AVPlayer `rate 0`) until `AVDisplayManager.isDisplayModeSwitchInProgress` goes false. Needs his engine for the 10 s case (he did not say). M, P5. |
| 13 | Loading screen: likes it; asks for the Nuvio / Stremio pulsing title (grows, shrinks, grows) | **FEAT-77** (new) | Product call | P4's loading overlay (stage text + bar). The official apps scale the title logo in the centre in a slow loop. | D18: an option or the default for the loading overlay: centred title logo with a 1.0 ↔ 1.08 scale loop (~1.6 s), stage text under it. S. His video is not needed; the official app is the reference. |
| 14 | "Links failing because of network issues": never reported it | BUG-143 | **Not his report** | rc5's notes / reply 3 listed BUG-143 (P4's network-aware rejected-link memory) among the player changes; it came from a device session on 10-04, not from him. | Say so in the reply: a general fix, nothing to check. |
| 15 | **Watched checkmark: thought it was added; marking a film watched shows no tick** | FEAT-64 | **Not shipped; wanted** | The badge exists in `PosterCard.watchBadge` for Library only (L1); Home rows never draw it. The 10-14 master plan put it in Batch B (old B10 → B14); it was not in B1–B10. | Batch B second half, first group (§ master plan 4.4). Badge on Home + folder rows, CW excluded; hide toggle D4 later. S–M. |
| 16 | White outline around posters (Card Depth ON, No Zoom OFF) is gone | BUG-158 (rc4 note "outlines with Zoom ON") | **CONFIRMED gone**, cause unverified | Nothing in rc5 targeted it. The likeliest change is Batch B's `CardSystemLiftStyle` rule (B3/B4: the system lift instead of the tile's manual lift in more cases), which removes the second edge the manual lift drew. | Close as positive; no work. |

### Not in this verdict

BUG-165 (exit eject, his short tap on Animals) and BUG-167 (start time) are not mentioned; both stay on the
separate repro card. BUG-160 (cold launch on Streaming Services), BUG-155 (search speed), Discover (FEAT-73),
BUG-163 (landscape trailer picture, implicitly fine: he describes the trailer enlarging) are not mentioned.

## What rc5 did for each of his rc4 asks

- **B1, B3, B7, B8, B9, B10** land as he asked (rows 1a, 5, 6, 7, 8, 10).
- **B6 (BUG-146)** shipped and is too small to see: 4 pt.
- **B4 (BUG-162)** fixed "too small" by going to the trailer tile's size; he wants the folder-tile size at
  rest and the big size only while the trailer plays.
- **B5 (BUG-156)** lands on the right card now, after a visible detour; the next step holds the detour.
- **B1** gated the folder's synopsis line but not the collection title in the stage meta line, which
  photo 3 shows as the second copy of the row heading.

## Suggested order (feeds the master plan's Batch B second half)

1. BUG-162 rest size (D16) + BUG-146 (a) heading → art 12 pt, verified on the rig in his config.
2. BUG-173 title once on Home (S).
3. BUG-156 hold the engine's first move (M, rig repro first).
4. FEAT-64 watched tick on Home + folder rows.
5. BUG-168 native: no empty preview frame (S); mpv after the repro card.
6. Then the old B11–B14 (Stage speed A/B, FEAT-73 Discover, search fan-out, wash / localized copy).
7. BUG-170 HDR-before-first-frame and FEAT-77 loading animation go to P5 with BUG-167; FEAT-76 per-collection
   layout after D17.

## Reply DM

Draft: `docs/comms-dm-drafts-2026-10-17-rc5-reply.md` (SlopMonster 5/5); SENT 2026-10-17 06:08:08Z on Christian's go.
