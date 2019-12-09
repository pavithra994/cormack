/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
        angular
            .module('cormack', [
                // Auth
                'angular-jwt',
                'ngStorage',
                // UI
                'ui.select',
                'ngSanitize', 
                'ngTagsInput',
                'ui.router',
                'xeditable',
                'ngMessages',
                'ocom.query',
                'ocom.xero',
                //dexie
                'ngdexie',
                'ngdexie.ui',
                'app.group_permissions',
                // Reusable components
                'app.ocom',
                'app.dashboard',
                'app.job',
                'app.repair',
                'app.mobile',
                'app.email',
            ]);
})();
