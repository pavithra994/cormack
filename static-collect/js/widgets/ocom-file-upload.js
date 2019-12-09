/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

// Upload and list files added for jobs/repairs
angular
    .module('app.ocom')
    .directive('ocomFileUpload', function ($state, $filter, $http, alerts, authService, dataService, Upload) {
        return {
            restrict: 'EA',
            scope: {
                form: '=',
                uploadedFiles: '=',
                model: '=',
                route: '=',
                prefixPath: '@',
                modelFiles: '=',
                fileTypes: '=',
                listOnly: '=',
                disabled: '=',
                noLink: '=',
                compileEmails: '=',
                showInternal: '=',
                fileTypeChangeOnly: '=',
                user: '='
            },
            templateUrl: 'js/widgets/ocom-file-upload.html',
            controller: function ($scope) {
                this.showModal = false;
                this.showView = false;
                this.counter = 1;
                this.toggleDialog = function () {
                    this.showModal = !this.showModal;
                };
                this.toggleView = function () {
                    this.showView = !this.showView;
                };
                this.changeDisplay = function () {
                    this.counter++;
                };

                $scope.upload = {};
                $scope.emailAttachment = [];
                $scope.emailRecipient = [];
                $scope.uploading = false;
                $scope.sending = false;

                var fileTypesById = [];
                var user = ($scope.user) ? $scope.user : authService.getCurrentUser();
                $scope.emailSource = user.email;

                $scope.uploadFile = function (obj, fileType) {
                    if (!angular.isDefined(obj.file)) {
                        return;
                    }

                    var data = {
                        file: obj.file,
                        name: obj.file.name,
                        prefix: $scope.prefixPath,
                        notify: obj.notify,
                        file_type: fileType
                    };

                    $scope.uploading = true;
                    Upload.upload({
                        url: '/api/files/',
                        data: data
                    }).then(function (resp) {
                        if (typeof fileType === 'undefined') {
                            fileType = null;
                        }
                        $scope.uploadedFiles.push(resp.data);
                        $scope.modelFiles.push({
                            id: resp.data.id,
                            notify: obj.notify,
                            file_type: fileType
                        });
                        $scope.uploading = false;
                        console.log("Uploaded:", resp.config.data.file.name, resp.data);
                    }, function (resp) {
                        $scope.uploading = false;
                        console.log("Error status:", resp.status);
                    }, function (evt) {
                        var progressPercentage = parseInt('' + (100.0 * evt.loaded / evt.total));

                        console.log("Progress:" + progressPercentage + "%", evt.config.data.file.name);
                    });
                };

                $scope.updateFileType = function (entry) {
                    var index = _.findIndex($scope.modelFiles, function (instance) {
                        return instance.id === entry.id;
                    });

                    if (index > -1) {
                        console.log("Updating file type...", index, $scope.modelFiles[index], entry.file_type);
                        $scope.modelFiles[index].file_type = entry.file_type;
                        if (entry.file_type === null) {
                            $scope.uploadedFiles[index].can_email = false;
                        } else {
                            if (fileTypesById[entry.file_type]) {
                                $scope.uploadedFiles[index].can_email = fileTypesById[entry.file_type].can_email;
                            }
                        }
                    }
                };

                $scope.removeFile = function (entry) {
                    var index = _.findIndex($scope.modelFiles, function (instance) {
                        return instance.id === entry.id;
                    });

                    console.log("Removing file...", index, entry);
                    $scope.modelFiles.splice(index, 1);
                    $scope.uploadedFiles.splice($scope.uploadedFiles.indexOf(entry), 1);
                    if (angular.isDefined($scope.form)) {
                        $scope.form.$setDirty();
                    }
                };

                $scope.showFile = function (entry) {
                    if ($scope.showInternal) {
                        return true;
                    }

                    var index = _.findIndex($scope.modelFiles, function (instance) {
                        return instance.id === entry.id;
                    });

                    if (index < 0) {
                        return false;
                    }
                    if ($scope.modelFiles[index].file_type === null) {
                        return false;
                    }
                    if ($scope.modelFiles[index].file_type) {
                        return !fileTypesById[$scope.modelFiles[index].file_type].is_internal;
                    }
                    return false; // cannot find file_type then assume can't see
                };

                $scope.isAuthorized = function (entry) {
                    if ($scope.user) {
                        return entry.who_uploaded === user.email || entry.who_uploaded === user.username;
                    }
                    return true;
                };

                $scope.$watch('fileTypes', function(newVal) {
                    fileTypesById = _.keyBy(newVal, 'id');
                });

                $scope.sendEmail = function () {
                    alerts.clearMessages();

                    $scope.email_data.links = _.filter($scope.files_to_send, function (instance) {
                        return instance._send;
                    });

                    if ($scope.email_data.to.trim() === '') {
                        console.log("Empty To List");
                        alerts.error("Unable to send email. You have no mail recipients.");
                        return;
                    }

                    if ($scope.email_data.from.trim() === '') {
                        console.log("Empty Email Source");
                        alerts.error("Unable to send email. You have no email assigned to your account.");
                        return;
                    }

                    if ($scope.email_data.subject.trim() === '') {
                        console.log("Empty Email Subject");
                        alerts.error("Unable to send email. You have no email subject.");
                        return;
                    }

                    if ($scope.email_data.body.trim() === '') {
                        console.log("Empty Email Message");
                        alerts.error("Unable to send email. You have no email message.");
                        return;
                    }

                    if ($scope.email_data.from=='ocomsoft@ocomsoft.com') {
                        $scope.email_data.from = 'carmel@cormackgroup.com.au';
                    }

                    $scope.sending = true;

                    $http.post('/send-email/', $scope.email_data).then(function(result) {
                        console.log("Send Success", result, $scope.email_data);
                        alerts.success("Message was sent.");
                        $scope.sending = false;
                    }, function (err) {
                        console.log("Send Fail", err);
                        alerts.error("Unable to send email.");
                        $scope.sending = false;
                    });
                };

                $scope.can_send_file = function (file) {
                    return fileTypesById[file.file_type].can_email;
                }

                $scope.selectEmail = function (email) {
                    $scope.email_data.to = ($scope.email_data.to || "") + email.email + ",";
                };

                $scope.emailPopup = function () {
                    $scope.emails = $scope.compileEmails();

                    var user = ($scope.user) ? $scope.user : authService.getCurrentUser();

                    $scope.email_data = {
                        from: user.email,
                        to:"",
                        subject: "",
                        body: ""
                    };

                    if ($scope.$parent.item.address) { // Totally wrong..
                        $scope.email_data.subject = $scope.$parent.item.address;
                    }

                    $scope.files_to_send = _.filter($scope.uploadedFiles, $scope.can_send_file);

                    // Tick them
                    _.each($scope.files_to_send, function (item) {
                        item._send = true;
                    })
                };
            }
        }
    });
