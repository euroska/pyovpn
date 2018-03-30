var pyovpn = angular.module(

    'pyovpn', [
        'ui.router',
        'pyovpn.logout',
        'pyovpn.login',
        'pyovpn.layout',

        'pyovpn.resource.vpn',
        'pyovpn.resource.user',
        'pyovpn.resource.template.server',
        'pyovpn.resource.template.user',

        'pyovpn.dashboard',
        'pyovpn.vpn',
        'pyovpn.vpnlist',
        'pyovpn.user',
        'pyovpn.userlist',
        'pyovpn.templateserverlist',
        'pyovpn.templateuserlist'
    ]

).config(function($urlRouterProvider, $stateProvider, $websocketProvider) {
    'ngInject';

    let loc = window.location, new_uri;
    if (window.location.protocol === "https:") {
        new_uri = "wss:";
    } else {
        new_uri = "ws:";
    }
    new_uri += `//${window.location.host}/api/ws`;

    $websocketProvider.url = new_uri;
    $urlRouterProvider.otherwise('/');

    $stateProvider.state('login', {
        url: '/login',
        component: 'login'
    })
    .state('logout', {
        url: '/logout',
        component: 'logout'
    })
    .state('pyovpn', {
        abstract: true,
        component: 'layout',
        url: '/',
        resolve: {
            logged: $auth => $auth.loginPromise()
        }
    })
    .state('pyovpn.dashboard', {
        url: '',
        views: {
            'main': 'dashboard'
        }
    })

    .state('pyovpn.userList', {
        url: 'user',
        views: {
            'main': 'userList'
        },
        resolve: {
            'userList': $user => $user.list()
        }
    })
    .state('pyovpn.userDetail', {
        url: 'user/:username',
        views: {
            'main': 'user'
        },
        resolve: {
            'user': ($stateParams, $user) => $user.get($stateParams.username)
        }
    })
    .state('pyovpn.vpnList', {
        url: 'vpn',
        views: {
            'main': 'vpnList'
        },
        resolve: {
            'vpnList': $vpn => $vpn.list()
        }
    })
    .state('pyovpn.vpnDetail', {
        url: 'vpn/:name',
        views: {
            'main': 'vpn'
        },
        resolve: {
            'vpn': ($stateParams, $vpn) => $vpn.get($stateParams.name)
        }
    })
    .state('pyovpn.template', {
        url: 'template',
        views: {
            'main': 'dashboard'
        }
    })
    .state('pyovpn.template.server', {
        url: '/server',
        views: {
            'main': 'templateServerList'
        },
        resolve: {
            'temlateList': $templateServer => $templateServer.list()
        }
    })
    .state('pyovpn.template.server.detail', {
        url: '/:name',
        views: {
            'main': 'templateServerList'
        }
    })
    .state('pyovpn.template.user', {
        url: '/user',
        views: {
            'main': 'templateUserList'
        },
        resolve: {
            'temlateList': $templateUser => $templateUser.list()
        }
    })
    .state('pyovpn.template.user.detail', {
        url: '/:name',
        views: {
            'main': 'dashboard'
        }
    })
    ;
});
