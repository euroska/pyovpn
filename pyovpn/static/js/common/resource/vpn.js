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
            $websocket.register('pyovpn.vpn.detail', this.vpnSet.bind(this));
            $websocket.register('pyovpn.vpn.del', this.vpnDel.bind(this));
        }

        vpnAdd(vpn) {
            return $websocket.emit({message: 'pyovpn.vpn.add', body: vpn}).then(body => $vpnDict[body.name]);
        }

        vpnSet(body) {
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

        vpnDel(body) {
            if (body.name in $vpnDict) {
                delete $vpnDict[body.name];
            }
        }

        get(name) {
            return $websocket.emit({message: 'pyovpn.vpn.detail', body: name}).then(body => this.vpnUpdate(body));
        }

        list(params) {
            if (typeof params === 'undefined') {
                params = {};
            }

            return $websocket.emit({message: 'pyovpn.vpn.list', body: params}).then(message => {
                let vpnList = [];

                for (let vpn of message.body) {
                    vpnList.push(this.vpnSet(vpn));
                }

                return vpnList;
            });
        }
    }

    return new VPNRepository();
}

