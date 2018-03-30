
angular.module(
    'pyovpn.logout', ['vpn.common.auth']
)
.component('logout', {
    templateUrl: '/js/view/logout.tpl.html',
    controller: LogoutController
//     controllAs: 'ctrl'
});

function LogoutController($log, $auth, $state) {
    'ngInject';
}

