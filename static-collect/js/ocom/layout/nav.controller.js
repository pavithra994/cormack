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
        .controller('NavbarController', NavbarController);

    function NavbarController($scope, $state, $rootScope, APP_NAME, NAV_MENU, alerts, authService, roleService,
                              $timeout, $sce, platform) {
        console.log('Navbar controller');

        $scope.platform = platform;

        var updateMenu = function (forceUnauthenticate) {
            var authenticated = authService.isAuthenticated();
            var adminDashboard = false;
            var user = authService.getCurrentUser();

            if (user) {
                adminDashboard = user.is_staff;
            }

            $scope.adminDashboard = adminDashboard;
            if (forceUnauthenticate) {
                $scope.isAuthenticated = false;
            } else {
                $scope.isAuthenticated = authenticated;
            }
            console.log('Nav page menu updated.', authenticated);
        };

        var getMenu = function() {
            var currentStateNameRoot = $state.current.name.split('.')[0];
            var navMenu = NAV_MENU[currentStateNameRoot];

            if (!navMenu) {
                navMenu = [];

                var allStates = $state.get();
                _.each(allStates, function (state) {
                    if (state.name.startsWith(currentStateNameRoot)) {
                        var stateName = state.name;

                        if (state.data && state.data.label) {
                            var label = state.data.label;
                            navMenu.push({link: stateName, name: label, stateName: stateName});
                        }
                    }
                });
            }

            $scope.navMenu = navMenu;
        };

        $scope.appName = $sce.trustAsHtml(APP_NAME);
        $scope.navMenu = null;

        $scope.logoutUser = function () {
            authService.unauthenticate();
            alerts.success("You have been logged out.");
            updateMenu(true);
        };

        $scope.$on("$accessSettingsUpdate", function () {
            updateMenu(false);
        });

        var authVerified = $rootScope.$on("$authVerified", function () {
            updateMenu(false);
        });

        $scope.$on("$rolesUpdate", function () {
            updateMenu(false);
        });

        $scope.$on('$destroy', function() {
            authVerified();
        });

        $scope.getName = function () {
            var user = authService.getCurrentUser();

            if (_.isEmpty(user) || !angular.isDefined(user.descriptive_name)) {
                if (user) {
                    if (angular.isDefined(user.first_name)) {
                        return user.first_name;
                    }
                    if (angular.isDefined(user.email)) {
                        return user.email;
                    }
                }
                return "";
            } else {
                return user.descriptive_name;
            }
        };

        $scope.can_take_screenshot = function() {
            if (typeof(html2canvas) != "undefined")
                return true
            else
                return false;
        };

        $scope.take_screen_shot = function () {
            var printWin = window.open("/screen_shot/", 'showScreenShot');
            printWin.focus();

            html2canvas(document.body).then (function (canvas) {
                var url = canvas.toDataURL("image/png");
                $timeout(function () {
                    var win = $(printWin.document);

                    var user = authService.getCurrentUser();
                    if (user) {
                        $("#username", win).val(user.username);
                    }

                    $("#url", win).val(window.location);
                    $("#image", win).val(url.replace("data:image/png;base64,", ""));

                    $("#screenshot", win).attr("src", url);
                    $("h1", win).hide();
                    $("div#the_form", win).show();

                    win.focus();
                }, 10);
            });
        };

        getMenu();
        updateMenu(false);
    }
})();
