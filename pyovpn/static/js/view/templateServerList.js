(function () {
    'use strict';


    class TemplateServerListController {

        constructor($log, $auth, $templateServer, $templateServerDict) {
            this.$log = $log;
            this.$auth = $auth;
            this.$templateServer = $templateServer;;
            this.$templateServerDict = $templateServerDict;
        }

        $postLink() {
            this.resetNewTemplate.call(this);
        }

        resetNewTemplate() {
            this.templateAddForm.$setUntouched();
            this.templateAddForm.$setPristine();
            this.name = '';
        }

        add() {
            console.log("ADD");
            this.$templateServer.add(this.name, '').then(() => {
                this.resetNewTemplate();
            });
        }

        del(name) {
            this.$templateServer.del(name);
        }

    }


    angular
        .module('pyovpn.templateserverlist', [])
        .component('templateServerList', {
            templateUrl: '/js/view/templateServerList.tpl.html',
            controller: TemplateServerListController,
            bindings: {
                templateList: '='
            }
        });
}());



