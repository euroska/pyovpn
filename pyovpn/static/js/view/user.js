
angular.module(
    'pyovpn.user', []
)
.component('user', {
    templateUrl: '/js/view/user.tpl.html',
    controller: UserController,
//     controllAs: 'ctrl'
    bindings: {
        user: '='
    }
});

function UserController($log, $auth) {
    'ngInject';
}
