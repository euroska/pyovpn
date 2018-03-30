
angular.module(
    'pyovpn.templateuserlist', []
)
.component('templateUSerList', {
    templateUrl: '/js/view/templateUserList.tpl.html',
    controller: TemplateUserListController,
//     controllAs: 'ctrl'
    bindings: {
        templateList: '='
    }
});

function TemplateUserListController($log, $auth) {
    'ngInject';
}


