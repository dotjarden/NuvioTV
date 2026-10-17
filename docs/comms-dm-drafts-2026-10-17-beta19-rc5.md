# DM draft — beta.19-rc5 (build 137) to Steven, 2026-10-17

**Status: SENT 2026-10-17 01:46:15Z + 01:46:23Z** as two bubbles on Christian's go (ego-browser space 24, verified by the walker: 295 and 2,545 chars incl. labels, both ending on their last line; `fetch-dms.sh` shows both events). Was: DRAFT, NOT SENT. Two bubbles: the first paragraph through the link line, then the rest. Link filled from the cut log (build 137 `eeca35353`, tag `tvos-v0.3.0-beta.19-rc5`, IPA 29,456,031 B, filebin until 2026-10-24, gofile backup https://gofile.io/d/wQSdLkVv). Lint 5/5 on the body; Codex cleanse skipped (login expired). Send through the ego-browser recipe in memory `reddit-chat-smash-fetch` on Christian's go.

Carries over rc4 (build 136): Batch B B1–B10 (`docs/batch-b-plan-2026-10-16.md`, his rc4 list), player P4 (`docs/player-revamp-plan-2026-10-06.md`), Batch D (`docs/batch-d-plan-2026-10-15.md`). Every "next build" promise from the two 10-16 replies is in and walked on the box (B4 + B10 in round 2, `b0b1312`). New settings and defaults: Appearance › Show Catalog Details in Headings OFF; Home Screen › Collections Layout, Rows; Playback › Loading Screen ON (was the plain spinner); Developer › Harvest Screenshot Path, Software for SDR. Not in this build: Discover grid, start time, thumbnail cadence, the info-overlay choppiness, the loading screen lingering, the description page work.

---

Hi Steven, the next build is up, same install as before:

https://filebin.net/nuviotv-beta19-rc5-a9f1c493/NuvioTV-beta19-rc5.ipa

Your list from rc4, in your order:

- Headings: the add-on name and the source count are gone from both Homes. If you ever want them back, Appearance › "Show Catalog Details in Headings", off by default.
- New Home headings: one step lower.
- Coming back from a film inside a collection lands on the film you left. Coming back to Home from a collection has the wider fix; if it still jumps on your box, tell me and I will ask for one screenshot.
- Wide posters from your add-on: the cards now take their size from your Poster Size setting, the heading sits right above them, and the trailer shows its picture on those cards. I tested it with a stand-in add-on, so a photo of your real row would still help.
- The far-left poster with "No Zoom on Focus" on: no longer cut.
- The grid/rows switch is out of the collection page and in Settings › Home Screen › Collections Layout.
- Best Result is down to the title with its year and type; the source and the rating are gone.
- Collections open on their first film's art and synopsis.
- Profile 5 files that play on mpv now pick the right renderer on their own, so the green picture does not come back even with the renderer switch off.
- Leaving mpv: the app side of the exit is now instant, and Menu is handled differently. Still curious whether yours was a short tap or a hold.

Also in this build, since you are trying the player:

- The native player (your profile 8 files) gets what mpv already had: a Playback tab with episodes and sources, a speed pill, subtitles in the app's style, the pause card, chapters from MKV files, and add-on subtitles that arrive after the start are now selectable without restarting.
- A loading screen with the poster and what the app is doing replaces the plain spinner on both players. Playback › Loading Screen, on by default, turn it off if you prefer the spinner. I know it stays up too long on your box after the picture starts; that part is logged, not fixed yet.
- A link that fails because of your network is no longer remembered as a bad link.
- Continue Watching puts a show back when you mark an episode watched, and TorBox cloud lists longer than one page load fully.
- SenPlayer is in the external player list. I could not test the hand-off, so if you have it installed, tell me what it does with the position and subtitles.

Not in this build: the Discover grid, the start time, the thumbnail timing, the choppy overlay, and the description page work. Those are the next batch.

Thanks, and tell me what you see.
