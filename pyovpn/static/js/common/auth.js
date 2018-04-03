(function () {
    'use strict';

    authService.$inject = ['$websocket', '$state', '$q', '$log'];

    angular
        .module('vpn.common.auth', [
            'vpn.common.websocket',
        ])
        .service('$auth', authService)
        .run(['$rootScope', '$auth', (rs, a) => rs.$auth = a]);


    function authService($websocket, $state, $q, $log) {
        class Auth {

            constructor() {
                this.authData = {};
                this.logged = false;
                this.resolved = false;
                this.token = this.getToken();
                this._loginDeferred = $q.defer();

                $websocket.register('connect', body => {
                    if (this.token) {
                        this.emitToken();
                    }
                    else {
                        this.resolved = true;
                    }
                });

                $websocket.register('pyovpn.current', body => {
                    this.logged = body.is_anonymouse === false;
                    this.resolved = true;
                    if (this.logged) this._loginDeferred.resolve(true);
                });
            }

            emitToken() {
                $websocket.emit({
                    message: 'pyovpn.token',
                    body: this.token
                });
            }

            loginPromise() {
                return this._loginDeferred.promise;
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
                        this.setToken(data.body.token || '');
                        this.emitToken();
                        return data.body.logged;
                    }

                    return false;
                });
            }

            logout() {
                this._loginDeferred = $q.defer();
                this.logged = false;

                $websocket.emit({
                    message: 'pyovpn.logout',
                    body: this.token
                }).then(() => {
                    this.setToken('');
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

}());
