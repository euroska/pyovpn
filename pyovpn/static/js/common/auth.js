'use strict';

angular.module(
    'vpn.common.auth',
    ['vpn.common.websocket']
).service('$auth', authService);


function authService($websocket, $state, $q) {
    'ngInject';
    class Auth {

        constructor() {
            this.authData = {};
        }

        loginRedirect() {
            let deferred = $q.defer();

            if(!this.authData.logged) {
                deferred.resolve(true);
                $state.go('login');
            }
            else {
                deferred.resolve(true);
            }
            return deferred;
        }

        login(username, password) {
            return $websocket.emit({
                message: 'pyovpn.login',
                body: {
                    username: username,
                    password: password
                }
            }).then(data => {
                if(data.message == 'pyovpn.login') {
                    angular.extend(this.authData, data.body);
                    console.log(this.authData);
                    return data.body.logged;
                }

                return false;
            });
        }

        token(token) {
        }
    }

    return new Auth();
}
