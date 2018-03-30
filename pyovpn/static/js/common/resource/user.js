angular.module(
    'pyovpn.resource.user', [])
    .factory('$user', UserFactory)
    .value('$userDict', {})

function UserFactory($log, $q, $websocket, $userDict) {

    class User {
        constructor(data) {
            this.$update(data);
        }

        $save(data) {
            if (typeof data === 'undefined') {
                data = this.$serialize();
            } else {
                this.$update(data);
            }

            return $websocket.emit({message: 'pyovpn.user.set', body: data}).then(data => {
                this.$update(data);
                return this;
            });
        }

        $delete() {
            return $websocket.emit({message: 'pyovpn.user.del', body: this.username});
        }


        $update(data) {
            this.$original = data;
            angular.extend(this, data);
        }

        $reset() {
            this.$update(this.$original);
        }

        $serialize() {
            return {
            };
        }
    }

    class UserRepository {
        constructor() {
            this.user = User;
            $websocket.register('pyovpn.user.detail', this.set.bind(this));
            $websocket.register('pyovpn.user.del', this.del.bind(this));
        }

        add(user) {
            return $websocket.emit(
                {message: 'pyovpn.user.add', body: user}
            ).then(message => {
                console.log(message.body);
                return $userDict[message.body.username]
            });
        }

        set(body) {
            let user = {};

            if (body.username in $userDict) {
                user = $userDict[body.username];
                user.$update(body);
            } else {
                user = new User(body);
                $userDict[body.username] = user;
            }
            return user;
        }

        del(body) {
            if (body in $userDict) {
                delete $userDict[body];
            }
        }

        get(name) {
            if(name in $userDict) {
                return $q.resolve($userDict[name]);
            }

            return $websocket.emit({message: 'pyovpn.user.detail', body: name}).then(message => {
                console.log(message, $userDict);
                return $userDict[message.body.username];
            });
        }

        list(params) {
            if (typeof params === 'undefined') {
                params = {};
            }

            return $websocket.emit({message: 'pyovpn.user.list', body: params}).then(message => {
                let userList = [];

                for (let user of message.body) {
                    userList.push(this.set(user));
                }

                return userList;
            });
        }
    }

    return new UserRepository();
}


