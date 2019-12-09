/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    /*
     * usage:
     * <input class="form-control" id="supervisor" ng-model="item.supervisor" name="supervisor"
     *        catch-server-errors="supervisor" errors="item._errors" />
        <div ng-messages="form.description.$error" role="alert" ng-show="form.supervisor.$touched">
            <p class="error margin-top-5px" ng-message="serverError">
                <div ng-model="item.supervisor" show-server-errors="supervisor" errors="item._errors"></div>
            </p>
        </div>

        show-server-errors: will show the Errors return from the Django API

        catch-server-errors: Will make the input invalid if there is an error from the Django API

        NOTE: item._errors is the data returned from the Django Rest api. ocom-form-buttons sets this when there is an error
     */
    angular
        .module('app.ocom')
        .directive('showErrors', showErrors)
        .directive('showServerErrors', function () {
            return {
                restrict: 'A',
                replace: false,
                scope: {
                    showServerErrors:"@",
                    errors: "="
                },
                template: "<span class=\"error\" ng-repeat=\"msg in errorsToShow\">{{msg}}<br></span>",
                link:function(scope, element, attrs) {
                    var listener = null;

                    function cancelWatch() {
                        if (listener)
                            listener(); // Cancel previous Watch
                    }

                    function newWatch (scopeWatch) {
                        cancelWatch();

                        listener = scope.$watch (scopeWatch, function (newValue, oldValue) {
                            if (newValue) {
                                alert ("We got an error!");
                            }

                            scope.errorsToShow = newValue;
                        });
                    }
                    scope.$watch('errors', function (newErrors) {
                        if (scope.showServerErrors)
                            newWatch("errors." + scope.showServerErrors);
                        else {
                            cancelWatch()
                        }
                    });

                    scope.$watch('showServerErrors', function(scope_path){
                        if(scope_path) {
                            newWatch("errors." + scope.showServerErrors);
                        }
                        else {
                            cancelWatch()
                        }
                    });
                },
                controller: ['$scope', function ($scope) {

                }]
            };
        })
        .directive('catchServerErrors', function () {
            return {
                restrict: 'AE',
                replace: false,
                require: "ngModel",
                scope: {
                    catchServerErrors: "@",
                    errors: "="
                },
                link: function(scope, element, attrs, ngModelController) {
                    var listener = null;

                    // replace blank catchServerErrors with name attribute is present
                    if (!scope.catchServerErrors && attrs.name) {
                        scope.catchServerErrors = attrs.name;
                    }

                    scope.$watch('catchServerErrors', function(scope_path) {
                        if (scope_path) {
                            var scopeWatch = "errors." + scope_path;

                            if (listener) {
                                listener(); // Cancel previous Watch
                            }

                            listener = scope.$watch (scopeWatch, function (newValue, oldValue) {
                                if (newValue) {
                                    ngModelController.$setValidity("serverError", false);
                                }
                                else {
                                    ngModelController.$setValidity("serverError", true);
                                }
                            });
                        }
                    });

                    ngModelController.$viewChangeListeners.push(
                        function handleNgModelChange() {
                            ngModelController.$setValidity("serverError", true); //reset to OK
                        }
                    );
                }
            };
        });


    function showErrors() {
        return {
            restrict: 'A',
            replace: false,
            scope: {
                showErrors: "@",
                item: "="
            },
            template: "<span class=\"help-block text-error\" ng-repeat=\"msg in item._errors[showErrors]\">{{msg}}<br /></span>"

        };
    }
})();
