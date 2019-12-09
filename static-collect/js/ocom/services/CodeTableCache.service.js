/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    /* NOTE Assumption - the assumption that any more than 10,000 items in a table and we have other problems to worry
        about so we limit to 10,000.
     */

    angular
        .module('app.ocom')
        .factory("CodeTableCacheService", ['$http', 'dataAPIService', '$localStorage', '$timeout', function ($http, dataAPIService, $localStorage, $timeout) {
            return {
                primeCache: primeCache,
                fetchFromCache: fetchFromCache,
                processLoadTables: processLoadTables
            };

            /* Fetch the data from the REST API and put into Localstorage for later */
            function primeCache(uri, modelName) {
                dataAPIService.getDataApi(uri,  modelName).list({offset:0, limit:10000}, function (response) {
                    $localStorage[modelName] = response.data;
                });
            }

            function fetchFromCache(uri, modelName, callback) {
                // If in Cache then use this..
                if ($localStorage[modelName]) {
                    callback($localStorage[modelName]);
                }
                else {
                    $localStorage[modelName] = []; // Init with empty array
                }

                // Get the last modified_date and ask for changes since then..
                var max_modified_date = _.maxBy($localStorage[modelName], function (o) {
                    return new Date(o.modified_date); // Convert to date
                });
                var options = {offset: 0, limit: 10000};
                if (max_modified_date) {
                    options['modified_date'] = max_modified_date.modified_date;
                }

                // Check with the Database for changes.
                dataAPIService.getDataApi(uri, modelName).list(options, function (response) {
                    if (!$localStorage[modelName])
                        $localStorage[modelName] = [];

                    var keyList = _.keyBy($localStorage[modelName], "id"); // convert to dict
                    _.forEach(response.results, function (item) {
                        keyList[item.id] = item; // Overwrite or add
                    });

                    $localStorage[modelName] = _.values(keyList); // convert back to array/list

                    callback($localStorage[modelName]);
                });

            }

            /**
             * Process Load tables into cacheable lists
             * @param {Array} loadTables a JSON list of getCache/ getApi configurations
             * @param {object} scope the $scope to set values from getCache/ getApi operations
             */
            function processLoadTables(loadTables, scope) {
                _.each (loadTables, function (item) {
                    fetchFromCache(item.uri, item.name, function (results) {
                        var filteredResponse = (item.callback) ? item.callback(results, item.params) : results;
                        if (item.scope) {
                            $timeout(function() {
                                scope[item.scope] = filteredResponse;
                                if (item.keyBy) {
                                    scope[item.scope + "_by_" + item.keyBy] = _.keyBy(filteredResponse, item.keyBy);
                                }
                            });
                        }
                    });

                });
            }

        }])
        .directive('loadCodeTable', ['CodeTableCacheService', function (CodeTableCacheService) {
            /*
            Usage put the directive before a SELECT etc.. Uses the CodeTableCacheService to load the data

            ie load-code-table="code_extra_type" options="options" uri="/sync/"
            Where
            load-code-table is the name of the code table in the cache etc.
            options = the object to put the result into. Will use the load-code-table value as the key
            uri = is the uri to use to get the data if online.
             */
            return {
                restrict: 'A',
                scope: {
                    options: '=', // The object to update
                    loadCodeTable: '@', // The name of the CodeTable to Load
                    uri: '@', // The name of the CodeTable to Load
                    keyBy: '@?'
                },
                link: function (scope, elem, attrs) {
                    scope.options["loading_" + scope.loadCodeTable] = true;
                    CodeTableCacheService.fetchFromCache(scope.uri || "/api/", scope.loadCodeTable, function (data) {
                        scope.options[scope.loadCodeTable] = data;

                        if (scope.keyBy) {
                            scope.options[scope.loadCodeTable + "_by_" + scope.keyBy] = _.keyBy(data, scope.keyBy);
                        }

                        scope.options["loading_" + scope.loadCodeTable] = false; // Loaded Now.
                    });
                }
            }
        }]);

})();
