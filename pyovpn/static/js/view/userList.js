(function () {
    'use strict';

    class UserListController {

        constructor($log, $auth, $user, $userDict) {
            this.$log = $log;
            this.$auth = $auth;
            this.$user = $user;
            this.$userDict = $userDict;
        }

        $onInit() {
            this.reload();
        }

        reload() {
            this.userList = [];
            for(let username in this.$userDict) {
                this.userList.push(this.$userDict[username]);
            }
        }

        userAdd() {
            return this.$user.add(this.new_user).then(() => {
                this.resetNewUser();
                this.reload();
            });
        }

        userDelete(user) {
            if(confirm("Are you sure?")) {
                user.$delete().then(() => {
                    this.reload();
                });
            }
        }

        $postLink() {
            this.resetNewUser.call(this);
        }

        resetNewUser() {
            this.userAddForm.$setUntouched();
            this.userAddForm.$setPristine();
            this.new_user = {
                is_admin: false,
                is_anonymouse: false
            };
        }
    }

    angular.module(
        'pyovpn.userlist', []
    )
    .component('userList', {
        templateUrl: '/js/view/userList.tpl.html',
        controller: UserListController,
        bindings: {
            users: '='
        }
    });
}());
