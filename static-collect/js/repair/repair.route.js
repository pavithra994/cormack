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
        .module('app.repair')
        .config(['$stateProvider', routeConfig]);

    /* @ngAnnotate */
    function routeConfig($stateProvider) {
        $stateProvider
            .state('repair', {
                abstract: true,
                url: "/repair",
                templateUrl: "js/ocom/layout/content.html"
            })
            .state('repair.list', {
                url: "/list?offset&limit&ordering&sort&order&searchField&filter&q",
                templateUrl: "js/repair/list.html",
                controller: "RepairListController",
                onEnter: ['$stateParams', 'stateStorage', 'DEFAULT_JOB_LIST_OPTIONS',
                    function ($stateParams, stateStorage, DEFAULT_JOB_LIST_OPTIONS) {
                        stateStorage.updateStateParams("repair.list", angular.copy(DEFAULT_JOB_LIST_OPTIONS),
                            $stateParams);
                    }
                ],
                data:{
                    store_state:true
                }
            })
            .state('repair.create', {
                url: "/create",
                templateUrl: "js/repair/create.html",
                controller: "RepairController"
            })
            .state('repair.edit', {
                url: "/edit/:id?skip",
                templateUrl: "js/repair/edit.html",
                controller: "RepairController"
            })
    }
})();
