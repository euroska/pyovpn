(function () {
    'use strict';

    window.pyovpn = angular.module(

        'pyovpn', [
            'ui.router',
            'pyovpn.login',
            'pyovpn.layout',

            'pyovpn.resource.vpn',
            'pyovpn.resource.user',
            'pyovpn.resource.template.server',
            'pyovpn.resource.template.user',

            'pyovpn.dashboard',
            'pyovpn.vpn',
            'pyovpn.vpnconfig',
            'pyovpn.vpnconfiguser',
            'pyovpn.vpntemplate',
            'pyovpn.vpntemplateuser',
            'pyovpn.vpnlog',
            'pyovpn.vpnlist',
            'pyovpn.user',
            'pyovpn.userlist',
            'pyovpn.templateserverlist',
            'pyovpn.templateserver',
            'pyovpn.templateuserlist',
            'pyovpn.templateuser'
        ]
    ).config(function($compileProvider, $urlRouterProvider, $stateProvider, $websocketProvider) {
'',
        $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|chrome-extension|data):/);

        let loc = window.location, new_uri;
        if (window.location.protocol === "https:") {
            new_uri = "wss:";
        } else {
            new_uri = "ws:";
        }
        new_uri += `//${window.location.host}/api/ws`;

        $websocketProvider.url = new_uri;
        $urlRouterProvider.otherwise('/');

        $websocketProvider.url = 'ws://localhost:8080/api/ws';
        $urlRouterProvider.otherwise('/');

        $stateProvider
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
                    main: 'dashboard'
                }
            })

            .state('pyovpn.userList', {
                url: 'user',
                views: {
                    main: 'userList'
                },
                resolve: {
                    users: $user => $user.list()
                }
            })
            .state('pyovpn.userDetail', {
                url: 'user/:username',
                views: {
                    main: 'user'
                },
                resolve: {
                    user: ($stateParams, $user) => $user.get($stateParams.username),
                    vpns: $vpn => $vpn.list()
                }
            })
            .state('pyovpn.vpnList', {
                url: 'vpn',
                views: {
                    main: 'vpnList'
                },
                resolve: {
                    vpns: $vpn => $vpn.list()
                }
            })
            .state('pyovpn.vpnDetail', {
                url: 'vpn/:name',
                views: {
                    main: 'vpn'
                },
                resolve: {
                    vpn: ($stateParams, $vpn) => $vpn.get($stateParams.name),
                    users: $user => $user.list()
                }
            })
            .state('pyovpn.vpnConfig', {
                url: 'vpnConfig/:name',
                views: {
                    main: 'vpnConfig',
                },
                resolve: {
                    vpn: ($stateParams, $vpn) => $vpn.get($stateParams.name)
                }
            })
            .state('pyovpn.vpnConfigUser', {
                url: 'vpnConfigUser/:name/:username',
                views: {
                    main: 'vpnConfigUser',
                },
                resolve: {
                    vpn: ($stateParams, $vpn) => $vpn.get($stateParams.name)
                }
            })
            .state('pyovpn.vpnTemplate', {
                url: 'vpnTemplate/:name',
                views: {
                    main: 'vpnTemplate',
                },
                resolve: {
                    vpn: ($stateParams, $vpn) => $vpn.get($stateParams.name)
                }
            })
            .state('pyovpn.vpnTemplateUser', {
                url: 'vpnTemplateUser/:name',
                views: {
                    main: 'vpnTemplateUser',
                },
                resolve: {
                    vpn: ($stateParams, $vpn) => $vpn.get($stateParams.name)
                }
            })
            .state('pyovpn.vpnLog', {
                url: 'vpnLog/:name',
                views: {
                    main: 'vpnLog',
                },
                resolve: {
                    vpn: ($stateParams, $vpn) => $vpn.get($stateParams.name)
                }
            })
            .state('pyovpn.templateServerList', {
                url: 'template/server',
                views: {
                    main: 'templateServerList'
                },
                resolve: {
                    templateList: $templateServer => $templateServer.list()
                }
            })
            .state('pyovpn.templateServer', {
                url: 'template/server/:name',
                views: {
                    main: 'templateServer'
                },
                resolve: {
                    name: $stateParams => $stateParams.name,
                    template: ($stateParams, $templateServer) => $templateServer.get($stateParams.name)
                }
            })
            .state('pyovpn.templateUserList', {
                url: 'template/user',
                views: {
                    main: 'templateUserList'
                },
                resolve: {
                    templateList: $templateUser => $templateUser.list()
                }
            })
            .state('pyovpn.templateUser', {
                url: 'template/user/:name',
                views: {
                    main: 'templateUser'
                },
                resolve: {
                    name: $stateParams => $stateParams.name,
                    template: ($stateParams, $templateUser) => $templateUser.get($stateParams.name)
                }
            })
            ;
    })
    .filter('in', function() {
        return function(input, value) {
            return value in input;
        };
    })
}());
