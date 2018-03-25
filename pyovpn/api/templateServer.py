import os
from .decorators import isAdmin, isAutorized, api


class TemplateServerApi(object):
    @isAdmin
    @api('pyovpn.template.server.list')
    async def templateServerList(self, body, user):
        path = os.path.join(self.manager.config['data_path'], 'templates/server')
        templates = {}
        for path, dirs, files in os.walk(path):
            for template in files:
                with open(os.path.join(path, template)) as f:
                    templates[template] = f.read()

        return templates

    @isAdmin
    @api('pyovpn.template.server.set', message_out='pyovpn.template.server.detail')
    async def templateServerSet(self, body, user):
        with open(
            os.path.join(
                self.manager.config['data_path'],
                'templates/server',
                body['name']
            ),
            'w'
        ) as f:
            f.write(body['template'])

        return {
            'name': body['name'],
            'template': body['template'],
        }

    @isAdmin
    @api('pyovpn.template.server.del')
    async def templateServerDel(self, body, user):
        path = os.path.join(
            self.manager.config['data_path'],
            'templates/server',
            body
        )
        if os.path.exists(path):
            os.unlink(path)

        return body
