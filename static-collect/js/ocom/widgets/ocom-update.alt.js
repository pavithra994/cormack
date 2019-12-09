/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

/**
 * Alt version of ocom-update.js
 */
(function () {
    angular
        .module('app.ocom')
        .directive('ocomUpdate', function () {
            return {
                restrict: 'EA',
                transclude: true,
                templateUrl: 'js/ocom/widgets/ocom-update.alt.html',
                link: function(scope, elem, attrs) {
                    scope.closeRedirect =  scope.$eval(attrs.closeRedirect) || '';
                    scope.create = scope.$eval(attrs.create) || false;
                    scope.skipDirtyCheck = scope.$eval(attrs.skipDirtyCheck) || false;
                    scope.sidebar = scope.$eval(attrs.sidebar) || false;

                    if (angular.isDefined(scope.refreshUpdateTable)) {
                        scope.hideDeleteButton = true;
                        scope.showRestoreButton = false;
                        scope.hideUpdateButton = true;
                    } else {
                        updateButtons();
                    }

                    scope.closeLabel = angular.isDefined(attrs.closeLabel) ? attrs.closeLabel : "Close";
                    if (scope.create) {
                        scope.updateLabel = angular.isDefined(attrs.updateLabel) ?
                            attrs.updateLabel.toString() : "Create";
                        scope.updateCloseLabel = angular.isDefined(
                            attrs.updateCloseLabel) ? attrs.updateCloseLabel : "Create & Close";
                    } else {
                        scope.updateLabel = angular.isDefined(attrs.updateLabel) ?
                            attrs.updateLabel.toString() : "Update";
                        scope.updateCloseLabel = angular.isDefined(
                            attrs.updateCloseLabel) ? attrs.updateCloseLabel : "Update & Close";
                        scope.deleteLabel = angular.isDefined(attrs.deleteLabel) ? attrs.deleteLabel : "Delete";
                        scope.restoreLabel = angular.isDefined(attrs.restoreLabel) ? attrs.restoreLabel : "Restore";
                    }
                    if (angular.isDefined(attrs.deletePrompt)) {
                        scope.deletePrompt = attrs.deletePrompt;
                    }
                    if (angular.isDefined(attrs.deleteSuccessMessage)) {
                        scope.deleteSuccessMessage = attrs.deleteSuccessMessage;
                    }
                    if (angular.isDefined(attrs.saveSuccessMessage)) {
                        scope.saveSuccessMessage = attrs.saveSuccessMessage;
                    }
                    if (angular.isDefined(attrs.restorePrompt)) {
                        scope.restorePrompt = attrs.restorePrompt;
                    }
                    if (angular.isDefined(attrs.restoreSuccessMessage)) {
                        scope.restoreSuccessMessage = attrs.restoreSuccessMessage;
                    }

                    scope.$watch('refreshUpdateTable', function (go) {
                        if (go) {
                            updateButtons();
                        }
                    });

                    // TEMP FIX
                    scope.$watch('item', function (item) {
                        if (angular.isDefined(item.is_active)) {
                            updateButtons();
                        }
                    });

                    function updateButtons () {
                        scope.hideDeleteButton = scope.$eval(attrs.hideDeleteButton) || scope.create;
                        scope.showRestoreButton = scope.$eval(attrs.showRestoreButton) || false;
                        scope.hideUpdateButton = scope.$eval(attrs.hideUpdateButton) || false;
                    }
                },
                controller: function ($scope, $state, dataService, roleService) {
                    var formSettings = roleService.getFormSettings();

                    $scope.formState = dataService.formState;
                    dataService.setReferenceApi($scope.api);
                    dataService.setForm($scope.form);
                    dataService.setScope($scope);

                    if (angular.isDefined(formSettings[$scope.modelName])) {
                        $scope.form_settings = formSettings[$scope.modelName];
                    }
                    $scope.update = function (item, successMessage) {
                        if (typeof $scope.preSaveItem === 'function') {
                            item = $scope.preSaveItem(item);
                        }

                        if ($scope.create) {
                            dataService.createItem(item, $scope.validateItem, function (response) {
                                dataService.confirmSave(response, true, true);
                            }, successMessage);
                        } else {
                            dataService.saveItem(item, $scope.validateItem, function (response) {
                                dataService.confirmSave(response, true, false);
                            }, successMessage);
                        }
                    };

                    $scope.isEdited = function () {
                        if ($scope.skipDirtyCheck) {
                            return true;
                        } else {
                            if (angular.isDefined($scope.form)) {
                                return $scope.form.$dirty;
                            }
                        }
                        return false;
                    };

                    $scope.updateAndClose = function (item, successMessage) {
                        if (typeof $scope.preSaveItem === 'function') {
                            item = $scope.preSaveItem(item);
                        }
                        if ($scope.create) {
                            dataService.createItem(item, $scope.validateItem, function (response) {
                                dataService.confirmSave(response, true, false);
                                dataService.closeForm();
                            }, successMessage);
                        } else {
                            dataService.saveItem(item, $scope.validateItem, function (response) {
                                dataService.confirmSave(response, false, false);
                                dataService.closeForm();
                            }, successMessage);
                        }
                    };

                    $scope.updateAndDelete = function (item, deletePrompt, successMesssage) {
                        dataService.deleteItem(item, deletePrompt, successMesssage);
                    };

                    $scope.updateAndRestore = function (item, restorePrompt, restoreSuccessMesssage) {
                        dataService.restoreItem(item, restorePrompt, restoreSuccessMesssage);
                    };

                    $scope.close = function () {
                        dataService.closeForm();
                    };

                    $scope.formDisabled = function () {
                        return $scope.form.$invalid || dataService.formState('saving') ||
                            dataService.formState('loading') || !$scope.form.$dirty
                    };

                    $scope.disableSave = function(form) {
                        return form.$invalid || dataService.formState('saving') ||
                            dataService.formState('loading') || !$scope.isEdited();
                    };

                    $scope.disableDelete = function () {
                        return dataService.formState('loading') || dataService.formState('saving')
                    };

                    $scope.showDelete = function () {
                        return !$scope.hideDeleteButton && !$scope.read_only;
                    };

                    $scope.viewOnly = function (item) {
                        if (!$scope.item.isActive && item !== 'active_end_date') {
                            return true;
                        }
                        return dataService.formState('saving') || dataService.formState('loading');
                        /*
                        if (roleService.isAccessible('job', $scope.route, 'update', item)) {
                            return dataService.formState('saving') || dataService.formState('loading');
                        } else {
                            return true;
                        }
                        */
                    }
                }
            }
        });
})();
