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

        this.userAdd = () => $user.add(this.new_user).then(resetNewUser.bind(this));
        this.userDelete = user => confirm("Are you sure?") && user.$delete();
        this.$postLink = () => resetNewUser.call(this);

        function resetNewUser() {
            this.userAddForm.$setUntouched();
            this.userAddForm.$setPristine();
            this.new_user = {
                is_admin: false,
                is_anonymouse: false
            };
        }
    }
}());
