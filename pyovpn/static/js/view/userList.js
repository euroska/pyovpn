
angular.module(
    'pyovpn.userlist', []
)
.component('userList', {
    templateUrl: '/js/view/userList.tpl.html',
    controller: UserListController,
//     controllAs: 'ctrl'
    bindings: {
        userList: '='
    }
});

function UserListController($log, $auth) {
    'ngInject';
}
