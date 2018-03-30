(function () {
    'use strict';

    angular.module(
        'pyovpn.user', []
    )
    .component('user', {
        templateUrl: '/js/view/user.tpl.html',
        controller: ['$log', '$auth', '$user', UserController],
    //     controllAs: 'ctrl'
        bindings: {
            user: '='
        }
    });



    function UserController($log, $auth, $user) {

        this.update = () => {
            this.user.$save();
            $log.debug("User saved");
        };

        this.reset = () => {
            this.user.$reset();
            $log.debug("Original values applied");
        };
    }

}());


