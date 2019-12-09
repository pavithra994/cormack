/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019 
 *
 */

angular.module('app.email')
    .config(routeConfig);

function routeConfig($stateProvider) {
    $stateProvider
        .state('email', {
            abstract: true,
            url: "/email",
            templateUrl: "js/ocom/layout/content.html"
        })
        .state('email.list', {
            url: "/list?offset&limit&ordering&sort&order&q&searchField&filter",
            templateUrl: "js/email/list.html",
            controller: EmailListController,
            onEnter: ['$stateParams', 'stateStorage', function ($stateParams, stateStorage) {
                var defaults = {
                    'limit': 10,
                    'offset': 0
                };
                stateStorage.updateStateParams("email.list", defaults, $stateParams);
            }],
            data:{
                store_state:true
            }
        })
        .state('email.assign', {
            url: "/assign/:id",
            templateUrl: "js/email/assign.html",
            controller: 'EmailController'
        })
}
