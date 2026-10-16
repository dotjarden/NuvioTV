# DM draft — reply 2 to Steven's rc4 follow-ups (2026-10-16)

**Status: SENT 2026-10-16 23:55:39Z** as one bubble on Christian's go (ego-browser space 23, `textarea[name="message"]` fill + "Send message" click, verified by the walker: last bubble `youngchris2989 said 1 minute ago`, 3,614 chars incl. the label, ends on the sign-off; `fetch-dms.sh` shows the event at 23:55:39.748Z). Lint 5/5 on the body; Codex cleanse skipped (login expired). Was: DRAFT, NOT SENT. Answers his 22:02Z and 22:09Z messages (DV fixed by the renderer, Harvest Only vs Harvest + Decode, the eject is mpv, choppy info overlay → BUG-169, Atmos, Profile 7 FEL, the rail mode in his video, the roadmap question, the lingering loading animation → BUG-170). One bubble. Send through the ego-browser recipe in memory `reddit-chat-smash-fetch` on Christian's go.

Facts behind the answers: `docs/player-revamp-plan-2026-10-06.md` (harvest = frames saved every 10 s of what has played; decode = the FFmpeg keyframe thumbnailer on scrub; native scrub previews never request an I-frame on tvOS 27, P3 spike), `docs/research/player-revamp-research-2026-10-06.md` (audio: AC3/EAC3 pass through the native remux, TrueHD/DTS become AAC 5.1, mpv has no passthrough), `PlayerSettingsPane.swift` (Keep Profile 7 FEL on mpv), `NavigationChrome.swift` (Hide While Browsing shows the rail at rest on Home row 0; Hidden never does), BUG-165 device repro (Batch B, B2: seven short Menu presses exit to the source list; the only eject was a Menu held 0.8 s, tvOS's own press-and-hold Back to Home), master plan §4.5 (Batch C: FEAT-60 header logo, scrim, synopsis) and FEAT-68 (the Wako fixed-slot row, Home rework).

---

Hi Steven,

Good news on the picture. The renderer switch is the fix for those profile 5 files, so that one is settled.

Thumbnails: "Harvest Only" saves a frame every ten seconds of what has already played, so when you scrub into a part you have not watched there is nothing to show, or only the nearest older frame. "Harvest + Decode" also decodes frames ahead while you scrub, so that is the one to try. Two limits you will still hit. On the native player (your profile 8 files) there are no scrub thumbnails at all; the hold-to-scan shows real pictures instead, and the paused preview stays blank, which is Apple's player, not something I can change. On mpv the frames come ten seconds apart and arrive late, which is on the list to tighten. The colour follows the picture, so with the renderer on they should no longer be green.

The exit to the home screen: thanks, mpv is what I needed. I spent today on it with the box here. Seven short Menu presses out of mpv, including a very quick tap and a double tap, all came back to the source list. The one way I could reproduce the home screen was holding Menu for close to a second, which is the Apple TV's own press-and-hold to go Home, and no app can intercept that. So one question: when it happens, is that a short tap or a longer press? Either way the next build changes how the exit handles Menu, so tell me if it still happens after it.

The choppy interface with the information overlay up: logged, I will measure it on the box.

Dolby Atmos: on the native player, Atmos carried in Dolby Digital Plus goes through to your receiver untouched. Atmos carried in TrueHD does not, because the Apple TV cannot play TrueHD, so those tracks are converted to 5.1. The mpv player decodes everything itself and sends no bitstream through. In short: Dolby Digital Plus Atmos yes on native, TrueHD Atmos no on either.

"Keep Profile 7 FEL on mpv": leave it off. It only concerns profile 7 FEL files, the dual-layer disc remuxes. Off, the native player plays them as profile 8 and drops the enhancement layer. On, they go to mpv as plain HDR10. Turn it on only if a profile 7 file looks wrong on native.

The sidebar in your video: "Hide During Navigation" is meant to show the sidebar when you land on the first row and hide it once you move down, so that row is its resting state. "Hidden" is the mode that never shows it at rest, and you said that one works for you, so I am not changing the other.

The roadmap: nothing you were told about is dropped, the order moved because your list from this build went first. After this fix build comes the description page work, the header logo that stays as you scroll, the darker band behind the synopsis, and the full-synopsis control. The Netflix-style row from the Wako video is still on the Home rework list after that, as is the collection title position. I will say when each has a build rather than a date.

The loading animation staying up after the film has started, then the black, then the switch to HDR: the black is the TV changing its display mode, which the Apple TV does when the video starts, so I cannot remove it. The animation staying on screen after the first picture is mine, and I have logged it with the start-time item. Switching the mode before the video starts is possible on the native path, where the app already knows the format; on mpv it only knows once the file opens.

Thanks for going through all of it.
