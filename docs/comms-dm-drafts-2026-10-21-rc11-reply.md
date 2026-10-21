# DM draft: reply to Steven's rc11 verdict (2026-10-21) — SENT

**Status: SENT 2026-10-21T18:42:25Z** as one bubble on Christian's go (the pre-send fetch found his three 18:08–18:30Z follow-ups, triaged and folded in first; `~/Library/Logs/NuvioDM/rc11-reply-send.js`, gated on his 18:30Z image being the newest bubble), verified by the script's walk and by `fetch-dms.sh`. **Correction owed in the NEXT DM (Christian's call 2026-10-21):** the "striped Netflix tile" line below is wrong; the stripes are his cover's own GIF animation (BUG-133, told to him in the rc2 reply). One line, no apology beyond that. Was: DRAFT, NOT SENT. Send rule (watermark `2026-10-21T07:48:19.967Z`; his verdict runs 14:57Z–16:52Z, follow-ups 18:08Z–18:30Z). Triage: `docs/steven-beta19-rc11-verdict-2026-10-21.md`.

Facts behind it:
- Edge in Centre approved; Corner's spec (flush top and left, expands downward) is S1 of the public beta plan, promised as "next build" in the rc11 DM already.
- FEAT-82 icon sizes and BUG-194 two moves: both passed on the rig in the system font with Labels Shown; his config is Open Sans + Icons Only + Cinematic. The DM says they will be re-tested in his exact setup, promises nothing else. His "drop the square buttons" is Christian's call; the DM does not answer it.
- BUG-206 Cinematic Detail choppier: a regression since rc7; measured next in his config. The DM acknowledges it without a cause.
- Native player: on the rig his file class did take the native path and either (a) fell over to mpv within seconds (BUG-199, fixed on the next build, device-passed) or (b) was sent to mpv up front when the stream probe hit its 4 s limit (seen once in four opens on a debrid link). The DM asks which he sees: mpv at once, or a switch after a few seconds, and for one stream name.
- Search returning nothing (BUG-208): the DM asks when it happens (while typing, or after a pause) since the photo shows the People row arriving and the title rows not.
- Search's first-open text (BUG-195 partial): that second is the system keyboard mounting on a cold start; the text is the app's own field drawn early so the screen is not black. The DM says so in one line and that the first-open look can be quieter.
- Classic row headings dropping a notch (BUG-209): seen in his video; filed.
- First Down too abrupt (BUG-153): filed for the easing pass.
- The redesigns (FEAT-81 Fusion Detail, UX-17 Wako/Netflix Home) are Christian's strategic call; the DM says they are heard and not when.
- His 18:08Z–18:30Z follow-ups (BUG-210 old hero text, BUG-211 catalog name twice, BUG-212 striped tile): filed, the striped tile named as the first to chase.
- No numbers, no dates, no promises beyond what rc11's DM already made (the corner rail, Card Depth).

SlopMonster: the body below lints 5/5 CLEAN (351 words); cleanse skipped (Codex quota until 10-29).

---

Hi Steven, thanks for the rc11 report, the photo and the video. Everything is filed.

Good to hear Edge works for you in Centre. For Corner I have your spec now: flush against the top and the left, and it opens downward. That is the next build.

Icons in Square and the two moves back from an actor: both passed on my TV, but my test setup runs the system font with labels on, and yours runs Open Sans with icons only. I will re-test both in your exact setup before I touch anything.

The description page getting choppier again is a regression on my side. It was smooth when you said so, and I will measure what changed in your setup.

The player: on my TV a file like yours does start in the Apple TV player and then hands over to mpv a few seconds in, because the remux failed on that file class. That is fixed in the next build. There is a second path: if the stream probe takes more than 4 seconds, the film goes to mpv at once. Could you tell me which one you see, mpv from the first frame, or a switch after a few seconds? And one stream name from your list would help.

Search coming back empty: in your photo the people row arrived and the title rows did not. Does it happen while you are still typing, or after you stop? That decides where I look.

The text you see for a second when Search opens after a relaunch is the field drawn early, so the screen is not black while the system keyboard loads. I can make that first-open look quieter.

In your video I can see the row heading landing high and dropping a notch on Classic; filed, along with the first Down being too abrupt. Your later messages too: the old title's text staying under the Prime Video logo for a moment, the catalog name shown twice under the logo and as the row heading, and the striped Netflix tile in your photo. All three are filed; the striped tile is the one I want to find first.

The two redesigns you describe, Fusion for the description page and Wako or Netflix for Home, are heard. That is a decision about where the app goes next, and I will come back to you on it rather than promise it here.
