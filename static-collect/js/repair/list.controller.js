/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019 
 *
 */

/***
 * Repair List Controller
 */
(function () {
    'use strict';

    angular
        .module('app.repair')
        .controller('RepairListController', ['$state', '$scope', 'authService', 'dataCacheService',
            'dataService', 'roleService', 'DEFAULT_JOB_LIST_OPTIONS', RepairListController]);

    /* @ngAnnotate */
    function RepairListController($state, $scope, authService, dataCacheService, dataService,
                                  roleService, DEFAULT_JOB_LIST_OPTIONS) {
        var filters = [
            {'id': 'all', 'name': 'All'},
            {'id': 'active', 'name': 'Active'},
            {'id': 'inactive', 'name': 'Inactive'},
            {'id': 'completed', 'name': 'Completed'},
            {'id': 'overdue', 'name': 'Over Due'}
        ];

        var fields = [
            {'id':"job__number", name:"Job Number"},
            {'id':"job__address", name:"Address"},
            {'id':"job__suburb", name:"Suburb"},
            {'id':"description", name:"Description"}
        ];

        var user = authService.getCurrentUser();
        $scope.isAdmin = user.is_staff;
        $scope.modelName = 'repair';
        // set defaults
        if (!angular.isDefined($state.params['sort'])) {
            $state.params['sort'] = 'date_received';
            if (!angular.isDefined($state.params['order'])) {
                $state.params['order'] = 'desc';
            }
        }
        if (!angular.isDefined($state.params['filter'])) {
            $state.params['filter'] = 'active';
        }
        if (!angular.isDefined($state.params['offset'])) {
            $state.params['offset'] = 0;
        }
        if (!angular.isDefined($state.params['limit'])) {
            $state.params['limit'] = 10;
        }

        $scope.listOptions = $state.params;
        $scope.listOptions.fieldList = _.map(fields, 'id');
        $scope.maxRanges = [10, 20, 50, 100];
        $scope.fields = fields;
        $scope.filters = filters;
        $scope.loadList = loadList;

        $scope.clearFilters = function () {
            $scope.listOptions = angular.copy(DEFAULT_JOB_LIST_OPTIONS);
            $scope.refreshList();
        };
        $scope.setUpdate = function (item, key) {
            item.is_update[key] = true;
        };

        $scope.setUpdateCancel = function (item, key) {
            item.is_update[key] = false
        };

        $scope.setAllUpdate = function (form_item, form_key) {
                angular.forEach($scope.list, function (items) {
                angular.forEach(items, function (item, key) {
                    if (form_item != items || key != form_key) {
                        if(items.is_update[key]){
                            $scope.patchItem(items , key)
                        }
                    }
                })
            })

        };
        $scope.patchItem = function (item, key) {
            var entry = {
                id: item.id
            };

            entry[key] = angular.isDefined(item[key]) ? item[key] : "";
            dataService.getApi('repair').patchItem(entry, function () {

                item.is_update[key] = false
            });
        };

        loadList();

        function loadList() {
            /*
            dataCacheService.getCache('business_unit', 'query', {}, true).then(function (response) {
                angular.forEach(response, function (item) {
                    $scope.filters.push(
                        {'id': 'business_unit:' + item.id, 'name': "Business Unit: " + item.name}
                    );
                });
            });
            */
            dataService
                .getApi('repair')
                .list($scope.listOptions, function (data) {
                    $scope.list = data.results;
                    $scope.accessible = roleService.isAccessible;
                    $scope.listOptions.total = data.count;
                    $scope.listOptions.currentPage = Math.ceil($scope.listOptions.offset / $scope.listOptions.limit) + 1;
                    angular.forEach($scope.list, function (value, key) {
                        value.is_update = {}
                    })
                });
        }
        var updateAdmin = function () {
            $scope.isAdmin = roleService.userHasThisRole('administrator');
        };

        roleService.subscribeAccessUpdate($scope, updateAdmin);
    }
})();
