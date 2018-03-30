
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

function VpnListController($log, $auth, $vpn) {
    'ngInject';

    this.new_vpn = {
        autostart: false,
        subject: {
            o: 'Test',
            ou: 'Test'
        }
    };

    this.add = () => {
        $vpn.add(this.new_vpn);
    };
}
