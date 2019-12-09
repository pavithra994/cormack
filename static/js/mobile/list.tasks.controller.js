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
        .module('app.mobile')
        .controller('MobileListTasksController', ['$state', '$scope', 'authService', 'dataCacheService',
            'dataAPIService', 'roleService', 'DEFAULT_JOB_LIST_OPTIONS', 'CodeTableCacheService',
            MobileListTasksController]);

    /* @ngAnnotate */
    function MobileListTasksController($state, $scope, authService, dataCacheService, dataAPIService, roleService,
                                       DEFAULT_JOB_LIST_OPTIONS, CodeTableCacheService) {
        var filters = [
            {'id': 'all', 'name': 'All'},
            {'id': 'active', 'name': 'Active'},
            {'id': 'inactive', 'name': 'Inactive'},
            {'id': 'completed', 'name': 'Completed'},
            {'id': 'cancelled', 'name': 'Cancelled'}

        ];

        var fields = [
            {'id':"client__name", name:"Client Name"},
            {'id':"job_type__description", name:"Job Type"},
            {'id':"address", name:"Address"},
            {'id':"description", name:"Description"},
            {'id':"suburb", name:"Suburb"}
        ];

        var user = authService.getCurrentUser();

        $scope.modelName = 'job';
        $scope.canSeePlansBeforeAccept = user.role.can_see_plans_before_accept;

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
        $scope.listOptions.job_type = parseInt($state.params['job_type'] || "0");

        if ($scope.listOptions.job_type === 0) {
            $scope.listOptions.job_type = null;
        }

        $scope.listOptions.fieldList = _.map(fields, 'id');
        $scope.maxRanges = [10, 20, 50, 100];
        $scope.fields = fields;
        $scope.filters = filters;
        $scope.loadList = loadList;

        $scope.clearFilters = function () {
            $scope.listOptions = angular.copy(DEFAULT_JOB_LIST_OPTIONS);
            $scope.refreshList();
        };

        loadList();

        function loadList() {
            if ($scope.listOptions.q) {
                $scope.listOptions.query = {
                    "logic": "or", "criteria": [
                        {"operation": "icontains", "name": "job__address", "params": [$scope.listOptions.q]},
                        {"operation": "icontains", "name": "job__suburb", "params": [$scope.listOptions.q]},
                        {"operation": "icontains", "name": "description", "params": [$scope.listOptions.q]},
                        {"operation": "icontains", "name": "job__client__name", "params": [$scope.listOptions.q]}
                    ]
                };
            }
            else {
                $scope.listOptions.query = {};// empty
            }

            $scope.list = [];
            dataAPIService
                .getDataApi("/api/", 'tasks')
                .list($scope.listOptions, function (data) {
                    $scope.list = _.union($scope.list, data.results);
                    $scope.accessible = roleService.isAccessible;
                    $scope.listOptions.total = $scope.list.length;

                    //$scope.listOptions.currentPage = Math.ceil($scope.listOptions.offset / $scope.listOptions.limit) + 1;
                    dataAPIService
                         .getDataApi("/api/", 'repair')
                         .list($scope.listOptions, function (data) {
                            // remove entries with rejected dates (see mechanism for removing items in $scope.reject
                             $scope.list = _.filter(_.union($scope.list, data.results), function (instance) {
                                 // should we filter using the backend instead?
                                 return !instance.rejected_date;
                             });
                             $scope.listOptions.total = $scope.list.length;
                         });

                });

            CodeTableCacheService.fetchFromCache("/api/", "code_job_type", function (results){
                $scope.codeJobTypes = results;
            });
            CodeTableCacheService.fetchFromCache("/api/", "code_task_type", function (results){
                $scope.codeTaskTypes = results;
            })
        }
        var updateAdmin = function () {
            $scope.isAdmin = roleService.userHasThisRole('administrator');
        };

        $scope.accept = function (item) {
            item.accepted_date = new Date();

            // check if item is task or repair
            if (item.task_type) {
                dataAPIService.getDataApi("/api/", 'tasks').updateItem(item.id, item, function (result) {
                    // Nothing to do here..
                });
            } else {
                if (item.repair_type) {
                    item.accepted_date = moment(item.accepted_date).format('YYYY-MM-DD');
                    dataAPIService.getDataApi("/api/", 'repair').updateItem(item.id, item, function (result) {
                        // Nothing to do here..
                    }, function (err) {
                        console.log("ERROR", err);
                    });
                }
            }
        };

        $scope.reject = function (item) {
            item.rejected_date = new Date();

            // check if item is task or repair
            if (item.task_type) {
                dataAPIService.getDataApi("/api/", 'tasks').updateItem(item.id, item, function (result) {
                    _.remove($scope.list, {'id':item.id});
                });
            } else {
                if (item.repair_type) {
                    item.back_charge = true;
                    item.rejected_date = moment(item.rejected_date).format('YYYY-MM-DD');
                    dataAPIService.getDataApi("/api/", 'repair').updateItem(item.id, item, function (result) {
                        _.remove($scope.list, {'id':item.id});
                    });
                }
            }
        };

        $scope.openMap = function (item, isJob) {
            if ((navigator.platform.indexOf("iPhone") !== -1) ||
                (navigator.platform.indexOf("iPad") !== -1) ||
                (navigator.platform.indexOf("iPod") !== -1))
                window.open("maps://maps.google.com/maps?daddr=<lat>,<long>&amp;ll=");
            else /* else use Google */ {
                var lookupAddress = (isJob) ?  item.address + " " + item.suburb : item.address_label + " " + item.suburb_label;

                console.log("TEST", item);
                window.open("https://www.google.com/maps/search/?api=1&query="+ lookupAddress);
            }
        };

        $scope.getTaskType = function (task_type) {
            var result = _.find ($scope.codeTaskTypes, {pk:task_type});

            return (result) ? result.description : task_type + " Unknown";
        };

        roleService.subscribeAccessUpdate($scope, updateAdmin);
    }
})();
