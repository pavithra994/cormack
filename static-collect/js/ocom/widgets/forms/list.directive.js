/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    angular.module('app.ocom')
    /**
     * Append item on an array list
     */
    .directive('listAppend', listAppend)
    /**
     * Move an item order down an array list
     */
    .directive('listMoveDown', listMoveDown)
    /**
     * Move an item order up an array list
     */
    .directive('listMoveUp', listMoveUp)
    /**
     * Remove an item from an array list
     */
    .directive('listRemove', listRemove)
    /**
     * Validator for checking an array length.
     * FROM https://stackoverflow.com/questions/22153552/angularjs-validate-form-array-length/32503969#32503969
     * @example
     *   <input ng-model="user.favoriteColors" validate-length />
     */
    .directive('validateLength', validateLength);

    function listAppend() {
        // noinspection JSUnusedLocalSymbols
        return {
            restrict: 'A',
            scope: {
                list: '=', // The List/Array to append to
                item: '@', // The item to add ie {} or {value:0'}
                listIndex: '=' // The Index to append at, so put 0 to put at start of list..
            },
            link: function (scope, elem, attrs) {
                elem.bind('click', function () {
                    var theList = scope.list;
                    var newItem = angular.copy(scope.$eval(scope.item));

                    if (angular.isUndefined(theList)) {
                        scope.list = [];
                        theList = scope.list;
                    }

                    if (newItem !== null) {
                        // noinspection JSUnresolvedVariable
                        scope.$apply(function () {
                            if (angular.isDefined(scope.insertIndex)) {
                                theList.splice(scope.insertIndex, 0, newItem);
                            } else {
                                theList.push(newItem);
                            }
                        });
                    }
                    return false;
                });
            }
        };
    }

    function listMoveDown() {
        // noinspection JSUnusedLocalSymbols
        return {
            restrict: 'A',
            scope: {
                list: '=', // The List/Array to Move Down
                item: '=', // The Item in the array to Move Down
                listIndex: '=' // The Index of the Item to Move Down.
            },
            link: function (scope, elem, attrs) {
                elem.bind('click', function () {
                    var list = scope.list;
                    var index = findIndex(scope.listIndex, list, scope.item);

                    if (index < list.length - 1) {
                        scope.$apply(function () {
                            var original = list[index + 1];

                            list[index + 1] = list[index];
                            list[index] = original;
                        });
                    }
                    return false;
                });
            }
        };
    }

    function listMoveUp() {
        // noinspection JSUnusedLocalSymbols
        return {
            restrict: 'A',
            scope: {
                list: '=', // The List/Array to Move Up
                item: '=', // The Item in the array to Move Up
                listIndex: '=' // The Index of the Item to Move Up.
            },
            link: function (scope, elem, attrs) {
                elem.bind('click', function () {
                    var list = scope.list;
                    var index = findIndex(scope.listIndex, list, scope.item);

                    if (index > 0) {
                        scope.$apply(function () {
                            var original = list[index - 1];

                            list[index - 1] = list[index];
                            list[index] = original;
                        });
                    }
                    return false;
                });
            }
        };
    }

    function listRemove() {
        return {
            restrict: 'A',
            scope: {
                form: '=', // The form to set ng-dirty to
                list: '=', // The List/Array to append to
                item: '=', // The Item in the array to Remove
                listIndex: '=', // The Index of the Item to remove.
                afterClick: '&' // Callback function after click event is triggered
            },
            link: function (scope, elem) {
                elem.bind('click', function () {
                    var index = findIndex(scope.listIndex, scope.list, scope.item);

                    if (index > -1) {
                        scope.$apply(function () {
                            // check if there's an active_end_date property, otherwise, use splice
                            var removeIt = true;

                            if ("active_end_date" in scope.list[index]) {
                                var date = new Date();

                                // minimize race conditions
                                date.setSeconds(0, 0);
                                scope.list[index].active_end_date = date.toJSON();

                                if (scope.list[index].id)
                                    removeIt = false; // don't remove it as there is an ID
                                if (scope.list[index].pk)
                                    removeIt = false; // don't remove it as there is an pk
                            }

                            if (removeIt) {
                                scope.list.splice(index, 1);
                            }
                            if (angular.isDefined(scope.form)) {
                                scope.form.$setDirty();
                            }
                            if (typeof scope.afterClick === 'function') {
                                scope.afterClick();
                            }
                        });
                    }
                    return false;
                });
            }
        };
    }

    function validateLength() {
        return {
            require: 'ngModel',
            link: function(scope, element, attrs, ngModel) {
                // do not set invalid model to undefined, should stay []
                if (!ngModel.$options) {
                        ngModel.$options = {};
                }
                ngModel.$options.allowInvalid = true;

                scope.$watch(function () {
                    return ngModel.$modelValue && ngModel.$modelValue.length; }, function() {
                        ngModel.$validate(); // validate again when array changes
                    }
                );

                ngModel.$validators.length = function() {
                    var arr = ngModel.$modelValue;

                    if(!arr) {
                        return false;
                    }
                    return arr.length > 0;
                };
            }
        };
    }

    function findIndex(listIndex, list, item) {
        if (angular.isDefined(listIndex)) {
            return listIndex;
        }
        return list.indexOf(item);
    }
})();
