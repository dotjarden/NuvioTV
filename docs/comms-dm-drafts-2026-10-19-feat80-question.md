# DM draft: FEAT-80 question to Steven (2026-10-19)

**Status: SENT 2026-10-19 on Christian's go** after a quiet pre-send fetch (21:00:31Z).
- The image went first, at 21:01:41.598Z: a 1600×900 JPEG uploaded through the chat's Matrix media API (`mxc://reddit.com/bzgns2wdnhwh1`) and posted as `m.image`. This is the first image send, and the API route works.
- The text followed at 21:02:45.018Z through the UI recipe; the room walker showed it as the newest bubble.
- `fetch-dms.sh` confirms one copy of each. DM watermark `2026-10-19T21:02:45.018Z`.

Was: DRAFT, NOT SENT. Attach `docs/research/feat80-top-bar-mock-2026-10-19/feat80-top-bar-mock.png` (1920×1080) as an image in the same message. The ego-browser recipe has only sent text so far, so the image upload is untested; if it fails, send the text and post the image by hand.

Why:
- Batch M decision D1 builds FEAT-80 as a horizontal icon strip at the top-left ("Top Bar"), replacing rc8's Top.
- His rc9 verdict says Top "isn't what I had in mind: a bar running along the very top left of the screen".
- One question before building avoids a third miss.

Facts behind it:
- The mock's left half is rc9's Top: the centred rail pinned to the top-left corner.
- The right half is the proposed Top Bar: icons in a row along the top-left, with the name under the focused icon.
- Icons Only keeping the glass is planned either way.

---

Quick question about the sidebar so I build the right thing this time: do you mean a bar like the right side of this picture, with the icons in a row along the top left and the name under the one you're on, or something else?
