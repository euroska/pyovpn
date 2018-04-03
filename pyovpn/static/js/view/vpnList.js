(function () {
    'use strict';


    class VpnListController {

        constructor($log, $auth, $vpn, $vpnDict) {
            this.$log = $log;
            this.$auth = $auth;
            this.$vpn = $vpn;
            this.$vpnDict = $vpnDict;
        }

        $onInit() {
            this.reload();
        }

        reload() {
            this.vpnList = [];
            for(let name in this.$vpnDict) {
                this.vpnList.push(this.$vpnDict[name]);
            }
        }

        vpnAdd () {
            this.vpnAddPending = true;
            this.$vpn.add(this.new_vpn)
                .then(() => {
                    this.resetNewVpn();
                    this.reload();
                })
                .catch(this.resetNewVpn.bind(this));
        };

        $postLink() {
            return this.resetNewVpn.call(this);
        }

        resetNewVpn() {
            this.vpnAddPending = false;
            this.vpnAddForm.$setUntouched();
            this.vpnAddForm.$setPristine();
            this.new_vpn = {
                autostart: false,
                subject: {
                    o: 'Test',
                    ou: 'Test'
                }
            };
        }
    }

    angular.module(
        'pyovpn.vpnlist', []
    )
    .component('vpnList', {
        templateUrl: '/js/view/vpnList.tpl.html',
        controller: VpnListController,
    //     controllAs: 'ctrl'
        bindings: {
            vpns: '='
        }
    });
}());
