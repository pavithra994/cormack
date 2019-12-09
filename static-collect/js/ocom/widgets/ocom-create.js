/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

/*** DEPRECATED IN FAVOR OF OCOM-UPDATE.ALT.JS ***/
/*
 * Needs the following scope variables to be defined in the main controller:
 * - modelName
 * - form
 * - formState
 * - api - derived from dataService.getApi
 * - item
 * Note: As for new projects, it is recommended to use ocom-update-alt
 * */
(function () {
    angular
        .module('app.ocom')
        .directive('ocomCreate', function () {
            return {
                restrict: 'EA',
                transclude: true,
                templateUrl: 'js/ocom/widgets/ocom-create.html',
                controller: function ($scope, $state, alerts, $localStorage) {

                    function saveErrorCallback(response) {
                        console.log(response);

                        $scope.item["_errors"] = response.data;

                        $scope.formState.saving = false;
                        alerts.error('Something went wrong. Please try again.', true);
                    }

                    $scope.doSave = function (item, success) {
                        $scope.formState.saving = true;
                        alerts.clearMessages();

                        if ($scope.validateItem(item)) {
                            var obj = new $scope.api(item);

                            // offline
                            //var jobjson = angular.toJson(obj);
                            // var instance = {};
                            // instance.data = $localStorage.getItem(jobjson);
                            // console.log(instance.data);
                            $localStorage.list = obj;
                            console.log($localStorage.list);

                            obj.$save(function (response) {
                                $scope.formState.saving = false;
                                $scope.item = {};
                                alerts.success(response.id + ' created.', true);
                                success(response.id);
                            }, saveErrorCallback);
                        } else {
                            alerts.showNow();
                            $scope.formState.saving = false;
                        }

                    };

                    $scope.create = function (item) {
                        $scope.doSave(item, function (itemId) {
                            $scope.form.$setPristine();
                            $state.go($scope.modelName + '.edit', {id: itemId});
                        });
                    };

                    $scope.createAndClose = function (item) {
                        $scope.doSave(item, function () {
                            $scope.form.$setPristine();
                            $scope.close();
                        });
                    };

                    $scope.createAndNew = function (item) {
                        $scope.doSave(item, function () {
                            $scope.form.$setPristine();
                            $state.go($scope.modelName + '.create', {}, {reload:true});
                        });
                    };

                    $scope.close = function (item) {
                        var goto = $scope.nextView || $scope.modelName + '.list';
                        var params = $scope.nextViewParams || {limit: 10, offset: 0};
                        $state.go(goto, params);
                    };

                    //TODO: REFACTOR!
                    $scope.toggleLock = toggleLock;

                    function toggleLock() {
                        if (!$scope.item.locked) {
                            $scope.item.locked = true;
                            $scope.create($scope.item);
                        } else {
                            $scope.item.locked = !$scope.item.locked;
                        }

                    }
                }
            }
        });
})();
