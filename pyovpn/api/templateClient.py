import os
from .decorators import isAdmin, isAutorized, api


class TemplateClientApi(object):
    @isAdmin
    @api('pyovpn.template.client.list')
    async def templateClientList(self, body, user):
        path = os.path.join(self.manager.config['data_path'],'templates/client')
        templates = {}
        for path, dirs, files in os.walk(path):
            for template in files:
                with open(os.path.join(path, template)) as f:
                    templates[template] = f.read()

        return templates

    @isAdmin
    @api('pyovpn.template.client.set', message_out='pyovpn.template.client.detail')
    async def templateClientSet(self, body, user):
        path = os.path.join(
            self.manager.config['data_path'],
            'templates/client',
            body['name']
        )

        with open(path, 'w') as f:
            f.write(body['template'])

        return {
            'name': body['name'],
            'template': body['template'],
        }

    @isAdmin
    @api('pyovpn.template.client.del')
    async def templateClientDel(self, body, user):
        path = os.path.join(
            self.manager.config['data_path'],
            'templates/client',
            body
        )
        if os.path.exists(path):
            os.unlink(path)

        return body
