(function () {
    'use strict';

    angular.module(
        'pyovpn.vpnlist', []
    )
    .component('vpnList', {
        templateUrl: '/js/view/vpnList.tpl.html',
        controller: ['$log', '$auth', '$vpn', VpnListController],
    //     controllAs: 'ctrl'
        bindings: {
            vpnList: '='
        }
    });

    function VpnListController($log, $auth, $vpn) {

        this.vpnAdd = () => {
            this.vpnAddPending = true;
            $vpn.add(this.new_vpn)
                .then(resetNewVpn.bind(this))
                .catch(resetNewVpn.bind(this));
        };

        this.$postLink = () => resetNewVpn.call(this);

        function resetNewVpn() {
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
}());
