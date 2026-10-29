// fetch-dms.mjs — read Christian's Reddit DMs for the beta-feedback sweep.
//
// Runs INSIDE the ego-browser node runtime (`ego-browser nodejs -e …`), driven by
// scripts/reddit/fetch-dms.sh. Do not run it with plain node: it needs the
// logged-in ego lite session for two things —
//   1. the Reddit *chat* access token (localStorage `chat:access-token` on
//      www.reddit.com/chat), which this script reads into memory and sends as a
//      Bearer header to the chat backend's Matrix API (matrix.redditspace.com);
//   2. the session cookies for the legacy inbox (`/message/inbox.json`:
//      private messages, comment replies, username mentions), fetched
//      same-origin from inside the page.
// The token never leaves the process and is never written anywhere.
//
// Why Matrix and not the chat page's DOM: the DOM walker only reads one known
// room and truncates nothing but is shadow-DOM dependent; `/joined_rooms` +
// `/rooms/{id}/messages` lists EVERY room (new testers included), with exact
// timestamps, in one pass. `/rooms/{id}/joined_members` 404s on Reddit's
// backend; `/rooms/{id}/members` works and carries `displayname`.
//
// The wrapper prepends `const CFG = {...};` with:
//   space   numeric ego-browser task-space id (by-name creation hangs
//           intermittently; numeric ids are reliable — see memory)
//   since   ISO timestamp; only events strictly newer are emitted
//   limit   max events fetched per room (pagination stops at `since`)
//   summary true → human-readable digest; false → JSON on stdout
//   log     absolute path of a progress log (ego only flushes stdout at exit)
//
// Exit codes: 0 ok · 3 no chat token / 401 (open reddit.com/chat in ego lite
// and sign in) · 4 ego-browser page/control-plane failure.

const fs = await import("node:fs/promises");
const L = async (m) => { if (CFG.log) { try { await fs.appendFile(CFG.log, new Date().toISOString() + " " + m + "\n"); } catch (e) {} } };
const sinceMs = CFG.since ? Date.parse(CFG.since) : 0;
const out = { fetchedAt: new Date().toISOString(), since: CFG.since || null, me: null, chat: [], inbox: [], errors: [] };

let task, page;
try {
  task = await taskSpace(CFG.space);
  await L("space " + CFG.space + " ok");
  page = await task.newPage();
  await page.goto("https://www.reddit.com/chat/");
  await new Promise((r) => setTimeout(r, 8000));
  await L("chat page loaded " + (await page.evaluate("location.href")));
} catch (e) {
  console.error("ego-browser failure: " + (e && e.message || e));
  process.exit(4);
}

const raw = await page.evaluate("localStorage.getItem(\"chat:access-token\") || \"\"");
if (!raw) {
  console.error("no chat access token in localStorage — open https://www.reddit.com/chat in ego lite and sign in, then rerun");
  await L("no token");
  process.exit(3);
}
let token;
try { token = JSON.parse(raw).token; } catch (e) { token = raw; }
const H = { Authorization: "Bearer " + token };
const base = "https://matrix.redditspace.com/_matrix/client/v3";
const get = async (p) => {
  const r = await fetch(base + p, { headers: H });
  const t = await r.text();
  let j = null; try { j = JSON.parse(t); } catch (e) {}
  return { status: r.status, json: j, text: t.slice(0, 200) };
};

const who = await get("/account/whoami");
if (who.status === 401 || who.status === 403) {
  console.error("chat token rejected (HTTP " + who.status + ") — sign in again at https://www.reddit.com/chat in ego lite");
  await L("token rejected " + who.status);
  process.exit(3);
}
out.me = who.json && who.json.user_id || null;
await L("whoami " + out.me);

const nameCache = {};
const displayName = async (uid) => {
  if (nameCache[uid]) return nameCache[uid];
  const p = await get("/profile/" + encodeURIComponent(uid) + "/displayname");
  nameCache[uid] = (p.json && p.json.displayname) || uid;
  return nameCache[uid];
};

const rooms = (await get("/joined_rooms")).json;
const roomIds = (rooms && rooms.joined_rooms) || [];
await L("rooms " + roomIds.length);

