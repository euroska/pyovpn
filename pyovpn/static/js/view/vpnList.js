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

        this.new_vpn = {
            autostart: false,
            subject: {
                o: 'Test',
                ou: 'Test'
            }
        };

        this.add = () => {
            $vpn.add(this.new_vpn);
        };
    }
}());
