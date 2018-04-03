(function () {
    'use strict';

    class TemplateUserListController {
        constructor($log, $auth, $templateUser, $templateUserDict) {

            this.$templateUser = $templateUser;
            this.$templateUserDict = $templateUserDict;
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
            this.$templateUser.add(this.name, '').then(() => {
                this.resetNewTemplate();
            });
        }

        del(name) {
            this.$templateUser.del(name);
        }

    }

    angular.module(
        'pyovpn.templateuserlist', []
    )
    .component('templateUserList', {
        templateUrl: '/js/view/templateUserList.tpl.html',
        controller: TemplateUserListController,
        bindings: {
            templateList: '='
        }
    });
}());
