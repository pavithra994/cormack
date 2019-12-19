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
        .controller('JobPourScheduleController', ['$filter', '$state', '$scope', 'authService', 'dataCacheService',
            'dataAPIService', 'roleService', 'stateStorage', 'DEFAULT_POUR_SCHEDULE_OPTIONS', 'CodeTableCacheService',
            JobPourScheduleController]);

    /* @ngAnnotate */
    function JobPourScheduleController($filter, $state, $scope, authService, dataCacheService, dataAPIService,
                                  roleService, stateStorage, DEFAULT_POUR_SCHEDULE_OPTIONS, CodeTableCacheService) {
        var fields = [
            {'id':"code", name:"Job No."},
        ];

        $scope.modelName = 'job';
        // set defaults
        if (!angular.isDefined($state.params['sort'])) {
            $state.params['sort'] = 'pour_date';
            if (!angular.isDefined($state.params['order'])) {
                $state.params['order'] = 'asc';
            }
        }
        if (!angular.isDefined($state.params['filter'])) {
            $state.params['filter'] = 'all';
        }
        if (!angular.isDefined($state.params['offset'])) {
            $state.params['offset'] = 0;
        }
        if (!angular.isDefined($state.params['limit'])) {
            $state.params['limit'] = 20;
        }

        $scope.listOptions = $state.params;
        

        $scope.listOptions.job_type = 1

        $scope.pour_date__ge = parseInt($state.params['pour_date__ge'] || "0");
        if ($scope.pour_date__ge === 0) {
            $scope.listOptions.pour_date__ge = (new Date()).toISOString()
        }
        if ($state.params['filter'] == "null_pour_date"){
            $scope.listOptions.pour_date__ge = null
        }

        $scope.maxRanges = [10, 20, 50, 100];
        $scope.fields = fields;

        $scope.toggles = [
            {'id': 'all', 'name': 'Pour Date Set'},
            {'id': 'null_pour_date', 'name': 'No Pour Date'}
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
        
        // function formatDate(date) {
        //     var d = new Date(date),
        //         month = '' + (d.getMonth() + 1),
        //         day = '' + d.getDate(),
        //         year = d.getFullYear();
        
        //     if (month.length < 2) 
        //         month = '0' + month;
        //     if (day.length < 2) 
        //         day = '0' + day;
        
        //     return [year, month, day].join('-');
        // }

        $scope.patchItem = function (item, key) {
            
            var entry = {
                id: item.id
            };
            // console.log(item.base_date);
            // var date2=formatDate(item.base_date);
            // console.log("date2 : ", date2);

            // if(formatDate(item.base_date)=="1970-01-01")
            // {
            //     item.base_date= new Date();
            // }
            entry[key] = angular.isDefined(item[key]) ? item[key] : "";
            dataAPIService.getDataApi("/api/", 'job').patchItem(entry, function () {
                item.is_update[key] = false
                // if(jQuery('tr[data-id="'+item.id+'"]').prev( ".data-"+item.pour_date+"")){
                //     if(item.pour_date != null){
                //         if(jQuery('tr[data-id="'+item.id+'"]').prev('tr.linerow')){
                //             jQuery('tr[data-id="'+item.id+'"]').prev('tr.linerow').remove();
                //         }
                //     if(jQuery('tr[data-id="'+item.id+'"]').prev('tr.ng-scope').attr('data-date')!=item.pour_date)
                //     {
                //         jQuery('tr[data-id="'+item.id+'"]').before('<tr class="linerow data-'+item.pour_date+'"><td colspan="28">'+item.pour_date+'</td></tr>')
                //     }}
                    
                // }
                // if(jQuery('tr[data-id="'+item.id+'"]').next( ".data-"+item.pour_date+"")){
                //     if(item.pour_date != null){
                //         if(jQuery('tr[data-id="'+item.id+'"]').next('tr.linerow')){
                //             jQuery('tr[data-id="'+item.id+'"]').next('tr.linerow').remove();
                //         }
                //     if(jQuery('tr[data-id="'+item.id+'"]').next('tr.ng-scope').attr('data-date')!=item.pour_date)
                //     {
                //         jQuery('tr[data-id="'+item.id+'"]').after('<tr class="linerow data-'+item.pour_date+'"><td colspan="28">'+jQuery('tr[data-id="'+item.id+'"]').next('tr.ng-scope').attr('data-date')+'</td></tr>')                    }}
                    
                // }
            });
        };

        function loadList() {
            dataAPIService
                .getDataApi("/api/", 'job')
                .list($scope.listOptions, function (data) {
                    console.warn("$scope.listOptions", JSON.stringify($scope.listOptions));
                    console.warn("data", data);
                    $scope.list = data.results;

                    angular.forEach($scope.list, function (value, key) {
                        value.is_update = {}
                    })

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
                        uri : '/api/',
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
                        params: {filter: 'active'},
                        scope: 'supplier',
                        keyBy: 'id'
                    },
                    {
                        uri: '/api/',
                        name: 'subbie',
                        params: {filter: 'active'},
                        callback: dataAPIService.applyFilters,
                        scope: 'subcontractors',
                        keyBy: 'id'
                    },
                    {
                        uri: '/api/',
                        name: 'code_depot_type',
                        params: {filter: 'active'},
                        callback: dataAPIService.applyFilters,
                        scope: 'code_depot_List',
                        keyBy: 'id'
                    },
                    {
                        uri: '/api/',
                        name: 'supervisor',
                        params: {filter: 'active'},
                        callback: dataAPIService.applyFilters,
                        scope: 'supervisors',
                        keyBy: 'id'
                    },
                    {
                        uri: '/api/',
                        name: 'client',
                        params: {filter: 'active'},
                        callback: dataAPIService.applyFilters,
                        scope: 'clients',
                        keyBy: 'id'
                    },
                    {
                        uri: '/api/',
                        name: 'code_time_of_day',
                        params: {filter: 'active'},
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


            CodeTableCacheService.fetchFromCache("/api/", "code_job_type", function (results){
                $scope.codeJobTypes = results;
            })
            
            if(jQuery('tr.select td div.linerow')){
                jQuery('.linespan').before('<br><br>')
                       }
            // console.log('  TEsting123 ');
        }
        var updateRoleInformation = function () {
            $scope.isAdmin = roleService.userHasThisRole('administrator');
            $scope.isClientView = roleService.userHasThisRole('supervisor') ||  roleService.userHasThisRole('client_manager');

            if ($scope.isAdmin) {
                $scope.toggles = [
                    {'id': 'all', 'name': 'Pour Date Set'},
                    {'id': 'null_pour_date', 'name': 'No Pour Date'}
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

// $(window).scroll(function () {
//     var scroll = $(window).scrollTop();
//     if(scroll>=207)jQuery('.fixed_header thead tr').css({'height':'125px'}); else {jQuery('.fixed_header thead tr').css({'height':'80px'});}
// });