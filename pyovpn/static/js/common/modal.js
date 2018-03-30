/**
 * Modified angularjs-bootstrap4-modal (https://github.com/rguruprakash/angularjs-bootstrap4-modal)
 */

(function() {

    function modalService($compile, $q, $controller, $rootScope, $templateRequest, $templateCache, ) {
        let el;
        let modalDeferred;

        function getTemplate(tmplUrl) {
            const deferred = $q.defer();
            const template = $templateCache.get(tmplUrl);
            const success = res => deferred.resolve(res);
            const error = err => deferred.reject(err);

            if (template) success(template);
            else $templateRequest(tmplUrl).then(success, error);
            return deferred.promise;
        }

        /**
         * Opens bootstarp modal with templateUrl, controller and modalData.
         *
         * @param {string} tmplUrl - template Url.
         * @param {string} controllerName - controller to bind to modal.
         * @param {*} [modalData] - this additional data will get injected as $scope.modalData.
         *
         * @return {object} promise which will be resolved or rejected while closing the modal.
         */
        function show(tmplUrl, controllerName, modalData) {
            hide();
            el = undefined;
            modalDeferred = $q.defer();

            getTemplate(tmplUrl).then(template => {
                const $scope = $rootScope.$new();
                if (modalData) $scope.modalData = modalData;

                const ctrl = $controller(controllerName, { $scope });
                const compiledData = $compile(template)($scope);
                compiledData.controller = ctrl;

                el = $(compiledData);
                el.appendTo('body');
                el.modal('show');
            }).catch(err => modalDeferred.reject(err));

            return modalDeferred.promise;
        }

        function close() {
            const deferred = $q.defer();

            el.modal('hide');
            el.on('hidden.bs.modal', e => {
                el.remove();
                deferred.resolve();
            });

            return deferred.promise;
        }

        /**
         * Closes the modal and resolves the modal promise with given data.
         *
         * @param {*} data
         */
        function hide(data) {
            if(el && modalDeferred) close().then(() =>modalDeferred.resolve(data));
        }

        /**
         * Closes the modal and rejects the modal promise with given data.
         *
         * @param {*} data
         */
        function cancel(data) {
            if (el && modalDeferred)
                close().then(() => modalDeferred.reject(data));
        }

        return {
            show,
            hide,
            cancel,
        };
    }

    modalService.$inject = [
      '$compile',
      '$q',
      '$controller',
      '$rootScope',
      '$templateRequest',
      '$templateCache',
    ];


    angular
      .module('pyovpn.service.modal', [])
      .service('$modal', modalService);
}());
