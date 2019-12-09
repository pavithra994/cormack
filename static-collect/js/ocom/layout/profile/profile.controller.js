/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    angular
        .module('app.ocom')
        .config(routeConfig)
        .controller('ProfileController', ProfileController);

    function routeConfig($stateProvider) {
        $stateProvider
            .state('index.profile', {
                url: "profile",
                templateUrl: "js/ocom/layout/profile/profile.html"
            })
    }

    function ProfileController($scope, $interval, authService, SETTINGS) {
        console.log("Profile Controller");

        $scope.home = authService.homeRoute;
        //$scope.api = dataService.getApi('user');

        var waitUntilChecked = $interval(function () {
            if (authService.tokenChecked()) {
                $interval.cancel(waitUntilChecked);
                $scope.item = authService.getCurrentUser();
            }
        }, SETTINGS.interval);
    }
})();
