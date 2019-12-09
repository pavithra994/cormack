/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

/**
 * extension of ui-select from ui-angular
 * to support infinity list of items
 *
 * http://plnkr.co/p6Dt3yvTq40Vn56AKiqC
 */

angular
    .module('ui-select-infinity', [])
    .directive('reachInfinity', ['$parse', '$timeout', '$q', function($parse, $timeout, $q) {
        function height(elem) {
            elem = elem[0] || elem;
            if (isNaN(elem.offsetHeight)) {
                return elem.document.documentElement.clientHeight;
            } else {
                return elem.offsetHeight;
            }
        }

        function offsetTop(elem) {
            if (!elem[0].getBoundingClientRect || elem.css('none')) {
                return;
            }
            return elem[0].getBoundingClientRect().top + pageYOffset(elem);
        }

        function pageYOffset(elem) {
            elem = elem[0] || elem;
            if (isNaN(window.pageYOffset)) {
                return elem.document.documentElement.scrollTop;
            } else {
                return elem.ownerDocument.defaultView.pageYOffset;
            }
        }

        /**
         * Since scroll events can fire at a high rate, the event handler
         * shouldn't execute computationally expensive operations such as DOM modifications.
         * based on https://developer.mozilla.org/en-US/docs/Web/Events/scroll#requestAnimationFrame_.2B_customEvent
         *
         * @param type
         * @param name
         * @param (obj)
         * @returns {Function}
         */
        function throttle(type, name, obj) {
            var running = false;

            obj = obj || window;

            var func = function() {
                if (running) {
                    return;
                }

                running = true;
                requestAnimationFrame(function() {
                    obj.dispatchEvent(new CustomEvent(name));
                    running = false;
                });
            };

            obj.addEventListener(type, func);

            return function() {
                obj.removeEventListener(type, func);
            };
        }

        return {
            link: function(scope, elem, attrs) {
                var container = elem,
                    scrollDistance = angular.isDefined(attrs.scrollDistance) ? parseInt(attrs.scrollDistance) : 0.3,
                    removeThrottle;

                function tryToSetupInfinityScroll() {

                    container = angular.element(elem.querySelectorAll('.ui-select-choices-content'));

                    var handler = function() {
                        var containerBottom = height(container),
                            containerTopOffset = 0,
                            elementBottom;

                        if (offsetTop(container) !== void 0) {
                            containerTopOffset = offsetTop(container);
                        }

                        var rows = elem.querySelectorAll('.ui-select-choices-row');
                        var lastChoice = angular.element(rows[rows.length - 1]);

                        elementBottom = offsetTop(lastChoice) - containerTopOffset + height(lastChoice);

                        var remaining = elementBottom - containerBottom,
                            shouldScroll = remaining <= height(container) * (scrollDistance + 1);

                        if (shouldScroll) {
                            $q.when($parse(attrs['reachInfinity'])(scope)).then(function() {
                                setTimeout(function() {
                                    rows = elem.querySelectorAll('.ui-select-choices-row');
                                    lastChoice = angular.element(rows[rows.length - 1]);
                                }, 0);
                            });
                        }
                    };

                    removeThrottle = throttle('scroll', 'optimizedScroll', container[0]);
                    container.on('optimizedScroll', handler);

                    scope.$on('$destroy', function() {
                        removeThrottle();
                        container.off('optimizedScroll', handler);
                    });

                    return true;
                }

                var unbindWatcher = scope.$watch('$select.open', function(newItems) {
                    if (!newItems) {
                        return;
                    }

                    $timeout(function() {
                        if (tryToSetupInfinityScroll()) {
                            unbindWatcher();
                        }
                    });
                });
            }
        }
    }]);
