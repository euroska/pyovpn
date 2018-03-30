(function () {
    'use strict';

    const templateServerListComponent = {
        templateUrl: '/js/view/templateServerList.tpl.html',
        controller: TemplateServerListController,
    //     controllAs: 'ctrl'
        bindings: {
            templateList: '='
        }
    };

    angular
        .module('pyovpn.templateserverlist', [])
        .component('templateServerList', templateServerListComponent);

    function TemplateServerListController($log, $auth) {

    }
}());



