# GitHub issue #6 reply (drafted 2026-10-24): BUG-172, ask the reporter to try beta.19. POSTED

Second reply on youngchris29-art/NuvioTV #6 "Streaming jittering-stuttering" (megustalamangusta666-pixel). He has not answered the 2026-10-20 questions. The plan row (`docs/open-items-plan-2026-10-21.md` §6) closes #6 "after a rig measure on a 23.976 MP4, then a comment asking him to try the public build". The measure is the 2026-10-21 BUG-199 run 3 on the box (`docs/research/wave3-device-pass-2026-10-21/README.md`): the Comet NF DV 23.976 fps MP4 played 165 segments natively with no `Packet duration` lines, so the fragment-start timestamp defect (the BUG-172 lead, `docs/wave3-critique-2026-10-21.md`) is gone on beta.19's remux. The stutter itself was never reproduced here; the comment says so.

**Status: POSTED 2026-10-24 on Christian's go as https://github.com/youngchris29-art/NuvioTV/issues/6#issuecomment-6378617777** (`gh issue comment`). Was: NOT SENT.

```
beta 19 is out: https://github.com/youngchris29-art/NuvioTV/releases/latest

It changes how the native player cuts a film into pieces for the Apple TV decoder. On the old build the first frame of each piece carried a wrong timestamp. I measured that on our Apple TV with a 23.976 fps file, and the pieces are 6 to 16 seconds long, which matches the rhythm you describe. I never saw the freeze itself here, so I can't promise this is your stutter, but it is the one defect on that rhythm I could find.

Please try beta 19 with the native player. If it still freezes, the five questions above are what I need, plus roughly how many seconds apart the freezes land.
```
