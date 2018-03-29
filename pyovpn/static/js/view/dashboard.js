
angular.module(
    'pyovpn.dashboard', []
)
.component('dashboard', {
    templateUrl: '/js/view/dashboard.tpl.html',
    controller: DashboardController
});

function DashboardController($log) {
    'ngInject';
}

