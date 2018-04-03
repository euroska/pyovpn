(function () {
    'use strict';


    class UserController {
        constructor($log, $auth, $vpnDict) {
            this.$log = $log;
            this.$auth = $auth;
            this.vpnDict = $vpnDict;
        }

        $onInit() {
            this.reload();
        }

        reload() {
            this.vpnList = []
            for(let vpn of this.vpns) {
                let present = (this.user.username in vpn.users);

                this.vpnList.push({
                    name: vpn.name,
                    running: vpn.running,
                    present: present,
                    username: this.user.username,
                    active: present ? vpn.users[this.user.username].active : false,
                    ip: present ? vpn.users[this.user.username].ip : ''
                })
            }
        }

        update(){
            this.user.$save();
        }

        reset() {
            this.user.$reset();
        }

        password(password) {
            this.user.$setPassword(password)
        };

        renew(name, username) {
            if(window.confirm(`Realy renew ${username} from ${name}?`)) {
                let vpn = this.vpnDict[name];
                vpn.$renew(username).then(() => {
                    this.reload();
                });
            }
        }

        revoke(name, username) {
            if(window.confirm(`Realy revoke ${username} from ${name}?`)) {
                let vpn = this.vpnDict[name];
                vpn.$revoke(username).then(() => {
                    this.reload();
                });
            }
        }

        add(name, username) {
            let vpn = this.vpnDict[name];
            vpn.$add(username).then(() => {
                this.reload();
            });
        }
    }

    angular.module(
        'pyovpn.user', []
    )
    .component('user', {
        templateUrl: '/js/view/user.tpl.html',
        controller: UserController,
    //     controllAs: 'ctrl'
        bindings: {
            user: '=',
            vpns: '='
        }
    });
}());


