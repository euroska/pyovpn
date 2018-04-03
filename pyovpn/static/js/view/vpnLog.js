(function () {
    'use strict';


    class VpnLogController {
        constructor($log, $vpn) {
            this.$log = $log;
            this.$vpn = $vpn;
            this.log = '';
        }

        $onInit() {
            this.vpn.$log().then(log => {
                this.log = log;
            });
        }
    }

    angular.module(
        'pyovpn.vpnlog', []
    )
    .component('vpnLog', {
        templateUrl: '/js/view/vpnLog.tpl.html',
        controller: VpnLogController,
        bindings: {
            vpn: '=',
        }
    });
}());





