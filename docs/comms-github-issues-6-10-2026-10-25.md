# GitHub replies owed on #6 and #10 (drafted 2026-10-25 evening sweep) — NOT SENT

Two drafts, one per issue. Nothing posted; each goes out only on Christian's go, through the copy rule (SlopMonster lint to 5/5 first). Facts come from the issue threads and tracker rows BUG-172, BUG-213, BUG-215.

## #6 "Streaming jittering-stuttering" — acknowledge and close (BUG-172)

Reporter megustalamangusta666-pixel confirmed on 2026-10-24 10:37Z that beta.19 fixed it (Dolby Vision file, very large, through TorBox). Post, then close the issue as completed.

```
Glad it's fixed. Thanks for trying beta 19 and for naming the file: a large Dolby Vision file through TorBox is exactly the case the new fragment timestamps were meant for, so I'm closing this as fixed. If it comes back on another file, open a new issue with the build number and the title and I'll pick it up from there.
```

## #10 "tvOS Settings: focus bugs, OLED on Add-ons, clipped focused rows…" — BUG-213 confirmed, BUG-215 reopened (erdist)

erdist retested beta.19 on 2026-10-23 08:35Z: item 1 (API key fields) works; item 3 (clipped focused row) still clips on the Settings page in Default style, simulator only, with a screenshot. BUG-215 is fixed and merged on the tip (`769e2c55e`) but not in a build yet. Do not promise a build number or date. Post only after Christian confirms the screenshot was read and the sim check passed.

```
Thanks for the retest, and for the screenshot with the page and the style named. That was the piece I was missing.

1. API key fields: good to hear they work, so I'm counting that one as done.

3. Clipped row: you were right. The Settings page in Default style cut the focused row's raised edge at the left side of the list. I fixed it and it's in the code now, but it isn't in a public build yet. I'll say here when it is, and I'd like you to check it in the same simulator spot. It only showed up on the simulator, never on my Apple TV, so your check is the one that counts.

Items 2 and 4 shipped in beta 19; if anything about the language pickers or the fallback rows feels off, add it here.
```

## Not drafted

- **Steven's standing DM answers** (mpv at once or later, the short-Back check, whether the local.properties note fixed his build): the cloud sweep can't read Reddit DMs, so I have not seen his exact questions. Draft in an interactive session that has the chat open.
- **#5 reply 2 and #11 first reply** are listed as owed in older sweep lines, but both were already posted (#5 on 2026-10-22 21:45Z, #11 on 2026-10-24 ~00:55Z). The sweep text is stale there; #5 now waits on the reporter and #11 on a cut.
