# DM draft: reply to Steven's rc7 verdict (2026-10-18)

**Status: DRAFT, NOT SENT.** SlopMonster lint 5/5 (408 words); Codex cleanse skipped (quota until 10-29). Written against the recommended scope in `docs/batch-g-steven-rc7-plan-2026-10-18.md` (D1–D5). If Christian picks a different option, the lines on Back from a player, the loading text and the sidebar change. Nothing promised for collections on Classic (FEAT-79, next batch).

Facts behind it:
- Already merged after rc7, not cut: wide-poster trailers play inside the normal focus size (`457a38d34`).
- External players: only the stream's own subtitles are passed today; no language preference reaches any player; audio language has no parameter in Infuse/SenPlayer/Native Player.
- BUG-180 likely cause: blurred glass panels over the video; BUG-181: Dolby Vision thumbnails come only from frames already played.
- BUG-178: no app layer scrolls with the page, so his video helps.

---

Thanks Steven, that's a great report, and it's nice to hear the app feels a bit like yours too. It is, a lot of what's in it came from your lists.

Already done for the next build:
- Wide posters now play the trailer inside the normal Apple TV focus size, no enlargement.

Working on for the next build:
- Back from a player (built-in or external) goes back to the page you started from, not the stream list.
- With automatic selection, Play goes straight to the loading screen, no stream list in between.
- The loading logo will keep pulsing through every step, and the text under it goes away. For series I'd keep the episode line, unless you'd rather see only the title there too.
- The choppy film behind the menus: the menus use a blur effect that the Apple TV redraws on every video frame. I'm swapping it for a plain dark background in the player and will measure the difference on a Dolby Vision film.
- Thumbnails on Animals: for Dolby Vision files, thumbnails only come from parts you've already played. Instead of an empty box, I'll show the nearest one I have.
- Focus ring and depth on trailers, episodes and season posters on the details page.
- The actor biography: clicking it will open the full text, like the synopsis.
- Continue Watching on Classic: the focused card will sit on top of its neighbour, like in your collections.
- Back from a collection on the new Home in one move.
- Sidebar: an option to place it at the top left, and one to show icons only.

The shadow that moves up on the details page: yes, please send the video. I can't find anything in the app that should move like that, so seeing it will help.

Collections with the Classic look when Classic is selected: good idea, but it's a bigger change, so it'll come in the build after.

Atmos is still on my list.

Your question about external players: right now the app's subtitle and language settings don't carry over. Only the subtitles that come with the stream itself are sent. In the next build I'll also send the subtitles from your subtitle add-ons, with your preferred language first. The audio language can't be passed: Infuse, SenPlayer and Native Player don't offer a way to set it from another app, so their own settings decide that.
