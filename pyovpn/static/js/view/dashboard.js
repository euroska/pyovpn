(function () {
    'use strict';

    const dashboardComponent = {
        templateUrl: '/js/view/dashboard.tpl.html',
        controller: DashboardController
    };

    angular
        .module('pyovpn.dashboard', [])
        .component('dashboard', dashboardComponent);

    function DashboardController($log) {

    }

}());

