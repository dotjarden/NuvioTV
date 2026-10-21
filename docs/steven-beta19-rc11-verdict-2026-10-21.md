# Steven's beta.19-rc11 verdict (2026-10-21 14:57Z–16:52Z) — triage

Read with `scripts/reddit/fetch-dms.sh --since 2026-10-21T07:48:19.967Z`: eight messages (one photo, one Smash video). Photo `docs/research/steven-rc11-verdict-2026-10-21/photo-1-9ixlxr7gmuwh1.jpeg` (Search "Avatar": the query chip, an empty results area, a People row only). Video `fromsmash.com/woa4RkMhOi-ct` (his Classic-Home + Cinematic-Detail setup for smoothness, and "titles positioned too high, dropping one notch each time on the standard home screen"). DM watermark stays `2026-10-21T07:48:19.967Z` until the reply is sent; the newest event read is 16:52:33.749Z.

## What he says, item by item

| Item | His words (condensed) | Verdict | Tracker |
|---|---|---|---|
| FEAT-80 Edge | "it works and I prefer it this way! Approved for Edge in Centre position." | ✅ Centre | FEAT-80 → Edge confirmed in Centre |
| FEAT-80 Corner | "the rail should sit flush against the top **and** the left edges, and the animation should expand downward rather than sideways" | 🔺 Corner still wrong, **now a precise spec** (public beta plan S1) | FEAT-80 Corner → S1 |
| BUG-196 Icons Only glass | "much lighter now, but personally I prefer it darker" | 🟡 fixed as asked, taste says darker | BUG-196 → confirmed; tint level = Christian's call |
| FEAT-82 square buttons | "The icons are still not all the same size." Later: "you could remove the square buttons from the description, they don't look as good as the rounded ones." | 🔺 NOT FIXED on his box, and he now wants Square gone | FEAT-82 reopened; D: drop the square style? (Christian) |
| Watched icon colour | "when the Watched icon is focused and you move to another one, it takes longer to return to its original colour, whereas the other icons switch back instantly (both corner styles)" | 🆕 new | **BUG-205** P4 |
| FEAT-61 four lines | "5 lines at Medium+ works (I never get 4)"; "I do indeed have 4 lines in Classic mode" | ✅ (five with his font, four in Classic) | FEAT-61 → confirmed |
| BUG-193 synopsis screen | "works. We'll see if you keep it once the description page is reworked" | ✅ | BUG-193 → confirmed |
| Detail choppier | "The description page has become choppier again … it was smooth in every situation when I told you so" + "Classic Detail runs smoothly, unlike the cinematic version" | 🔺 REGRESSION, Cinematic only | **BUG-206** P2 |
| BUG-194 actor Back | "Going back from an actor still takes two moves" | 🔺 NOT FIXED on his box (rig saw one move with the rungs) | BUG-194 reopened; his config differs: find what |
| BUG-195 Search black | "it opens directly and it's better, but only from the second time onward. After relaunching the app, the 'Search for a movie or show' text stays on screen for about a second before the keyboard appears over it." | 🟡 PARTIAL: the placeholder is what he sees for a second on a cold start (by design, the field mounts at +1.1 s); he reads it as a delay | BUG-195 → partial; cold-start keyboard mount is UIKit's; option: hide the prompt text, keep only the magnifier? (Christian) |
| UX-16 Home | "smoother, I can definitely feel it, even if it's not fully optimised yet"; later "I switched the home screen back to classic … it feels smoother now. It's as if the new home screen was making the whole app slower" | 🟡 PARTIAL, matches the rig (Stage floor ~3.5 hitches/press; Card Depth next) | UX-16 → partial; S2 |
| First Down abrupt | "the first animation (the first tap at the bottom) is too abrupt, it should be made less abrupt, like taps 2, 3" | 🔺 still (his rc10 reply said the same of Detail; now Home) | BUG-153 → Home first-press easing |
| Stream picker | "Stream selection page: scrolling isn't smooth" | 🆕 new | **BUG-207** P3 |
| Search empty results | "sometimes the search doesn't return any results, and I have to run it again" + photo (Avatar: People row only, no titles) | 🆕 new, P2 | **BUG-208** P2 |
| Player DV native | "every HDR movie I open launches in mpv with HDR10. I'm giving up on the native player for now and sticking with an external player" | 🔺 **his files never take the native path** | BUG-166 reopened for HIS files: need one of his stream names; our rig's Animals MP4 took native and then failed over (BUG-199) — he may be seeing BUG-199's handover as "launches in mpv" |
| Dialogue | not tested (Sonos does it) | — | — |
| FEAT-81 / UX-17 | "What I'm looking forward to most: a redesign of the description page in the style of Fusion; a redesign of Home in the style of Wako / Netflix. If you plan to do these, stop optimising what's there." | 💬 the strategic ask | FEAT-81, UX-17 → his priority; Christian's call |
| Classic titles too high | video: "titles are positioned too high and drop down one notch each time on the standard home screen" | 🆕 from the video | **BUG-209** P3 (pending the video read) |

## Reading

1. **The two big positives are structural:** Edge in Centre is approved; Home is felt smoother; Search opens directly after the first visit. Those were the three rc11 bets.
2. **Three "not fixed on his box" items agree with each other:** FEAT-82 (icon sizes), BUG-194 (two moves), BUG-201 (Cinematic Detail choppier). All three live on the Cinematic Detail page, all three were measured on the rig in Test 2 and passed. His config has Icons Only + Square + Open Sans + Cinematic; the rig's device pass used Square but the system font and Labels Shown. **The next rig session must install HIS exact Detail config** (Appearance table in `docs/steven-beta19-rc10-reply-2026-10-20.md` + Open Sans + Cinematic) before touching code.
3. **Native player:** "every HDR movie launches in mpv with HDR10" on rc11. On the rig the same class of file (NF WEB-DL DV MP4) DID take native and failed over to mpv within seconds (BUG-199, fixed in Wave 3). He most likely saw the failover, not a routing miss. Wave 3's fix answers this; the reply should say so and ask him to try one title on rc12.
4. **The strategic ask** (Fusion Detail, Wako/Netflix Home) is Christian's: it decides whether S1/S2 polish continues or the redesign starts. Not promised in the reply.
5. **Search empty results (BUG-203)** is the one new P2: intermittent, with a photo; the BUG-155 cancellation work shipped in rc7 (he confirmed it then), so this is a new symptom: probably a superseded request leaving an empty page when the final keystroke's search is dropped. Needs `[SearchPerf]` lines from his box or a rig repro by typing fast.

## Owed

- Reply DM (SlopMonster 5/5, NOT SENT): thanks; Edge noted; Corner spec understood and in the next wave; the three Detail items will be re-tested in his exact config; the native player likely fell over to mpv mid-play (fixed in the next build); ask for one stream name that "launched in mpv"; the search-empty case: ask whether it happens on the first keystrokes or after a pause; the redesign question is Christian's to answer.
- Tracker rows above; `docs/beta-feedback-items.json`.
- Video read (download in progress): the Classic "titles too high" bug and the smoothness comparison.
