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
        .factory('dataService', dataService); /* Old Original Service - need to migrate off it */

    /**
     * Data communication service with the Django (DRF) backend
     * @param {object} $state Angular $state provider
     * @param {object} $filter Angular $filter provider
     * @param {object} $localStorage ng-storage $localStorage service {@link https://www.npmjs.com/package/ng-storage}
     * @param {object} $window Angular $window provider
     * @param {object} alerts Local alert messages provider
     * @param {object} SweetAlert SweetAlert popup provider
     * @param {object} dataAPIService dataAPIService provider
     * @param {object} formStateService formStateService provider
     */
    function dataService($state, $filter, $localStorage, $window, alerts, SweetAlert, dataAPIService, formStateService) {
        var _generalApiBaseUrl = '/api/';
        var _interrupt = false;
        var _api, _form, _scope;
        var _normalizedDateFormat = 'YYYY-MM-DD';

        // cache functions require the use of the Hash model and the presence of a rest API from the hash_api url
        return {
            interrupt: _interrupt,
            getApi: getApi, /* Please migrate to using getDataApi */
            setScope: setScope,
            setForm: setForm,
            setReferenceApi: setApi,
            saveError: saveError,
            createItem: createItem,
            saveItem: saveItem,
            deleteItem: deleteItem,
            restoreItem: restoreItem,
            confirmSave: confirmSave,
            closeForm: close,
            setGeneralApiBaseUrl: setGeneralApiBaseUrl,
            applyFilters: applyFilters,
            getListOptions: getListOptions,
            normalizedDate: normalizedDate,

            /* Migrate to using FormStateService instead */
            setLoaded:formStateService.setLoaded,
            isLoaded: formStateService.isLoaded,
            formState: formStateService.getFormState,
            setFormState: formStateService.setFormState,
            resetFormState: formStateService.resetFormState
        };

        /**
         * Set General Api Base URL
         * @param {string} url: the general url address to set
         */
        function setGeneralApiBaseUrl (url) {
            console.error ("Please don't use setGeneralApiBaseUrl. Please use new getDataApi instead");

            _generalApiBaseUrl = url;
        }


        /**
         * Filter data based on property equal to value
         * @param {Array} data an Array containing the data to filter
         * @param {string} property the name of the property to check
         * @param {string} value the value of the property to compare
         * @returns {Array} the filtered data
         */
        function filterPropertyEquals (data, property, value) {
            var filteredData = [];

            if (data.constructor === Array) {
                angular.forEach(data, function (item) {
                    //noinspection JSUnresolvedVariable
                    if (angular.isDefined(item[property])) {
                        //noinspection JSUnresolvedVariable
                        if (item[property] === value) {
                            filteredData.push(item);
                        }
                    }
                });
            }
            return filteredData;
        }

        /**
         * Filter data based on sub-property equal to value
         * @param {Array} data an Array containing the data to filter
         * @param {string} property the name of the property to check
         * @param {string} sub the name of the sub-property to check
         * @param {string} value the value of the sub-property to compare
         * @returns {Array} the filtered data
         */
        function filterSubPropertyEquals (data, property, sub, value) {
            var filteredData = [];

            if (data.constructor === Array) {
                angular.forEach(data, function (item) {
                    //noinspection JSUnresolvedVariable
                    if (angular.isDefined(item[property]) && angular.isDefined(item[property][sub])) {
                        //noinspection JSUnresolvedVariable
                        if (item[property][sub] === value) {
                            filteredData.push(item);
                        }
                    }
                });
            }
            return filteredData;
        }

        /**
         * Filter data based on Active End Date
         * @param {Array} data an Array containing the data to filter
         * @returns {Array} the filtered data
         */
        function filterActiveDate (data) {
            if (data.constructor === Array) {
                var filteredData = [];

                //noinspection JSUnusedLocalSymbols
                angular.forEach(data, function (item, key) {
                    //noinspection JSUnresolvedVariable
                    if (angular.isDefined(item.active_start_date) && angular.isDefined(item.active_end_date)) {
                        //noinspection JSUnresolvedVariable,JSValidateTypes
                        if (item.active_end_date !== null && $filter('amDifference')(item.active_end_date, null) < -60) {
                            console.log("Filtered Item due to active end date:", item);
                        } else {
                            filteredData.push(item);
                        }
                    } else {
                        filteredData.push(item);
                    }
                });
                return filteredData;
            } else {
                // do nothing
                return data;
            }
        }

        /**
         * Apply filters on data
         * @param {Array} data the content to filter
         * @param {object} params general parameters
         * @returns {Array}
         */
        function applyFilters (data, params) {
            var filteredData = angular.copy(data);
            var filters;

            if (angular.isDefined(params.filter)) {
                if (params.filter.constructor === Array) {
                    filters = params.filter;
                } else {
                    filters = [params.filter];
                }
            }

            angular.forEach(filters, function (filter) {
                if (filter === 'active') {
                    filteredData = filterActiveDate(filteredData);
                } else {
                    // up to two-levels deep filter search
                    for (var name in filter) {
                        if (filter.hasOwnProperty(name)) {
                            var subFilter = filter[name];

                            if (subFilter.constructor === {}.constructor) {
                                for (var subName in subFilter) {
                                    if (subFilter.hasOwnProperty(subName)) {
                                        filteredData = filterSubPropertyEquals(filteredData, name, subName,
                                            subFilter[subName]);
                                    }
                                }
                            } else {
                                filteredData = filterPropertyEquals(filteredData, name, subFilter);
                            }
                        }
                    }
                }
            });
            return filteredData;
        }

        function getApi (model) {
            // Note: data is ideally not filtered out as we rely Angular/JS on that regard

            console.log("This is the OLD API - please convert to the getDataApi");

            if (_interrupt) {
                return null;
            }

            formStateService.setLoaded(model, false);

            //noinspection JSValidateTypes
            return dataAPIService.getDataApi(_generalApiBaseUrl, model); //for backwards compatibility
        }

        /**
         * Return default list options to Ajax backend
         */
        function getListOptions() {
            return {
                total: 0,
                currentPage: 1,
                filter: $state.params.filter || "active",
                sort: $state.params.sort || "",
                order: $state.params.order || "asc",
                q: $state.params.q || "",
                searchField: $state.params.searchField || "",
                ordering: $state.params.ordering || "",
                limit: parseInt($state.params.limit) || 10,
                offset: parseInt($state.params.offset) || 0
            }
        }

        /**
         * Set scope reference
         * @param {object} controllerScope the $scope reference from the controller accessing widgetService
         */
        function setScope (controllerScope) {
            console.log("Scope: ", controllerScope);
            _scope = controllerScope;
            _scope.skipConfirm = false;
        }

        /**
         * Set Form reference
         * @param {object} sourceForm the Form object to use
         */
        function setForm (sourceForm) {
            _form = sourceForm;
        }

        /**
         * Set Current API reference
         * @param {object} sourceApi the API object to use
         */
        function setApi (sourceApi) {
            _api = sourceApi;
        }

        /**
         * Callback function for saving error message to scope
         * @param {object} response the API response
         */
        function saveError (response) {
            console.log("ERROR", response);
            _scope.item['_errors'] = response.data;
            formStateService.setFormState({
                saving: false,
                gotError: true,
                invalid: false,
                saveOk: false
            });
            alerts.error("Something went wrong. Please try again.", true);
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
                close();
            } else {
                _form.$setPristine();
            }
        }

        function restoreSuccess (data, message, closeForm) {
            if (!angular.isDefined(message)) {
                message = "Item was restored.";
            }
            console.log("Restored item index: ", data.id, message);
            alerts.warning(message, true);
            formStateService.setFormState({
                deleting: false,
                gotError: false,
                deleteOk: true
            });

            // close unless explicitly specified not to
            if (closeForm || true) {
                close();
            } else {
                _form.$setPristine();
            }
        }

        function createItem (item, validateCallback, successCallback, customSuccessMessage) {
        /**
         * Perform create operation on an item using the set API
         * @param {object} item the item to save (must conform to the API's format)
         * @param {function} validateCallback the callback function to run prior to saving the item
         * @param {function} successCallback the callback function to run when save is successful
         * @param {string} customSuccessMessage Display a custom success message alert or set to false to suppress it
         */

            if (_api) {
                formStateService.setFormState({
                    saving: true,
                    gotError: false,
                    invalid: false,
                    saveOk: false
                });
                alerts.clearMessages();
                console.log("Creating item...", item);
                if (typeof validateCallback === 'function' && angular.isDefined(_api) && validateCallback(item)) {
                    var obj = new _api(item);

                    obj.$save(function (response) {
                        formStateService.setFormState({
                            saving: false,
                            gotError: false,
                            invalid: false,
                            saveOk: true
                        });
                        // we need to clear the item and probably refresh it later
                        _scope.item = {};
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
            if (_api) {
                formStateService.setFormState({
                    saving: true,
                    gotError: false,
                    invalid: false,
                    saveOk: false
                });
                alerts.clearMessages();
                console.log("Saving item...", item);
                if (typeof validateCallback === 'function' && angular.isDefined(_api) && validateCallback(item)) {
                    _api.update({id: $state.params.id}, new _api(item), function (response) {
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
         * Perform delete operation on an item using the set API
         * @param {object} item the item to delete (must conform to the API's format)
         * @param {string} deletePrompt the warning popup message to display when attempting to delete data
         * @param {string} successMessage the success message to display when data is deleted
         */
        function deleteItem(item, deletePrompt, successMessage) {
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
                    _scope.skipConfirm = true;
                    var obj = new _api(item);
                     //noinspection JSUnresolvedFunction
                    obj.$delete(function (data) {
                         deleteSuccess(data, successMessage);
                    }, function (err) {
                         console.log("Delete ERROR", err);
                         formStateService.setFormState({
                             deleting: false,
                             gotError: true
                         });
                    });
                }
            });
        }

        /**
         * Perform restore/undelete operation on an item using the set API
         * @param {object} item the item to delete (must conform to the API's format)
         * @param {string} restorePrompt the warning popup message to display when attempting to restore data
         * @param {string} restoreSuccessMessage the success message to display when data is restored
         */
        function restoreItem(item, restorePrompt, restoreSuccessMessage) {
            SweetAlert.swal({
                title: "Are you sure?",
                text: restorePrompt || "Are you sure you want to restore this?",
                type: "warning",
                showCancelButton: true,
                confirmButtonColor: "#DD6B55",
                confirmButtonText: "Yes, restore it!",
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
                    _scope.skipConfirm = true;
                    item.active_end_date = null;
                    _api.update({id: $state.params.id}, new _api(item), function (data) {
                        restoreSuccess(data, restoreSuccessMessage);
                    }, function (err) {
                        console.log("Restore ERROR", err);
                        formStateService.setFormState({
                            deleting: false,
                            gotError: true
                        });
                    });
                }
            });
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

            if (typeof _scope.successSaveItem === 'function') {
                _scope.successSaveItem(item, created);
            }
            _form.$setPristine();
            if (forward && angular.isDefined(item.id)) {
                $state.go(getModelUrl(_url), {id: item.id, skip: true}, {reload: true});
            }
        }

        /**
         * Return the model url from the given scope and base
         */
        function getModelUrl (baseUrl) {
            var _url = angular.isDefined(baseUrl) ? baseUrl : 'list';

            return _scope.modelName + '.' + _url;
        }

        /**
         * Close current form and proceed to the parent view
         */
        function close (url) {
            var returnUrl;

            if (_scope.closeRedirect) {
                returnUrl = _scope.closeRedirect;
            } else {
                if (_scope.nextView) {
                    returnUrl = _scope.nextView;
                } else if (angular.isDefined($localStorage.lastLink) &&
                    $window.location.href !== $localStorage.lastLink) {
                    console.log("Proceeding to...", $localStorage.lastLink);
                    $window.location.href = $localStorage.lastLink;
                    return;
                } else if (angular.isDefined(_scope.modelName)) {
                    returnUrl = getModelUrl(url);
                }
            }

            if (returnUrl) {
                var params = _scope.nextViewParams || {limit: 10, offset: 0};

                $state.go(returnUrl, params);
            } else {
                console.log("Error: no specified return path.")
            }

        }

        /***
         * Normalize date going to DRF/backend (Note: requires moment.js)
         * @param {string} dateString the date string to normalize / convert
         * @returns {string} the normalized string
         */
        function normalizedDate (dateString) {
            var theDate = (dateString) ? new Date(dateString) : new Date();

            return moment(theDate).format(_normalizedDateFormat)
        }


    }
})();
