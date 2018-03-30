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
            this.logged = $q.defer();
            this.token = this.getToken();

            if(this.token) {
                $websocket.emit({
                    message: 'pyovpn.token',
                    body: this.token
                });
            }

            $websocket.register('pyovpn.current', body => {
                if(body.is_anonymouse === false) {
                    console.log("LOGGED!!!");
                    this.logged.resolve(true);
                }
            });
        }

        loginPromise() {
            return this.logged.promise;
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
                    this.setToken(this.body.token || '');
                    return data.body.logged;
                }

                return false;
            });
        }

        logout() {
            this.logged = $q.defer();
            console.log(`TOKEN ${this.token}`);

            $websocket.emit({
                message: 'pyovpn.logout',
                body: this.token
            }).then(() =>  {
                this.setToken('');
                $state.go('logout');
            });
        }

        setToken(token) {
            this.token = token;
            localStorage.setItem('TOKEN', token);
        }

        getToken() {
            return localStorage.getItem('TOKEN');
        }

    }

    return new Auth();
}
