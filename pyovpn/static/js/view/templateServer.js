(function () {
    'use strict';


    class TemplateServerController {

        constructor($log, $auth, $templateServer) {
            this.$log = $log;
            this.$auth = $auth;
            this.$templateServer = $templateServer;
        }

        save() {
            this.$templateServer.add(this.name, this.template);
        }
    }

    angular
        .module('pyovpn.templateserver', [])
        .component('templateServer', {
            templateUrl: '/js/view/templateServer.tpl.html',
            controller: TemplateServerController,
            bindings: {
                name: '=',
                template: '='
            }
        });
}());



