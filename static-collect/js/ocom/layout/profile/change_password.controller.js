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
        .controller('ChangePasswordController', ChangePasswordController);

    function routeConfig($stateProvider) {
        $stateProvider
            .state('index.change_password', {
                url: "change_password",
                templateUrl: "js/ocom/layout/profile/change_password.html"
            })
    }

    function ChangePasswordController($scope, $interval, authService, SETTINGS, $http) {
        console.log("Change Password Controller");

        $scope.changePassword = function () {
            $scope.success_message = null;
            $scope.error_message = null;
            $http.post("/rest-auth/password/change/", {old_password: $scope.old_password,
                                                       new_password1: $scope.new_password1,
                                                       new_password2: $scope.new_password2})
              .success(function (response) {
                console.log(response);
                $scope.success_message = response.detail;
              })
              .error(function (error) {
                console.log(error);
                error_msg = Object.keys(error);
                console.log(error[error_msg[0]][0]);
                $scope.error_message = error[error_msg[0]][0];
              });
        }

        /*$scope.home = authService.homeRoute;
        //$scope.api = dataService.getApi('user');

        var waitUntilChecked = $interval(function () {
            if (authService.tokenChecked()) {
                $interval.cancel(waitUntilChecked);
                $scope.item = authService.getCurrentUser();
            }
        }, SETTINGS.interval);*/
    }
})();
