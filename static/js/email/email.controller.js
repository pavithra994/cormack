/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019 
 *
 */

(function () {
    'use strict';

    var JOB_CREATE_FROM_EMAIL_KEY = "job.create.email";
    var REPAIR_CREATE_FROM_EMAIL_KEY = "repair.create.email";

    angular
        .module('app.email')
        .controller('EmailController', ['$http', '$state', '$scope', '$sessionStorage', '$interval', '$timeout',
            'alerts', 'dataAPIService', 'formStateService', 'authService', 'roleService', EmailController]);

    function EmailController($http, $state, $scope, $sessionStorage, $interval, $timeout, alerts, dataAPIService,
                             formStateService, authService, roleService) {

        var user = authService.getCurrentUser();

        $scope.modelName = 'email';
        $scope.allowDelete = roleService.allowDelete;
        $scope.allowRestore = roleService.allowRestore;
        $scope.route = $state.current.name;
        $scope.data_api = dataAPIService.getDataApi("/api/", 'mail-messages');
        $scope.validateItem = validateItem;
        $scope.viewable = viewable;
        $scope.viewOnly = viewOnly;

        loadItem();

        function loadItem() {
            $scope.item = {};
            if ($state.params.id) {
                formStateService.setFormState({loading: true});
                $scope.data_api.list({id: $state.params.id}, function (response) {
                    $scope.attachments = [];
                    $scope.item = response;
                    $scope.accessible = roleService.isAccessible;
                    $scope.editable = roleService.isEditable;

                    for (var i = 0; i < response.attachments.length; i++) {
                        response.attachments[i]['include'] = true;
                        $scope.attachments.push(response.attachments[i]);
                    }
                    formStateService.setFormState({loading: false});
                    roleService.triggerPageLoaded($scope);
                });
            }
        }

        // convenience function for checking if item is viewable
        function viewable(item) {
            return roleService.isAccessible('email', 'email.assign', 'view', item);
        }

        // convenience function for checking if item is disabled
        function viewOnly(item) {
            if (roleService.isAccessible('email', 'email.assign', 'update', item)) {
                return formStateService.formState('saving') || formStateService.formState('loading');
            } else {
                return true;
            }
        }

        function getFilesFromAttachments(attachments) {
            var files = [];

            angular.forEach(attachments, function (attachment) {
                if (attachment.include) {
                    files.push({
                        id: attachment.id,
                        file: attachment.document,
                        name: attachment.document.split('\\').pop().split('/').pop(),
                        who_uploaded: user.username,
                        file_type: ''
                    });
                }
            });

            return files;
        }

        $scope.createJob = function (item) {
            var newItem = {
                email: true,
                date_received: new Date(),
                part_a_date: null,  // we have to set this so it will not trigger required for part a booking no.
                notes: [{
                    note: item.text,
                    when_formatted: "Pending (1)",
                    who: user.username
                }],
                files: []
            };

            newItem.files = getFilesFromAttachments($scope.attachments);
            $sessionStorage[JOB_CREATE_FROM_EMAIL_KEY] = newItem;
            $state.go('job.create', {}, {reload: true});
        };

        $scope.createRepair = function (item) {
            var newItem = {
                email: true,
                date_received: new Date(),
                part_a_date: null,  // we have to set this so it will not trigger required for part a booking no.
                notes: [{
                    note: item.text,
                    when_formatted: "Pending (1)",
                    who: user.username
                }],
                files: []
            };

            newItem.files = getFilesFromAttachments($scope.attachments);
            $sessionStorage[REPAIR_CREATE_FROM_EMAIL_KEY] = newItem;
            $state.go('repair.create', {}, {reload: true});
        };

        /* Override for default impls */

        //noinspection JSUnusedLocalSymbols
        function validateItem(item) {
            return true;
        }
    }
})();
