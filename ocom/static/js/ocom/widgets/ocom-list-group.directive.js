/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

/*
 * Needs the following scope variables to be defined in the main controller:
 * - modelName
 * - list
 * - listOptions
 * - maxRanges
 * - fields
 * - filters
 * */
angular
    .module('app.ocom')
    .directive('ocomListGroup', function () {
        return {
            restrict: 'EA',
            transclude: {
                'filter':'?filter',
                'filterRight':'?filterRight',
                'toolbar':'?toolbar',
                'list': 'list'
            },
            templateUrl: 'js/ocom/widgets/ocom-list-group.html',
            link: function(scope, elem, attrs) {
                scope.hideNewButton = scope.$eval(attrs.hideNewButton) || false;
                scope.destination = attrs.destination || "";
            },
            controller: function ($scope, $sessionStorage, stateStorage) {
                $scope.refreshList = refreshList;
                $scope.changeOptionAndRefresh = changeOptionAndRefresh;
                $scope.changeLimit = changeLimit;
                $scope.selectPage = selectPage;
                $scope.pageChanged = pageChanged;

                $scope.$watch('listOptions', function (list) {
                    if (angular.isDefined($scope.altFilters) && $scope.altFilters.length && angular.isDefined(list)) {
                        var filter = _.find($scope.altFilters, function (item) {
                            // noinspection JSUnresolvedVariable
                            return item.id.toString() === list.filter;
                        });
                        if (filter) {
                            $scope.backgroundColour = filter.backgroundColour;
                            $scope.foregroundColour = filter.foregroundColour;
                        } else {
                            $scope.backgroundColour = '#dddddd';
                            $scope.foregroundColour = '#000000';
                        }
                    } else {
                        $scope.backgroundColour = '#fff';
                        $scope.foregroundColour = '#000';
                    }
                });

                function refreshList (except) {
                    var options = angular.copy($scope.listOptions);
                    var destination = ($scope.destination) ? $scope.destination : $scope.modelName + ".list";
                    // noinspection JSUnresolvedVariable
                    var finalExcept = angular.isDefined(except) ?
                        angular.copy(except) : (angular.isDefined($scope.exceptSearch) ? $scope.exceptSearch : []);

                    finalExcept = _.union(finalExcept, ['total', 'currentPage']);
                    for (var i = 0; i < finalExcept.length; i++) {
                        delete options[finalExcept[i]];
                    }
                    stateStorage.storeStateThenGo(destination, options, true);
                }

                function changeOptionAndRefresh (field, value) {
                    $scope.listOptions[field] = value;
                    $scope.refreshList(); // Update When changed.
                }

                function changeLimit (limit) {
                    $scope.listOptions.offset = 0;
                    $scope.changeOptionAndRefresh("limit", limit);
                }

                function selectPage (page) {
                    $scope.changeOptionAndRefresh("offset", $scope.listOptions.limit * (page - 1));
                }

                function pageChanged () {
                    $scope.selectPage($scope.listOptions.currentPage);
                }
            }
        }
    });
