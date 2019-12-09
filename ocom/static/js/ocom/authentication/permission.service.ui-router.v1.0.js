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
 * @author Scott Warren<scottwarren@ocomsoft.com> for Ocom Software
 */
angular
    .module('app.ocom.auth')
    .run(['$rootScope', 'authService', 'permissionService', 'SweetAlert','$transitions', function run($rootScope, authService, permissionService, SweetAlert, $transitions) {
        function checkRoute (toState) {
            if (!permissionService.can_goto_state(toState)) {
                SweetAlert.swal({
                  title: "Access Denied",
                  text: "You don't have access to that page. Contact your admin if you believe you should be able to see this page",
                  type: "error",
                  showCancelButton: true,
                  cancelButtonColor: "#DD6B55",
                  confirmButtonText: "Ok",
                  cancelButtonText: "Login Again",
                  closeOnConfirm: true,
                  closeOnCancel: true
                },
                function(isConfirm) {
                  if (!isConfirm) {
                      authService.unauthenticate();
                  }
                });
                return false;
            }
            else {
                return true;
            }
        }
        $transitions.onStart({}, function (trans) {
            var toState = trans.$to();

            if (!checkRoute(toState)) {
                return false;
            }
        });
        /* Checks the to State if disabled then don't allow */
        $rootScope.$on('$stateChangeStart',
            function (event, toState, toParams, fromState, fromParams, options) {
                if (!checkRoute(toState)) {
                    event.preventDefault();
                }
            });

        $rootScope.$on('$stateNotFound', function (event, unfoundState, fromState, fromParams) {
            console.log("Cannot find State:", +unfoundState); //Log for simpler debugging
        });
    }])
    .service('roleService', function () {
        /*

         A Dummy service - use put the OLD service after this otherwise this provides empty methods to fake the Role service

         */
        return {
            resetRoles: function () { /* noop */ },
            getFormSettings: function () {return {};},
        };
    })
    .service('permissionService', ['$localStorage', '$state', '$rootScope', 'authService', function ($localStorage, $state, $rootScope, authService) {
        /***
         * Role Service used in conjunction with Auth groups and Ocom Role model
         * @param $interval Angular $interval provider {@link http://docs.angularjs.org/api/ng.$interval}
         * @param {object} $localStorage ng-storage $localStorage service {@link https://www.npmjs.com/package/ng-storage}
         * @param {object} $state Angular $state provider
         * @param {object} $rootScope Angular $rootScope provider {@link http://docs.angularjs.org/api/ng.$http}
         */

        function calculatePermissions(user) {
            /* Convert Groups and Permissions to a Map*/
            console.log(user);

            var statesAccess = {};

            function processPermission(perm) {
                function get (dict, key, defaultVal) {
                    var result = dict[key];
                    if (!result) {
                        result = defaultVal;
                        dict[key] = result;
                    }

                    return result;
                }

                var elements = perm.codename.split(":");


                if (elements.length > 1) {
                    var statePerm = get(statesAccess, elements[1], {models: {}} );

                    if (elements[0] === "STATE") {
                        statePerm[elements[2].toLowerCase()] = true;
                    }

                    if (elements[0] === "FIELD") {
                        // “FIELD:state:modelName:FieldName:READ:DENY”
                        var modelPerm = get(statePerm.models, elements[2], {fields: {}} );
                        var fieldPerm = get(modelPerm.fields, elements[3], {} );

                        fieldPerm[elements[4].toLowerCase()] = false; // Deny this field access
                    }
                }
            }

            if (!_.isEmpty(user.permissionMap)) { // Map came from server so use it otherwise calculate the old way
                user._permissionMap = user.permissionMap;
            }
            else { // Use permission classes - should be removed
                // Do Groups first then User's own overwrite..
                _.each(user.groups, function (group) {
                        console.log("Permission Map", group);
                    _.each(group.permissions, processPermission);
                });
                _.each(user.user_permissions, processPermission);


                user._permissionMap = statesAccess;
            }
        }

        function handles_state(stateName) {
            if (!stateName) {
                return null; // WE don't handle this one!
            }

            var user = authService.getCurrentUser();

            if (user) {
                // if the user has changed then this map is not there so we need to calculate it ONCE.
                if (!("_permissionMap" in user)) {
                    calculatePermissions(user);
                }

                // check state param base
                if (user._permissionMap) {
                    // check if current state is defined
                    if (stateName in user._permissionMap) {
                        // Return the State's Entry
                        return user._permissionMap[stateName];
                    }

                    /* Checks parent states ie if there is a deny for state 'jobs'
                     * then we deny all 'jobs.*' states
                     */

                    // check if parent states are blocked as well
                    var checkStates = stateName.split(".");

                    while (checkStates.length > 1) {
                        checkStates.pop();

                        var parentState = checkStates.join();

                        if (parentState in user._permissionMap) {
                            // Return the parent State's Entry
                            return user._permissionMap[parentState]; // return the state
                        }
                    }
                }
            }
            return null; // We don't handle this state
        }

        function can_goto_state(state) {
            var stateName;

            if (typeof state === "string") {
                stateName = state;
            } else if (angular.isDefined(state.name)) {
                stateName = state.name;
            } else {
                return false;
            }

            var user = authService.getCurrentUser();

            if (user) {
                // if the user has changed then this map is not there so we need to calculate it ONCE.
                if (!("_permissionMap" in user)) {
                    calculatePermissions(user);
                }

                var found_state = handles_state(stateName);

                if (found_state != null) {
                    if (found_state.deny === true)
                        return false;
                }

                // // check state param base
                // if (user._permissionMap) {
                //     // check if current state is denied
                //     if (stateName in user._permissionMap && user._permissionMap[stateName].deny === true) {
                //         //console.log("Current state is blocked:", stateName);
                //         return false; // they have a permission Blocking them.
                //     }
                //     // check if parent states are blocked as well
                //     var checkStates = stateName.split(".");
                //
                //     while (checkStates.length > 1) {
                //         checkStates.pop();
                //
                //         var parentState = checkStates.join();
                //
                //         if (parentState in user._permissionMap && user._permissionMap[parentState].deny === true) {
                //             //console.log("Parent state is blocked:", parentState);
                //             return false; // they have a permission Blocking them.
                //         }
                //     }
                // }
            } else {
                if (state.allow_annonymous) { // This state has been marked to allow annonymous access always
                    return true;
                }

                if (["index.home", "login", "index.login", "index.logout"].indexOf(stateName) === -1) {
                    return false;
                }
            }

            return true;
        }

        function handles_permission (stateName, model, field, action) {
            var user = authService.getCurrentUser();
            var action_name = action.toLowerCase();

            if (stateName in user._permissionMap && user._permissionMap[stateName]) {
                var modelParam = user._permissionMap[stateName]['models'][model];

                if (modelParam) {
                    if (field in modelParam.fields) {
                        if (action_name in modelParam.fields[field]) { // Has an entry for 'read' or 'update'
                            return modelParam.fields[field];
                        }
                    }
                }
            }
            return null;
        }

        function has_permission (stateName, model, field, action) {
            var user = authService.getCurrentUser();
            var action_name = action.toLowerCase();

            if (user) {
                // if the user has changed then this map is not there so we need to calculate it ONCE.
                if (!("_permissionMap" in user)) {
                    calculatePermissions(user)
                }

                function getFieldParam (stateName, model, field) {
                    if (stateName in user._permissionMap && user._permissionMap[stateName]) {
                        var modelParam = user._permissionMap[stateName]['models'][model];

                        if (modelParam) {
                            return modelParam.fields[field];
                        }
                    }
                    return null;
                }

                // check state param base
                if (user._permissionMap) {
                    var fieldAction = getFieldParam(stateName, model, field);

                    if (fieldAction && action_name in fieldAction) {
                        return fieldAction[action_name] === true;
                    }

                    // check if parent states are blocked as well
                    var checkStates = stateName.split(".");

                    while (checkStates.length > 1) {
                        checkStates.pop();

                        var parentState = checkStates.join();
                        var parentFieldAction = getFieldParam(parentState, model, field);

                        if (parentFieldAction && action_name in parentFieldAction) {
                            return parentFieldAction[action_name] === true;
                        }
                    }
                }
                return true; // Assume for Annonymous it's Not visible to protect data
            }

            return false;
        }

        function get_has_permission () {
            /* Return curried function for Scope that can be used to check permission
              Uses current state.
             */
            return function (model, field, action) {
                has_permission ($state.current.name, model, field, action);
            }
        }

        return {
            handles_state: handles_state,
            handles_permission: handles_permission,
            can_goto_state: can_goto_state,
            can_goto_state_by_name : function (stateName) {
                return can_goto_state({name:stateName});
            },
            get_has_permission: get_has_permission,
            has_permission:has_permission
        }
    }])
    .directive('canGotoState', ['ngIfDirective', 'permissionService', function(ngIfDirective, permissionService) {
        /*
        usage: <div can-go-to-state="item.list">,,,</div>
        Will use ng-if will not show html if the user cannot access the state. It will NOT handle if the state allows_annonymous.
         */
        var ngIf = ngIfDirective[0];

        return {
            transclude: ngIf.transclude,
            priority: ngIf.priority - 1,
            terminal: ngIf.terminal,
            restrict: ngIf.restrict,
            link: function(scope, element, attributes) {
                // find the initial ng-if attribute
                var initialNgIf = attributes.ngIf, ifEvaluator;
                // if it exists, evaluates ngIf && ifAuthenticated
                if (initialNgIf) {
                    ifEvaluator = function () {
                        return scope.$eval(initialNgIf) && permissionService.can_goto_state({name:attributes.canGotoState});
                    };
                } else { // if there's no ng-if, process normally
                    ifEvaluator = function () {
                        return permissionService.can_goto_state({name:attributes.canGotoState});
                    };
                }
                attributes.ngIf = ifEvaluator;
                ngIf.link.apply(ngIf, arguments);
            }
        };
    }])
    .directive('disabledCanGotoState', ['ngDisabledDirective', 'permissionService', function(ngDisabledDirective, permissionService) {
        /*
        usage: <div disabled-can-go-to-state="item.list">,,,</div>
        Will use ng-disabled will not Disable the html if the user cannot access the state. It will NOT handle if the state allows_annonymous.
         */
        var ngDisabled = ngDisabledDirective[0];

        return {
            transclude: ngDisabled.transclude,
            priority: ngDisabled.priority - 1,
            terminal: ngDisabled.terminal,
            restrict: ngDisabled.restrict,
            link: function(scope, element, attributes) {
                // find the initial ng-if attribute
                var initialngDisabled = attributes.ngDisabled, disableEvaluator;
                // if it exists, evaluates ngDisabled && ifAuthenticated
                if (initialngDisabled) {
                    disableEvaluator = function () {
                        return scope.$eval(initialngDisabled) && !permissionService.can_goto_state({name:attributes.canGotoState});
                    };
                } else { // if there's no ng-if, process normally
                    disableEvaluator = function () {
                        return !permissionService.can_goto_state({name:attributes.disabledCanGotoState});
                    };
                }
                attributes.ngDisabled = disableEvaluator;
                ngDisabled.link.apply(ngDisabled, arguments);

                // Apply bootstrap disabled class if disabled.
                scope.$watch(disableEvaluator, function(newValue) {
                    if (newValue !== undefined) {
                        element.toggleClass("disabled", newValue);
                    }
                });


                element.on("click", function(e) { // for A elements
                    if (disableEvaluator()) {
                        e.preventDefault();
                    }
                });
            }
        };
    }])
    .directive('permCanRead', ['ngIfDirective', 'permissionService', '$state', function(ngIfDirective, permissionService, $state) {
        /*
        usage <div perm-can-read="fieldnameFromModel" model="model-name" >,,,</div>
        Will use ng-if will not show html if the user cannot READ the field for the model in the current state.
         */
        var ngIf = ngIfDirective[0];

        return {
            transclude: ngIf.transclude,
            priority: ngIf.priority - 1,
            terminal: ngIf.terminal,
            restrict: ngIf.restrict,
            link: function(scope, element, attrs) {
                // find the initial ng-if attribute
                var initialNgIf = attrs.ngIf, ifEvaluator;
                // if it exists, evaluates ngIf && ifAuthenticated
                if (initialNgIf) {
                    ifEvaluator = function () {
                        return scope.$eval(initialNgIf) && permissionService.has_permission($state.current.name, attrs.model, attrs.permCanRead, "READ");
                    };
                } else { // if there's no ng-if, process normally
                    ifEvaluator = function () {
                        return permissionService.has_permission($state.current.name, attrs.model, attrs.permCanRead, "READ");
                    };
                }
                attrs.ngIf = ifEvaluator;
                ngIf.link.apply(ngIf, arguments);
            }
        };
    }])
    .directive('permCanUpdate', ['ngDisabledDirective', 'permissionService', '$state', function(ngDisabledDirective, permissionService, $state) {
        /*
        usage <input perm-can-update="fieldnameFromModel" model="model-name" >,,,</input>
        Will disable the element if the user cannot UPDATE the field for the model in the current state.
         */
        var ngDisabled = ngDisabledDirective[0];

        return {
            transclude: ngDisabled.transclude,
            priority: ngDisabled.priority - 1,
            terminal: ngDisabled.terminal,
            restrict: ngDisabled.restrict,
            link: function(scope, element, attrs) {
                // find the initial ng-if attribute
                var initialNgIf = attrs.ngDisabled, disabledEvaluator;
                // if it exists, evaluates ngDisabled && ifAuthenticated
                if (initialNgIf) {
                    disabledEvaluator = function () {
                        return scope.$eval(initialNgIf) && !permissionService.has_permission($state.current.name, attrs.model, attrs.permCanUpdate, "UPDATE");
                    };
                } else { // if there's no ng-if, process normally
                    disabledEvaluator = function () {
                        return !permissionService.has_permission($state.current.name, attrs.model, attrs.permCanUpdate, "UPDATE");
                    };
                }
                attrs.ngDisabled = disabledEvaluator;
                ngDisabled.link.apply(ngDisabled, arguments);
            }
        };
    }])

})();
