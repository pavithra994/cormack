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
        .module('app.mobile')
        .config(['$stateProvider', routeConfig]);

    /* @ngAnnotate */
    function routeConfig($stateProvider) {
        $stateProvider
            .state('mobile', {
                abstract: true,
                url: "/mobile",
                templateUrl: "js/ocom/layout/content.html"
            })
            .state('mobile.listtasks', {
                url: "/listTask?q",
                templateUrl: "js/mobile/list.tasks.html",
                controller: "MobileListTasksController",
                onEnter: ['$stateParams', 'stateStorage', 'DEFAULT_JOB_LIST_OPTIONS',
                    function ($stateParams, stateStorage, DEFAULT_JOB_LIST_OPTIONS) {
                        stateStorage.updateStateParams("mobile.listtasks", angular.copy(DEFAULT_JOB_LIST_OPTIONS),
                            $stateParams);
                    }
                ],
                data:{
                    store_state:true
                }
            });
    }
})();
