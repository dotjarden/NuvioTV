import asyncio, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath("scripts/device/atvctl.py")))
from atvctl import load_env, BUTTONS
import pyatv
from ipaddress import IPv4Address
from pyatv.conf import AppleTV, ManualService
from pyatv.const import Protocol
async def main(log, timeout):
    env = load_env(); conf = AppleTV(IPv4Address(env["ATV_ADDRESS"]), env["ATV_NAME"])
    svc = ManualService(env["ATV_ID"], Protocol.Companion, env["port"], {}); svc.credentials = env["creds"]; conf.add_service(svc)
    atv = await pyatv.connect(conf, asyncio.get_running_loop(), protocol=Protocol.Companion)
    api = atv.remote_control.main_instance.api
    start = os.path.getsize(log); t0 = time.time(); fired = None
    try:
        while time.time() - t0 < timeout:
            with open(log, "rb") as f:
                f.seek(start); chunk = f.read().decode("utf-8", "replace")
            if "[UpNext] search begin" in chunk:
                await asyncio.sleep(1.5)  # let the card draw
                await api.hid_command(True, BUTTONS["menu"]); await asyncio.sleep(0.15); await api.hid_command(False, BUTTONS["menu"])
                fired = time.strftime("%H:%M:%S"); print("MENU fired at", fired, flush=True); break
            await asyncio.sleep(0.3)
        if not fired: print("TIMEOUT no chip", flush=True)
        await asyncio.sleep(0.5)
    finally:
        atv.close(); await asyncio.sleep(0.2)
asyncio.run(main(sys.argv[1], float(sys.argv[2])))
