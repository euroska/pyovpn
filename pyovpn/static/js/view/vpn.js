(function () {
    'use strict';

    angular.module(
        'pyovpn.vpn', []
    )
    .component('vpn', {
        templateUrl: '/js/view/vpn.tpl.html',
        controller: VpnController,
    //     controllAs: 'ctrl'
        bindings: {
            vpn: '='
        }
    });

    function VpnController($log, $auth) { }
}());


