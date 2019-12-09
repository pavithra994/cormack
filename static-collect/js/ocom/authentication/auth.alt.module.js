/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    // upper-tier const of routes and path for $state.go and $location.path
    var loginRoute = 'index.login';
    var homeRoute = 'index.home';
    var loginPath = '/login';
    var homePath = '/';
    var allowRoles = true;
    var apiToken = {
        path: {
            refresh: '/api-token-refresh/',
            auth: '/api-token-auth/',
            expire: '/api-token-expire/'
        }
    };

    /**
     * Alternate Auth module
     */
    angular
        .module('app.ocom.auth', ['ngStorage', 'angular-jwt'])
        .config(jwtConfig)
        .config(routeConfig)
        .run(run)
        .service('authService', authService)
        .controller('loginController', LoginController);

    function jwtConfig($httpProvider, $localStorageProvider, jwtOptionsProvider) {
        jwtOptionsProvider.config({
            tokenGetter: function () {
                return $localStorageProvider.get('token');
            }
        });
        // noinspection JSUnresolvedVariable
        $httpProvider.interceptors.push('jwtInterceptor');
    }

    function routeConfig($stateProvider) {
        $stateProvider
            .state(loginRoute, {
                url: "login",
                templateUrl: "js/ocom/authentication/login.html",
                controller: LoginController,
                allow_annonymous:true /* Mark as allow annonymous when not logged in*/
            })
            .state('403', {
                url: "403",
                templateUrl: "js/ocom/authentication/403.html",
                allow_annonymous: true
            });
    }

    function run($localStorage, $state, $location, $rootScope, authService, dataService, dataAPIService, focus) {
        $rootScope.$state = $state;
        $rootScope.$on('$authVerified', function () {
            if ($location.path().indexOf(authService.loginPath) > -1) {
                // Force redirect user to prevent access to login screen while already logged in
                console.log("Verified. Redirecting to main route...");
                $state.go(authService.homeRoute);
            }
        });

        $rootScope.$on('$locationChangeStart', function (event, absNewUrl, absOldUrl) {
            var path = $location.path();

            if (absNewUrl !== absOldUrl) {
                if ($state.params.skip) {
                    // do nothing
                } else {
                    $localStorage.lastLink = absOldUrl;
                }
            }

            // Keep track of lastLink so we can "return" to it require in data.service.js
            if (!angular.isDefined($localStorage.lastLink)) {
                $localStorage.lastLink = '';
            }

            if (path === '') {
                console.log("Empty path. Ignoring process...");
            } else {
                if ($localStorage.isAuthenticated) {
                    console.log("Verifying user login...");
                    $localStorage.lastLinkBeforeLogin = "";
                    authService.checkToken();
                } else {
                    // Redirect user to login screen
                    if (path.indexOf(authService.loginPath) < 0 || path === authService.homePath) {
                        console.log("Redirecting to login...");
                        // remember path
                        $localStorage.lastLinkBeforeLogin = absNewUrl;
                        //noinspection JSUnresolvedFunction
                        event.preventDefault();
                        //$location.path(authService.loginPath);
                        $state.go(authService.loginRoute);
                    }
                    focus('repeat-login');
                }
            }
        });

        $rootScope.$on('$forceRedirect', function () {
            console.log("Force redirect to homepage...");
            dataService.interrupt = true; // backward compatibility
            dataAPIService.interrupt = true;
            $state.go(authService.homeRoute);
        });

        $rootScope.$on('$tokenHasExpired', function () {
            console.log("Token has expired!");
            authService.refreshToken(true);
        });
    }

    function authService($http, $state, $localStorage, $rootScope, $q, $window, roleService, jwtHelper, platform) {
    // TODO: reduce reliance on localStorage except for token
        var tokenInspected = false;

        var currentUser = function () {
            return $localStorage.user;
        };

        /**
         * If auth token is checked, return true
         * @returns {boolean}
         */
        var tokenChecked = function () {
            return tokenInspected;
        };

        var isAuthenticated = function () {
            return $localStorage.isAuthenticated;
        };

        function checkToken () {
            var deferred = $q.defer();
            var expired = true;

            if ("token" in $localStorage) {
                try {
                    expired = jwtHelper.isTokenExpired($localStorage.token);
                } catch (e) {
                    expired = true;
                }
            }

            var handleSuccess = function (result){
                 tokenInspected = true;
                 console.log("Auth checked out", result.data.user);
                 storeAuthentication(result.data.token, result.data.user);
                 $rootScope.$broadcast('$authVerified');
                 return deferred.resolve(true);
            };

            if (expired) {
                var ignoreAjaxError = platform.canGoOffline();

                var tokenData = {
                    token: $localStorage.token
                };

                tokenInspected = false;
                $http.post(apiToken.path.refresh, tokenData).then(function(result) {
                    if (ignoreAjaxError) {
                        platform.setOffline(false);
                    }

                    handleSuccess(result);
                }, function (result) { //failed
                    if (ignoreAjaxError && result.status < 0) { // We are on a tablet and Offline

                        platform.setOffline(true);

                        // Send Fake Result likes it is still OK
                        handleSuccess({'data':{
                             'token': $localStorage.token,
                             'user': $localStorage.user
                            }});
                    }
                    else {
                        tokenInspected = true;
                        console.log("Token expired or invalid: ", result.data);
                        clearAuthentication(false);
                        $rootScope.$broadcast('$tokenHasExpired');
                        return deferred.resolve(false);
                    }
                });
            }
            else {
                tokenInspected = true;

                $rootScope.$broadcast('$authVerified');

                deferred.resolve(true); // We check it's OK so let keep going..
            }

            return deferred.promise;
        }

        function storeAuthentication (token, user) {
            $localStorage.isAuthenticated = true;
            $localStorage.token = token;
            $localStorage.user = user;
        }

        function clearAuthentication(forward) {
            var clearAndForward = function () {
                // TODO: if we're going to user localStorage for persistent data, do we need to clear everything?
                console.log("Cleared token.");
                var newLocalStorage = {
                    isAuthenticated: false,
                    user: null,
                    token: null
                };

                // If there is an array of preserve then copy these then the logout happens to keep them.
                // BE CAREFUL USING THIS AS IT MIGHT CAUSE security issues
                if ('_preserve' in $localStorage) {
                    var preserved = $localStorage['_preserve'];
                    _.each(preserved, function (key) {
                        newLocalStorage[key] = $localStorage[key];
                    });

                }
                $localStorage.$reset(newLocalStorage);

                if (forward) {
                    $state.go(loginRoute, {
                        reload: true
                    });
                }
            };

            //noinspection JSUnusedLocalSymbols
            $http.post(apiToken.path.expire, {'token': $localStorage.token}).finally (function (result) {
                clearAndForward();
                tokenInspected = false;
                $rootScope.$broadcast('$authLogout');
            })
        }

        return {
            apiToken: apiToken, // URI for JWT Ajax Calls.
            homeRoute: homeRoute,  // the home state route; you may want to change this in your app.config.js
            loginRoute: loginRoute, // the login state route; you may want to change this in your app.config.js
            loginPath: loginPath, // the login path; you may want to change this in your app.config.js
            homePath: homePath, // the login path; you may want to change this in your app.config.js
            allowRoles: allowRoles,
            refreshToken: function (forward) {
                clearAuthentication(forward);
            },
            obtainToken: function (username, password) {
                return $http.post(apiToken.path.auth, {
                    username: username,
                    password: password
                }).then(function (result) {
                    if (result.status === 404) {
                        return {
                            success: false
                        }
                    } else {
                        return {
                            success: true,
                            token: result.data.token,
                            user: result.data.user
                        };
                    }
                });
            },
            checkToken: checkToken,
            authenticate: function (token, user) {
                storeAuthentication(token, user);
                if (allowRoles) {
                    roleService.resetRoles();
                }
                $localStorage.$apply();
                if ($localStorage.lastLinkBeforeLogin) {
                    console.log("Proceeding to...", $localStorage.lastLinkBeforeLogin);
                    $window.location.href = $localStorage.lastLinkBeforeLogin;
                    $localStorage.lastLinkBeforeLogin = "";
                } else {
                    $state.go(homeRoute, {
                        reload: true
                    });
                }
            },
            unauthenticate: function () {
                clearAuthentication(true);
            },
            getCurrentUser: currentUser,
            tokenChecked: tokenChecked,
            isAuthenticated: isAuthenticated
        };
    }

    function LoginController($scope, $rootScope, authService, alerts, focus, widgetService) {
        widgetService.setShowFooter(false);

        var invalidLogin = function () {
            focus('repeat-login');
            alerts.error("Invalid Username/password - Please try again.", true);
            $rootScope.$broadcast('$authLoginFail');
        };

        $scope.loginUser = function (form) {
            if (!angular.isDefined(form)) {
                form = {
                    username: '',
                    password: ''
                };
            }
            alerts.clearMessages();
            //noinspection JSUnusedLocalSymbols
            authService.obtainToken(form.username, form.password)
                .then(function (result) {
                    if (result.success) {
                        //authManager.authenticate();
                        authService.authenticate(result.token, result.user);
                        $rootScope.$broadcast('$authLoginSuccess');
                    } else {
                        invalidLogin();
                    }
                }, function (result) {
                    invalidLogin();
                });
        };
    }
})();
