(function () {
    'use strict';

    TemplateServerFactory.$inject = ['$log', '$q', '$websocket', '$templateServerDict'];

    angular.module(
        'pyovpn.resource.template.server', [])
        .factory('$templateServer', TemplateServerFactory)
        .value('$templateServerDict', {})

    function TemplateServerFactory($log, $q, $websocket, $templateServerDict) {
        class TemplateServer {
            constructor(data) {
                this.$update(data);
            }

            $save(data) {
                if (typeof data === 'undefined') {
                    data = this.$serialize();
                } else {
                    this.$update(data);
                }

                return $websocket.emit({message: 'pyovpn.template.server.set', body: data}).then(data => {
                    this.$update(data);
                    return this;
                });
            }

            $delete() {
                return $websocket.emit({message: 'pyovpn.template.server.del', body: this.name});
            }


            $update(data) {
                this.$original = data;
                angular.extend(this, data);
            }

            $reset() {
                this.$update(this.$original);
            }

            $serialize() {
                return {
                };
            }
        }

        class TemplateServerRepository {
            constructor() {
                this.templateServer = TemplateServer;
                $websocket.register('pyovpn.template.server.detail', this.set.bind(this));
                $websocket.register('pyovpn.template.del', this.del.bind(this));
            }

            set(name, template) {
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
