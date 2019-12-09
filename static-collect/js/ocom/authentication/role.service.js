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
    .module('app.ocom.auth')
    .run(run)
    .service('roleService', roleService);

/**
 * initialize roleService
 * @param {object} $rootScope Angular $rootScope provider {@link http://docs.angularjs.org/api/ng.$http}
 * @param {object} authService Django-ocom Auth Service provider {@link roleService}
 * @param {object} roleService Django-ocom Role Service provider {@link roleService}
 */
function run($rootScope, authService, roleService) {
    $rootScope.$on('$authLoginSuccess', function () {
        // do something here
    });

    $rootScope.$on('$authVerified', function () {
        // always update roles
        if (authService.allowRoles) {
            console.log("Updating user roles...");
            roleService.updateUserRoles();
        } else {
            console.log("Skipping user roles...");
        }
    });

    $rootScope.$on('$authLogout', function () {
        // do something here
    });
}

/***
 * Role Service used in conjunction with Auth groups and Ocom Role model
 * @param $interval Angular $interval provider {@link http://docs.angularjs.org/api/ng.$interval}
 * @param {object} $localStorage ng-storage $localStorage service {@link https://www.npmjs.com/package/ng-storage}
 * @param {object} $q Angular $qProvider {@link http://docs.angularjs.org/api/ng.$q}
 * @param {object} $state Angular $state provider
 * @param {object} $rootScope Angular $rootScope provider {@link http://docs.angularjs.org/api/ng.$http}
 * @param {object} dataAPIService Django-ocom dataAPI service provider
 * @param {object} dataResourceService - the ONLINE data service - Temp fix to load the Roles when ONLINE
 * @param {object} SETTINGS Django-ocom SETTINGS config
 * @param {object} $injector - used to get permissionService.
 */
