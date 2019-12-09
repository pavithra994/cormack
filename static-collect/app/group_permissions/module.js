/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    'use strict';

    angular.module('app.group_permissions', [])
        .config(['$stateProvider', function ($stateProvider) {
            $stateProvider
                .state('group_permissions', {
                    abstract: true,
                    url: "/group_permissions",
                    templateUrl: "js/ocom/layout/content.html"
                })
                .state('group_permissions.list', {
                    url: "/list?offset&limit&ordering&sort&order&searchField&filter&q",
                    templateUrl: "app/group_permissions/list.html",
                    controller: "GroupPermissionsListController",
                    data: {label:"Manage Group Permission", store_state:true},
                    /* NOTE: this is for ui-router 1.X */
                    params: {
                        'total': {value:"0" },
                        'currentPage': {value:"1"},
                        'filter': {value:"all"}, // TODO: Change filter if necessary
                        'sort': {value:"id"},      // TODO: Change default sort column field if necessary
                        'order': {value:"asc"},   // TODO: Change default sort column field if necessary
                        'q': {value:""},
                        'query': {value:{}},
                        'searchField': {value:""},
                        'ordering': {value:""},
                        'limit': {value:"20"},
                        'offset': {value:"0"},
                    }
                    /* End UI-Router 1.X code */
                    /* This code is for pre 1.0 - TODO: Uncomment this and remove above to use in old projects
                    onEnter: ['$stateParams', 'stateStorage', function ($stateParams, stateStorage) {
                        var defaults = {
                            'total': 0,
                            'currentPage': 1,
                            // TODO: Change filter if necessary
                            'filter': "active",
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
                        stateStorage.updateStateParams("group_permissions.list", defaults, $stateParams);
                    }] */
                })
                .state('group_permissions.create', {
                    url: "/create",
                    templateUrl: "app/group_permissions/create.html",
                    controller: "GroupPermissionsController",
                    data: {label:"New Group Permission"},
                })
                .state('group_permissions.edit', {
                    url: "/edit/:id?skip",
                    templateUrl: "app/group_permissions/edit.html",
                    controller: "GroupPermissionsController"
                });
        }])
        .run (['$transitions', 'authService', function ($transitions, authService) {
             $transitions.onStart({}, function (trans) {
                var toState = trans.$to();

                if (toState.name.startsWith("group_permissions")) {
                    var user = authService.getCurrentUser();
                    if (!user) {
                        return false;
                    }
                    else {
                        return user.is_staff;
                    }
                }
            });
        }]);
})();
