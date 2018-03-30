angular.module(
    'pyovpn.resource.vpn', [])
    .factory('$vpn', VpnFactory)
    .value('$vpnDict', {})

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

        $serialize() {
            return {
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
            return $websocket.emit({message: 'pyovpn.vpn.add', body: vpn}).then(message => $vpnDict[message.body.name]);
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

