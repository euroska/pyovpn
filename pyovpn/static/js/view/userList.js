(function () {
    'use strict';

    angular.module(
        'pyovpn.userlist', []
    )
    .component('userList', {
        templateUrl: '/js/view/userList.tpl.html',
        controller: ['$log', '$auth', '$user', '$userDict', UserListController],
    //     controllAs: 'ctrl'
        bindings: {
        }
    });

    function UserListController($log, $auth, $user, $userDict) {

        this.userList = $userDict;

        this.new_user = {
            is_admin: false,
            is_anonymouse: false
        };

        this.add = () => {
            $user.add(this.new_user);
        };

        this.userDelete = user => {
            if (confirm("Are you sure?")) {
                user.$delete();
            }
        };
    }
}());
