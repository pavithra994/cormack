/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

// Remove console.log output on non-dev environment
if (! (window.location.host.indexOf('127.0.0.1') > -1 || window.location.host.indexOf('localhost') > -1 || window.location.host.indexOf('0.0.0.0') > -1)) {
    console.log = function () {
    };
}

// https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/padStart
if (!String.prototype.padStart) {
    String.prototype.padStart = function padStart(targetLength,padString) {
        targetLength = targetLength>>0; //truncate if number or convert non-number to 0;
        padString = String((typeof padString !== 'undefined' ? padString : ' '));
        if (this.length > targetLength) {
            return String(this);
        }
        else {
            targetLength = targetLength-this.length;
            if (targetLength > padString.length) {
                padString += padString.repeat(targetLength/padString.length); //append to original to ensure we are longer than needed
            }
            return padString.slice(0,targetLength) + String(this);
        }
    };
}

(function () {
    var settings = {
        interval: 200,      //  no. of milliseconds to wait for each wait interval or timeout function
        queryRefresh: 500   //  no. of miliiseconds to wait for each query refresh interval
    };

    angular
        .module('app.ocom')
        .constant('SETTINGS', settings)
        .config(growlConfig)
        .config(httpConfig)
        .config(routeConfig)
        .filter('sumByKey', sumByKey)
        .directive('stringToNumber', stringToNumber)
        .directive('stringToInt', stringToInt)
        .run(run);

    function run($state, $rootScope, widgetService) {
        $rootScope.port = window.location.port;
        $rootScope.$state = $state;
        $rootScope.setVersion = function (version) {
            console.log("Version", version);
            widgetService.version = version;
        }

        // Log ui-router changes
        $rootScope.$on('$stateChangeStart',function(event, toState, toParams, fromState, fromParams){
          console.log('$stateChangeStart to '+toState.name+'- fired when the transition begins. toState,toParams : \n',toState, toParams);
        });

        $rootScope.$on('$stateChangeError',function(event, toState, toParams, fromState, fromParams){
          console.log('$stateChangeError - fired when an error occurs during transition.');
          console.log(arguments);
        });

        $rootScope.$on('$stateChangeSuccess',function(event, toState, toParams, fromState, fromParams){
          console.log('$stateChangeSuccess to '+toState.name+'- fired once the state transition is complete.');
        });

        $rootScope.$on('$viewContentLoaded',function(event){
          console.log('$viewContentLoaded - fired after dom rendered',event);
        });

        $rootScope.$on('$stateNotFound',function(event, unfoundState, fromState, fromParams){
          console.log('$stateNotFound '+unfoundState.name+'  - fired when a state cannot be found by its name.');
          console.log(unfoundState, fromState, fromParams);
        });
    }

    function routeConfig($urlRouterProvider, $resourceProvider) {
        $urlRouterProvider.otherwise("/");
        $resourceProvider.defaults.stripTrailingSlashes = false;
    }

    function growlConfig($urlRouterProvider, $stateProvider, $resourceProvider, growlProvider, $httpProvider, $localStorageProvider) {
        growlProvider.onlyUniqueMessages(true);
        growlProvider.globalTimeToLive({success: 2000, error: -1, warning: 3000, info: 4000});
        growlProvider.globalDisableCountDown(true);
    }

    function httpConfig(growlProvider, $httpProvider) {
        // --- Html cache busting start
        console.log("Busting cache...");
        if (!$httpProvider.defaults.headers.get) {
            $httpProvider.defaults.headers.get = {};
        }
        $httpProvider.defaults.headers.common['If-Modified-Since'] = 'Sun, 10 Jun 2001 10:00:00 GMT';
        $httpProvider.defaults.headers.common['Cache-Control'] = 'no-cache';
        $httpProvider.defaults.headers.common.Pragma = 'no-cache';
        // --- Html cache busting end

        $httpProvider.interceptors.push(growlProvider.serverMessagesInterceptor);
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    }

    function sumByKey() {
        return function (data, key) {
            if (typeof (data) === 'undefined' || typeof (key) === 'undefined') {
                return 0;
            }

            var sum = 0;
            for (var i = data.length - 1; i >= 0; i--) {
                //var val = parseInt(data[i][key]);
                var val = parseFloat(data[i][key]);

                if (!isNaN(val))
                    sum += val;
            }

            return sum;
        };
    }

    function stringToNumber() {
        return {
            require: 'ngModel',
            link: function (scope, element, attrs, ngModel) {
                ngModel.$parsers.push(function (value) {
                    if (angular.isDefined(value)) {
                        return '' + value;
                    }
                    return '';
                });
                ngModel.$formatters.push(function (value) {
                    return parseFloat(value);
                });
            }
        };
    }

    function stringToInt() {
        return {
            require: 'ngModel',
            link: function(scope, element, attrs, ngModel) {
                ngModel.$parsers.push(function(value) {
                    return parseInt(value, 10);
                });
                ngModel.$formatters.push(function(value) {
                    if (angular.isDefined(value)) {
                        return '' + value;
                    }
                    return '';
                });
            }
        };
    }
})();
