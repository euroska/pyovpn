(function () {
    'use strict';

    VpnFactory.$inject = ['$log', '$q', '$websocket', '$vpnDict'];

    angular.module(
        'pyovpn.resource.vpn', [])
        .value('$vpnDict', {})
        .factory('$vpn', VpnFactory)

    function VpnFactory($log, $q, $websocket, $vpnDict) {

        class VPN {
            constructor(data) {
                this.$update(data);
            }

            $save(data) {
                if (typeof data === 'undefined') {
                    data = this.$serialize();
                } else {
                    this.$update(data);
                }

                return $websocket.emit({message: 'pyovpn.vpn.set', body: data}).then(data => {
                    this.$update(data);
                    return this;
                });
            }

            $delete() {
                return $websocket.emit({message: 'pyovpn.vpn.del', body: this.name});
            }


            $update(data) {
                this.$original = data;
                angular.extend(this, data);
            }

            $reset() {
                this.$update(this.$original);
            }

            $renew(username) {
                return $websocket.emit({
                    message: 'pyovpn.vpn.user.renew',
                    body: {name: this.name, username: username}
                });
            }

            $revoke(username) {
                return $websocket.emit({
                    message: 'pyovpn.vpn.user.revoke',
                    body: {name: this.name, username: username}
                });
            }

            $add(username) {
                return $websocket.emit({
                    message: 'pyovpn.vpn.user.add',
                    body: {name: this.name, username: username}
                });
            }

            $config() {
                return $websocket.emit({
                    message: 'pyovpn.vpn.config',
                    body: {
                        name: this.name,
                    }
                }).then(message => message.body.config);
            }

            $configSet(config) {
                return $websocket.emit({
                    message: 'pyovpn.vpn.config.set',
                    body: {
                        name: this.name,
                        config: config
                    }
                }).then(message => message.body.config);
            }

            $serialize() {
                return {
                    name: this.name,
                    description: this.description,
                    autostart: this.autostart,
                    subject: this.subject
                };
            }
        }

        class VPNRepository {
            constructor() {
                this.vpn = VPN;
                $websocket.register('pyovpn.vpn.detail', this.set.bind(this));
                $websocket.register('pyovpn.vpn.del', this.del.bind(this));
            }

            add(vpn) {
                return $websocket.emit({message: 'pyovpn.vpn.set', body: vpn}).then(
                    message => $vpnDict[message.body.name]
                );
            }

            set(body) {
                let vpn = {};

                if (body.name in $vpnDict) {
                    vpn = $vpnDict[body.name];
                    vpn.$update(body);
                } else {
                    vpn = new VPN(body);
                    $vpnDict[body.name] = vpn;
                }

                return vpn;
            }

            del(body) {
                if (body.name in $vpnDict) {
                    delete $vpnDict[body.name];
                }
            }

            get(name) {
                if(name in $vpnDict) {
                    let deferred = $q.defer()
                    deferred.resolve($vpnDict[name])
                    return deferred.promise;
                }

                return $websocket.emit(
                    {message: 'pyovpn.vpn.detail', body: name}
                ).then(message => $vpnDict[name]);
            }

            list(params) {
                if (typeof params === 'undefined') {
                    params = {};
                }

                return $websocket.emit({message: 'pyovpn.vpn.list', body: params}).then(message => {
                    let vpnList = [];

                    for (let vpn of message.body) {
                        vpnList.push(this.set(vpn));
                    }

                    return vpnList;
                });
            }
        }

        return new VPNRepository();
    }
}());
