/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    'use strict';

    angular.module('app.group_permissions')
        .controller('GroupPermissionsListController', ['$state', '$scope', '$filter', 'CodeTableCacheService', 'dataAPIService', 'platform', 'formStateService', 'permissionService',
    function ($state, $scope, $filter, CodeTableCacheService, dataAPIService, platform, formStateService, permissionService) {
        $scope.platform = platform;
        $scope.modelName = 'group_permissions';
        $scope.listOptions = {
            'total': 0,
            'currentPage': 1,
            'filter': $state.params.filter || "",
            // TODO: Change default sort column field if necessary
            'sort': $state.params.sort || "id",
            'order': $state.params.order || "asc",
            'q': $state.params.q || "",
            'query': {},
            'searchField': $state.params.searchField || "",
            'ordering': $state.params.ordering || "",
            'limit': $state.params.limit || 20,
            'offset': $state.params.offset || 0
        };
        $scope.maxRanges = [10, 20, 50, 100];
        $scope.formState = formStateService.formState;
        $scope.fields =  [ // TODO Check These are right..
           {'id':"group__state_name", 'code':"group__state_name", 'name': "Group"},
         {'id':"states", 'code':"states", 'name': "States"},
                            ];

        $scope.filters = [ //TODO Set these up
            {'id': 'all', 'name': 'All'}
        ];

        $scope.loadList = function() {
            $scope.list = [];

            function addToQuery(field) {
                if (angular.isDefined(field.operation)) {
                    if (['eq', 'lt', 'gt', 'ge', 'le'].indexOf(field.operation) > -1) {
                        // param must be a number
                        if (isNaN(+$scope.listOptions.q)) {
                            return;
                        }
                    }
                }
                $scope.listOptions.query.criteria.push({
                    "operation": (field.code === field.id) ? "icontains" : field.operation,
                    "name": field.code,
                    "params": [$scope.listOptions.q]
                });
            }

            formStateService.setFormState({'loading': true});
            if ($scope.listOptions.q) {
                $scope.listOptions.query = {"logic":"or", "criteria":[]};
                angular.forEach($scope.fields, function (field) {
                    if ($scope.listOptions.searchField) {
                        if ($scope.listOptions.searchField === field.code ||
                            $scope.listOptions.searchField === field.id) {

                            addToQuery(field);
                        }
                    } else {
                        addToQuery(field);
                    }
                });
                console.log("Query parameters:", $scope.listOptions.query);
            } else {
                $scope.listOptions.query = {};
            }

            dataAPIService
                .getDataApi("/api/", $scope.modelName)
                .list($scope.listOptions, function (data) {
                    $scope.list = data.results;
                    $scope.listOptions.total = data.count;
                    $scope.listOptions.currentPage = Math.ceil($scope.listOptions.offset / $scope.listOptions.limit) + 1;
                    // set is_active for fields (should work offline)
                    var resultsWithKey = _.transform(data.results, function(result, value, key) {
                        value.key = key;
                        result[key] = value;
                    }, []);
                    var activeFields = $filter("activeOnly")(resultsWithKey);

                    angular.forEach(activeFields, function (item) {
                        $scope.list[item.key].is_active = true;
                    });

                    formStateService.setFormState({'loading': false});
                }, function(err) {
                    console.error("Failed to retrieve data", err);
                    formStateService.setFormState({'loading': false});
                });
        };

        $scope.loadOptions = function() {
            var loadTables = [
                // TODO: Make sure we only get the same Name ONCE..
                {
                    name: 'group_list',
                    uri : '/api/',
                    scope: 'group_List',
                    keyBy: 'id'
                },
            ];

            $scope.options = {};
            if (!_.isEmpty(loadTables)) {
                CodeTableCacheService.processLoadTables(loadTables, $scope.options);
            }
        };

        $scope.loadList();
        $scope.loadOptions();

        $scope.clearFilters = function () {
            $scope.listOptions = {
                    'total': 0,
                    'currentPage': 1,
                    'filter': "",
                    // TODO: Change default sort column field if necessary
                    'sort': "id",
                    'order': "asc",
                    'q': "",
                    'query': {},
                    'searchField': "",
                    'ordering': "",
                    'limit': 20,
                    'offset': 0
            };
            $scope.refreshList();
        };

        $scope.hideNewButton = function () {
            return !permissionService.can_goto_state_by_name('group_permissions.create') || platform.isTablet();
        }
    }]);
})();
