
angular.module(
    'pyovpn.login', ['vpn.common.auth']
)
.component('login', {
    templateUrl: '/js/view/login.tpl.html',
    controller: ['$log', '$auth', LoginController],
});

function LoginController($log, $auth) {

    this.submit = () => {
        $auth.login(this.username, this.password);
    };
}
