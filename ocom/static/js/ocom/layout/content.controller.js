/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    angular
        .module('app.ocom')
        .controller('ContentController', ContentController);

    function ContentController($filter, $scope) {
        console.log('Content controller');

        // experimental: we'll share this to child controllers
        $scope.formatDate = function (str) {
            var d = "None";
            if (str) d = new Date(str);
            return $filter('date')(d, "dd/MM/yyyy");
        };
    }
})();
