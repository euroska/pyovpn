
angular.module(
    'pyovpn.login', ['vpn.common.auth']
)
.component('login', {
    templateUrl: '/js/view/login.tpl.html',
    controller: LoginController
//     controllAs: 'ctrl'
});

function LoginController($log, $auth, $state) {
    'ngInject';

    this.submit = () => {
        $auth.login(this.username, this.password).then(logged => {

            if(logged)
                $state.go('pyovpn.dashboard');
        })
    };
}
