/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    angular
        .module('app.ocom', [
            /*
             * Angular modules
             */
            'ngSanitize', 'ngResource', 'ui.router', 'ngStorage', 'ngMessages',

            'ngdexie', 'ngdexie.ui',
            /*
             * Our reusable cross app code modules
             */
            'app.ocom.auth',

            /*
             * 3rd Party modules
             */
            'ui.bootstrap',
            'ui.bootstrap.tpls',
            'mgcrea.ngStrap',
            'angular-growl',
            'angular.filter',
            'oitozero.ngSweetAlert',
            'angular-loading-bar',
            'angularMoment',
            'ngFileUpload',
            'mgcrea.ngStrap.timepicker',
            'mgcrea.ngStrap.datepicker',
        ]);
})();
