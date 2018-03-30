'use strict';

authService.$inject = ['$websocket', '$state', '$q', 'loginModal'];

angular
    .module('vpn.common.auth', [
        'vpn.common.websocket',
        'pyovpn.component.loginModal',
    ])
    .service('$auth', authService);


function authService($websocket, $state, $q, loginModal) {
    class Auth {

        constructor() {
            this.authData = {};
            this.login = $q.defer();
            this.logged = false
            this.token = this.getToken();

            if (this.token) this.emitToken();

            $websocket.register('pyovpn.current', body => {
                this.logged = body.is_anonymouse === false;
                if (this.logged) {
                    console.log("LOGGED!!!");
                    this.login.resolve(true);
                }
            });
        }

        emitToken() {
            $websocket.emit({
                message: 'pyovpn.token',
                body: this.token
            });
        }

        loginPromise() {
            return this.login.promise;
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
                    this.emitToken();
                    return data.body.logged;
                }

                return false;
            });
        }

        logout() {
            this.login = $q.defer();
            this.logged = false;
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