function roleService($interval, $localStorage, $q, $state, $rootScope, dataAPIService, dataResourceService, SETTINGS, $injector) {
    var roles = [],
        permissions = [],
        form_settings = [],
        access = [],
        links = [], // deprecated
        routes = [],
        modifiedRoles = false,
        modifiedPermissions = false,
        modifiedFormSettings = false;

    var permissionService = null;

    function tryGetPermissionService() {
        if (permissionService == null) {
            try {
                if ($injector.has("permissionService")) {
                    permissionService = $injector.get('permissionService');
                    console.log('Injector has permissionService service!');
                }
            } catch (e) {
                console.log('Injector does not have permissionService service!');
            }
        }

        return permissionService;
    }

    /**
     * Broadcast a '$forceRedirect' event on $rootScope if redirection is not allowed
     *
     * ALSO checks permissionService if the service exists!!
     *
     * @returns {boolean} true if redirected
     */
    var broadcastRedirectIfNotPermitted = function () {
        var allowed = false;
        var route = $state.current.name;
        var model;

        var permissionService = tryGetPermissionService();

        if (permissionService != null) {
            var foundState = permissionService.handles_state(route);

            if (foundState != null) {
                var result = permissionService.can_goto_state(route); // use this instead of below..

                if (!result) {
                    // Use same code as below
                    console.log('Initiating redirection...', route);
                    $rootScope.$broadcast('$forceRedirect');
                    return true; // Did redirect
                } else {
                    return false; // We handled it here and didn't redirect
                }
            }
        }

        dataResourceService.interrupt = false;
        dataAPIService.interrupt = false;
        if (angular.isDefined(access)) {
            angular.forEach(access, function (item, key) {
                if (!allowed) {
                    model = key;
                    if (angular.isDefined(access[model][route])) {
                        if (angular.isDefined(access[model][route]['view'])) {
                            if (access[model][route]['view'] === true) {
                                allowed = true;
                            } else {
                                if (Array.isArray(access[model][route]['view']) &&
                                    access[model][route]['view'].length > 0) {

                                    allowed = true;
                                }
                            }

                        } else {
                            if (access[model][route] === true) {
                                allowed = true;
                            }
                        }
                    } else {
                        // allow if we only need to go back to home page
                        if (route === 'index.home') {
                            allowed = true;
                        }
                    }
                }
            });
            if (!allowed) {
                model = '';
            }
        }
        if (!allowed) {
            console.log('Initiating redirection...', model, route);
            $rootScope.$broadcast('$forceRedirect');
        }
        return !allowed;
    };

    /**
     * Clear roles and broadcast event to $rootScope
     *
     * Called When we authenticate() in auth.alt.module.js
     */
    var resetRoles = function () {
        var vm = this;

        vm.additionalRoles = [];
        roles = [];
        modifiedRoles = false;
        console.log('Roles reset: ', roles);
        $rootScope.$broadcast('$rolesReset');
    };

    /**
     * Update roles and broadcast event to $rootScope
     * @param {object} newRoles the generated Roles object to assign as the new Roles set
     */
    var updateRoles = function (newRoles) {
        roles = angular.copy(newRoles);
        modifiedRoles = true;
        console.log('Roles updated: ', newRoles);
        $rootScope.$broadcast('$rolesUpdate');
    };

    /**
     * Update permissions and broadcast event to $rootScope
     * @param {object} newPermissions the generated Permissions object to assign as the new Permission set
     */
    var updatePermissions = function (newPermissions) {
        permissions = angular.copy(newPermissions);
        modifiedPermissions = true;
        console.log('Permissions updated: ', newPermissions);
        $rootScope.$broadcast('$permissionsUpdate');
    };

    /**
     * Retrieve the current roles available
     * @returns {object} the list of roles
     */
    var getRoles = function () {
        return roles;
    };

    /**
     * Retrieve the Role object from a given role name
     * @param {string} role the role name
     * @returns {object} the role or an empty object
     */
    var getRole = function (role) {
        if (modifiedRoles) {
            if (angular.isDefined(roles[role])) {
                return roles[role];
            }
        }
        return {};
    };

    /**
     * Retrieve the Role object from a given role name with a promise option
     * @param {string} role the role name
     * @param {boolean} wait if true, defers output until Roles set is modified
     * @returns {object} the role or an empty object
     */
    var getRoleWait = function (role, wait) {
        if (wait) {
            var deferred = $q.defer();
            var waitUntilRolesAppear = $interval(function () {
                if (modifiedRoles) {
                    $interval.cancel(waitUntilRolesAppear);
                    return deferred.resolve(getRole(role));
                }
            }, SETTINGS.interval);
            return deferred.promise;
        } else {
            return getRole(role);
        }
    };

    /**
     * Retrieve the Permission object from a given role name
     * @param {string} role the role name
     * @returns {object} the permission or an empty object
     */
    var getPermission = function (role) {
        if (typeof permissions[role] !== 'undefined') {
            return permissions[role];
        }
        return {};
    };

    /**
     * Return true if Role set is modified
     * @returns {boolean}
     */
    var isRolesModified = function () {
        return modifiedRoles;
    };

    /**
     * Return true if Permission set is modified
     * @returns {boolean}
     */
    var isPermissionsModified = function () {
        return modifiedPermissions;
    };

    /**
     * Return a list of Roles that the current user is part of
     * @returns {object}
     */
    var userHasTheseRoles = function () {
        var groups = [];
        var vm = this;

        if (typeof roles === 'undefined' || roles.length === 0) {
            return groups;
        }
        for (var i = 0; i < $localStorage.user.groups.length; i++) {
            // Django drops off special chars such as underscore to space for group names
            groups.push($localStorage.user.groups[i].name.toLowerCase().replace(' ', '_'));
        }
        // check for additional roles
        for (var j = 0; j < vm.additionalRoles.length; j++) {
            if (typeof roles[vm.additionalRoles[j]] !== 'undefined' && roles[vm.additionalRoles[j]]) {
                groups.push(vm.additionalRoles[j]);
            }
        }
        return groups;
    };

    /**
     * Return true if a role is found for the current user
     * @param {string} role the role name
     * @returns {boolean}
     */
    var userHasThisRole = function (role) {
        var vm = this;
        var user = $localStorage.user;

        // check for user.role
        if (angular.isDefined(user.role) && angular.isDefined(user.role[role]) && user.role[role]) {
            console.log('Role found (ROLE): ', role);
            return true;
        }

        for (var i = 0; i < user.groups.length; i++) {
            if (user.groups[i].name.toLowerCase() === role) {
                console.log('Role found (GROUP): ', role);
                return true;
            }
        }

        // check for additional roles
        for (var j = 0; j < vm.additionalRoles.length; j++) {
            if (typeof roles[vm.additionalRoles[j]] !== 'undefined' && roles[vm.additionalRoles[j]]
                && vm.additionalRoles[j] === role) {
                console.log('Role found: ', role, roles[vm.additionalRoles[j]]);
                return true;
            }
        }

        console.log('Role not found!', role);
        return false;
    };

    /**
     * DEPRECATED
     * Update Form Settings object and broadcast event to $rootScope
     * @param {object} newFormSettings the generated Form Settings object to assign as the new Form Settings
     */
    var updateFormSettings = function (newFormSettings) {
        form_settings = angular.copy(newFormSettings);
        modifiedFormSettings = true;
        console.log('Form settings updated: ', newFormSettings);
        $rootScope.$broadcast('$formSettingsUpdate');
    };

    /**
     * DEPRECATED
     * Return a list of Link Settings based on user roles
     * @returns {object}
     */
    var getLinkSettings = function () {
        return links;
    };

    /**
     * DEPRECATED
     * Update Link Settings object and broadcast event to $rootScope
     * @param {object} newLinkSettings the generated Link Settings object to assign as the new Link Settings
     */
    var updateLinkSettings = function (newLinkSettings) {
        links = angular.copy(newLinkSettings);
        console.log('Link settings updated: ', newLinkSettings);
        $rootScope.$broadcast('$linkSettingsUpdate');
    };

    /**
     * Return a list of Access Settings based on user roles
     * @returns {object}
     */
    var getAccessSettings = function () {
        return access;
    };

    /**
     * Update Access Settings object and broadcast event to $rootScope
     * @param {object} newAccessSettings the generated Access Settings object to assign as the new Access Settings
     */
    var updateAccessSettings = function (newAccessSettings) {
        access = angular.copy(newAccessSettings);
        console.log('Access settings updated: ', newAccessSettings);
        if (!broadcastRedirectIfNotPermitted()) {
            $rootScope.$broadcast('$accessSettingsUpdate');
        }
    };

    /**
     * DEPRECATED
     * Return a list of Form Settings based on user roles
     * @returns {object}
     */
    var getFormSettings = function () {
        if (modifiedFormSettings) {
            return form_settings;
        }
        return {
            read_only: false
        };
    };

    /**
     * Update Route Mapping object and broadcast event to $rootScope
     * @param {object} newMapping the generated Link Settings object to assign as the new Link Settings
     */
    var updateRouteMapping = function (newMapping) {
        routes = angular.copy(newMapping);
        console.log('Route settings updated: ', newMapping);
        $rootScope.$broadcast('$routeMappingUpdate');
    };

    /**
     * Get and update user roles from Auth
     * @param {object} customRole if not null or empty, define as a custom role
     */
    var updateUserRoles = function (customRole) {
        if ("user" in $localStorage && "role" in $localStorage.user) { //Do we have the role as part of the stored User Data? If so use this instead of asking with Ajax
            updateRoles($localStorage.user.role)
        }
        else { // Deprecated. The Role should come from the Authentication request as part of the "user"
            dataResourceService.getDataApi("/api/", 'roles').query({user: $localStorage.user.id}, function (response) {
                console.log('Updating roles...', response);
                if (angular.isDefined(response[0])) {
                    updateRoles(response[0]);
                } else {
                    if (angular.isDefined(customRole)) {
                        updateRoles(customRole);
                    } else {
                        updateRoles({});
                    }
                }
            });
        }
    };

    /**
     * Trigger a '$pageLoaded' event in $rootScope when Roles has been updated
     * Note: this needs to be below any $formSettingsUpdate event handler
     * @param {object} scope the $scope reference from the controller accessing roleService
     */
    var triggerPageLoaded = function (scope) {
        console.log("Page Load event triggered.");
        if (isRolesModified()) {
            $rootScope.$broadcast('$pageLoaded');
        } else {
            scope.$on('$rolesUpdate', function () {
                $rootScope.$broadcast('$pageLoaded');
            });
        }
    };

    /**
     * Subscribe to a access update event trigger
     * @param {object} scope the $scope reference from the controller accessing roleService
     * @param {function} callback the function callback to run on access update (optional)
     */
    var subscribeAccessUpdate = function (scope, callback) {
        console.log("Subscribed to Update access event.");

        scope.$on('$accessSettingsUpdate', function () {
            if (typeof callback === 'function') {
                callback();
            }
            broadcastRedirectIfNotPermitted();
        });
        triggerPageLoaded(scope);
    };

    /**
     * Subscribe to a form update event trigger with a callback function
     * @param {object} scope the $scope reference from the controller accessing roleService
     * @param {function} callback a function reference with 'form' parameter that is called when event is triggered
     */
    var subscribeUpdateFormCallback = function (scope, callback) {
        console.log("Subscribed to Update form with callback event.");

        scope.$on('$formSettingsUpdate', function () {
            var form = getFormSettings();

            console.log("Triggering Form settings change with callback...");
            callback(form);
        });
    };

    /**
     * Redirect if the form encounters a 404 error from DRF ajax calls
     * @param {object} scope the $scope reference from the controller accessing roleService
     */
    var redirectOn404Error = function (scope) {
        console.log("Redirect on API 404 result.");
        scope.$on('$Got404Error', function () {
            console.log("Intercepted 404 error.");
            $rootScope.$broadcast('$forceRedirect');
        });
    };

    /**
     * Return accessibility flag of form based on routeMapping and permissions
     * @param {string} model the model name
     * @param {string} routeLink the route link to check (Optional)
     * @returns {boolean} True if model is editable, or model with route is editable based on current permission
     */
    var isFormEditable = function (model, routeLink) {
        var result = false;
        var findKey = 'update';

        // var permissionService = tryGetPermissionService();
        //
        // if (permissionService != null) {
        //    var foundState = permissionService.handles_state(routeLink);
        //
        //     if (foundState != null) {
        //         return permissionService.can_goto_state(routeLink); // use this instead of below..
        //     }
        // }

        if (angular.isDefined(access[model]) && angular.isDefined(routes[model])) {
            if (typeof routeLink === 'undefined' || routeLink.trim() === "") {
                // if there's an invalid property set to true then we make that module inaccessible
                if (angular.isDefined(access[model][findKey]) && access[model][findKey] === true) {
                    result = true;
                }
            } else {
                if (angular.isDefined(access[model][routeLink])
                    && angular.isDefined(access[model][routeLink][findKey])) {

                    if (Array.isArray(access[model][routeLink][findKey])
                        && access[model][routeLink][findKey].length > 0) {

                        result = true;
                    } else {
                        if (access[model][routeLink][findKey] === true) {
                            result = true;
                        }
                    }
                }
            }
        }
        return result;
    };

    /**
     * TODO: allow per-item evaluation
     * Return if routeMapping and permissions allow deletion of item
     * @param {string} model the model name
     * @param {string} alias the model alias used for routing
     * @returns {boolean} True if model instance is removable, or model with route has removable property based on
     *          current permission
     */
    var allowDelete = function (model, alias) {
        var result = false;
        var routeLink = ((typeof alias === 'undefined' || alias.trim() === "") ? model : alias) + '.delete';

        var permissionService = tryGetPermissionService();

        if (permissionService != null) {
           var foundState = permissionService.handles_state(routeLink); // ie look for "model.delete" state allowed.

            if (foundState != null) {
                return permissionService.can_goto_state(routeLink); // use this instead of below..
            }
        }

        if (angular.isDefined(access[model]) && angular.isDefined(routes[model])) {
            if (angular.isDefined(access[model][routeLink])) {
                if (Array.isArray(access[model][routeLink]) && access[model][routeLink].length > 0) {
                    result = true;
                } else {
                    if (access[model][routeLink] === true) {
                        result = true;
                    }
                }
            }
        }
        return result;
    };

        /**
     * TODO: allow per-item evaluation
     * Return if routeMapping and permissions allow restoration of item
     * @param {string} model the model name
     * @param {string} alias the model alias used for routing
     * @returns {boolean} True if model instance is restorable, or model with route has restorable property based on
     *          current permission
     */
    var allowRestore = function (model, alias) {
        /*
        var result = false;
        var routeLink = ((typeof alias === 'undefined' || alias.trim() === "") ? model : alias) + '.restore';

        if (angular.isDefined(access[model]) && angular.isDefined(routes[model])) {
            if (angular.isDefined(access[model][routeLink])) {
                if (Array.isArray(access[model][routeLink]) && access[model][routeLink].length > 0) {
                    result = true;
                } else {
                    if (access[model][routeLink] === true) {
                        result = true;
                    }
                }
            }
        }
        return result;
        */
        return allowDelete(model, alias);
    };

    /**
     * Return accessibility flag based on routeMapping and permissions
     *
     * ALSO checks permissionService if the service exists!!
     *
     * @param {string} model the model name
     * @param {string} routeLink the route link to check (Optional)
     * @param {string} action the mode to check ('view', 'edit', etc.)
     * @param {string} field the field name to check (Optional)
     * @returns {boolean} True if model is accessible, or model with route is accessible based on current permission
     */
    var isAccessible = function (model, routeLink, action, field) {

        var permissionService = tryGetPermissionService();

        if (permissionService != null) {
            var stateName = routeLink || model; // if just model assume it's the stateName

            if (action == null) {

                var foundState = permissionService.handles_state(stateName);

                if (foundState != null) {
                    return permissionService.can_goto_state(stateName); // use this instead of below..
                }
            }
            else{ // A field
                var actions = {'view':'read', 'update':'update'};

                var permAction = actions[action];

                var foundPerm = permissionService.handles_permission(stateName, model, field, permAction);

                if (foundPerm != null) {
                    return permissionService.has_permission(stateName, model, field, permAction);
                }
            }
        }

        var result = false;

        if (angular.isDefined(access[model]) && angular.isDefined(routes[model])) {
            if (typeof routeLink === 'undefined' || routeLink.trim() === "") {
                // if there's an invalid property set to true then we make that module inaccessible
                if (angular.isDefined(access[model]['inactive']) && access[model]['inactive']) {
                    result = false;
                    return result;
                }
                angular.forEach(routes[model], function (item) {
                    if (angular.isDefined(access[model][item])) {
                        if (access[model][item] === true) {
                            result = true;
                        } else {
                            for (var prop in access[model][item]) {
                                if (access[model][item].hasOwnProperty(prop)) {
                                    if (access[model][item][prop] === true || (Array.isArray(access[model][item][prop])
                                        && access[model][item][prop].length > 0)) {
                                        result = true;
                                        break;
                                    }
                                }
                            }
                        }
                        if (result) {
                            return result;
                        }
                    }
                });
            } else {
                if (angular.isDefined(access[model][routeLink])) {
                    if (typeof action !== 'string') {
                        if (angular.isDefined(access[model][routeLink]['inactive']) &&
                            access[model][routeLink]['inactive']) {

                            result = false;
                        } else {
                            if (typeof access[model][routeLink] === 'boolean') {
                                result = access[model][routeLink];
                            } else {
                                for (var item in access[model][routeLink]) {
                                   if (access[model][routeLink].hasOwnProperty(item)) {
                                       if (access[model][routeLink][item]) {
                                           result = true;
                                           break;
                                       }
                                   }
                                }
                            }
                        }
                    } else {
                        if (action.trim() !== "") {
                            if (typeof access[model][routeLink] === 'boolean') {
                                return access[model][routeLink];
                            }
                            if (angular.isDefined(access[model][routeLink][action])) {
                                if (typeof field === 'string' && field.trim() !== "") {
                                    if (Array.isArray(access[model][routeLink][action])) {
                                        result = access[model][routeLink][action].indexOf(field) > -1;
                                    } else {
                                        if (access[model][routeLink][action] === true) {
                                            result = true;
                                        }
                                    }
                                } else {
                                    if (access[model][routeLink][action] === true) {
                                        result = true;
                                    }
                                }
                            } else {
                                if (access[model][routeLink][action] === true) {
                                    result = true;
                                }
                            }
                        }
                    }
                }
            }
        }
        return result;
    };

    return {
        additionalRoles: [],
        accessCallback: null,
        resetRoles: resetRoles,
        updateRoles: updateRoles,
        updateFormSettings: updateFormSettings,
        getRole: getRole,
        getRoleWait: getRoleWait,
        getRoles: getRoles,
        updatePermissions: updatePermissions,
        getPermission: getPermission,
        getFormSettings: getFormSettings,
        getLinkSettings: getLinkSettings,
        updateLinkSettings: updateLinkSettings,
        updateRouteMapping: updateRouteMapping,
        getAccessSettings: getAccessSettings,
        updateAccessSettings: updateAccessSettings,
        isAccessible: isAccessible,
        isEditable: isFormEditable,
        allowDelete: allowDelete,
        allowRestore: allowRestore,
        isPermissionsModified: isPermissionsModified,
        isRolesModified: isRolesModified,
        userHasThisRole: userHasThisRole,
        userHasTheseRoles: userHasTheseRoles,
        triggerPageLoaded: triggerPageLoaded,
        subscribeAccessUpdate: subscribeAccessUpdate,
        subscribeUpdateFormCallback: subscribeUpdateFormCallback,
        updateUserRoles: updateUserRoles,
        redirectOn404Error: redirectOn404Error
    }
}
})();
