# DM draft — reply 3 to Steven's 00:52Z + 00:59Z messages (2026-10-17)

**Status: DRAFT, NOT SENT.** Answers the two messages that crossed the rc5 DM (sent 01:46Z without a fresh fetch; lesson in memory `reddit-chat-smash-fetch`): Harvest + Decode results, the Atmos point, "all my HDR films open in mpv" + a per-film player choice, the settings list, the short-tap eject on Animals, the trailer overlay question. One bubble. Fetch the room against the watermark (2026-10-17T01:46:23.623Z) right before sending.

Facts: `PlayerEngineRouter.swift` (mpv when the native player is off, the source is not seekable, the container is not MKV/MP4, the video is not HEVC/H.264, DV profile 5 inside an MP4, DV profile 7 two-track / FEL with the toggle / no convertible RPU, or no audio track among AAC/AC3/EAC3/FLAC/ALAC/MP3/TrueHD/DTS; the player's stream info line prints "Native · reason" / "mpv · reason"); no per-source player choice exists (new FEAT row owed); mpv's audio output decodes to PCM, so E-AC-3 JOC Atmos metadata is lost there while the native remux passes E-AC-3 through (research doc, BUG-139 note); P3 I-frame scan on native stops at the preview byte budget (P3-F1/F2); the thumbnail causes on his file are NOT known yet, so the draft promises a repro, not a cause; the trailer overlay came with rc4 (his verdict praised it); BUG-165 reopened on his "short tap, Animals".

---

Hi Steven, our messages crossed: your two from last night arrived while the build note was being written, so it asked you a question you had already answered. Sorry about that, here is the rest.

The settings for testing the player, all in Settings › Player: "Native player (Dolby Vision & HDR)" on, "Enhanced Video Renderer" on, "Match Content Frame Rate" on, "Keep Profile 7 FEL on mpv" off, and in Settings › Developer, "Seek Preview Frames" at Harvest + Decode. Playback › Loading Screen on. With those, the app picks the player per file, and you can read its choice in the player's info panel, where the line starts with "Native" or "mpv" and gives the reason.

Why your HDR films open in mpv: the native player takes MKV and MP4 files with HEVC or H.264 video and at least one audio track it can carry (AAC, AC3, Dolby Digital Plus, FLAC, ALAC, MP3, or TrueHD and DTS, which it converts to AAC). Everything else goes to mpv, and so does one HDR case: Dolby Vision profile 5 inside an MP4, which is what Netflix-style "Dolby Vision TV" releases are, including Animals. Profile 5 in an MKV, profile 8, and plain HDR10 all play on the native player. So if you want to compare the two players on the same film, a profile 8 or an HDR10 source will do it today. A way to choose the player yourself for a given source is a fair ask and I will add one. I will tell you when it has a build.

Atmos: you are right about mpv. It decodes the audio itself, so the Atmos part of a Dolby Digital Plus track does not reach your receiver. The native player sends that track through untouched. That is one more reason to get your films onto the native player.

Thumbnails, said more plainly. On mpv the app builds its own pictures two ways: it takes a snapshot every ten seconds while the film plays, and, with Harvest + Decode on, it also reads ahead in the file and decodes frames while you scrub. "Green" was about your earlier Animals playback: the pictures copy whatever the player is showing, so a wrong-colour picture gave wrong-colour thumbnails, and with the renderer on that goes away. On your test neither way produced a frame, which is not what I expected, so I am reproducing it on the same kind of file before I tell you why. On the native player the pictures you saw while holding come from a small preview track the app serves, and it stops serving new ones once a per-film data limit is reached, which is why they ran out after scrubbing. That limit was set cautiously to protect the stream and is being revisited.

The exit on Animals with a short tap: noted, and different from what I reproduced here, which was a hold. The next thing I do is play a profile 5 file the way you did and tap once. The new build also changes the exit, so if you see it there, tell me and I will keep going.

The trailer overlaying the other posters is intentional. It came in with the previous build.

Thanks for taking the time on the player. That is exactly the testing it needs.