for (const roomId of roomIds) {
  const room = { roomId, with: [], newest: null, messages: [] };
  try {
    const mem = await get("/rooms/" + encodeURIComponent(roomId) + "/members");
    for (const ev of (mem.json && mem.json.chunk) || []) {
      if (ev.state_key && ev.state_key !== out.me) {
        const n = ev.content && ev.content.displayname;
        if (n) nameCache[ev.state_key] = n;
        room.with.push(n || await displayName(ev.state_key));
      }
    }
    let from = null, fetched = 0, stop = false;
    while (!stop && fetched < CFG.limit) {
      const q = "/rooms/" + encodeURIComponent(roomId) + "/messages?dir=b&limit=50" + (from ? "&from=" + encodeURIComponent(from) : "");
      const m = await get(q);
      const chunk = (m.json && m.json.chunk) || [];
      if (!chunk.length) break;
      for (const ev of chunk) {
        fetched++;
        if (ev.type !== "m.room.message") continue;
        if (!room.newest || ev.origin_server_ts > room.newest.ts) room.newest = { ts: ev.origin_server_ts, sender: ev.sender };
        if (ev.origin_server_ts <= sinceMs) { stop = true; continue; }
        const c = ev.content || {};
        const kind = c.msgtype === "m.image" ? "image" : c.msgtype === "m.video" ? "video" : c.msgtype === "m.file" ? "file" : "text";
        room.messages.push({
          ts: new Date(ev.origin_server_ts).toISOString(),
          sender: await displayName(ev.sender),
          isMe: ev.sender === out.me,
          kind,
          body: kind === "text" ? String(c.body || "") : "[" + kind + (c.url ? " " + c.url : "") + (c.body ? " " + c.body : "") + "]",
        });
      }
      from = m.json && m.json.end;
      if (!from) break;
    }
    room.messages.reverse();
    if (room.newest) room.newest = { ts: new Date(room.newest.ts).toISOString(), sender: await displayName(room.newest.sender), isMe: room.newest.sender === out.me };
  } catch (e) {
    out.errors.push("room " + roomId + ": " + (e && e.message || e));
  }
  out.chat.push(room);
  await L("room " + roomId.slice(0, 12) + " with=" + room.with.join(",") + " new=" + room.messages.length);
}

// Legacy inbox: private messages (t4), comment replies and mentions (t1).
try {
  const txt = await page.evaluate("(async () => { const r = await fetch(\"/message/inbox.json?raw_json=1&limit=50\", {credentials: \"include\"}); return r.status + \"\\n\" + (await r.text()); })()");
  const nl = txt.indexOf("\n");
  const status = txt.slice(0, nl);
  if (status !== "200") throw new Error("inbox.json HTTP " + status);
  const j = JSON.parse(txt.slice(nl + 1));
  for (const ch of (j.data && j.data.children) || []) {
    const d = ch.data || {};
    const ts = (d.created_utc || 0) * 1000;
    if (ts <= sinceMs) continue;
    out.inbox.push({
      ts: new Date(ts).toISOString(),
      kind: ch.kind === "t4" ? "pm" : (d.type === "username_mention" ? "mention" : "comment_reply"),
      author: d.author,
      subject: d.subject || d.link_title || null,
      subreddit: d.subreddit || null,
      permalink: d.context ? "https://www.reddit.com" + d.context : (d.id && ch.kind === "t4" ? "https://www.reddit.com/message/messages/" + d.id : null),
      unread: !!d.new,
      body: String(d.body || ""),
    });
  }
  out.inbox.sort((a, b) => a.ts.localeCompare(b.ts));
  await L("inbox new=" + out.inbox.length);
} catch (e) {
  out.errors.push("inbox: " + (e && e.message || e));
}

const newestChat = out.chat.map((r) => r.newest && r.newest.ts).filter(Boolean).sort().pop() || null;
const newestInbox = out.inbox.map((i) => i.ts).sort().pop() || null;
out.newest = [newestChat, newestInbox].filter(Boolean).sort().pop() || null;

if (!CFG.summary) {
  console.log(JSON.stringify(out, null, 2));
} else {
  const lines = [];
  lines.push("Reddit DM check — fetched " + out.fetchedAt + " as " + (nameCache[out.me] || out.me) + (CFG.since ? " — events newer than " + CFG.since : " — full read"));
  const active = out.chat.filter((r) => r.messages.length);
  lines.push("Chat: " + out.chat.length + " rooms, " + active.length + " with new messages, newest event " + (newestChat || "n/a"));
  for (const r of active) {
    lines.push("");
    lines.push("## Chat with " + (r.with.join(", ") || "(unknown)") + "  [" + r.roomId + "]");
    for (const m of r.messages) lines.push("- " + m.ts + "  " + m.sender + (m.isMe ? " (me)" : "") + ": " + m.body.replace(/\s+/g, " ").trim());
  }
  lines.push("");
  lines.push("Inbox (PMs, comment replies, mentions): " + out.inbox.length + " new, newest " + (newestInbox || "n/a"));
  for (const i of out.inbox) lines.push("- " + i.ts + "  " + i.kind + " from u/" + i.author + (i.subreddit ? " in r/" + i.subreddit : "") + (i.subject ? " — " + i.subject : "") + (i.permalink ? " — " + i.permalink : "") + "\n  " + i.body.replace(/\s+/g, " ").trim().slice(0, 400));
  if (out.errors.length) { lines.push(""); lines.push("Errors: " + out.errors.join(" | ")); }
  lines.push("");
  lines.push("Newest event overall (next watermark): " + (out.newest || "n/a"));
  console.log(lines.join("\n"));
}
await L("done");
