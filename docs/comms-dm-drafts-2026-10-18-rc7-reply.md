# DM draft: reply to Steven's rc7 verdict + beta.19-rc8 (2026-10-18)

**Status: SENT 2026-10-19 02:59:51.233Z** as one bubble on Christian's go, verified in the room and by `fetch-dms.sh` (one copy); DM watermark `2026-10-19T02:59:51.233Z`. Was: DRAFT, NOT SENT. SlopMonster lint 5/5. Pre-send fetch 02:58Z found his 00:00:38Z note (the loading logo is always English); one line added for it. The rc7 reply and the rc8 announcement folded into one message on Christian's call. Codex cleanse skipped (quota until 10-29).

Facts behind it:
- rc8 = build 140, tag `tvos-v0.3.0-beta.19-rc8` (`09b901c2` on `tvos-shared-extraction`), outer pointer `934c0f2`. IPA 29,652,348 B at https://filebin.net/nuviotv-beta19-rc8-0ec9a1e5/NuvioTV-beta19-rc8.ipa (filebin, until 2026-10-26; gofile backup https://gofile.io/d/arQBG41O).
- Over rc7: Batch G (all rc7 items, device-passed by Christian 10-18 on his remote + the rig), BUG-176 fixed, wide trailers at the resting size (`457a38d34`), BUG-130 + BUG-128 (`843f84738`), Batch C part 2 (darker Detail bottom band, FEAT-60 compact logo; `38bd6b932`), synopsis "more" + glass focus (`ea09c4ea8`).
- External players: only the stream's own subtitles were passed before; rc8 adds add-on subtitles, preferred language first; no audio language parameter exists in Infuse/SenPlayer/Native Player.
- BUG-178: the fix hides tvOS's own top scroll-edge effect on Detail; unconfirmed against his case, so the video is still asked for if it persists.
- New settings: Appearance › Rail Position (Centre default) and Rail Labels (Shown default), shown in Rail mode.
- Not in rc8: FEAT-79 (Classic look in collections), Atmos (FEAT-75).

---

Hi Steven, thanks for the great report, and it's nice to hear the app feels a bit like yours too. It is, a lot of what's in it came from your lists.

rc8 is ready: https://filebin.net/nuviotv-beta19-rc8-0ec9a1e5/NuvioTV-beta19-rc8.ipa (build 140). Everything from your rc7 list is in:
- Back from a player (built-in or external) goes back to the page you started from, not the stream list.
- With automatic selection, Play goes straight to the loading screen, no stream list in between.
- The loading logo keeps pulsing through every step, and the text under it is gone. For series the episode line stays, unless you'd rather see only the title there too.
- The choppy film behind the menus: they used a blur effect that the Apple TV redraws on every video frame. The player now uses a plain dark background, and the film stays smooth behind it.
- Thumbnails on Animals: for Dolby Vision files, thumbnails only come from parts you've already played. Instead of an empty box, the preview shows the nearest one from the last two minutes, or a dark card with the time when there's none that close.
- Focus ring and depth on trailers, episodes and season posters on the details page.
- The actor biography: clicking it opens the full text.
- Continue Watching: the focused card sits on top of its neighbour.
- Going back from a collection on the new Home: the Apple TV was briefly handing focus to a placeholder in the row above, which scrolled the page up before the app pulled it back. Fixed, and a press made right after coming back now counts the first time.
- Sidebar: Settings › Appearance has Rail Position (Centre or Top, Centre by default) and Rail Labels (Shown or Icons Only, Shown by default).
- Wide posters play the trailer inside the normal focus size, no enlargement.
- The shadow moving up on the details page: I removed an Apple TV scroll effect that matches what you described. If you still see it, please send the video.

Also new in rc8:
- The darker area behind the synopsis and at the bottom of the details page you asked for.
- A long synopsis ends with "more", the area lights up when focused, and Select opens the full text.
- Scrolling down the details page shows the title's logo at the top.
- Trailers no longer freeze partway through, and going full screen picks up where the background trailer was.

Collections with the Classic look when Classic is selected: good idea, it's a bigger change, so it'll come in the build after. Atmos is still on my list. I just saw your note about the loading logo always being in English: it uses a logo source that only has the English version, so I'll look at using the one in your language there too.

Your question about external players: the app's subtitle and language settings didn't carry over before; only the subtitles that come with the stream itself were sent. rc8 also sends the subtitles from your subtitle add-ons, with your preferred language first. The audio language can't be passed: Infuse, SenPlayer and Native Player don't offer a way to set it from another app, so their own settings decide that.
