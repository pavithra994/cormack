/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    /**
     * Common filters for Ocomsoft angularJs templates
     * @author Peter Garas <peter.garas@ocomsoft.com> for Ocom Software
     */
    angular
        .module('app.ocom')
        .filter('properDate', properDate)
        .filter('yesNo', yesNo)
        .filter('previousDate', previousDate)
        .filter('nextDate', nextDate)
        .filter('dateLesser', dateLesser)
        .filter('dateGreater', dateGreater)
        .filter('toArray', toArray)
        .filter('activeOnly', activeDates)
        .filter('hasProp', hasProp)
        .filter('activeExpiring', activeExpiring)
        .filter('dateRange', dateRange);

    function properDate(widgetService) {
        /**
         * Convert date to proper UI format
         * @param {string} date the date to format
         * @param {string} format the date format recognizable by moment.js (e.g. 'MM/DD/YY')
         * @param {string} emptyLabel text to display if date is empty
         * @returns {string} the formatted date
         */
        return function (date, format, emptyLabel) {
            if (!angular.isDefined(format)) {
                format = widgetService.dateFormat;
            }
            if (!angular.isDefined(emptyLabel)) {
                emptyLabel = "-";
            }

            if (date) {
                return moment(new Date(date)).format(format);
            } else {
                return emptyLabel;
            }
        };
    }

    function yesNo() {
        /**
         * Return "Yes" or "No" depending on item boolean value
         * @param item the item we check for its boolean value
         * @returns {string} Yes | No
         */
        return function (item) {
            return item ? "Yes" : "No";
        }
    }

    function previousDate(dataService) {
        /**
         * Return previous date from the given date
         * @param date the date to use
         * @returns {string} the date's previous date
         */
        return function (date) {
            return (date) ? dataService.normalizedDate(moment(new Date(date)).add(-1, 'days')) : '';
        }
    }

    function nextDate(dataService) {
        /**
         * Return the next date from the given date
         * @param date the date to use
         * @returns {string} the date's next date
         */
        return function (date) {
            return (date) ? dataService.normalizedDate(moment(new Date(date)).add(1, 'days')) : '';
        }
    }

    function toArray() {
        /**
         * Convert a list of objects into an array
         * @param list the list to convert
         * @returns {Array} the converted list
         */
        return function (list) {
            if (!(list instanceof Object)) return list;
            return _.map(list, function (val, key) {
                return Object.defineProperty(val, '$key', {__proto__: null, value: key});
            });
        }
    }

    function hasProp() {
        /**
         * Return from the list those which has the property value only
         * @param list the list to filter
         * @param prop the prop to check
         * @param propValue the prop value that each itm in list should have
         * @returns {Array} the filtered list
         */
        return function (list, prop, propValue) {
            var filtered = [];

            // noinspection JSUnusedLocalSymbols
            angular.forEach(list, function (value, key) {
                var add = true;

                if (value.hasOwnProperty(prop)){
                    if (value[prop] !== propValue){
                        add = false;
                    }
                }

                if (add) {
                    this.push(value);
                }
            }, filtered);

            return filtered;
        }
    }

    function activeDates() {
        /**
         * Return from the list those with active status only (or active end date is blank or greater than current date)
         * @param list the list to filter
         * @param exceptId if id exists in the list's indices, add it regardless
         * @returns {Array} the filtered list
         */
        return function (list, exceptId) {
            var filtered = [];
            var now = moment();

            // noinspection JSUnusedLocalSymbols
            angular.forEach(list, function (value, key) {
                if (angular.isDefined(exceptId) && angular.isDefined(value.id) && value.id === exceptId) {
                    this.push(value);
                } else {
                    var add = true;

                    if (value && value.hasOwnProperty('active_start_date')) {
                        if (value.active_start_date) {
                            var activeStartDate = moment(value.active_start_date);

                            if (activeStartDate.isAfter(now)) {
                                add = false;
                            }
                            if (add && value.active_end_date) {
                                var activeEndDate = moment(value.active_end_date);

                                if (activeEndDate.isBefore(now))
                                    add = false;
                            }
                        }
                    }
                    if (add) {
                        this.push(value);
                    }
                }
            }, filtered);

            return filtered;
        }
    }

    function activeExpiring() {
        /**
         * Return from the list those with active status only (or active end date is blank or greater than current date)
         * @param list the list to filter
         * @param max_days maximum number of days to check for expiration
         * @returns {Array} the filtered list
         */
        return function (list, max_days) {
            var filtered = [];
            var now = moment();

            // noinspection JSUnusedLocalSymbols
            angular.forEach(list, function (value, key) {
                var add = false;

                if (value.hasOwnProperty('active_start_date')) {
                    if (value.active_start_date && value.active_end_date) {
                        var activeEndDate = moment(value.active_end_date);

                        if (activeEndDate.isAfter(now) && activeEndDate.isBefore(now.add(max_days, "days"))) {
                            add = true;
                        }
                    }
                }
                if (add) {
                    this.push(value);
                }
            }, filtered);

            return filtered;
        }
    }

    function dateLesser() {
        /**
         * Return the lesser date between the two
         * @param compDate the date to compare with the date to filter
         * @returns the lesser date
         */

        return function (currentDate, compDate) {
            if (currentDate && !compDate) {
                return currentDate;
            }
            if (!currentDate && compDate) {
                return compDate;
            }
            return (currentDate <= compDate) ? currentDate : compDate;
        }
    }

    function dateGreater() {
        /**
         * Return the greater date between the two
         * @param compDate the date to compare with the date to filter
         * @returns the greater date
         */

        return function (currentDate, compDate) {
            if (currentDate && !compDate) {
                return currentDate;
            }
            if (!currentDate && compDate) {
                return compDate;
            }
            return (currentDate > compDate) ? currentDate : compDate;
        }
    }

    function dateRange() {
        /**
         * Return an array based on field specified between date ranges
         * @param (string) dateField the name of the date field or array element object with a date to compare with
         * @param startDate the date to start filtering the list with
         * @param endDate the date to end filtering the list with
         * @returns {Array} the filtered list
         */
        return function (items, dateField, startDate, endDate) {
            var result = [];

            if (!startDate && !endDate) {
                return items;
            }
            angular.forEach(items, function (item) {
                if (item.hasOwnProperty(dateField)) {
                    var queryDate = item[dateField];

                    // skip if date is not present
                    if (queryDate !== null && moment(queryDate).isAfter(startDate) &&
                        moment(queryDate).isBefore(endDate)) {

                        result.push(item);
                    }
                }
            });
            return result;
        }
    }
})();
