(function () {
    'use strict';


    class VpnConfigUserController {
        constructor($log, $vpn, $stateParams) {
            this.$log = $log;
            this.$vpn = $vpn;
            this.$stateParams = $stateParams;
            this.username = $stateParams.username;
            this.config = '';
        }

        $onInit() {
            this.vpn.$configUser(this.username).then(config => {
                this.config = config;
            });
        }

        download() {
            return `data:text/plain,${this.config}`;
        }
    }

    angular.module(
        'pyovpn.vpnconfiguser', []
    )
    .component('vpnConfigUser', {
        templateUrl: '/js/view/vpnConfigUser.tpl.html',
        controller: VpnConfigUserController,
        bindings: {
            vpn: '=',
        }
    });
}());




