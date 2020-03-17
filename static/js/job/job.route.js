/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019 
 *
 */

(function () {
    'use strict';

    angular
        .module('app.job')
        .config(['$stateProvider', routeConfig]);

    /* @ngAnnotate */
    function routeConfig($stateProvider) {
        $stateProvider
            .state('job', {
                abstract: true,
                url: "/job",
                templateUrl: "js/ocom/layout/content.html"
            })
            .state('job.list', {
                url: "/list?offset&limit&ordering&sort&order&searchField&filter&q&pour_date__ge&job_type&call_up_reset",
                templateUrl: "js/job/list.html",
                controller: "JobListController",
                onEnter: ['$stateParams', 'roleService', 'stateStorage', 'DEFAULT_JOB_LIST_OPTIONS',
                    function ($stateParams, roleService, stateStorage, DEFAULT_JOB_LIST_OPTIONS) {
                        var modified = angular.copy(DEFAULT_JOB_LIST_OPTIONS);

                        if (roleService.userHasThisRole('employee')) {
                            modified['filter'] = 'called_up';
                        }
                        if (roleService.userHasThisRole('supervisor')) {
                            modified['filter'] = 'active';
                            modified['sort'] = 'call_up_date';
                            modified['order'] = 'asc';
                        }

                        stateStorage.updateStateParams("job.list", modified,
                            $stateParams);
                    }
                ],
                data: {
                    store_state: true
                }
            })
            .state('job.paving_list', {
                url: "/paving_list?offset&limit&ordering&sort&order&searchField&filter&q&pour_date__ge&job_type&call_up_reset",
                templateUrl: "js/job/paving_schedule/list.html",
                controller: "PavingJobListController",
                onEnter: ['$stateParams', 'stateStorage', 'roleService', 'DEFAULT_PAVING_SCHEDULE_OPTIONS',
                    function ($stateParams, stateStorage, roleService, DEFAULT_PAVING_SCHEDULE_OPTIONS) {
                        var modified = angular.copy(DEFAULT_PAVING_SCHEDULE_OPTIONS);

                        if (roleService.userHasThisRole('supervisor')) {
                            modified['filter'] = 'active';
                            modified['sort'] = 'call_up_date';
                            modified['order'] = 'asc';
                        }

                        stateStorage.updateStateParams("job.paving_list", modified,
                            $stateParams);
                    }
                ],
                data: {
                    store_state: true
                }
            })
            .state('job.enumber_list', {
                url: "/enumber_list?offset&limit&ordering&sort&order&searchField&filter&q&pour_date__ge&job_type&call_up_reset",
                templateUrl: "js/job/enumber_schedule/list.html",
                controller: "ENumberListController",
                onEnter: ['$stateParams', 'stateStorage', 'roleService', 'DEFAULT_ENUMBER_SCHEDULE_OPTIONS',
                    function ($stateParams, stateStorage, roleService, DEFAULT_ENUMBER_SCHEDULE_OPTIONS) {
                        var modified = angular.copy(DEFAULT_ENUMBER_SCHEDULE_OPTIONS);

                        if (roleService.userHasThisRole('supervisor')) {
                            modified['filter'] = 'called_up';
                            modified['sort'] = 'call_up_date';
                            modified['order'] = 'asc';
                        }

                        stateStorage.updateStateParams("job.enumber_list", modified,
                            $stateParams);
                    }
                ],
                data: {
                    store_state: true
                }
            })
            .state('job.create', {
                url: "/create",
                templateUrl: "js/job/create.html",
                controller: "JobController"
            })
            .state('job.edit', {
                url: "/edit/:id?skip",
                templateUrl: "js/job/edit.html",
                controller: "JobController"
            })
            .state('job.pour-schedule', {
                url: "/slab-schedule?offset&limit&ordering&sort&order&searchField&filter&q&pour_date__ge&job_type&call_up_reset",
                templateUrl: "js/job/pour_schedule/pour-schedule.html",
                controller: "JobPourScheduleController",
                onEnter: ['$stateParams', 'roleService', 'stateStorage', 'DEFAULT_POUR_SCHEDULE_OPTIONS',
                    function ($stateParams, roleService, stateStorage, DEFAULT_POUR_SCHEDULE_OPTIONS) {
                        stateStorage.updateStateParams("job.pour-schedule", angular.copy(DEFAULT_POUR_SCHEDULE_OPTIONS),
                            $stateParams);
                    }
                ]
            })
            .state("job.pour-schedule-test", {
                url: "/pour-schedule-test",
                templateUrl: "js/job/pour_schedule_test/pour_schedule_test.html",
                controller: "JobPourScheduleTestController"
            })
    }
})();
