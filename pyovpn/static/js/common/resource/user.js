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
            return $websocket.emit({message: 'pyovpn.user.del', body: this.name});
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
            $websocket.register('pyovpn.user.detail', this.userSet.bind(this));
            $websocket.register('pyovpn.user.del', this.userDel.bind(this));
        }

        userAdd(user) {
            return $websocket.emit({message: 'pyovpn.user.add', body: user}).then(body => $userDict[body.name]);
        }

        userSet(body) {
            let user = {};

            if (body.name in $userDict) {
                user = $userDict[body.name];
                user.$update(body);
            } else {
                user = new User(body);
                $userDict[body.name] = user;
            }

            return user;
        }

        userDel(body) {
            if (body.name in $userDict) {
                delete $userDict[body.name];
            }
        }

        get(name) {
            return $websocket.emit({message: 'pyovpn.user.detail', body: name}).then(body => this.userUpdate(body));
        }

        list(params) {
            if (typeof params === 'undefined') {
                params = {};
            }

            return $websocket.emit({message: 'pyovpn.user.list', body: params}).then(message => {
                let userList = [];

                for (let user of message.body) {
                    userList.push(this.userSet(user));
                }

                return userList;
            });
        }
    }

    return new UserRepository();
}


