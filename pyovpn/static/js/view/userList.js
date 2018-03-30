
angular.module(
    'pyovpn.userlist', []
)
.component('userList', {
    templateUrl: '/js/view/userList.tpl.html',
    controller: UserListController,
//     controllAs: 'ctrl'
    bindings: {
    }
});

function UserListController($log, $auth, $user, $userDict) {
    'ngInject';

    this.userList = $userDict;

    this.new_user = {
        is_admin: false,
        is_anonymouse: false
    };

    this.add = () => {
        $user.add(this.new_user);
    };
}
