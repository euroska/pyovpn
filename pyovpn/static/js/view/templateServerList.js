(function () {
    'use strict';


    class TemplateServerListController {

        constructor($log, $auth) {
            this.$log = $log;
            this.$auth = $auth;
        }
    }

    angular
        .module('pyovpn.templateserverlist', [])
        .component('templateServerList', {
            templateUrl: '/js/view/templateServerList.tpl.html',
            controller: TemplateServerListController,
            bindings: {
                templateList: '='
            }
        });
}());



