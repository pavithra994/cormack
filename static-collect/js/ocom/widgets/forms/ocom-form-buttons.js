/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

/**
 * Alt version of ocom-update.js and ocom-update.alt.js
 *
 * TODO Move all UI stuff to this directive out of DataService
 * User dataApi
 */
(function () {
    angular
        .module('app.ocom')
        .directive('ocomFormButtons', [function () {
            return {
                restrict: 'EA',
                transclude: true,
                templateUrl: 'js/ocom/widgets/forms/ocom-form-buttons.html',
                link: function(scope, elem, attrs) {
                    scope.closeRedirect =  attrs.closeRedirect || '';
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
                    scope.$watch('item.is_active', function (item) {
                        updateButtons();
                    });

                    // TEMP FIX
                    scope.$watch('item.isActive', function (item) {
                        updateButtons();
                    });

                    function updateButtons () {
                        scope.hideDeleteButton = scope.$eval(attrs.hideDeleteButton) || scope.create;
                        scope.showRestoreButton = scope.$eval(attrs.showRestoreButton) || false;
                        scope.hideUpdateButton = scope.$eval(attrs.hideUpdateButton) || false;
                    }
                },
                controller: function ($scope, $state, $localStorage, $window, roleService, alerts, formStateService,
                                      SweetAlert) {
                    var formSettings = roleService.getFormSettings();

                    $scope.formState = formStateService.formState;

                    if (angular.isDefined(formSettings[$scope.modelName])) {
                        $scope.form_settings = formSettings[$scope.modelName];
                    }


                    function createItem (item, validateCallback, successCallback, customSuccessMessage) {
                    /**
                     * Perform create operation on an item using the set API
                     * @param {object} item the item to save (must conform to the API's format)
                     * @param {function} validateCallback the callback function to run prior to saving the item
                     * @param {function} successCallback the callback function to run when save is successful
                     * @param {string} customSuccessMessage Display a custom success message alert or set to false to suppress it
                     */

                        if ($scope.data_api) {
                            formStateService.setFormState({
                                saving: true,
                                gotError: false,
                                invalid: false,
                                saveOk: false
                            });
                            alerts.clearMessages();
                            console.log("Creating item...", item);
                            if (typeof validateCallback === 'function' && angular.isDefined($scope.data_api) && validateCallback(item)) {
                                $scope.data_api.createItem(item,  function (response) {
                                    formStateService.setFormState({
                                        saving: false,
                                        gotError: false,
                                        invalid: false,
                                        saveOk: true
                                    });
                                    // we need to clear the item and probably refresh it later
                                    $scope.item = {};
                                    if (typeof customSuccessMessage === "string") {
                                        if (customSuccessMessage !== "") {
                                            alerts.success(customSuccessMessage, true);
                                        }
                                    } else {
                                        alerts.success(response.id + " created", true);
                                    }
                                    if (typeof successCallback === 'function') {
                                        successCallback(response);
                                    }
                                }, saveError);
                            } else {
                                alerts.showNow();
                                formStateService.setFormState({
                                    saving: false,
                                    gotError: false,
                                    invalid: true,
                                    saveOk: false
                                });
                            }
                        }
                    }

                    /**
                     * Perform update operation on an item using the set API
                     * @param {object} item the item to save (must conform to the API's format)
                     * @param {function} validateCallback the callback function to run prior to saving the item
                     * @param {function} successCallback the callback function to run when save is successful
                     * @param {string} customSuccessMessage Display a custom success message alert or set to false to suppress it
                     */
                    function saveItem (item, validateCallback, successCallback, customSuccessMessage) {
                        if ($scope.data_api) {
                            formStateService.setFormState({
                                saving: true,
                                gotError: false,
                                invalid: false,
                                saveOk: false
                            });
                            alerts.clearMessages();
                            console.log("Saving item...", item);
                            if (typeof validateCallback === 'function' && angular.isDefined($scope.data_api) && validateCallback(item)) {
                                $scope.data_api.updateItem($state.params.id, item, function (response) {
                                    formStateService.setFormState({
                                        saving: false,
                                        gotError: false,
                                        invalid: false,
                                        saveOk: true
                                    });
                                    console.log("Item saved", response);

                                    if (typeof customSuccessMessage === "string") {
                                        if (customSuccessMessage !== "") {
                                            alerts.success(customSuccessMessage, true);
                                        }
                                    } else {
                                        alerts.success(response.id + " updated", true);
                                    }
                                    if (typeof successCallback === 'function') {
                                        successCallback(response);
                                    }
                                }, saveError);
                            } else {
                                alerts.showNow();
                                formStateService.setFormState({
                                    saving: false,
                                    gotError: false,
                                    invalid: true,
                                    saveOk: false
                                });
                            }
                        }
                    }
                    /**
                     * Return the model url from the given scope and base
                     */
                    function getModelUrl (baseUrl) {
                        var _url = angular.isDefined(baseUrl) ? baseUrl : 'list';

                        return $scope.modelName + '.' + _url;
                    }

                    function doUpdate (item, successMessage, callback) {
                        if (typeof $scope.preSaveItem === 'function') {
                            item = $scope.preSaveItem(item);
                        }
                        // for some reason, $submitted does not get triggered so we set it manually
                        $scope.form.$setSubmitted();
                        if ($scope.create) {
                            createItem(item, $scope.validateItem, function (response) {
                                confirmSave(response, true, true);
                                callback(response);
                            }, successMessage);
                        } else {
                            saveItem(item, $scope.validateItem, function (response) {
                                confirmSave(response, true, false);
                                callback(response);
                            }, successMessage);
                        }
                    }

                    /**
                     * Close current form and proceed to the parent view
                     */
                    function doCloseForm (url) {
                        var returnUrl;

                        if ($scope.closeRedirect) {
                            console.log("CLOSE REDIRECT", $scope.closeRedirect);
                            returnUrl = $scope.closeRedirect;
                        } else {
                            if ($scope.nextView) {
                                returnUrl = $scope.nextView;
                            } else if (angular.isDefined($localStorage.lastLink) &&
                                $window.location.href !== $localStorage.lastLink) {
                                console.log("Proceeding to...", $localStorage.lastLink, $window.location.href);
                                $window.location.href = $localStorage.lastLink;
                                return;
                            } else if (angular.isDefined($scope.modelName)) {
                                returnUrl = getModelUrl(url);
                            }
                        }

                        if (returnUrl) {
                            var params = $scope.nextViewParams || {limit: 10, offset: 0};

                            $state.go(returnUrl, params);
                        } else {
                            console.log("Error: no specified return path.")
                        }

                    }

                    $scope.update = function (item, successMessage) {
                        doUpdate(item, successMessage, function (response) {
                           // Nothing
                        });
                    };

                    $scope.updateAndClose = function (item, successMessage) {
                        doUpdate(item, successMessage, function (response) {
                            doCloseForm();
                        });
                    };

                    $scope.close = function () {
                        doCloseForm();
                    };


                    /**
                     * Perform delete operation on an item using the Dataset API
                     * @param {object} item the item to delete (must conform to the API's format)
                     * @param {string} deletePrompt the warning popup message to display when attempting to delete data
                     * @param {string} successMessage the success message to display when data is deleted
                     */
                    $scope.updateAndDelete = function (item, deletePrompt, successMessage) {
                        SweetAlert.swal({
                            title: "Are you sure?",
                            text: deletePrompt || "Are you sure you want to delete this?",
                            type: "warning",
                            showCancelButton: true,
                            confirmButtonColor: "#DD6B55",
                            confirmButtonText: "Yes, delete it!",
                            closeOnConfirm: true
                        },
                        function (isConfirm) {
                            if (isConfirm) {
                                formStateService.setFormState({
                                    deleting: true,
                                    gotError: false,
                                    invalid: false,
                                    deleteOk: false
                                });
                                $scope.data_api.delete(item, function (data) {
                                    deleteSuccess(data, successMessage || "Item deleted");
                                }, function(err){
                                    console.log("Delete ERROR", err);
                                    formStateService.setFormState({
                                         deleting: false,
                                         gotError: true
                                    });
                                });
                            }
                        });
                    };

                     function restoreSuccess (data, message, closeForm) {
                        if (!angular.isDefined(message)) {
                            message = "Item was restored.";
                        }
                        console.log("Restored item index: ", data.id, message);
                        alerts.warning(message, true);
                        formStateService.setFormState({
                            restoring: false,
                            deleteOk: true
                        });

                        // close if explicitly specified  to
                        if (closeForm || false) {
                            doCloseForm();
                        } else {
                            $scope.form.$setPristine();
                        }
                    }

                    /**
                     * Perform Restore operation on an item using the Dataset API
                     * @param {object} item the item to restore (must conform to the API's format)
                     * @param {string} restorePrompt the warning popup message to display when attempting to Restore data
                     * @param {string} restoreSuccessMessage the success message to display when data is restored
                     */
                    $scope.updateAndRestore = function (item, restorePrompt, restoreSuccessMessage) {
                         SweetAlert.swal({
                            title: "Are you sure?",
                            text: restorePrompt || "Are you sure you want to restore this?",
                            type: "warning",
                            showCancelButton: true,
                            confirmButtonColor: "#DD6B55",
                            confirmButtonText: "Yes, Restore it!",
                            closeOnConfirm: true
                        },
                        function (isConfirm) {
                            if (isConfirm) {
                                formStateService.setFormState({
                                    restoring: true,
                                    gotError: false,
                                    invalid: false,
                                    deleteOk: false
                                });
                                item.active_end_date = null; // Clear End Date

                                $scope.data_api.updateItem(item.id, item, function (data) {
                                    restoreSuccess(data, restoreSuccessMessage || "Item Restored", true);
                                }, function(err){
                                    console.log("Restore ERROR", err);
                                    formStateService.setFormState({
                                         restoring: false,
                                         gotError: true
                                    });
                                });
                            }
                        });
                    };

                    /** ===================================================================
                     * Call Back functions when Data saved etc - Let the user know how we went
                     * ===================================================================
                     */

                    /**
                     * Callback function for saving error message to scope
                     * @param {object} response the API response
                     */
                    function saveError (response) {
                        console.log("ERROR", response);
                        $scope.item['_errors'] = response.data;
                        formStateService.setFormState({
                            saving: false,
                            gotError: true,
                            invalid: false,
                            saveOk: false
                        });
                        alerts.error("Something went wrong. Please check all your data and try again.", true);
                    }


                    function deleteSuccess (data, message, closeForm) {
                        if (!angular.isDefined(message)) {
                            message = "Item was deleted.";
                        }
                        console.log("Deleted item index: ", data.id, message);
                        alerts.warning(message, true);
                        formStateService.setFormState({
                            deleting: false,
                            deleteOk: true
                        });

                        // close unless explicitly specified not to
                        if (closeForm || true) {
                            doCloseForm();
                        } else {
                            $scope.form.$setPristine();
                        }
                    }

                    /**
                     * Confirm saving of item
                     * @param {object} item the item to edit / open a form with
                     * @param {boolean} forward if true, proceed to open item in a form
                     * @param {boolean} created if true, signifies that the item was created
                     * @param {string} url the base url of the form to use if forward is true (optional)
                     */
                    function confirmSave (item, forward, created, url) {
                        var _url = angular.isDefined(url) ? url : 'edit';

                        if (typeof $scope.successSaveItem === 'function') {
                            $scope.successSaveItem(item, created);
                        }
                        // for some reason form does not trigger submitted so we trigger it manually
                        $scope.form.$setPristine();
                        if (forward && angular.isDefined(item.id)) {
                            $state.go(getModelUrl(_url), {id: item.id, skip: true}, {reload: true});
                        }
                    }



                    /** ===================================================================
                     * Button and UI State Functions for Directive
                     * ===================================================================
                     */
                    function _isEdited (form) {
                        if ($scope.skipDirtyCheck) {
                            return true;
                        } else {
                            if (angular.isDefined(form)) {
                                return form.$dirty;
                            }
                        }
                        return false;
                    }

                    $scope.formDisabled = function () {
                        return $scope.form.$invalid || $scope.formState.formState('saving') ||
                            $scope.formState.formState('loading') || !$scope.form.$dirty
                    };

                    $scope.disableSave = function(form) {
                        return form.$invalid || $scope.formState('saving') ||
                            $scope.formState('loading') || !_isEdited(form)
                    };

                    $scope.disableDelete = function () {
                        return $scope.formState('loading') || $scope.formState('saving')
                    };

                    $scope.showDelete = function () {
                        return !$scope.hideDeleteButton && !$scope.read_only;
                    };
                }
            }
        }]);
})();
