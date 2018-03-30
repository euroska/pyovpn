'use strict';

angular.module(
    'vpn.common.websocket',
    [])
    .provider('$websocket', ws);

function ws() {
    'ngInject';

    return {
        url: 'ws://localhost:8080/api/ws', setUrl: function(url = null) {
            this.url = url;
            return this;
        },

        $get: function($q, $log, $rootScope, $timeout) {
            let _url = this.url;

            class WSClient {
                constructor(url = _url, _opt = {}) {
                    {
                        let {
                            reconnectDelay = 2000
                        } = _opt;

                        this.opt = {reconnectDelay};
                    }

                    this.urlSet(url);
                    this.connect();
                    this.promisses = {};
                    this.callbacks = {};
                }

                urlSet(url = _url) {
                    if (angular.isString(url)) {
                        this.url = url;
                    }

                    return this;
                }

                connect() {
                    this.timer = null;

                    if (!this.url) {
                        $log.error("$websocket - connect:", "unknown WebSocket url");
                        return this;
                    }

                    this.ws = new WebSocket(this.url);
                    this.ws.onopen = this.onopen.bind(this);
                    this.ws.onclose = this.onclose.bind(this);
                    this.ws.onmessage = this.onmessage.bind(this);
                    return this;
                }

                onopen() {
                    this.$opened = true;
                    $log.info(`$websocket- oAuth token: token`);
                    return this;
                }

                onmessage(evt) {
                    if (!angular.isObject(evt)) {
                        $log.error("$websocket - event parameter is not set");
                        return this;
                    }

                    const msg = JSON.parse(evt.data);
                    if (msg.message == null) {
                        $log.error('Device is not connected');
                    } else {

                        if (msg.message in this.callbacks) {
                            for (let i = 0; i < this.callbacks[msg.message].length; i++) {
                                this.callbacks[msg.message][i](msg.body);
                            }
                        }

                        if (msg.id in this.promisses) {
                            if (!msg.message.startsWith('pyovpn.error')) {
                                this.promisses[msg.id].resolve(msg);

                            } else {

                                if (Array.isArray(msg.body.description)) {
//                                     for (let error of msg.body.description)
//                                         notificationsService.error(error);

                                } else {
//                                     notificationsService.error(msg.body.description);
                                }

                                this.promisses[msg.id].reject(msg);
                            }
                        }

                        $rootScope.$broadcast(`websocket.${msg.message}`, msg.body);
                        $timeout(() => $rootScope.$apply());
                    }
                }

                register(type, callback) {
                    $log.info(`register callback: ${type}`);

                    if (!(type in this.callbacks)) {
                        this.callbacks[type] = [];
                    }

                    this.callbacks[type].push(callback);
                }

                onclose() {
                    this.$opened = false;
                    if (!this.timer && this.opt.reconnectDelay) {
                        this.timer = setTimeout(this.connect.bind(this), this.opt.reconnectDelay);
                    } else if (!this.opt.reconnectDelay) {
                        this.connect();
                    }

                    return this;
                }

                uuid4() {
                    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                        let r = Math.random() * 16 | 0;
                        let v = c == 'x' ? r : (r & 0x3 | 0x8);
                        return v.toString(16);
                    });
                }

                emit(msg, deferred) {

                    if (typeof deferred === 'undefined') {
                        deferred = $q.defer();
                    }

                    if (typeof msg.id === 'undefined') {
                        msg.id = this.uuid4();
                    }

                    this.promisses[msg.id] = deferred;

                    // if websocket is not opened
                    if (this.ws.readyState !== this.ws.OPEN) {
                        $timeout(() => this.emit(msg, deferred), 100);
                        return deferred.promise;
                    }

                    const payload = JSON.stringify(msg);
                    this.ws.send(payload);

                    return deferred.promise;
                }
            }

            return new WSClient();
        }
    };
}
