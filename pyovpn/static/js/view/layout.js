(function () {
    'use strict';

    const layoutComponent = {
        bindings: { },
        templateUrl: '/js/view/layout.tpl.html',
        controller: LayoutController
    };

    angular
        .module('pyovpn.layout', [])
        .component('layout', layoutComponent);

    function LayoutController($log, $auth) {
        this.logout = e => (e.preventDefault(), $auth.logout());
    }
}());


