/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    angular
        .module('cormack')
        .directive('jobEnter', function () { /* TODO Add this as a directive in ocom submodule */
            return function (scope, element, attrs) {
                element.bind("keydown keypress", function (event) {
                    var key = typeof event.which === "undefined" ? event.keyCode : event.which;
                    if(key === 13) {
                        scope.$apply(function (){
                            scope.$eval(attrs.jobEnter);
                        });

                        event.preventDefault();
                    }
                });
            };
        })
        .directive("jobSelect", ['$http', '$sessionStorage', '$q', 'dataAPIService', 'SweetAlert', function($http, $sessionStorage, $q, dataAPIService, SweetAlert) {
            return {
                restrict: 'A',
                require: ['ngModel', '^form'],
                scope: {
                    ngModel: '=',
                    onChange: "&",
                    onNewJob: "&",
                    ngDisabled: "="
                },
                templateUrl: "js/widgets/select_job.directive.html",
                link: function (scope, elem, attrs, controllers) {
                    var ngModel = controllers[0];
                    var formController = controllers[1];

                    scope.job = null;
                    scope.searchText = "";

                    function getJob(job) {
                        dataAPIService.getDataApi("/api/", "job").getItem(job, function (result) {
                            scope.job = result;
                            scope.searchText = result.address; // set Search to the Job Address for next time
                            scope.joblist = [result]; // Set initial list to the current job if there is one.

                            if (scope.onChange) {
                                scope.onChange({item: result}); // Notify
                            }
                        }, function (err) {
                            scope.job = null;
                            scope.joblist = [];
                        });
                    }

                    function updateTheValue() {
                        if (ngModel.$modelValue) {
                            getJob(ngModel.$modelValue);
                        }
                    }

                    scope.start_again = function () {
                        formController.$setDirty();
                        ngModel.$setDirty();
                        scope.old_job = scope.job; // store so we can highlight what they picked last time.
                        scope.job = null;
                        scope.search (scope.searchText); // start search again..
                    };


                    scope.search = function(searchText) {
                        var params ={limit:50, q:searchText};

                        scope.searching = true;
                        dataAPIService.getDataApi("/api/", "job").list(params, function (response) {
                            scope.joblist = response.results; // Set inital list to the current job if there is one.

                            if (response.count > 50) {
                                SweetAlert.swal("Jobs Found!", "We found over 50 jobs matching your criteria, Try being more specific.", "success");
                            }

                            if (scope.joblist.length < 1) {
                                SweetAlert.swal("No Jobs Found", "No jobs found match the text '" + searchText + "'. Please try again. Try to be less specific ie search by Street name", "error");
                            }

                            scope.searching = false;
                        }, function (err) {
                            scope.searching = false;
                            scope.joblist = [];
                        });

                    };

                    scope.select = function (item) {
                        scope.job = item;

                        if (item) {
                            getJob(item.id);
                            ngModel.$setViewValue(item.id);
                            ngModel.$setDirty();
                            formController.$setDirty();
                        }
                    };

                    scope.noJob = function (searchText) {
                        if (scope.onNewJob) {
                            scope.onNewJob({searchText:searchText})
                        }
                        ngModel.$setViewValue(null);
                        ngModel.$setDirty();
                        formController.$setDirty();
                    };

                    ngModel.$render = function() {
                        updateTheValue();
                    };
                }
            }
        }]);
})();
