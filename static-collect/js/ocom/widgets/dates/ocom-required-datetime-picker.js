/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

/*** DEPRECATED IN FAVOR OF DATETIME-PICKER.JS ***/
(function () {
    angular
        .module('app.ocom')
        .directive('ocomRequiredDatetimePicker', ocomRequiredDatetimePicker)
        .directive('ocomRequiredDatePicker', ocomRequiredDatePicker);

    function ocomRequiredDatetimePicker($parse, alerts) {
        return {
            restrict: 'EA',
            templateUrl: "js/ocom/widgets/dates/ocom-required-datetime-picker.html",
            scope: {
                model: '=',
                item: '=',
                placeholder: '@',
                fullRow: '@',
                required: '@',
                title: '@',
                minDate: "@"
            },

            controller: function ($scope) {
                $scope.required = $scope.required === 'true';

                if ($scope.fullRow === "true")
                    $scope.colSize = "6";
                else
                    $scope.colSize = "3";
                $scope.setToday = function () {
                    $scope.model = new Date();
                };

                $scope.clearDate = function () {
                    $scope.model = null;
                };
            }

        };
    }

    function ocomRequiredDatePicker($parse) {
        return {
            restrict: 'EA',
            templateUrl: "js/ocom/widgets/dates/ocom-required-date-picker.html",
            scope: {
                model: '=',
                item: '=',
                placeholder: '@',
                fullRow: '@',
                required: '@',
                title: '@',
                minDate: "@"
            },

            controller: function ($scope) {
                $scope.required = $scope.required === 'true';

                if ($scope.fullRow === "true")
                    $scope.colSize = "6";
                else
                    $scope.colSize = "3";
                $scope.setToday = function () {
                    $scope.model = new Date();
                };

                $scope.clearDate = function () {
                    $scope.model = null;
                };

            }

        };
    }
})();
