#!/usr/bin/env python3
"""Pair pyatv's Companion protocol with the Apple TV using a manual config.

The Living Room box advertises _companion-link._tcp without an rpMRtID property,
so `atvremote scan` drops it (no identifier). This builds the config by hand.

Usage: pair.py <address> <port> <id> <pin-file> <credentials-out>
The TV shows a PIN; write it to <pin-file> (one line) and this script finishes
the pairing and writes the credential string to <credentials-out> (mode 600).
"""
import asyncio
import os
import sys
import time
from ipaddress import IPv4Address

from pyatv import pair
from pyatv.conf import AppleTV, ManualService
from pyatv.const import Protocol


async def main(address, port, ident, pin_file, cred_out, wait_s=1200):
    conf = AppleTV(IPv4Address(address), "Living Room")
    conf.add_service(ManualService(ident, Protocol.Companion, int(port), {}))
    loop = asyncio.get_running_loop()
    pairing = await pair(conf, Protocol.Companion, loop, name="NuvioTV device rig")
    await pairing.begin()
    print(f"PAIRING_BEGUN provides_pin={pairing.device_provides_pin} "
          f"waiting_for={pin_file}", flush=True)
    deadline = time.time() + wait_s
    pin = None
    while time.time() < deadline:
        if os.path.exists(pin_file):
            with open(pin_file) as f:
                pin = f.read().strip()
            if pin:
                break
        await asyncio.sleep(1)
    if not pin:
        print("PAIRING_TIMEOUT no PIN file", flush=True)
        await pairing.close()
        return 2
    pairing.pin(int(pin))
    try:
        await pairing.finish()
    except Exception as exc:  # noqa: BLE001
        print(f"PAIRING_FAILED {type(exc).__name__}: {exc}", flush=True)
        await pairing.close()
        return 1
    ok = pairing.has_paired
    if ok:
        creds = pairing.service.credentials
        with open(cred_out, "w") as f:
            f.write(creds + "\n")
        os.chmod(cred_out, 0o600)
        print(f"PAIRING_OK credentials written to {cred_out} ({len(creds)} chars)", flush=True)
    else:
        print("PAIRING_FAILED has_paired=False", flush=True)
    await pairing.close()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main(*sys.argv[1:6])))
