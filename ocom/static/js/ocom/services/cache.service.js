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
        .factory('dataCacheService', dataCacheService);

    /**
     * Data Cache service
     *
     * @param {object} $q Angular $qProvider {@link http://docs.angularjs.org/api/ng.$q}
     * @param {object} $resource Angular $resource provider
     * @param {object} $localStorage ng-storage $localStorage service {@link https://www.npmjs.com/package/ng-storage}
     * @param {object} dataAPIService Ocom Date Service provider (Make sure dataService module is loaded)
     * @param {object} formStateService Ocom Form State Service provider
     */
    function dataCacheService($q, $resource, $localStorage, dataAPIService, formStateService) {
        var _hashApiBaseUrl = '/api/hash/';

        return {
            setHashApiBaseUrl: setHashApiBaseUrl,
            getCache: getQueryCache,
            setCache: setQueryCache,
            saveCache: saveQueryCache,
            lastCacheKeyInfo: lastCacheKeyInfo,
            processLoadTables: processLoadTables
        };

        /**
         * Set Hash Api Base URL
         * @param {string} url: the base url address to set
         */
        function setHashApiBaseUrl (url) {
            _hashApiBaseUrl = url;
        }

        /**
         * Check if cache storage is initialized and do such if it is not
         */
        function checkAndInitializeCacheStorage () {
            if (!angular.isDefined($localStorage.cache)) {
                $localStorage.cache = [];
            }
            if (!angular.isDefined($localStorage.cache_date)) {
                $localStorage.cache_date = [];
            }
        }

        /**
         * Return last cache key info
         * @returns {*} the last cache info or blank string if none
         */
        function lastCacheKeyInfo () {
            if (angular.isDefined($localStorage.lastCacheKeyInfo)) {
                return $localStorage.lastCacheKeyInfo;
            }
            return '';
        }

        /**
         * Get Cache from model and params
         * @param {string} model the name of the model
         * @param {string} action the getApi method to perform (e.g. 'list', 'update', 'query')
         * @param {object} params the parameters to use such as filters, sorting, etc.
         * @param {boolean} revert if true, revert to getApi function if cache is not found
         */
        function getQueryCache (model, action, params, revert) {
            var deferred = $q.defer();

            getCacheKeyInfo(model, action, params).then(function (response) {
                var runGetApiSwitch = 0;

                if (dataAPIService.interrupt) {
                    deferred.resolve(false);
                    return deferred.promise;
                }

                console.log("Cache Key result for " + model, response);
                //TODO: check out why cache is not being refreshed (e.g. if items are edited in Admin dashboard, no trigger as of 01/30/2018)
                // if (response === false) {
                if (true) {
                    if (revert) {
                        runGetApiSwitch = 1;
                    } else {
                        deferred.resolve(false);
                    }
                } else {
                    $localStorage.lastCacheKeyInfo = response;
                    if (angular.isDefined($localStorage.cache) &&
                        angular.isDefined($localStorage.cache[response.key])) {
                        console.log("Cache found for " + model + ".", $localStorage.cache[response.key],
                            $localStorage.cache_date[response.key]);
                        // check if cache is stale
                        //noinspection JSUnresolvedVariable
                        if ($localStorage.cache_date[response.key] < response.modified_date) {
                            console.log("Cache for " + model + " is stale.");
                            if (revert) {
                                runGetApiSwitch = 2;
                            } else {
                                deferred.resolve(null);
                            }
                        } else {
                            formStateService.setLoaded(model, true);
                            deferred.resolve($localStorage.cache[response.key]);
                        }
                    } else {
                        if (revert) {
                            runGetApiSwitch = 2;
                        } else {
                            deferred.resolve(null);
                        }
                    }
                }
                if (runGetApiSwitch) {
                    console.log("Reverting to " + model + " api...");
                    dataAPIService.getDataApi("/api/", model)[action](params, function (apiResponse) {
                        if (runGetApiSwitch === 1) {
                            console.log("Saving cache result of " + model + "...");
                            saveQueryCache(model, action, params, apiResponse);
                        } else {
                            console.log("Setting cache result of " + model + "...");
                            setQueryCache(response, apiResponse);
                        }
                        deferred.resolve(apiResponse);
                    });
                }
            });
            return deferred.promise;
        }

        function getCacheKeyInfo (model, action, params) {
            var deferred = $q.defer();
            //noinspection JSValidateTypes
            var Hash = $resource(_hashApiBaseUrl, {
                model: model,
                action: action,
                params: params
            });

            Hash.query(function (response) {
                console.log("Hash Response", response);
                if (angular.isDefined(response[0])) {
                    deferred.resolve(response[0]);
                } else {
                    deferred.resolve(false);
                }
            });
            return deferred.promise;
        }

        /**
         * Saves cache to the $localStorage
         * @param {object} keyInfo the key info object to reference cache keys and other stuff from
         * @param {object} cacheData the data to store to the cache
         */
        function setQueryCache (keyInfo, cacheData) {
            checkAndInitializeCacheStorage();
            $localStorage.cache[keyInfo.key] = cacheData;
            //noinspection JSUnresolvedVariable
            $localStorage.cache_date[keyInfo.key] = keyInfo.modified_date;
            $localStorage.$apply();
            console.log("keyInfo Setting and cache dates:", keyInfo, $localStorage.cache_date);
        }

        /**
         * Saves cache to localStorage and updates cache key info
         * @param {string} model the name of the model
         * @param {string} action the getApi method to perform (e.g. 'list', 'update', 'query')
         * @param {object} params the parameters to use such as filters, sorting, etc.
         * @param {object} cacheData the data to store to the cache
         * @returns {string} the cache key
         */
        function saveQueryCache (model, action, params, cacheData) {
            var deferred = $q.defer();
            //noinspection JSValidateTypes
            var Hash = $resource(_hashApiBaseUrl, {
                model: model,
                action: action,
                params: params
            });

            Hash.save(function (response) {
                console.log("Key Save Response", response);
                checkAndInitializeCacheStorage();
                deferred.resolve(response.key);
                setQueryCache(response.key, cacheData);
            });
            return deferred.promise;
        }

        /**
         * Process Load tables into cacheable lists
         * @param {Array} loadTables a JSON list of getCache/ getApi configurations
         * @param {object} scope the $scope to set values from getCache/ getApi operations
         * @param {string} action the getApi action to perform (e.g. 'query', 'list')
         */
        function processLoadTables(loadTables, scope, action) {
            angular.forEach(loadTables, function (item) {
                var thisAction = angular.isDefined(item.action) ? item.action : action;

                getQueryCache(item.name, thisAction, item.params, true).then(function (response) {
                    var filteredResponse = (item.callback) ? item.callback(response, item.params) : response;

                    if (item.scope) {
                        scope[item.scope] = filteredResponse;
                    }
                });
            });
        }
    }
})();
