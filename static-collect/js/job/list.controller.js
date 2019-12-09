/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019 
 *
 */

/***
 * Job List Controller
 */
(function () {
    'use strict';

    angular
        .module('app.job')
        .controller('JobListController', ['$state', '$scope', 'authService', 'dataCacheService',
            'dataAPIService', 'roleService', 'stateStorage', 'DEFAULT_JOB_LIST_OPTIONS', 'CodeTableCacheService',
            JobListController]);

    /* @ngAnnotate */
    function JobListController($state, $scope, authService, dataCacheService, dataAPIService,
                                  roleService, stateStorage, DEFAULT_JOB_LIST_OPTIONS, CodeTableCacheService) {
        var fields = [
            {'id':"code", name:"Job No."},
            {'id':"client__name", name:"Client Name"},
            {'id':"job_type__description", name:"Job Type"},
            {'id':"address", name:"Address"},
            {'id':"description", name:"Description"},
            {'id':"suburb", name:"Suburb"}
        ];

        $scope.modelName = 'job';
        // set defaults
        if (!angular.isDefined($state.params['sort'])) {
            $state.params['sort'] = 'date_received';
            if (!angular.isDefined($state.params['order'])) {
                $state.params['order'] = 'desc';
            }
        }
        if (!angular.isDefined($state.params['call_up_reset'])) {
            $state.params['call_up_reset'] = "0";
        }
        if (!angular.isDefined($state.params['filter'])) {
            $state.params['filter'] = 'active';

            if (roleService.userHasThisRole('employee')) {
                $state.params['filter'] = 'called_up';
            }
            // Pour Date for Supervisor and Client Manager
            if (roleService.userHasThisRole('supervisor') ||  roleService.userHasThisRole('client_manager')) {
                $state.params['ordering'] = 'pour_date';
                $state.params['sort'] = 'pour_date';
                $state.params['order'] = 'asc';
            }

            // Sort by Call Up (DESC) for Employee
            if (roleService.userHasThisRole('employee')) {
                $state.params['ordering'] = 'call_up_date';
                $state.params['sort'] = 'call_up_date';
                $state.params['order'] = 'desc';
            }
        }
        if (!angular.isDefined($state.params['offset'])) {
            $state.params['offset'] = 0;
        }
        if (!angular.isDefined($state.params['limit'])) {
            $state.params['limit'] = 10;
        }

        $scope.listOptions = $state.params;

        $scope.listOptions.job_type = parseInt($state.params['job_type'] || "0");
        if ($scope.listOptions.job_type === 0) {
            $scope.listOptions.job_type = null;
        }

        // $scope.listOptions.fieldList = _.map(fields, 'id');
        $scope.maxRanges = [10, 20, 50, 100];
        $scope.fields = fields;
        $scope.filters = [ // Filters for Everyone
            {'id': 'all', 'name': 'All'},
            {'id': 'active', 'name': 'Active'},
            {'id': 'inactive2', 'name': 'Inactive'},
            {'id': 'not_called_up', 'name': 'Not Called Up'},
            {'id': 'called_up', 'name': 'Called Up', 'ordering':'call_up_date', 'sort':'call_up_date', 'order':'desc'}
        ];
        $scope.showPourDateColumn = ($scope.listOptions.job_type === 1 || !$scope.listOptions.job_type);
        $scope.showCallUpDateColumn = ($scope.listOptions.job_type !== 1 || !$scope.listOptions.job_type);
        $scope.loadList = loadList;

        $scope.clearFilters = function () {
            $scope.listOptions = angular.copy(DEFAULT_JOB_LIST_OPTIONS);
            if (roleService.userHasThisRole('employee')) {
                $scope.listOptions.filter = 'called_up';
            }
            if (roleService.userHasThisRole('supervisor')) {
                $scope.listOptions.filter = 'active';
                $scope.listOptions.sort = 'call_up_date';
                $scope.listOptions.order = 'asc';
            }
            stateStorage.storeStateThenGo("job.list", $scope.listOptions, true);
        };

        $scope.triggerCallupReset = function (status) {
            $scope.listOptions.call_up_reset = (status) ? "1" : "0";
        };

        function loadList() {
            // check if Job Type is Paving or Enumber
            // Note: we might need to use dynamic preferences here if job type id would change so we won't
            // manually change this
            if ($scope.listOptions.job_type === 2 || $scope.listOptions.job_type === 3) {
                if ($scope.listOptions.call_up_reset === "1") {
                    $scope.listOptions.call_up_reset = "0";
                    $scope.listOptions.sort = 'call_up_date';
                    $scope.listOptions.order = 'asc';
                }
            } else if ($scope.listOptions.job_type === 1) {
                if ($scope.listOptions.call_up_reset === "1") {
                    $scope.listOptions.call_up_reset = "0";
                    $scope.listOptions.sort = 'pour_date';
                    $scope.listOptions.order = 'asc';
                }
            }
            dataAPIService
                .getDataApi("/api/", 'job')
                .list($scope.listOptions, function (data) {
                    $scope.list = data.results;
                    $scope.accessible = roleService.isAccessible;
                    $scope.listOptions.total = data.count;
                    $scope.listOptions.currentPage = Math.ceil($scope.listOptions.offset / $scope.listOptions.limit) + 1;
                });

                var loadTables = [
                    {
                        name: 'code_job_type',
                        uri : '/api/',
                        scope: 'job_types_List',
                        keyBy: 'id'
                    },
                    {
                        name: 'client',
                        uri : '/api/',
                        scope: 'client_List',
                        keyBy: 'id'
                    },
                    {
                        name: 'supervisor',
                        uri : '/api/',
                        scope: 'supervisor_List',
                        keyBy: 'id'
                    }
                ];

                $scope.options = {};
                CodeTableCacheService.processLoadTables(loadTables, $scope.options);


            CodeTableCacheService.fetchFromCache("/api/", "code_job_type", function (results){
                $scope.codeJobTypes = results;
            })
        }
        var updateRoleInformation = function () {
            $scope.isAdmin = roleService.userHasThisRole('administrator');
            $scope.isClientView = roleService.userHasThisRole('supervisor') ||  roleService.userHasThisRole('client_manager');

            if ($scope.isAdmin) {
                $scope.filters = [
                    {'id': 'all', 'name': 'All'},
                    {'id': 'active', 'name': 'Active'},
                    {'id': 'inactive2', 'name': 'Inactive'},
                    {'id': 'not_called_up', 'name': 'Not Called Up'},
                    {'id': 'called_up', 'name': 'Called Up', 'ordering':'call_up_date', 'sort':'call_up_date', 'order':'desc'},
                    {'id': 'not_invoiced', 'name': 'Not Invoiced'},
                    {'id': 'overdue', 'name': 'Overdue'}
                ];
            }
            if (roleService.getRole("supervisor")) {
                $scope.listOptions.supervisor = roleService.getRole("supervisor_id");
            }

            if (roleService.getRole("subcontractor")) {
                // TODO something??
            }

            loadList();
        };

        roleService.subscribeAccessUpdate($scope, updateRoleInformation);
    }
})();
