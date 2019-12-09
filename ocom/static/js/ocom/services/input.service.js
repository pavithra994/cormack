/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    // Factories and services affecting html input elements

    angular
        .module('app.ocom')
        .factory('focus', function ($rootScope, $timeout) {
            return function (name) {
                $timeout(function () {
                    console.log('Set focus...');
                    $rootScope.$broadcast('focusOn', name);
                });
            }
        })
})();
