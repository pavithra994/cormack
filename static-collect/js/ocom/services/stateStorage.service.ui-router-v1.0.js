/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

/**
 * Created by scottwarren on 7/04/17.
 */
(function () {
    angular
        .module('app.ocom')
        .factory('stateStorage', ['$state',
            function ($state) {
            return {
                updateStateParams : function (stateName, defaults, $stateParams) {
                },
                storeStateParams: function (stateName, stateParams, clear) {},
                storeStateThenGo: function (destination, toStore, clear) {
                     // Here for backward compatibility
                     $state.go(destination, toStore, {reload: true});
                }
            };
        }])
        .run(['$transitions', '$sessionStorage', function run($transitions, $sessionStorage) {
            function storeParams (state, stateParams) {
                if (state.data && state.data.store_state) {
                    var stateName = state.name;

                    $sessionStorage[stateName + "_stateParams"] = Object.assign({}, stateParams); // Store cloned version of params
                }
            }

           $transitions.onBefore({}, function(transition) {
                if (transition.$to().name == transition.$from().name) {
                    var $stateParams = Object.assign({}, transition.params("to"));
                    var stateName = transition.$to().name;

                    storeParams(transition.$to(), $stateParams);// Store for next time so it's found in storage again

                    return true; // continue as before they are the same state
                }

                storeParams(transition.$from(), transition.params("from"));

                // Don't mutate the current parameters
                var $stateParams = Object.assign({}, transition.params("to"));
                var stateName = transition.$to().name;

                var stateService = transition.router.stateService;

                // Don't modify the params if clearState is set to true.
                if (angular.isDefined($sessionStorage[stateName + '_clearState']) && $sessionStorage[stateName + '_clearState']) {
                    delete $sessionStorage[stateName + '_clearState'];
                } else {
                    var storedParams = $sessionStorage[stateName + "_stateParams"] || null;

                    if (storedParams) { // Only do this if there is a value
                        var changed = false;
                        _.forEach($stateParams, function (value, key) {
                            if ($stateParams[key] != storedParams[key]) { // Assign if undefined and changed
                                $stateParams[key] = storedParams[key];
                                changed = true;
                            }
                        });

                        if (changed) { // Only do this if we changed something - avoids it coming back into here.
                            storeParams(transition.$to(), $stateParams);

                            return stateService.target(transition.to(), $stateParams);
                        }
                    }
                }

           });
        }]);
})();
