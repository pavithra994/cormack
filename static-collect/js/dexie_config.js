/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

var codeTables = ['code_job_type', 'code_subbie_type', 'code_paving_colour', 'code_paving_type',
            'code_repair_type', 'code_drain_type', 'code_file_type', 'code_task_type', 'template'];

(function () {
angular.module('app.ocom')
    .config(function(ngDexieProvider) {
        ngDexieProvider.setOptions({name: 'cormack', debug: false});
        ngDexieProvider.setConfiguration(function (db) {

            var codeTableDef ="++id,active_start_date,active_end_date,description";

            var stores = {
                //'jobs': "++id, pour_date,original_job_number, customer, site_address, suburb, crew, pump, bob_cat",
                'jobs': "++id",
                'files': "++id",
                'repairs': "++id",
                'entry': "++id",
                'synclog': "++id,when"};

            _.each (codeTables, function (codeTableName) {
                stores[codeTableName] = codeTableDef;
            });

            db.version(1).stores(stores);

            db.on('error', function (err) {
                // Catch all uncatched DB-related errors and exceptions
                console.error("db error err=" + err);
            });

        });
    });

})();
