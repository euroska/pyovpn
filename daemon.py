#!/home/euro/Projects/open-source/pyovpn/env/bin/python
import datetime
import asyncio
import signal
import sys


loop = asyncio.get_event_loop()
loop.add_signal_handler(
    getattr(signal, 'SIGHUP'),
    lambda : print("SIGHUP")
)

loop.add_signal_handler(
    getattr(signal, 'SIGUSR1'),
    lambda : print("SIGUSR1")
)

loop.add_signal_handler(
    getattr(signal, 'SIGINT'),
    lambda : print("SIGINT") or loop.stop()
)

async def cycle(loop):
    while True:
    #for x in range(2):
        print(datetime.datetime.now(), flush=True)
        await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(cycle(loop))
