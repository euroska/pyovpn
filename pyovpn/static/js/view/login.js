(function () {
    'use strict';

    const loginComponent = {
        templateUrl: '/js/view/login.tpl.html',
        controller: ['$log', '$auth', LoginController],
    };

    angular
        .module('pyovpn.login', ['vpn.common.auth'])
        .component('login', loginComponent);

    function LoginController($log, $auth) {
        this.submit = () => {
            $auth.login(this.username, this.password);
        };
    }
}());


