import asyncio
import sys

async def get_date():
    # Create the subprocess, redirect the standard output into a pipe
    proc = await asyncio.create_subprocess_exec(
        '/usr/bin/openvpn', 'sourcelab.conf',
        stdout=asyncio.subprocess.PIPE
    )

    # Read one line of output
    #for n in range(3):
    x = 0
    response = ""
    async for data in proc.stdout:
    #while True:
        #data = await proc.stdout.readline()
        response = data.decode('utf-8')
        x += 1
        print("DAEMON", response)

        if not data:
            break

    # Wait for the subprocess exit
    print("EXIT")
    return response


loop = asyncio.get_event_loop()
date = loop.run_until_complete(get_date())
print("Current date: %s" % date)
