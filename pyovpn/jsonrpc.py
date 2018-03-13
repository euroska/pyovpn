from aiohttp.web import json_response

class JsonRPC(object):

    def __init__(self, manager):
        self.manager = manager


    async def __call__(self, request):
        return json_response({'test': "All right!"})
