var pyovpn = angular.module(

    'pyovpn', [
        'ui.router',
        'pyovpn.login',
        'pyovpn.layout',

        'pyovpn.resource.vpn',
        'pyovpn.resource.user',

        'pyovpn.dashboard',
        'pyovpn.vpnlist',
        'pyovpn.userlist'
    ]

).config(function($urlRouterProvider, $stateProvider) {
    'ngInject';

    $urlRouterProvider.otherwise('/');

    $stateProvider.state('login', {
        url: '/login',
        component: 'login'
    })
    .state('pyovpn', {
        abstract: true,
        component: 'layout',
        url: '/',
        resolve: {
            logged: function($auth) {
                return $auth.loginRedirect();
            }
        }
    })
    .state('pyovpn.dashboard', {
        url: '',
        views: {
            'main': 'dashboard'
        }
    })
    .state('pyovpn.user', {
        url: 'user',
        views: {
            'main': 'userList'
        },
        resolve: {
            'userList': $user => $user.list()
        }
    })
    .state('pyovpn.user.detail', {
        url: ':username',
        views: {
            'main': 'dashboard'
        }
    })
    .state('pyovpn.vpn', {
        url: 'vpn',
        views: {
            'main': 'vpnList'
        },
        resolve: {
            'vpnList': $vpn => $vpn.list()
        }
    })
    .state('pyovpn.vpn.detail', {
        url: ':name',
        views: {
            'main': 'dashboard'
        }
    })
    ;
});
