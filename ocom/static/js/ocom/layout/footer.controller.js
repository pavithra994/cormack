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
        .controller('FooterController', FooterController);

    function FooterController($scope, $rootScope, authService, widgetService) {
        function updateFooter() {
            $scope.isAuthenticated = authService.isAuthenticated();
            $scope.showFooter = widgetService.showFooter();
            $scope.version = widgetService.version;
        }

        // deprecate in favor of footer toggle
        $scope.$on("$formSettingsUpdate", function () {
            updateFooter();
        });

        var footerToggled = $rootScope.$on("$footerToggled", function () {
            console.log("Footer toggle intercepted.");
            updateFooter();
        });

        updateFooter();

        $scope.$on('$destroy', function() {
            footerToggled();
        });
    }
})();
