(function () {
    'use strict';


    class VpnController {
        constructor($log, $auth) {
            this.$log = $log;
            this.$auth = $auth;
            this.edit = false;
        }

        $onInit() {
            this.reload();
        }

        save() {
            this.vpn.$save().then(() => {
                this.edit = false;
            });
        }

        autostart() {
            this.vpn.autostart = !this.vpn.autostart;
            this.vpn.$save();
        }

        reload() {
            this.userList = []
            for(let user of this.users) {
                let present = (user.username in this.vpn.users);

                this.userList.push({
                    present: present,
                    username: user.username,
                    active: present ? this.vpn.users[user.username].active : false,
                    ip: present ? this.vpn.users[user.username].ip : ''
                })
            }
        }

        renew(username) {
            if(window.confirm(`Realy renew ${username}?`)) {
                this.vpn.$renew(username).then(() => {
                    this.reload();
                })
            }
        }

        revoke(username) {
            if(window.confirm(`Realy revoke ${username}?`)) {
                this.vpn.$revoke(username).then(() => {
                    this.reload();
                })
            }
        }

        add(username) {
            this.vpn.$add(username).then(() => {
                this.reload();
            })
        }
    }

    angular.module(
        'pyovpn.vpn', []
    )
    .component('vpn', {
        templateUrl: '/js/view/vpn.tpl.html',
        controller: VpnController,
    //     controllAs: 'ctrl'
        bindings: {
            vpn: '=',
            users: '='
        }
    });
}());


