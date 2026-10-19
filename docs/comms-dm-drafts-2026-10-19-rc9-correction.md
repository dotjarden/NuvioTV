# DM draft: correction to the beta.19-rc9 DM (2026-10-19)

**Status: DRAFT, NOT SENT.** Send only on Christian's go, through the ego-browser recipe (memory `reddit-chat-smash-fetch`), after a pre-send `fetch-dms.sh` check; if Steven has replied by then, fold this into that reply instead.

Pre-send fetch 2026-10-19T17:19Z: Steven asked about the contradiction himself (16:16:22Z: rc8 said all four were fixed); the text below answers him and says he'll report on rc8 + rc9.

Why: the rc8 DM (SENT 2026-10-19 02:59Z, `docs/comms-dm-drafts-2026-10-18-rc7-reply.md`) told Steven the choppy film behind menus, the Animals thumbnails, the logo pulse restart and the stream-list flash were all fixed. The rc9 DM (SENT 16:05Z, `docs/comms-dm-drafts-2026-10-19-beta19-rc9.md`) ended with "Still on my list from rc7" naming the same four. The rc9 line is wrong: all four shipped in rc8 (Batch G, `docs/batch-g-steven-rc7-plan-2026-10-18.md`) and are in rc9.

Facts behind it:
- BUG-180 choppy film behind menus: G5, overlays on a solid dark surface instead of live glass; Christian checked a DV film behind the open panel on the Living Room TV 10-18.
- BUG-181 Animals thumbnails: G6 + `d6794f810`, nearest stored frame within two minutes, else a dark card with the time; confirmed by Christian.
- BUG-182 logo pulse restart: G3, one pulse clock across every loading step.
- BUG-183 stream list flash with auto-select: G2, the loading screen covers the list from the first frame.
- All four are in rc8 (build 140) and rc9 (build 141).
- Still really open: Atmos on mpv (FEAT-75).

---

You're right, that last paragraph was my mistake. Those four (the choppy film behind the menus, the Animals thumbnails, the logo restarting its pulse, and the stream list flashing with auto-select) were fixed in rc8, so they're in rc9 too. If you still see any of them on rc9, tell me which one. Atmos is the one that's still open. Enjoy the couch!
