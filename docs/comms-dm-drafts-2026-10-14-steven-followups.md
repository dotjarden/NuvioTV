# DM draft: reply to Steven's 10-08/09 follow-ups (2026-10-14)

Covers BUG-155/156/157/158, FEAT-64/65, BUG-147 pointer. Talking points: `docs/master-plan-2026-10-14.md` §5. One bubble, same register as `docs/comms-dm-drafts-2026-10-08-rc3-reply.md`. "Next build" = rc4, within the week. SlopMonster: lint 5/5 (338 words). Codex cleanse skipped: plain bullet list, one lint hit (a literal term) fixed by hand. **NOT SENT**: waits for Christian's go. After sending, move the DM watermark.

---

Hey Steven, thanks for the follow-ups and the photos. I read all of them.

Here is where each one stands:

- Search: the slowness is in the search itself. When you type a new letter, the add-on requests from the previous letter keep running, so they pile up. The results screen also redraws on every letter. Both get fixed in the next build. One question: does the cursor lag show up before any result has arrived, or only once results are coming in?
- Position after leaving a collection: confirmed in the code, on both Homes. Neither remembers the row and card you were on. Next build puts you back on both. On "also in the old home page", did you mean Home after leaving a collection, or the collection page after Back from a film?
- Wide-poster catalog drawn as tall posters: the app reads the add-on's poster shape and then never uses it. Next build draws those catalogs as wide cards. Could you send me the add-on's manifest URL so I can test with the real thing?
- White box with No Zoom on Focus: that is the outline the still card draws, and the playing trailer card draws a second one on top of it. Next build shows one outline on the playing card, and in still mode it takes the poster's colour. Which of your two photos is No Zoom on, and which is off?
- Watched badge: I saw the photo of the official app. The check badge on Home rows comes next build. A hide option follows.
- Opening straight into a profile: a "Remember Last Profile" setting, next build. Profiles with a PIN still ask.
- OLED video at 3:00: seen. It is on the list with the sharpness of the collection page.

"Next build" means rc4, within the week. It also carries the new Search & Discover and the new player (thumbnails while you scrub, swipe scrub, chapters), so the message that comes with it will be a long one.
