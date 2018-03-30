
angular.module(
    'pyovpn.templateserverlist', []
)
.component('templateServerList', {
    templateUrl: '/js/view/templateServerList.tpl.html',
    controller: TemplateServerListController,
//     controllAs: 'ctrl'
    bindings: {
        templateList: '='
    }
});

function TemplateServerListController($log, $auth) {
    'ngInject';
}

