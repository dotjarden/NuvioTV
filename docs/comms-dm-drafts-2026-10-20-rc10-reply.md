# DM draft: reply to Steven's beta.19-rc10 verdict (2026-10-20). NOT SENT

Answers `docs/steven-beta19-rc10-verdict-2026-10-20.md`. Send only on Christian's go, through the ego-browser recipe (memory `reddit-chat-smash-fetch`), after a pre-send `fetch-dms.sh --since 2026-10-20T17:40:28.256Z`. move the watermark after. SlopMonster lint on the body below the line. Codex cleanse skipped (quota out until 10-29).

Facts behind it:
- FEAT-80: Christian's call (2026-10-20): his own preference is the rail as it is now (16 pt in, glass around the icons). the flush Nuvio-style rail will be added as a Settings option. Icons Only losing its glass (Batch M D2) is still open.
- BUG-153 and UX-16: nothing in rc10 was measured on his hardware. the next batch starts with a profile in his configuration, so the DM asks for a short video and his Appearance settings, and offers the accent-ring A/B to split BUG-153 from the rest.
- FEAT-82, FEAT-61 (Medium+ lines), BUG-193 (synopsis blur), BUG-194 (two-step return) are small and go in the next batch. promised as "next build" only for those four. BUG-190 needs his photo first. FEAT-66 (logo on the right) is noted, not promised.
- mpv DV / Atmos: mpv has no Dolby Vision output and decodes audio to PCM. the P5 branch (`claude/player-p5`, not merged) routes DV profile 5 MP4s to the Apple TV player with real DV and E-AC-3 passthrough. Promised softly ("should"), with the Animals ask.
- Not promised: UX-16 numbers, a date.

---

Hi Steven, thanks for the rc10 report and the photos, all read.

Smoothness first, since that matters most. Nothing in rc10 was measured on a TV set up like yours, and I don't want to guess. Could you film a short clip of a walk through the Stage Home and the side menu, and send a photo of your Appearance settings? That gives me something to profile against. The next build starts with that work.

The ring on trailers, episodes and seasons: one quick test would help me. Turn off the accent focus ring in Appearance, open the same big Detail page, and tell me whether the lag goes with it. If it does, I know where to cut.

The side menu: my own preference is how it looks now, with the glass around the icons rather than a box in the corner. I hear you on the flush style, so I'll build it the way Nuvio does it and make it an option in Settings. The missing transparency in the icons-only mode is on the list too.

In the next build: the square buttons on the Detail page all get the same width. Four lines of synopsis in Classic at Medium+, which I'll measure with your size. The blur behind the full synopsis gets a proper backdrop and a calmer animation. And back from an actor lands on the card in one move, no detour.

Two questions. Which screen was the "logo in the centre" photo? It didn't arrive with the others. And for the logo on the right: noted, with your note about the Classic collections.

Good to hear the card flicker is much rarer. I'm still chasing the rest of it.

On the MPV player: it has no Dolby Vision output, so it converts DV to HDR, and it decodes the sound itself, which drops Atmos. I have a fix on the way: DV films in MP4 files, like Animals, should play on the Apple TV player in the next build, with real Dolby Vision and the sound passed straight to your receiver. When it lands, try Animals there and tell me whether Atmos lights up.
