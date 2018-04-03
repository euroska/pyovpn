(function () {
    'use strict';


    class VpnConfigController {
        constructor($log, $vpn) {
            this.$log = $log;
            this.$vpn = $vpn;
            this.config = '';
        }

        $onInit() {
            this.vpn.$config().then(config => {
                this.config = config;
            });
        }

        save() {
            this.vpn.$configSet(this.config).then(config => {
                this.config = config;
            });
        }

        generate() {
            this.vpn.$configSet(null).then(config => {
                this.config = config;
            });
        }

        download() {
            return `data:text/plain,${this.config}`;
        }
    }

    angular.module(
        'pyovpn.vpnconfig', []
    )
    .component('vpnConfig', {
        templateUrl: '/js/view/vpnConfig.tpl.html',
        controller: VpnConfigController,
        bindings: {
            vpn: '=',
        }
    });
}());



