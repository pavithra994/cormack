/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019 
 *
 */

angular
    .module('app.email')
    .controller('EmailListController', EmailListController);

function EmailListController($state, $http, $scope, alerts, dataAPIService, roleService, widgetService) {
    var fields = [
        {'id': 'subject', 'name': 'Subject'}
    ];

    widgetService.setShowFooter(true);

    $scope.modelName = 'email';
    $scope.accessible = roleService.isAccessible;
    $scope.listOptions = {
        total: 0,
        currentPage: 1,
        filter: $state.params.filter || "",
        sort: $state.params.sort || "id",
        order: $state.params.order || "desc",
        q: $state.params.q || "",
        searchField: $state.params.searchField || "",
        ordering: $state.params.ordering || "",
        limit: parseInt($state.params.limit) || 10,
        offset: parseInt($state.params.offset) || 0
    };
    $scope.listLoaded = false;
    $scope.maxRanges = [10, 20, 50, 100];
    $scope.fields = fields;

    loadList();

    function loadList() {
        var options = angular.copy($scope.listOptions);

        dataAPIService
            .getDataApi('/api/', 'mail-messages')
            .list(options, function (data) {
                $scope.list = data.results;
                $scope.listOptions.total = data.count;
                $scope.listOptions.currentPage = Math.ceil($scope.listOptions.offset / $scope.listOptions.limit) + 1;
                $scope.listLoaded = true;
            });
    }

    $scope.getNewMails = function () {
        // TODO: use staggered loading of emails to prevent long waits / timeouts
        $http.get('/fetch-emails/').then(function (response) {
            if (response.data.count > 0) {
                alerts.success("New emails retrieved: " + response.data.count, true);
                $state.reload();
            } else {
                alerts.info("No new emails found.");
            }
        })
    };

    $scope.$on('$formSettingsUpdate', function () {
        $scope.access = roleService.getAccessSettings();
    });

    roleService.subscribeAccessUpdate($scope);
}
