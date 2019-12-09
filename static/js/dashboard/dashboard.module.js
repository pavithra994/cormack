/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019 
 *
 */

angular
    .module('app.dashboard', [])
    .config(routeConfig)
    .controller('MainController', MainController);


function MainController($scope, $rootScope, authService, roleService, widgetService) {
    $scope.accessible = roleService.isAccessible;
    widgetService.setShowFooter(true);
    $scope.isAuthenticated = authService.isAuthenticated;

    $scope.$on('$formSettingsUpdate', function () {
        $scope.getBootstrapGridColumns = getBootstrapGridColumns;
        $scope.isAuthenticated = authService.isAuthenticated;
    });

    $scope.retryLogin = function () {
        authService.refreshToken(true);
    };
    roleService.triggerPageLoaded($scope);

    function getBootstrapGridColumns() {
        var count = 0;

        switch(count) {
            case 3:
                return '4';
            case 2:
                return '6';
            default:
                return '12';
        }
    }
}

function routeConfig($stateProvider) {
    $stateProvider
        .state('index', {
            abstract: true,
            url: "/",
            templateUrl: "js/ocom/layout/content.html"      // customise your template here
        })
        .state('index.home', {
            url: "?limit&offset&ordering&sort&order&q&searchField&filter",
            templateUrl: "js/dashboard/home.html",
            controller: MainController
        });
}
