(function () {
    'use strict';

    TemplateServerFactory.$inject = ['$log', '$q', '$websocket', '$templateServerDict'];

    angular.module(
        'pyovpn.resource.template.server', [])
        .factory('$templateServer', TemplateServerFactory)
        .value('$templateServerDict', {})

    function TemplateServerFactory($log, $q, $websocket, $templateServerDict) {

        class TemplateServerRepository {
            constructor() {
                $websocket.register('pyovpn.template.server.detail', this.set.bind(this));
                $websocket.register('pyovpn.template.del', this.del.bind(this));
            }

            get(name) {
                if(name in $templateServerDict) {
                    return $q.resolve($templateServerDict[name])
                }

                return this.list().then(() => {
                    return $templateServerDict[name];
                });
            }

            set(body) {
                $templateServerDict[body.name] = body.template;
                return body.template;
            }

            add(name, template) {
                return $websocket.emit({message: 'pyovpn.template.server.set', body: {name, template}}).then(body => $templateServerDict[body.name]);
            }

            del(name) {
                if (body.name in $userDict) {
                    delete $userDict[body.name];
                }
            }

            list(params) {
                if (typeof params === 'undefined') {
                    params = {};
                }

                return $websocket.emit({message: 'pyovpn.template.server.list', body: params}).then(message => {
                    angular.extend($templateServerDict, message.body);
                    return $templateServerDict;
                })
            }
        }

        return new TemplateServerRepository();
    }

}());
