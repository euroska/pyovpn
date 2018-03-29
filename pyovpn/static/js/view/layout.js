
angular.module(
    'pyovpn.layout', []
)
.component('layout', {
    bindings: { },
    templateUrl: '/js/view/layout.tpl.html',
    controller: LayoutController
});

function LayoutController($log) {
    'ngInject';
}
