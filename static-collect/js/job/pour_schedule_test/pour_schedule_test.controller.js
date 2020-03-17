/**
 * pour-schedule.controller.js
 * 
 * This controller handles the display of the job schedule for concrete pours. This is called the "Slab Schedule" in
 * most user-facing forms.
 */

(function () {
    "use strict";

    angular
        .module("app.job")
        .controller("JobPourScheduleTestController", [
            "$scope",
            "$resource",
            "dataAPIService",
            JobPourScheduleTestController
        ]);
    
    function JobPourScheduleTestController(
        $scope,
        $resource,
        dataAPIService)
    {
        initialize();

        /**
         * Contains code to set up the initial state of the controller.
         */
        function initialize()
        {
            var resource = $resource("/api/job/:id", { id: "@id" }, {
                "list": {
                    method: "GET",
                    model: "job",
                    interceptor: {
                        response: function (data) {
                            $scope.list = data.results;
                        },
                        responseError: function (err) {
                            console.error("Error fetching resource:", err);
                        }
                    }
                }
            });

            resource.list({}, function () { console.log("A"); }, function () { console.log("B"); })

            /*
            dataAPIService.getDataApi("/api/", "job")
                .list({}, function (data) {
                    $scope.list = data.results
                });
            */
        }

        function getWatchersFromScope(scope) {
            if (scope)
                return scope.$$watchers || [];
            else
                return [];
        }
    }
})();
