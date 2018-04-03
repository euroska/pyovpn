import os
import datetime
import hashlib
import logging
from .default import Auth

logger = logging.getLogger(__name__)

class SimpleAuth(Auth):

    def hashPassword(self, password, salt=None):
        if salt is None:
            salt = self.manager.config['secret']

        h = hashlib.sha256(password.encode('utf8'))
        h.update(salt.encode('utf8'))
        return h.hexdigest()

    async def checkPassword(self, username, password):
        user = self.manager.config['users'][username]
        return self.hashPassword(password) == user['password']

    async def login(self, username, password):
        if username in self.manager.config['users']:
            return await self.checkPassword(username, password)

        return False

    async def getToken(self, username, permanent=False):
        path = ''
        while True:
            hash =  hashlib.sha256(
                (username + datetime.datetime.now().isoformat()).encode('utf-8')
            )
            path = os.path.join(self.manager.config['data_path'], 'tokens', hash.hexdigest())
            if not os.path.exists(path):
                break

        with open(path, 'w') as f:
            f.write(username)

        token = hash.hexdigest()
        self.tokens[token] = username
        return token

    async def checkToken(self, token):
        if not token:
            return False

        if token in self.tokens:
            return self.tokens[token]

        path = os.path.join(self.manager.config['data_path'], 'tokens', token.strip())
        if os.path.exists(path):
            with open(path, 'r') as f:
                username = f.read()
                self.tokens[token] = username
                return username

        return False

    async def delToken(self, token):
        path = os.path.join(self.manager.config['data_path'], 'tokens', token)

        if os.path.exists(path):
            os.unlink(path)

        if token in self.tokens:
            del self.tokens[token]

        return True

    async def clearTokens(self, delta):
        arbitrary = datetime.datetime.now() - delta
        for root, dirs, tokens in os.walk(os.path.join(
            self.manager.config['data_path'], 'tokens'
        )):
            for token in tokens:
                path = os.path.join(root, f)
                if arbitrary > os.path.getctime(path):
                    os.unlink(path)
                    if token in self.tokens:
                        del self.tokens[token]

        return True
