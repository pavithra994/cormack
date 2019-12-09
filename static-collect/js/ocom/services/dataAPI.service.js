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
        .factory("dataResourceService", ['$rootScope', '$resource', '$localStorage', '$timeout', '$state',
            '$stateParams', 'formStateService',
            function($rootScope, $resource, $localStorage, $timeout, $state, $stateParams, formStateService) {

            return {
                getDataApi:getDataApi
            };

            /**
             * Server error response handler
             * @param {object} response the HTTP response status
             */
            function resourceErrorHandler (response) {
                if (response.status === 403) {
                    $localStorage.isAuthenticated = false;
                    $localStorage.returnToURL = $state.current.name;
                    $localStorage.returnParams = $state.params;

                    //noinspection JSValidateTypes
                    $timeout(function () {
                        // Allow $localStorage digest work. see https://github.com/gsklee/ngStorage#watch-the-watch
                        $state.go("index.login"); // relogin
                    }, 5);
                } else if (response.status === 404) {
                    console.log("State", $state, $stateParams);
                    $rootScope.$broadcast("$Got404Error");
                }
            }

            function responseHandler (response) {
                console.log("API", response.config.model, response.config.method, response.data);
                formStateService.setLoaded(response.config.model, true);
                return response.data;
            }
            /*private*/
            function _getResource(base, model) {
                // Used by OLD getApi and the new getDataApi (until it's replaced)

                return $resource(base + model + '/:id/', {id: '@id'}, {
                    'list': {
                        method: 'GET',
                        model: model,
                        interceptor: {
                            response: responseHandler,
                            responseError: resourceErrorHandler
                        }
                    },
                    'update': {
                        method: 'PUT',
                        model: model,
                        interceptor: {
                            response: responseHandler,
                            responseError: resourceErrorHandler
                        }
                    },
                    'query': {
                        method: 'GET',
                        model: model,
                        isArray: true,
                        interceptor: {
                            response: responseHandler,
                            responseError: resourceErrorHandler
                        }
                    },
                    'patch': {
                        method: 'PATCH',
                        model: model,
                        interceptor: {
                            response: responseHandler,
                            responseError: resourceErrorHandler
                        }
                    },
                    'action': {
                        method: 'POST',
                        model: model,
                        isArray: false,
                        interceptor: {
                            response: responseHandler,
                            responseError: resourceErrorHandler
                        }
                    }
                });
            }

            function getDataApi(base, modelName) {
                var resource = _getResource(base, modelName);

                return {
                    _getResource:function () {
                        console.log ("Replace this code with code using the methods below");
                        return resource;
                    },
                    list:function (options, successCallback, failureCallback) {
                        resource.list(options, successCallback, failureCallback);
                    },
                    getItem:function (id, successCallback, failureCallback) {
                        resource.list({'id': id}, successCallback, failureCallback);
                    },
                    createItem:function (item, successCallback, failureCallback) {
                        var obj = new resource(item);

                        obj.$save(successCallback, failureCallback);
                    },
                    updateItem:function (id, item, successCallback, failureCallback) {
                        resource.update({'id': id}, new resource(item), successCallback, failureCallback);
                    },
                    patchItem:function (item, successCallback, failureCallback) {
                        var obj = new resource(item);

                        obj.$patch(successCallback, failureCallback);
                    },
                    delete:function (item, successCallback, failureCallback) {
                        var obj = new resource(item);

                        //noinspection JSUnresolvedFunction
                        obj.$delete(successCallback, failureCallback);

                    },
                    query:function (params, successCallback, failureCallback) {
                        resource.query(params, successCallback, failureCallback);
                    },
                    action:function (params, successCallback, failureCallback) {
                        resource.action(params, successCallback, failureCallback);
                    }
                };
            }

        }])
        .factory("offlineDataService", ['$localStorage', '$timeout', 'formStateService', 'ngDexie', 'dataResourceService', '$injector',
            function($localStorage, $timeout, formStateService, ngDexie, dataResourceService, $injector) {
            var OPERATIONS = {
                'UPDATE': 1,
                'CREATE': 2,
                'DELETE': 3,
                'NOOP': 10 /* When it has been CREATED then DELETED on the device it becomes NOOP - this will do nothing */
            };

            function recordLogEntry (logentry) {
                ngDexie.add("synclog", logentry).then (function (newID) {
                        console.log ("SyncLog ID:" + newID);
                    }, function (err) {
                        console.log (err);
                    }
                );
            }

            function recordUpdate(uri, modelName, item) {
                var logEntry = {'uri':uri, 'modelName': modelName, 'modelId': item.id, 'operation': OPERATIONS.UPDATE, 'when': new Date()};
                recordLogEntry (logEntry);
            }

            function recordInsert(uri, modelName, itemID) {
                var logEntry = {'uri':uri, 'modelName': modelName, 'modelId': itemID, 'operation': OPERATIONS.CREATE, 'when': new Date()};
                recordLogEntry (logEntry);
            }

            function recordDelete (uri, modelName, itemID) {
                var logEntry = {'uri':uri, 'modelName': modelName, 'modelId': itemID, 'operation': OPERATIONS.DELETE, 'when': new Date()};
                recordLogEntry (logEntry);
            }

            return {
                list:function (modelName, options, successCallback, failureCallback) {
                    ngDexie.getDb(function (db) {
                        var ctx = db[modelName];
                        var ctx2 = db[modelName];
                        var ordering = '';

                        // for some reason orderBy will drop rows with undefined values for the index so this is
                        // probably a dexie.js bug. Due to ngDexie.js (0.21) lack of support for dexie versions > 1.4.2.
                        // we do this to restore the missing data
                        var restoreDroppedRows = function (data) {
                            if (options.q || !_.isEmpty(options.query)) {
                                console.log("Extracted Rows", modelName, data);
                                successCallback({'count': data.length, 'results': data});
                            } else {
                                ctx2.toArray().then(function (actual_data) {
                                    $timeout(function () {
                                        var reconstruct = actual_data.length !== data.length;
                                        if (reconstruct) {
                                            // we restore some of the lost data
                                            if (ordering === 'DESC') {
                                                // we can't do union directly with actual data as it affects the order
                                                data = _.concat(
                                                    _.reverse(_.differenceWith(actual_data, data, _.isEqual)), data);
                                            } else {
                                                data = _.unionWith(data, actual_data, _.isEqual);
                                            }
                                        }
                                        console.log("Extracted Rows", modelName, data, reconstruct ? "Reconstructed": "");
                                        successCallback({'count': data.length, 'results': data});
                                    });
                                });
                            }
                        };

                        if (options.sort) {
                            ctx = ctx.orderBy(options.sort);
                        }
                        if (options.order) {
                            ordering = options.order.toUpperCase();
                            if (ordering === 'DESC') {
                                ctx = ctx.reverse();
                            }
                        }
                        if (options.q) {
                            var q = _.toUpper(options.q);

                            var isNumber = false; // Assume String
                            var q_num = _.toNumber(options.q);

                            if (_.isFinite(q_num)) {
                                isNumber = true;
                            }

                            ctx = ctx.filter(function (item) {
                                if (isNumber) {
                                    if (options.searchField) {
                                        return item[options.searchField] == q_num;
                                    }
                                    else {
                                        var result = false;
                                        _.mapKeys(item, function (value, key) {
                                            if (_.isFinite(value)) {
                                                if (value == q_num) {
                                                    result = true; // Matches
                                                }
                                            }
                                        });

                                        return result;
                                    }
                                }
                                else { // Match on String
                                    if (options.searchField) {
                                        return _.includes(_.toUpper(item[options.searchField]), q);
                                    }
                                    else {
                                        var result = false;
                                        _.mapKeys(item, function (value, key) {
                                            if (_.isString(value)) {
                                                if (_.includes(_.toUpper(value), q)) {
                                                    result = true; // WE got one!!
                                                }
                                            }
                                        });

                                        return result;
                                    }
                                }
                            });
                        }
                        if (!_.isEmpty(options.query)) {
                            var jsonQuery = options.query;

                            var queryFactory = $injector.get("queryFactory");
                            if (queryFactory) {
                                queryFactory.prepare(jsonQuery);

                                var filterfunction = jsonQuery.filter;

                                if (angular.isDefined(filterfunction)) {
                                    ctx = ctx.filter(filterfunction);
                                }
                            }

                            ctx.toArray().then(function (data) {
                                $timeout(function () {
                                    restoreDroppedRows(data);
                                });
                            });
                        } else {
                            if (angular.isUndefined(ctx) || ctx === null) {
                                if (typeof failureCallback === 'function') {
                                    failureCallback("Cannot find table:" + modelName + " offline");
                                }
                                console.error("Missing table:", modelName);
                            }
                            else {
                                ctx.offset(options.offset).limit(options.limit).toArray().then(function (data) {
                                    restoreDroppedRows(data);
                                });
                            }
                        }
                    }, false);
                },
                getItem:function (modelName, id, successCallback, failureCallback) {
                    ngDexie.get(modelName, parseInt(id)).then (function(data) {
                        successCallback(data);
                    }, function (error) {
                        failureCallback(error)
                    });
                },
                createItem:function (uri, modelName, item, successCallback, failureCallback) {
                    if ('created_date' in item) {
                        item.created_date = new Date(); // Update to NOW

                        if ('modified_date' in item) {
                            item.modified_date = item.created_date;
                        }
                    }

                    ngDexie.put(modelName, item).then (function (newID) {
                            recordInsert(uri, modelName, newID);

                            item.id = newID;
                            successCallback(item)
                        }, failureCallback);
                },
                updateItem:function (uri, modelName, id, item, successCallback, failureCallback) {
                    if ('modified_date' in item) {
                        item.modified_date = new Date(); // Update to NOW
                    }

                    ngDexie.put(modelName, item).then (function (result) {
                        recordUpdate(uri, modelName, item);
                        successCallback(item);
                    }, failureCallback);
                },
                patchItem:function (uri, modelName, item, successCallback, failureCallback) {
                    if ('modified_date' in item) {
                        item.modified_date = new Date(); // Update to NOW
                    }

                    // we use put
                    ngDexie.put(modelName, item).then (function (result) {
                        recordUpdate(uri, modelName, item);
                        successCallback(item);
                    }, failureCallback);
                },
                delete:function (uri, modelName, item, successCallback, failureCallback) {
                    ngDexie.remove(modelName, item.id).then(function () {
                            recordDelete(uri, modelName, item.id);

                            successCallback(item)
                        }, failureCallback);
                },
                query:function (modelName, params, successCallback, failureCallback) {
                    ngDexie.getDb(function (db) {
                        db[modelName].orderBy(params.sort).offset(params.offset).limit(params.limit).toArray().then(function (data) {
                            db[modelName].count().then (function (count) {
                                successCallback({'count':count, 'results': data});
                            });

                        });
                    }, false);
                },
                removeChange: function (change, successCallback, failureCallback) {
                    ngDexie.remove("synclog", change.id).then(successCallback, failureCallback);
                },
                getChanges:function (callback) {
                    ngDexie.list("synclog").then(function(allChanges) {
                        var changes = _.groupBy(allChanges, function (change) {
                           return change.modelName + ":" + change.modelId;
                        });

                        // Get the Higest operation ie Delete before Create before Update
                        _.forIn(changes, function(value, key) {
                            var create = _.find(value, function (o) {
                               return o.operation == OPERATIONS.CREATE;
                            });

                            if (create) {
                                var removed = _.find(value, function (o) {
                                    return o.operation == OPERATIONS.DELETE;
                                });

                                if (removed) {
                                    removed.operation = OPERATIONS.NOOP; // Will do nothing for this operation
                                }
                            }

                            var ids = _.map(value, "id");

                            changes[key] = _.maxBy(value, "operation");

                            changes[key].ids = ids; // Record the OTHER ID's so we can remove them from the SyncLog (maybe)
                            changes[key].selected = changes[key].operation != OPERATIONS.NOOP; // Select for processing..
                        });


                        var filteredChanges = _.sortBy(_.valuesIn(changes), "when"); // or sort by ID??

                        callback(filteredChanges);
                    });
                },
                executeLog:function (syncLogEntry, successCallback, failureCallback) {
                    ngDexie.get(syncLogEntry.modelName, syncLogEntry.modelId).then (function(item) {
                        syncLogEntry.completed = false;

                        if (syncLogEntry.operation == OPERATIONS.NOOP) {
                            syncLogEntry.completed = true;

                            successCallback(syncLogEntry, item);

                            return true;
                        }

                        var dataAPI = dataResourceService.getDataApi(syncLogEntry.uri || "/api/", syncLogEntry.modelName)
                        if (syncLogEntry.operation == OPERATIONS.DELETE) {
                            dataAPI.delete(item, function (done) {
                                syncLogEntry.completed = true;

                                successCallback(syncLogEntry, item);
                            });
                            return true;
                        }

                        // TODO Check and change any foreignKeys pointing to a NEW entry made here.

                        if (syncLogEntry.operation == OPERATIONS.UPDATE) {
                            dataAPI.updateItem(item.id, item, function (done) {
                                syncLogEntry.completed = true;

                                successCallback(syncLogEntry, item);
                            });
                        }
                        else if (syncLogEntry.operation == OPERATIONS.CREATE) {
                            var ourNewID = item.id;

                            delete item.id; // remove the id

                            dataAPI.createItem(item, function (done) {
                                syncLogEntry.new_id = done.id;

                                syncLogEntry.completed = true;

                                successCallback(syncLogEntry, item);
                            });
                        }
                    });
                }
            };
        }])
        .factory("dataAPIService", ['$rootScope', '$resource', '$filter', '$localStorage', '$timeout', '$state',
            '$stateParams', 'formStateService', 'offlineDataService', 'dataResourceService', 'platform',
            function($rootScope, $resource, $filter, $localStorage, $timeout, $state, $stateParams, formStateService,
                     offlineDataService, dataResourceService, platform) {

            /* Use this service for Data processes - it used dataResourceService or offlineDataService */

            var  _interrupt;
            // SW: Not sure what this DOES except stop it returning an API all of a sudden. Added for backward
            // compatibility

            return {
                interrupt: _interrupt,
                getDataApi:getDataApi,
                applyFilters: applyFilters
            };

            function getDataApi(base, modelName) {
                // Returns a "Service" that works like the old $resource.
                // We will be replacing the implementation later at the moment this is just a proxy to $resource.

                if (_interrupt) {
                    return null;
                }

                var resourcedDataService = dataResourceService.getDataApi(base, modelName);

                formStateService.setLoaded(modelName, false);

                return {
                    list:function (options, successCallback, failureCallback) {
                        if (!options) {
                            options = {limit:1000}
                        }
                        if (!('limit' in options)) {
                            options.limit = 1000;
                        }

                        if (platform.isOffline()) {
                            offlineDataService.list(modelName, options, successCallback, failureCallback);
                        }
                        else {
                            resourcedDataService.list(options, successCallback, failureCallback);
                        }
                    },
                    getItem:function (id, successCallback, failureCallback) {
                        if (platform.isOffline()) {
                            offlineDataService.getItem(modelName, id, successCallback, failureCallback);
                        }
                        else {
                            resourcedDataService.getItem(id, successCallback, failureCallback);
                        }
                    },
                    createItem:function (item, successCallback, failureCallback) {
                        if (platform.isOffline()) {
                            offlineDataService.createItem (base, modelName, item, successCallback, failureCallback);
                        }
                        else {
                            resourcedDataService.createItem(item, successCallback, failureCallback);
                        }
                    },
                    updateItem:function (id, item, successCallback, failureCallback) {
                        if (platform.isOffline()) {
                            offlineDataService.updateItem (base, modelName, id, item, successCallback, failureCallback);
                        }
                        else {
                            resourcedDataService.updateItem (id, item, successCallback, failureCallback);
                        }
                    },
                    patchItem:function (item, successCallback, failureCallback) {
                        if (platform.isOffline()) {
                            offlineDataService.patchItem (base, modelName, item, successCallback, failureCallback);
                        }
                        else {
                            resourcedDataService.patchItem (item, successCallback, failureCallback);
                        }
                    },
                    delete:function (item, successCallback, failureCallback) {
                        if (platform.isOffline()) {
                            offlineDataService.delete (base, modelName, item, successCallback, failureCallback);
                        }
                        else {
                            resourcedDataService.delete (item, successCallback, failureCallback);
                        }
                    },
                    query:function (params, successCallback, failureCallback) {
                        if (platform.isOffline()) {
                            offlineDataService.query(modelName, params, successCallback, failureCallback);
                        }
                        else {
                            resourcedDataService.query (params, successCallback, failureCallback);
                        }
                    },
                    action:function (params, successCallback, failureCallback) {
                        if (platform.isOffline()) {
                            //TODO offlineDataService.query(modelName, params, successCallback, failureCallback);
                        }
                        else {
                            resourcedDataService.action(params, successCallback, failureCallback);
                        }
                    },
                };
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
        }]);

})();
