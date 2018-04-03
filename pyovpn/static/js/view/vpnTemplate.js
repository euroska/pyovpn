(function () {
    'use strict';


    class VpnTemplateController {
        constructor($log, $vpn, $templateServer) {
            this.$log = $log;
            this.$vpn = $vpn;
            this.template = '';
            this.$templateServer = $templateServer;
        }

        $onInit() {
            this.vpn.$template().then(template => {
                this.template = template;
            });

            this.$templateServer.list().then(list => {
                this.templates = list;
            });
        }

        save() {
            this.vpn.$templateSet(this.template).then(template => {
                this.template = template;
            });
        }
    }

    angular.module(
        'pyovpn.vpntemplate', []
    )
    .component('vpnTemplate', {
        templateUrl: '/js/view/vpnTemplate.tpl.html',
        controller: VpnTemplateController,
        bindings: {
            vpn: '=',
        }
    });
}());




