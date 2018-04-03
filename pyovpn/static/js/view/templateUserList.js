(function () {
    'use strict';

    angular.module(
        'pyovpn.templateuserlist', []
    )
    .component('templateUserList', {
        templateUrl: '/js/view/templateUserList.tpl.html',
        controller: TemplateUserListController,
        bindings: {
            templateList: '='
        }
    });

    function TemplateUserListController($log, $auth) {
        this.test = 'koko2';
    }
}());
