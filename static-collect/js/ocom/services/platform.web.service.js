/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    /* Service to handle offline/online modes
    *  This is the WEB platform.
    *  It's is always online..
    *
    *  ONLY INCLUDE ONE OF THESE PLATFORM.SERVICE FILES
    * */

    angular
        .module('app.ocom')
        .factory("platform", ['$rootScope', function ($rootScope) {
            return {
                canGoOffline: function() {
                    return false;
                },
                isWeb: function () {
                    return true;
                },
                isTablet: function () {
                    return false;
                },
                setOffline:function (value) {
                   // NO OP
                },
                isOffline:function () {
                    return false;
                }

            };

        }]);
})();
