(function () {
    'use strict';

    TemplateUserFactory.$inject = ['$log', '$q', '$websocket', '$templateUserDict'];

    angular.module(
        'pyovpn.resource.template.user', [])
        .factory('$templateUser', TemplateUserFactory)
        .value('$templateUserDict', {})

    function TemplateUserFactory($log, $q, $websocket, $templateUserDict) {

        class TemplateUser {
            constructor(data) {
                this.$update(data);
            }

            $save(data) {
                if (typeof data === 'undefined') {
                    data = this.$serialize();
                } else {
                    this.$update(data);
                }

                return $websocket.emit({message: 'pyovpn.template.user.set', body: data}).then(data => {
                    this.$update(data);
                    return this;
                });
            }

            $delete() {
                return $websocket.emit({message: 'pyovpn.template.user.del', body: this.name});
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

        class TemplateUserRepository {
            constructor() {
                this.templateUser = TemplateUser;
                $websocket.register('pyovpn.template.user.detail', this.set.bind(this));
                $websocket.register('pyovpn.template.del', this.del.bind(this));
            }

            set(name, template) {
                return $websocket.emit({message: 'pyovpn.template.user.set', body: {name, template}}).then(body => $templateUserDict[body.name]);
            }

            update(body) {

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

                return $websocket.emit({message: 'pyovpn.template.user.list', body: params}).then(message => {
                    angular.extend($templateUserDict, message.body);
                    return $templateUserDict;
                });
            }
        }

        return new TemplateUserRepository();
    }
}());


