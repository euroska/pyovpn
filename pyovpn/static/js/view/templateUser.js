(function () {
    'use strict';


    class TemplateUserController {

        constructor($log, $auth, $templateUser) {
            this.$log = $log;
            this.$auth = $auth;
            this.$templateUser = $templateUser;
        }

        save() {
            this.$templateUser.add(this.name, this.template);
        }
    }

    angular
        .module('pyovpn.templateuser', [])
        .component('templateUser', {
            templateUrl: '/js/view/templateUser.tpl.html',
            controller: TemplateUserController,
            bindings: {
                name: '=',
                template: '='
            }
        });
}());



