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
        .directive('sortable', sortable)
        .directive('ordering', function() {
            /*
             * This directive will use the Django Rest's OrderingFilter
             */
            var asc = "asc", desc = "desc";
            var sortField = "";

            /* parse the Django ordering field
             * Find the Fieldname and the order.
             *
             * Update Scope as required.
             */
            function parseOrdering(value, scope) {
                var result = {order_asc:true, sort:value};

                if (value) {
                    if (value.startsWith("-")) {
                        result.order_asc = false;
                        result.sort = value.substr(1);
                    }
                }

                scope.currentAsc = (result.sort === scope.fieldToOrderBy && result.order_asc);
                scope.currentDesc = (result.sort === scope.fieldToOrderBy && !result.order_asc);

                scope.ordering = result;
            }

            return {
                restrict: 'AE',
                replace: false,
                scope: {
                    listOptions: '=ngModel', /* The listOptions to change/update */
                    changed: '&changed', /* Called when changed */
                },
                transclude: true,
                templateUrl: 'js/ocom/widgets/lists/ordering.directive.html',
                link: function (scope, elem, attrs) {
                    if (scope.listOptions) {
                        currentOrderingField = scope.listOptions.ordering;
                    }

                    scope.fieldToOrderBy = attrs.ordering;

                    scope.ordering = null; // init

                    if (scope.fieldToOrderBy !== '') {
                        if (angular.isDefined(scope.listOptions)) {
                            parseOrdering(scope.listOptions.ordering, scope);
                        }

                        elem.bind('click', function () {
                            scope.$apply(function () {
                                if (scope.ordering && scope.ordering.sort === scope.fieldToOrderBy) {
                                    if (scope.ordering.order_asc) {
                                        scope.listOptions.ordering = "-" + scope.fieldToOrderBy; // Sort by this field Desc.
                                    }
                                    else {
                                        scope.listOptions.ordering = scope.fieldToOrderBy; // Sort by this field ASC
                                    }
                                }
                                else {
                                    scope.listOptions.ordering = scope.fieldToOrderBy; // Sort by this field ASC
                                }

                                scope.changed();
                            });
                        });
                    }
                },
                controller: function ($scope, $location) {
                    $scope.location = $location.path();
                    $scope.$watch('listOptions', function (value) {
                        if (value && value.ordering) {
                            parseOrdering(value.ordering, $scope);
                        }
                    });
                }
            };
    });

    function sortable() {
        var asc = "asc", desc = "desc";
        var sortField = "";

        return {
            restrict: 'AE',
            replace: false,
            scope: {
                listOptions: '=ngModel',
                changed: '&changed',
                sortIf: '=',
                item: '='
            },
            transclude: true,
            // require: '^ngModel',
            templateUrl: 'js/ocom/widgets/lists/sortable.directive.html',
            link: function (scope, elem, attrs) {
                if (scope.listOptions) {
                    sortField = scope.listOptions.sort;
                }
                if (angular.isUndefined(scope.sortIf)) {
                    scope.allowSort = true;
                } else {
                    scope.allowSort = scope.sortIf;
                }
                if (angular.isUndefined(scope.item) || !scope.item) {
                    scope.attrSortField = attrs.sortable;
                } else {
                    scope.attrSortField = scope.item.sortable ? scope.item.sortable : attrs.sortable;
                }
                if (scope.attrSortField !== '') {
                    if (angular.isDefined(scope.listOptions)) {
                        scope.currentAsc = (sortField === scope.attrSortField && scope.listOptions.order === asc);
                        scope.currentDesc = (sortField === scope.attrSortField && scope.listOptions.order === desc);
                    }
                    if (scope.allowSort) {
                        elem.bind('click', function () {
                            scope.$apply(function () {
                                if (scope.listOptions.sort === scope.attrSortField) {
                                    scope.listOptions.order = (scope.listOptions.order === asc) ? desc: asc;
                                }
                                else {
                                    scope.listOptions.sort = scope.attrSortField;
                                    scope.listOptions.order = asc;
                                }
                            });
                            scope.changed();
                        });
                    }
                }
            },
            controller: function ($scope, $location) {
                $scope.location = $location.path();
                $scope.$watch('listOptions', function (value) {
                    if (value && value.sort === $scope.attrSortField) {
                        $scope.currentAsc = (value.order === asc);
                        $scope.currentDesc = (value.order === desc);
                    }
                });
            }
        };
    }
})();
