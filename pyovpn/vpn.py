import asyncio
from .ca import CA

class VPN(object):


    def __init__(self, manager, name, enable=True):
        self.manager = manager
        self.name = name
        self.enable = enable
        self.config = self.createConfig()
        self.ca = CA(self.config)

        self.output = []
        self.process = None
        self.loop = None

    def createConfig(self):
        return {

        }

    def start(self):
        self.await = self.run()

    async def run(self):
        self.process = await asyncio.create_subprocess_exec(
            '/usr/bin/openvpn', 'sourcelab.conf',
            stdout=asyncio.subprocess.PIPE
        )

        async for data in self.process.stdout:
            if not data:
                break

            self.output = self.output[:100] + [data]

        self.process = None


    def reload(self):
        if self.process is None:
            return False

        self.process.send_signal(1)
        return True

    def kill(self):
        if self.process is None:
            return False

        self.process.kill()
        return True


    def stop(self):
        if self.process is None:
            return False

        self.process.terminate()
        return True

