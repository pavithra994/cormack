/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    angular
        .module('ocom.query')
        .factory("dexieQuery", ['ngDexie', '$timeout', 'queryFactory',
            function (ngDexie, $timeout, queryFactory) {
                function executeQuery(tableName, query, successCallback) {
                    ngDexie.getDb(function (db) {
                        var ctx = db[tableName];

                        queryFactory.prepare(query);

                        var filter = query.filter;

                        //TODO Limit, Offset, Sorting..
                        ctx.filter(filter).toArray().then(function (data) {
                            $timeout(function () {
                                successCallback({'count': data.length, 'results': data});
                            });
                        });
                    });
                }

                return {
                    runQuery: executeQuery
                }
            }]);
})();
