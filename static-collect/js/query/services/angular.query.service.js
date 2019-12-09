/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019 
 *
 */

(function () {
    angular
        .module('ocom.query', [])
        .factory("queryFactory", [function() {
            var operations = {
                'eq': function (fieldname, params) {
                    return function (item) {
                        return item[fieldname] == params[0];
                    }
                },
                'gt': function (fieldname, params) {
                    return function (item) {
                        return item[fieldname] > params[0];
                    }
                },
                'ge': function (fieldname, params) {
                    return function (item) {
                        return item[fieldname] >= params[0];
                    }
                },
                'lt': function (fieldname, params) {
                    return function (item) {
                        return item[fieldname] < params[0];
                    }
                },
                'le': function (fieldname, params) {
                    return function (item) {
                        return item[fieldname] <= params[0];
                    }
                },
                'is_null': function (fieldname, params) {
                    return function (item) {
                        return item[fieldname] == null;
                    }
                },
                'is_not_null': function (fieldname, params) {
                    return function (item) {
                        return item[fieldname] != null;
                    }
                },
                'between': function (fieldname, params) {
                    return function (item) {
                        return item[fieldname] >= params[0] && item[fieldname] <= params[1];
                    }
                },
                'contains': function (fieldname, params) {
                    params[0] = String(params[0]); // Pre-convert to String to ensure it's always a String

                    return function (item) {
                        return String(item[fieldname]).includes(params[0]);
                    }
                },
                'icontains': function (fieldname, params) {
                    params[0] = String(params[0]).toUpperCase(); // Pre-convert to Uppercase String to ensure it's always an Uppercase String

                    return function (item) {
                        return String(item[fieldname]).toUpperCase().includes(params[0]);
                    }
                },
            };


            var special_codes = {
                "date-now": function () {
                    return [new Date()];
                },
                "date-today": function () {
                    var result = moment(0, "HH");

                    return [result.toDate()];
                },
                "date-tomorrow":function () {
                    var result = moment(0, "HH");

                    result = result.add(1, "days");

                    return [result.toDate()];
                },
                "date-yesterday":function () {
                    var result = moment(0, "HH");

                    result = result.subtract(1, "days");

                    return [result.toDate()];
                },
                "this-week": function () {
                    var result1 = moment().startOf('week');

                    var result2 = result1.add(1, "weeks");

                    return [result1, result2];
                },
                "last-week": function () {
                    var result1 = moment().startOf('week');

                    result1 = result1.subtract(1, "weeks");

                    var result2 = result1.add(1, "weeks");

                    return [result1, result2];
                },
                "next-week": function () {
                    var result1 = moment().startOf('week');

                    result1 = result1.add(1, "weeks");

                    var result2 = result1.add(1, "weeks");

                    return [result1, result2];
                }
                // TODO Others..
            };
            function prepareCriteria(query) {
                // ie {name:"fieldname", operation:"op", params:[], special:'special-code'}
                // special is optional - if found then looks up  special_codes dict for code to generate params

                var fieldname = query.name;
                var op = query.operation;
                var params = query.params;

                query.toString = function () {
                    return fieldname + " " + op + " " + params;
                };

                if ("special" in query) {
                    query.params = special_codes[query.special](); // Get "Special" Values
                }

                var found = operations[op];
                if (found)
                    query.filter = found(fieldname, params);
                else
                    query.filter = function (item) {
                        return true; // NOOP
                    };
            }

            function prepareAnd(query) {
                // ie {logic:"and", criteria:[item, item]}
                _.each(query.criteria, function (queryItem) {
                    prepareItem(queryItem);
                });

                query.toString = function () {
                    return "AND";
                };

                query.filter = function (item) {
                    var result = true;

                    _.each(query.criteria, function (queryItem) {
                        if (_.isFunction(queryItem.filter)) {
                            if (result) {
                                var filterResult = queryItem.filter(item);
                                result = result && filterResult;

                                console.log(queryItem.toString() + " == " + filterResult);
                            }
                        }
                    });

                    return result;
                }
            }

            function prepareOr(query) {
                // ie {logic:"or", criteria:[item, item]}

                _.each(query.criteria, function (queryItem) {
                    prepareItem(queryItem);
                });

                query.toString = function () {
                    return "OR";
                };

                query.filter = function (item) {
                    var result = false;

                    _.each(query.criteria, function (queryItem) {
                        if (!result) {
                            if (_.isFunction(queryItem.filter)) {
                                var filterResult = queryItem.filter(item);

                                if (filterResult) {
                                    result = true;
                                }

                                console.log(queryItem.toString() + " == " + filterResult);
                            }
                        }
                    });

                    return result;
                }
            }


            /*
                Determine type of Query Item
             */
            function prepareItem(query) {
                if ('name' in query) {
                    prepareCriteria(query)
                }
                if ("logic" in query) {
                    if (query.logic == 'or') {
                        prepareOr(query);
                    }
                    if (query.logic == 'and') {
                        prepareAnd(query);
                    }
                }
            }

            return {
                prepare: prepareItem
            }
        }]);
})();
