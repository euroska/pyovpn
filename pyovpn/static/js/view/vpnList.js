
angular.module(
    'pyovpn.vpnlist', []
)
.component('vpnList', {
    templateUrl: '/js/view/vpnList.tpl.html',
    controller: VpnListController,
//     controllAs: 'ctrl'
    bindings: {
        vpnList: '='
    }
});

function VpnListController($log, $auth) {
    'ngInject';
}
