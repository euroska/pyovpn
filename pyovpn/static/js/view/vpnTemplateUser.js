(function () {
    'use strict';


    class VpnTemplateUserController {
        constructor($log, $vpn, $templateUser) {
            this.$log = $log;
            this.$vpn = $vpn;
            this.template = '';
            this.$templateUser = $templateUser;
        }

        $onInit() {
            this.vpn.$templateUser().then(template => {
                this.template = template;
            });

            this.$templateUser.list().then(list => {
                this.templates = list;
            });
        }

        save() {
            this.vpn.$templateUserSet(this.template).then(template => {
                this.template = template;
            });
        }

        download() {
            return `data:text/plain,${this.template}`;
        }
    }

    angular.module(
        'pyovpn.vpntemplateuser', []
    )
    .component('vpnTemplateUser', {
        templateUrl: '/js/view/vpnTemplateUser.tpl.html',
        controller: VpnTemplateUserController,
        bindings: {
            vpn: '=',
        }
    });
}());





