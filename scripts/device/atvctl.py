#!/usr/bin/env python3
"""Sequence runner for the NuvioTV device rig: several inputs over ONE Companion connection.

    atvctl.py <step> [<step> …]        steps, each a word or word=args:
      up down left right select menu home play_pause     press (PRESS_MS long, default 100)
      hold=<button>,<seconds>           press-and-hold (FF/RW scan, hold menus, hold-to-manage)
      swipe=x0,y0,x1,y1[,ms]            Siri Remote swipe on the 0..1000 touch surface
      click[=0|1|2]                     touch click: single / double / hold
      text=<string>                     type into the focused text field
      sleep=<seconds>                   pause between steps
      waitlog=<pattern>|<log>|<timeout>[|<settle>]   wait for a console line, then run the next step at once
      app                               print the foreground app
      wake | sleep_tv

Env: NUVIOTV_DEVICE_CONF (default ~/.config/nuviotv-device) holds atv.env + atv-credentials.
Exits 0 when every step ran; the per-step log goes to stdout (STEP … / DONE …).
"""
import asyncio
import os
import sys
import time
from ipaddress import IPv4Address

import pyatv
from pyatv.conf import AppleTV, ManualService
from pyatv.const import InputAction, Protocol
from pyatv.protocols.companion.api import HidCommand

PRESS_MS = float(os.environ.get("PRESS_MS", "100"))

BUTTONS = {
    "up": HidCommand.Up, "down": HidCommand.Down, "left": HidCommand.Left, "right": HidCommand.Right,
    "select": HidCommand.Select, "menu": HidCommand.Menu, "home": HidCommand.Home,
    "play_pause": HidCommand.PlayPause, "volume_up": HidCommand.VolumeUp, "volume_down": HidCommand.VolumeDown,
}


def load_env():
    conf = os.environ.get("NUVIOTV_DEVICE_CONF", os.path.expanduser("~/.config/nuviotv-device"))
    env = {}
    with open(os.path.join(conf, "atv.env")) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k] = os.path.expandvars(v.strip().strip('"'))
    with open(env["ATV_CREDENTIALS_FILE"]) as f:
        env["creds"] = f.read().strip()
    env["port"] = int(os.environ.get("ATV_PORT_OVERRIDE", env["ATV_COMPANION_PORT"]))
    return env


async def run(steps):
    env = load_env()
    conf = AppleTV(IPv4Address(env["ATV_ADDRESS"]), env["ATV_NAME"])
    svc = ManualService(env["ATV_ID"], Protocol.Companion, env["port"], {})
    svc.credentials = env["creds"]
    conf.add_service(svc)
    loop = asyncio.get_running_loop()
    atv = await pyatv.connect(conf, loop, protocol=Protocol.Companion)
    api = atv.remote_control.main_instance.api  # CompanionRemoteControl behind the facade relayer
    t0 = time.monotonic()
    try:
        for step in steps:
            name, _, arg = step.partition("=")
            at = f"+{time.monotonic() - t0:6.2f}s"
            print(f"STEP {at} {step}", flush=True)
            if name in BUTTONS:
                # A human press lasts ~100 ms. pyatv's own press sends down+up back to back (0 ms),
                # and a 0 ms Menu that exits the mpv player ejected the app to the tvOS home screen
                # (2026-10-15); timed presses never did. PRESS_MS overrides the default.
                await api.hid_command(True, BUTTONS[name]); await asyncio.sleep(PRESS_MS / 1000); await api.hid_command(False, BUTTONS[name])
            elif name == "hold":
                btn, secs = arg.split(","); secs = float(secs)
                # Always release: a connection error mid-hold once left Right held on the TV (the
                # native FF scan ran on for 20 s and the next Menus were swallowed). If the release
                # itself fails, the caller must send a plain press of the same button.
                await api.hid_command(True, BUTTONS[btn])
                try:
                    await asyncio.sleep(secs)
                finally:
                    try:
                        await api.hid_command(False, BUTTONS[btn])
                    except Exception as exc:  # noqa: BLE001
                        print(f"RELEASE_FAILED {btn}: {exc} — send `atv.sh press {btn}` to release", file=sys.stderr)
                        raise
            elif name == "swipe":
                p = [int(x) for x in arg.split(",")]
                ms = p[4] if len(p) > 4 else 200
                await atv.touch.swipe(p[0], p[1], p[2], p[3], ms)
            elif name == "click":
                await atv.touch.click(InputAction(int(arg or 0)))
            elif name == "text":
                await atv.keyboard.text_set(arg)
            elif name == "sleep":
                await asyncio.sleep(float(arg))
            elif name == "waitlog":
                # waitlog=<pattern>|<log path>|<timeout s>[|<settle s>]: block until the console log
                # grows a line containing <pattern> (literal), then wait <settle> (default 1.5) and go
                # on with the NEXT step over the SAME connection. The up-next card's ~8 s window was
                # lost twice to a per-call connect (3.7 s) plus a dropped press; one held session won.
                pat, path, tmo, *rest = arg.split("|"); settle = float(rest[0]) if rest else 1.5
                start = os.path.getsize(path); deadline = time.time() + float(tmo); hit = False
                while time.time() < deadline:
                    with open(path, "rb") as f:
                        f.seek(start); chunk = f.read().decode("utf-8", "replace")
                    if pat in chunk:
                        hit = True; break
                    await asyncio.sleep(0.3)
                print(f"WAITLOG {'hit' if hit else 'TIMEOUT'} {pat!r} at +{time.monotonic() - t0:6.2f}s", flush=True)
                if not hit:
                    return 3
                await asyncio.sleep(settle)
            elif name == "app":
                try:
                    print(f"APP {atv.metadata.app}", flush=True)
                except Exception as exc:  # Companion alone has no now-playing metadata
                    print(f"APP unavailable ({type(exc).__name__})", flush=True)
            elif name == "wake":
                await atv.power.turn_on()
            elif name == "sleep_tv":
                await atv.power.turn_off()
            else:
                print(f"UNKNOWN step {step}", file=sys.stderr); return 64
        print(f"DONE +{time.monotonic() - t0:6.2f}s {len(steps)} steps", flush=True)
        return 0
    finally:
        atv.close()
        await asyncio.sleep(0.2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(64)
    sys.exit(asyncio.run(run(sys.argv[1:])))
