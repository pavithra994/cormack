/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    angular
        .module('app.ocom')
        .directive('ocomTimePicker', ocomTimePicker)
        .directive('ocomDatetimePicker', ocomDatetimePicker)
        .directive('ocomDatePicker', ocomDatePicker)
        .directive('ocomMonthPicker', ocomMonthPicker)
        .directive('ocomTableDatePicker', ocomTableDatePicker);

    function momentDate (date) {
        return moment(date).format("YYYY-MM-DD");
    }

    function clearValidation (scope, value) {
        if (scope.name && scope.form) {
            if (!angular.isDefined(scope.form[scope.name])) {
                scope.form[scope.name] = {$error: []};
            }
            scope.form[scope.name].$setDirty();
            if (scope.required) {
                if (angular.isUndefined(value) || value === null) {
                    scope.form[scope.name].$setValidity('required', false);
                } else {
                    scope.form[scope.name].$setValidity('required', true);
                }
            } else {
                if (value === null) {
                    scope.form[scope.name].$setValidity('max', true);
                    scope.form[scope.name].$setValidity('min', true);
                }
            }
        }
    }

    function setDate (scope, value) {
        if (angular.isDefined(scope.datepicker)) {
            scope.datepicker.setMode(0);
            scope.datepicker.select(value);
            if (angular.isDefined(scope.timepicker)) {
                scope.form[scope.name + '-time'].$setDirty();
                scope.model = value;
            }
        } else {
            scope.model = value;
            if (angular.isDefined(scope.form)) {
                scope.form.$setDirty();
            }
        }
        clearValidation(scope, value);
    }

    function formatDate(date) {
        var d = new Date(date),
            month = '' + (d.getMonth() + 1),
            day = '' + d.getDate(),
            year = d.getFullYear();
    
        if (month.length < 2) 
            month = '0' + month;
        if (day.length < 2) 
            day = '0' + day;
    
        return [year, month, day].join('-');
    }


    function ocomDatetimePicker ($datepicker, $timepicker) {
        return {
            restrict: 'EA',
            templateUrl: "js/ocom/widgets/dates/ocom-datetime-picker.html",
            scope: {
                form: '=',
                model: '=',
                // Optional: Only used in shifts - for determining if the widget should be disabled.
                item: '=',
                name: '@',
                required: '=',
                readOnly: '=',
                disabled: '=',
                placeholder: '@',
                fullRow: '@',
                minDate: '@',
                maxDate: '@',
                hideTime: '=?'
            },
            link: function (scope, element) {
                if (scope.name && scope.form) {
                    scope.datepicker = $datepicker(element, scope.form[scope.name], {});
                    scope.timepicker = $timepicker(element, scope.form[scope.name], {});
                }
            },
            controller: function ($scope) {
                $scope.hideTime = $scope.hideTime || false;

                $scope.colSize = ($scope.fullRow === "true") ? "6" : "3";

                $scope.setToday = function () {
                    setDate($scope, new Date());
                };

                $scope.clearDate = function () {
                    setDate($scope, null);
                };

                $scope.onPickerBlur = function () {
                    if(formatDate($scope.model)=="1970-01-01"){
                        $scope.model = new Date();
                    }
                    clearValidation($scope, $scope.model);
                };
            }

        };
    }

    function ocomTimePicker ($datepicker, $timepicker) {
        return {
            restrict: 'EA',
            templateUrl: "js/ocom/widgets/dates/ocom-time-picker.html",
            scope: {
                form: '=',
                model: '=',
                // Optional: Only used in shifts - for determining if the widget should be disabled.
                item: '=',
                name: '@',
                required: '=',
                readOnly: '=',
                disabled: '=',
                placeholder: '@',
                fullRow: '@',
                minDate: '@',
                maxDate: '@'
            },
            link: function (scope, element) {
                if (scope.name && scope.form) {
                    scope.datepicker = $datepicker(element, scope.form[scope.name], {});
                    scope.timepicker = $timepicker(element, scope.form[scope.name], {});
                }
            },
            controller: function ($scope) {
                $scope.colSize = ($scope.fullRow === "true") ? "6" : "3";

                $scope.setToday = function () {
                    setDate($scope, new Date());
                };

                $scope.clearDate = function () {
                    setDate($scope, null);
                };

                $scope.onPickerBlur = function () {
                    clearValidation($scope, $scope.model);
                };
            }

        };
    }

    function ocomDatePicker($datepicker) {
        return {
            restrict: 'EA',
            require: '^form',
            templateUrl: "js/ocom/widgets/dates/ocom-date-picker.html",
            scope: {
                form: '=',
                model: '=',
                // Optional: Only used in shifts - for determining if the widget should be disabled.
                item: '=',
                name: '@',
                required: '=',
                readOnly: '=',
                disabled: '=',
                hasTime: '@',
                placeholder: '@',
                fullRow: '@',
                minDate: '@',
                maxDate: '@',
                dateType: '@',
                modelDateFormat: '@'
            },
            link: function (scope, element) {
                if (scope.name && scope.form) {
                    scope.datepicker = $datepicker(element, scope.form[scope.name], {});
                }
            },
            controller: function ($scope) {
                $scope.colSize = ($scope.fullRow === "true") ? "6" : "3";
                if ($scope.model && $scope.hasTime !== "true") {
                    $scope.model = new Date($scope.model);
                }

                $scope.setToday = function () {
                    var value = new Date();

                    setDate($scope, value);
                };

                $scope.clearDate = function () {
                    setDate($scope, null);
                };

                $scope.dateChanged = function () {
                    
                    if ($scope.model && $scope.hasTime !== "true") {
                        $scope.model = momentDate($scope.model);
                    }
                };

                $scope.onPickerBlur = function () {
                    
                    clearValidation($scope, $scope.model);
                };
            }

        };
    }

    function ocomTableDatePicker($datepicker) {
        return {
            restrict: 'EA',
            require: '^form',
            templateUrl: "js/ocom/widgets/dates/ocom-date-picker.html",
            scope: {
                form: '=',
                model: '=',
                // Optional: Only used in shifts - for determining if the widget should be disabled.
                item: '=',
                name: '@',
                required: '=',
                readOnly: '=',
                disabled: '=',
                hasTime: '@',
                placeholder: '@',
                fullRow: '@',
                minDate: '@',
                maxDate: '@',
                dateType: '@',
                modelDateFormat: '@'
            },
            link: function (scope, element) {
                if (scope.name && scope.form) {
                    scope.datepicker = $datepicker(element, scope.form[scope.name], {});
                    scope.element = element
                }
            },
            controller: function ($scope, $timeout) {
                $scope.colSize = ($scope.fullRow === "true") ? "6" : "3";
                if ($scope.model && $scope.hasTime !== "true") {
                    $scope.model = new Date($scope.model);
                }

                $scope.setToday = function () {
                    var value = new Date();

                    setDate($scope, value);
                    
                };

                $scope.clearDate = function () {
                    setDate($scope, null);
                };

                $scope.dateChanged = function () {
                   
                    if ($scope.model && $scope.hasTime !== "true") {
                        if(formatDate($scope.model)=="1970-01-01"){
                            $scope.model = new Date();
                        }
                        $scope.model = momentDate($scope.model);
                    }
                };

                $scope.onPickerBlur = function (event) {
                    clearValidation($scope, $scope.model);
                    $timeout(function() {
                        angular.element($scope.element).parents("form").find('button[type="submit"]').click()
                    });
                };
            }

        };
    }

    function ocomMonthPicker($datepicker) {
        return {
            restrict: 'EA',
            templateUrl: "js/ocom/widgets/dates/ocom-month-picker.html",
            scope: {
                form: '=',
                model: '=',
                item: '=',
                name: '@',
                required: '=',
                readOnly: '=',
                disabled: '=',
                placeholder: '@',
                fullRow: '@',
                minDate: '@',
                maxDate: '@'
            },
            link: function (scope, element) {
                if (scope.name && scope.form) {
                    scope.datepicker = $datepicker(element, scope.form[scope.name], {});
                }
            },
            controller: function ($scope) {
                $scope.colSize = ($scope.fullRow === "true") ? "6" : "3";

                if ($scope.model) {
                    $scope.model = new Date($scope.model);
                }

                $scope.setToday = function () {
                    //setDate($scope, momentDate(new Date().setDate(1)));
                    setDate($scope, new Date());
                };

                $scope.clearDate = function () {
                    setDate($scope, null);
                };

                $scope.dateChanged = function () {
                    if ($scope.model) {
                        $scope.model = momentDate($scope.model);
                    }
                };

                $scope.onPickerBlur = function () {
                    clearValidation($scope, $scope.model);
                };
            }
        };
    }
})();
