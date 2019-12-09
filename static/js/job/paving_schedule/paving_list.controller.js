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
        .controller('PavingJobListController', ['$state', '$scope', 'authService', 'dataCacheService',
            'dataAPIService', 'roleService', 'stateStorage', 'DEFAULT_PAVING_SCHEDULE_OPTIONS', 'CodeTableCacheService',
            PavingJobListController]);

    /* @ngAnnotate */
    function PavingJobListController($state, $scope, authService, dataCacheService, dataAPIService,
                                  roleService, stateStorage, DEFAULT_PAVING_SCHEDULE_OPTIONS, CodeTableCacheService) {
        var fields = [
            {'id':"client__name", name:"Client Name"},
            {'id':"job_type__description", name:"Job Type"},
            {'id':"address", name:"Address"},
            {'id':"description", name:"Description"},
            {'id':"suburb", name:"Suburb"}
        ];

        var user = authService.getCurrentUser();
        var role = roleService.getRole();

        $scope.modelName = 'job';
        // set defaults

        if (!angular.isDefined($state.params['ordering'])) {
            $state.params['ordering'] = 'pour_date';
        }
        if (!angular.isDefined($state.params['call_up_reset'])) {
            $state.params['call_up_reset'] = "1";
        }
        if (!angular.isDefined($state.params['filter'])) {
            $state.params['filter'] = 'called_up';
        }
        if ($state.params['filter'] === 'called_up') {
            if ($state.params['call_up_reset'] === "1") {
                $state.params['ordering'] = 'call_up_date';
                $state.params['call_up_reset'] = "0";
            }
        } else {
            $state.params['call_up_reset'] = "1";
        }
        if (!angular.isDefined($state.params['offset'])) {
            $state.params['offset'] = 0;
        }
        if (!angular.isDefined($state.params['limit'])) {
            $state.params['limit'] = 50;
        }

        $scope.listOptions = $state.params;
        // always paving
        $scope.listOptions.job_type = "3";

        $scope.listOptions.fieldList = _.map(fields, 'id');
        $scope.maxRanges = [10, 20, 50, 100];
        $scope.fields = fields;

        // {'id': 'paving_inactive', 'name': 'No Pour Date'},, {'id': 'paving_active', 'name': 'To Pour'},
        $scope.filters = [ // Filters for Everyone
            {'id': 'all', 'name': 'All'},


            {'id': 'completed', 'name': 'Completed', 'ordering':'call_up_date', 'sort':'call_up_date', 'order':'desc'},
            {'id': 'not_called_up', 'name': 'Not Called Up'},
            {'id': 'called_up', 'name': 'Called Up'},
            {'id': 'cancelled', 'name': 'Cancelled'}

        ];
        $scope.loadList = loadList;

        $scope.clearFilters = function () {
            $scope.listOptions = angular.copy(DEFAULT_PAVING_SCHEDULE_OPTIONS);
            $scope.listOptions.job_type = "3";

            if (roleService.userHasThisRole('supervisor')) {
                $scope.listOptions.filter = 'active';
                $scope.listOptions.sort = 'call_up_date';
                $scope.listOptions.order = 'asc';
            }

            $scope.refreshList();
            stateStorage.storeStateParams("job.paving_list", DEFAULT_PAVING_SCHEDULE_OPTIONS, true);
        };

        $scope.refreshList = function() {
            loadList(); // TODO REload URL
        };

        /*
        $scope.onChangeFilter = function() {
            switch ($scope.listOptions.filter) {
                case 'called_up':
                    // set default sorting
                    $scope.listOptions.sort = 'call_up_date';
                    break;
                // Add more filter change results here if needed
                default:
                    // do something here
            }
        };
        */

        function loadLookups() {
            $scope.options = {};

            var loadTables = [
                {
                    uri: '/api/',
                    name: 'code_paving_colour',
                    scope: 'code_paving_colour',
                    keyBy: "id"
                },
                {
                    uri: '/api/',
                    name: 'client',
                    scope: 'client',
                    keyBy: "id"
                },
                {
                    uri: '/api/',
                    name: 'supervisor',
                    scope: 'supervisor',
                    keyBy: "id"
                },
                {
                    name: 'code_job_type',
                    uri : '/api/',
                    scope: 'job_types_List',
                    keyBy: 'id'
                }
            ];

            CodeTableCacheService.processLoadTables(loadTables, $scope.options);
        }
        loadLookups();


        function loadList() {
            dataAPIService
                .getDataApi("/api/", 'job')
                .list($scope.listOptions, function (data) {
                    $scope.list = data.results;
                    $scope.accessible = roleService.isAccessible;
                    $scope.listOptions.total = data.count;
                    $scope.listOptions.currentPage = Math.ceil($scope.listOptions.offset / $scope.listOptions.limit) + 1;
                });

            CodeTableCacheService.fetchFromCache("/api/", "code_job_type", function (results){
                $scope.codeJobTypes = results;
            })
        }
        var updateRoleInformation = function () {
            $scope.isAdmin = roleService.userHasThisRole('administrator');

            if ($scope.isAdmin) {
                /*
                    {'id': 'paving_active', 'name': 'To Pour'},
                    {'id': 'paving_inactive', 'name': 'No Pour Date'},
                    {'id': 'not_called_up', 'name': 'Not Called Up'},
                 */
                $scope.filters = [
                    {'id': 'all', 'name': 'All'},
                    {'id': 'completed', 'name': 'Completed'},
                    {'id': 'called_up', 'name': 'Called Up', 'ordering':'call_up_date', 'sort':'call_up_date', 'order':'desc'},
                    {'id': 'not_invoiced', 'name': 'Not Invoiced'},
                    {'id': 'cancelled', 'name': 'Cancelled'},
                    {'id': 'overdue', 'name': 'Overdue'}

                ];
            }
            if (roleService.getRole("supervisor")) {
                $scope.filters = [
                    {'id': 'called_up', 'name': 'Called Up', 'ordering':'call_up_date', 'sort':'call_up_date', 'order':'desc'},
                    {'id': 'inactive2', 'name': 'Completed'}

                ];

                $scope.listOptions.supervisor = roleService.getRole("supervisor_id");
            }

            if (roleService.getRole("subcontractor")) {
                // TODO something??
            }

            loadList();
        };

        $scope.patchItem = function (item, key) {
            var entry = {
                id: item.id
            };

            entry[key] = angular.isDefined(item[key]) ? item[key] : "";
            dataAPIService.getDataApi("/api/", 'job').patchItem(entry, function () {
            });
        };


         $scope.stepsConfig = [
            {label:"Dug", field:"dug_date"},
            {label:"Prepared", field:"prepared_date"},
            {label:"Poured", field:"poured_date"},
            {label:"Cut", field:"cut_date"},
            {label:"Sealed", field:"sealed_date"},
        ];

         $scope.checklistFields = [
            {label:"Down Pipes", field:"down_pipes_installed",  title:"Down Pipes Installed?"},
            {label:"Gas", field:"gas_line_installed",  title:"Gas Line Installed?"},
            {label:"Rebates", field:"rebates_brickwork",  title:"Rebates Flush with Brickwork?"},
            {label:"Risers", field:"risers_correct_location",  title:"Risers in Correct Location?"},
            {label:"Access", field:"good_access_rear_paving",  title:"Good Access for Rear Paving?"},
         ];

        roleService.subscribeAccessUpdate($scope, updateRoleInformation);
    }
})();
