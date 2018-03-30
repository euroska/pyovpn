


function loginModalFactory($q) {
    const deferred = $q.defer();

    return {
        element: null,

        open() {
            this.promise.then(el => {
                el.modal('show');
                el[0].addEventListener('click', e => {
                    e.preventDefault();
                    e.stopPropagation();
                }, true);
                el.on('click',);
                console.log('open', el);
            });
        },

        promise: deferred.promise,

        register(el) {
            this.element = el;
            deferred.resolve(el);
        }
    };
}
loginModalFactory.$inject = ['$q'];

class LoginModalCtrl {
    constructor($element, loginModal) {
        angular.extend(this, {
            $element, loginModal
        });
    }
    $postLink() {
        this.modal = angular.element('#loginModal', this.$element);
        if (!this.modal) return;
        this.loginModal.register(this.modal);
    }
}

const loginModalComponent = {
    controller: ['$element', 'loginModal', LoginModalCtrl],
    templateUrl: '/js/common/component/loginModal.tpl.html',
};

angular.module('pyovpn.component.loginModal', [])
    .factory('loginModal', loginModalFactory)
    .component('loginModal', loginModalComponent)
    ;
