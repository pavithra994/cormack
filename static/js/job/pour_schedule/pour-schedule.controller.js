/**
 * pour-schedule.controller.js
 * 
 * This controller handles the display of the job schedule for concrete pours. This is called the "Slab Schedule" in
 * most user-facing forms.
 */

(function () {
    'use strict';
    angular
        .module('app.job')
        .controller(
            'JobPourScheduleController',
            [
                '$filter',
                '$state',
                '$scope',
                'dataAPIService',
                'roleService',
                'stateStorage',
                'DEFAULT_POUR_SCHEDULE_OPTIONS',
                'CodeTableCacheService',
                JobPourScheduleController
            ]);

    /* @ngAnnotate */
    function JobPourScheduleController(
        $filter,
        $state,
        $scope,
        dataAPIService,
        roleService,
        stateStorage,
        DEFAULT_POUR_SCHEDULE_OPTIONS,
        CodeTableCacheService)
    {
        setupInitialState();
        roleService.subscribeAccessUpdate($scope, updateRoleInformation);

        /**
         * Contains the code to set up the $state and $scope variables with their starting values if none are set.
         */
        function setupInitialState()
        {
            $scope.startTime = new Date();
            console.warn("JobPourScheduleController constructor called at " + $scope.startTime.toISOString());

            $scope.modelName = 'job';
            $scope.fields = [
                { 'id': "code", name: "Job No." },
            ];

            // Set default values for certain state variables.
            $state.params["sort"]   = $state.params["sort"]   || "pour_date";
            $state.params["order"]  = $state.params["order"]  || "asc";
            $state.params["filter"] = $state.params["filter"] || "all";
            $state.params["offset"] = $state.params["offset"] || 0;
            $state.params["limit"]  = $state.params["limit"]  || 30;

            // Set up the scope options.
            $scope.listOptions = $state.params;
            $scope.listOptions.job_type = 1

            $scope.pour_date__ge = parseInt($state.params['pour_date__ge'] || "0");
            if ($scope.pour_date__ge === 0)
                $scope.listOptions.pour_date__ge = (new Date()).toISOString();
            if ($state.params['filter'] == "null_pour_date")
                $scope.listOptions.pour_date__ge = null

            $scope.maxRanges = [10, 30, 50, 100];
            $scope.toggles = [
                { 'id': 'all', 'name': 'Pour Date Set' },
                { 'id': 'null_pour_date', 'name': 'No Pour Date' }
            ];

            $scope.showPourDateColumn = ($scope.listOptions.job_type === 1 || !$scope.listOptions.job_type);
            $scope.showCallUpDateColumn = ($scope.listOptions.job_type !== 1 || !$scope.listOptions.job_type);
            $scope.loadList = loadList;

            $scope.clearFilters = function () {
                $scope.listOptions = angular.copy(DEFAULT_POUR_SCHEDULE_OPTIONS);
                $scope.listOptions.filter = 'all';
                stateStorage.storeStateThenGo("job.slab-schedule", $scope.listOptions, true);
            };

            $scope.triggerCallupReset = function (status) {
                $scope.listOptions.call_up_reset = (status) ? "1" : "0";
            };

            $scope.setUpdate = function (item, key) {
                item.is_update[key] = true;
            };

            $scope.setUpdateCancel = function (item, key) {
                item.is_update[key] = false;
            };

            $scope.setAllUpdate = function (form_item, form_key) {
                angular.forEach($scope.list, function (items) {
                    angular.forEach(items, function (item, key) {
                        if ((form_item != items || key != form_key) && items.is_update[key])
                            $scope.patchItem(items, key);
                    })
                })
            };

            $scope.patchItem = function (item, key) {
                var entry = { id: item.id };
                entry[key] = angular.isDefined(item[key]) ? item[key] : "";
                dataAPIService.getDataApi("/api/", 'job').patchItem(entry, function () {
                    item.is_update[key] = false
                });
            };
        }

        /**
         * Load the list of jobs when the page loads.
         */
        function loadList() {
            
            dataAPIService
                .getDataApi("/api/", 'job')
                .list($scope.listOptions, function (data) {
                    $scope.list = data.results;

                    angular.forEach($scope.list, function (value, key) {
                        value.is_update = {}
                    });

                    $scope.accessible = roleService.isAccessible;
                    $scope.listOptions.total = data.count;
                    $scope.listOptions.currentPage = Math.ceil($scope.listOptions.offset / $scope.listOptions.limit) + 1;
                });
                
            var loadTables = [
                {
                    name: 'code_job_type',
                    uri: '/api/',
                    scope: 'job_types_List',
                    keyBy: 'id'
                },
                {
                    name: 'client',
                    uri: '/api/',
                    scope: 'client_List',
                    keyBy: 'id'
                },
                {
                    name: 'supervisor',
                    uri: '/api/',
                    scope: 'supervisor_List',
                    keyBy: 'id'
                },
                {
                    name: 'code_supplier',
                    uri: '/api/',
                    scope: 'supplier_List',
                    keyBy: 'id'
                },
                {
                    name: 'subbie',
                    uri: '/api/',
                    scope: 'subbie_List',
                    keyBy: 'id'
                },
                {
                    name: 'code_depot_type',
                    uri: '/api/',
                    scope: 'depot_types_List',
                    keyBy: 'id'
                },
                {
                    name: 'code_time_of_day',
                    uri: '/api/',
                    scope: 'time_of_day_List',
                    keyBy: 'id'
                }
            ];

            $scope.options = {};
            CodeTableCacheService.processLoadTables(loadTables, $scope.options);

            var loadTables = [
                {
                    uri: '/api/',
                    name: 'code_supplier',
                    params: { filter: 'active' },
                    scope: 'supplier',
                    keyBy: 'id'
                },
                {
                    uri: '/api/',
                    name: 'subbie',
                    params: { filter: 'active' },
                    callback: dataAPIService.applyFilters,
                    scope: 'subcontractors',
                    keyBy: 'id'
                },
                {
                    uri: '/api/',
                    name: 'code_depot_type',
                    params: { filter: 'active' },
                    callback: dataAPIService.applyFilters,
                    scope: 'code_depot_List',
                    keyBy: 'id'
                },
                {
                    uri: '/api/',
                    name: 'supervisor',
                    params: { filter: 'active' },
                    callback: dataAPIService.applyFilters,
                    scope: 'supervisors',
                    keyBy: 'id'
                },
                {
                    uri: '/api/',
                    name: 'client',
                    params: { filter: 'active' },
                    callback: dataAPIService.applyFilters,
                    scope: 'clients',
                    keyBy: 'id'
                },
                {
                    uri: '/api/',
                    name: 'code_time_of_day',
                    params: { filter: 'active' },
                    callback: dataAPIService.applyFilters,
                    scope: 'time_of_day_List',
                    keyBy: 'id'
                }
            ];

            var models = []
            models = _.map(loadTables, 'name');
            if ($state.params.id) {
                models.push('job');
            }
            models.push('tasks');

            CodeTableCacheService.processLoadTables(loadTables, $scope);
            CodeTableCacheService.fetchFromCache("/api/", "code_job_type", function (results) {
                $scope.codeJobTypes = results;
            });

            if (jQuery('tr.select td div.linerow'))
                jQuery('.linespan').before('<br><br>');
        }

        /**
         * Update the user role information when the page loads.
         */
        function updateRoleInformation () {
            $scope.isAdmin = roleService.userHasThisRole('administrator');
            $scope.isClientView = roleService.userHasThisRole('supervisor') || roleService.userHasThisRole('client_manager');

            if ($scope.isAdmin) {
                $scope.toggles = [
                    { 'id': 'all', 'name': 'Pour Date Set' },
                    { 'id': 'null_pour_date', 'name': 'No Pour Date' }
                ];
            }
            if (roleService.getRole("supervisor")) {
                $scope.listOptions.supervisor = roleService.getRole("supervisor_id");
            }

            loadList();
        };
    }
})();
