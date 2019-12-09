/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {

    /**
     * @author Peter Garas <peter.garas@ocomsoft.com> for Ocom Software
     */
    angular
        .module('app.ocom')
        .service('widgetService', WidgetService);

    /***
     * Widget Service for common functions used in Widget directives
     */
    function WidgetService($timeout, $rootScope, $state, $injector) {
        var showFooterFlag = false;
        var version = '';
        // var dateFormat = 'DD/MM/YYYY';  // default date format recognizable by moment.js
        // var _normalizedDateFormat = 'YYYY-MM-DD';
        var dateFormat = 'ddd DD MMM';  
        var _normalizedDateFormat = 'YYYY-MM-DD';

        /**
         * Set Show Footer flag
         * @param {boolean} option the value to set
         */
        var setShowFooter = function (option) {
            console.log("Footer Toggled", option);
            showFooterFlag = option;
            $rootScope.$broadcast("$footerToggled");
        };

        /**
         * Return current show footer flag
         * @returns {boolean}
         */
        var showFooter = function () {
            return showFooterFlag;
        };

        /**
         * Focus on a tagged element
         * @param {string} name the element tag name
         */
        var focus = function (name) {
            $timeout(function () {
                console.log("Setting focus...");
                $rootScope.$broadcast('focusOn', name);
            });
        };

        /**
         * Store states on local storage then proceed to destination
         * Deprecated; use stateStorage instead
         * @param {string} destination the destination route
         * @param {object} toStore the values to store
         * @param {boolean} clear if true, signals clear to Search
         */
        var storeStateThenGo = function (destination, toStore, clear) {
            var stateStorage;

            try { // If the service is in the database
                stateStorage = $injector.get('stateStorage');
                stateStorage.storeStateParams(destination, toStore, clear); // Store for next time..
            } catch (e) {
                //pass
            }
            $state.go(destination, toStore, {reload: true});
        };

        /***
         * Normalize date going to DRF/backend (Note: requires moment.js)
         * @param {string} dateString the date string to normalize / convert
         * @returns {string} the normalized string
         */
        function normalizedDate (dateString) {
            var theDate = (dateString) ? new Date(dateString) : new Date();

            return moment(theDate).format(_normalizedDateFormat)
        }

        return {
            setShowFooter: setShowFooter,
            showFooter: showFooter,
            focus: focus,
            storeStateThenGo: storeStateThenGo,
            normalizedDate: normalizedDate,
            dateFormat: dateFormat,
            version: version
        }
    }
})();
