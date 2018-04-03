(function () {
    'use strict';

    TemplateUserFactory.$inject = ['$log', '$q', '$websocket', '$templateUserDict'];

    angular.module(
        'pyovpn.resource.template.user', [])
        .factory('$templateUser', TemplateUserFactory)
        .value('$templateUserDict', {})

    function TemplateUserFactory($log, $q, $websocket, $templateUserDict) {

        class TemplateUserRepository {
            constructor() {
                $websocket.register('pyovpn.template.user.detail', this.set.bind(this));
                $websocket.register('pyovpn.template.user.del', this._del.bind(this));
            }

            get(name) {
                if(name in $templateUserDict) {
                    return $q.resolve($templateUserDict[name])
                }

                return this.list().then(() => {
                    return $templateUserDict[name];
                });
            }

            set(body) {
                $templateUserDict[body.name] = body.template;
                return body.template;
            }

            add(name, template) {
                return $websocket.emit({message: 'pyovpn.template.user.set', body: {name, template}}).then(body => $templateUserDict[body.name]);
            }

            _del(name) {
                if (name in $templateUserDict) {
                    delete $templateUserDict[name];
                }
            }

            del(name) {
                return $websocket.emit({message: 'pyovpn.template.user.del', body: name});
            }

            list(params) {
                if (typeof params === 'undefined') {
                    params = {};
                }

                return $websocket.emit({message: 'pyovpn.template.user.list', body: params}).then(message => {
                    angular.extend($templateUserDict, message.body);
                    return $templateUserDict;
                })
            }
        }

        return new TemplateUserRepository();
    }

}());
