/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    /* From https://stackoverflow.com/questions/14833326/how-to-set-focus-on-input-field
     * Add this to a form input to autofocus on it when focus is run from controller
     * From html:
     *      <input id="example" type="text" focus-on="some-reference">
     * From controller:
     *      .controller('SomeController', [..., 'focus'], someController]);
     *      function someController(..., focus) {
     *          function empty() {
     *              ...
     *              // in this example, this will trigger focus onto input#example
     *              focus('some-reference');
     *          }
     *      }
     */

    angular
        .module('app.ocom')
        .directive('focusOn', focusOn);

    function focusOn () {
        return function(scope, element, attr) {
            scope.$on('focusOn', function(e, name) {
                if(name === attr.focusOn) {
                    element[0].focus();

                    if (element[0].nodeName==="INPUT") {
                        element[0].select();
                    }
                }
            });
        };
    }
})();
