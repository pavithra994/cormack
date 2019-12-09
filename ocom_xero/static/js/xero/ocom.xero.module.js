/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    var global_xero_items = null;

    angular
        .module('ocom.xero', [])

        .directive("xeroSelectItem", ['$http', '$sessionStorage', '$q', function($http, $sessionStorage, $q) {
            return {
                restrict: 'A',
                require: 'ngModel',
                scope: {
                    ngModel: '=',
                    onChange: "&",
                    ngDisabled: "="
                },
                templateUrl: "js/xero/xero.select.item.html",
                link: function (scope, elem, attrs, ngModel) {
                    function updateTheValue () {
                        if (ngModel.$modelValue) {
                            scope.value = _.find(scope.items, {'Code': ngModel.$modelValue});
                        }
                    }

                    scope.reload = function (force) {
                        scope.items_loaded = false;

                        if (!force) {
                            if (global_xero_items) {
                                scope.items_loaded = true;
                                scope.items = global_xero_items;

                                return
                            }

                        }

                        if ($sessionStorage.xero_items_loaded && !force) {
                            scope.items_loaded = true;
                            scope.items = $sessionStorage.xero_items;

                            global_xero_items = scope.items;

                            updateTheValue();
                        }
                        else {
                            $sessionStorage.xero_items_loaded = false;
                            $sessionStorage.xero_items = [];

                            $http.get("/xero/items", {params:{"force":force}}).then(function (items) {
                                scope.items_loaded = true;
                                scope.items = items.data;

                                $sessionStorage.xero_items_loaded = true;
                                $sessionStorage.xero_items = items.data;

                                global_xero_items = items.data; // Store in global for next SELECT

                                updateTheValue();
                            });
                        }
                    };

                    scope.get_data = function ($select) {
                        var deferred = $q.defer();

                        var searchString = ($select.search || "").trim().toUpperCase();

                        scope.searchResults = _.filter(scope.items, function (item) {
                            var fullText = _.join([item.Description, item.codeName, item.Code, item.Name], "").toUpperCase();

                            return fullText.indexOf(searchString) > 0;
                        });

                        deferred.resolve(scope.searchResults);

                        return deferred.promise;
                    };

                    scope.reload(false); // Use $sessionStorage if it's already there

                    scope.selectChanged = function (value) {
                        // scope.$apply(function() {
                        if (angular.isDefined(value)) {
                            ngModel.$setViewValue(value.Code);
                            //scope.value = _.find(scope.items, {'Code': ngModel.$modelValue});
                            if (scope.onChange) {
                                scope.onChange({item: value}); // Notify
                            }
                        }
                        updateTheValue();
                    };

                    ngModel.$render = function() {
                        updateTheValue();
                    };
                }
            }
        }]);
})();
