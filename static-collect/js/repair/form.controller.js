/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    'use strict';

    var REPAIR_CREATE_FROM_EMAIL_KEY = "repair.create.email";

    angular
        .module('app.repair')
        .controller('RepairController', ['$interval', '$state', '$scope', '$sessionStorage', 'alerts', 'filterFilter',
            'authService', 'dataAPIService', 'CodeTableCacheService', 'formStateService', 'roleService', 'SETTINGS',
            '$localStorage',
            RepairController]);

    /* @ngAnnotate */
    function RepairController($interval, $state, $scope, $sessionStorage, alerts, filterFilter, authService,
                              dataAPIService, CodeTableCacheService, formStateService, roleService, SETTINGS, $localStorage) {
        var models = [];
        var user = $scope.limitUser = authService.getCurrentUser();
        var loadJobsUntilExhausted = null;

        $scope.allowDelete = roleService.allowDelete;
        $scope.allowRestore = roleService.allowRestore;
        $scope.editable = roleService.isEditable;
        $scope.route = $state.current.name;
        $scope.jobLoaded = false;
        $scope.pendingNoteCount = 0;
        $scope.showNotesStatus = false;
        $scope.ongoingRevenue = [];
        $scope.datePaid = [];
        $scope.stagesLoaded = false;
        $scope.employeesLoaded = false;
        $scope.filesEditable = false;
        //$scope.preSaveItem = beforeSave;
        $scope.editorName = user.username;
        $scope.modelName = 'repair';
        $scope.data_api = dataAPIService.getDataApi("/api/", 'repair');
        //$scope.jobApi = dataAPIService.getDataApi("/api/", 'job');
        $scope.uploadedFiles = [];
        $scope.uploadedJobFiles = []; // Job's files!

        $scope.accessible = roleService.isAccessible;
        $scope.formState = formStateService.formState;
        $scope.offset = 5; // number of searches per query
        $scope.item = {
            files: [],
            date_received: new Date(),
            isActive: false
        };
        $scope.activeJobs = [{
            id: 0
        }];

        $scope.token = function () {
            return  $localStorage.token;
        }

        loadLookUps();

        function loadLookUps() {
            var baseFilter = {
                filter: 'active'
            };

            function removePurchaseOrders (data, params) {
                var result = dataAPIService.applyFilters(data, params);

                if (!user.role.administrator && (user.role.subcontractor || user.role.supervisor)) {
                    var filtered = [];

                    // If code in the DB was changed, please change this as well!
                    angular.forEach(result, function (item) {
                        if (item.code !== "PO") {
                            filtered.push(item);
                        }
                    });
                    return filtered;
                } else {
                    return result;
                }
            }

            var loadTables = [
                {
                    uri: '/api/',
                    name: 'subbie',
                    params: baseFilter,
                    callback: dataAPIService.applyFilters,
                    scope: 'repairSubbies'
                },
                {
                    uri: '/api/',
                    name: 'code_repair_type',
                    params: baseFilter,
                    callback: dataAPIService.applyFilters,
                    scope: 'repairTypes'
                },
                {
                    uri: '/api/',
                    name: 'code_file_type',
                    params: baseFilter,
                    callback: removePurchaseOrders,
                    scope: 'fileTypes',
                    keyBy: 'id'
                },
                {
                    uri: '/api/',
                    name: 'supervisor',
                    params: baseFilter,
                    callback: dataAPIService.applyFilters,
                    scope: 'supervisors'
                }
            ];
            models = _.map(loadTables, 'name');
            if ($state.params.id) {
                models.push('repair');
            }
            //models.concat(['repairs', 'files', 'template']);
            CodeTableCacheService.processLoadTables(loadTables, $scope);
        }

        function loadAccountingItems() {
            $scope.xero_entities = []; // have an empty array

            var query = {"logic":"and", "criteria":[{"operation":"eq","name":"other_id","params":[$scope.item.id]},
                    {"operation":"eq","name":"other_name","params":["repair"]}]};

            dataAPIService.getDataApi("/xero/", "xero_entity").list({query:query, offset:0, limit:10000}, function (data) {
                $scope.xero_entities = data.results;
            });
        }

        function loadItem () {
            formStateService.setFormState({loading: true});

            if ($state.params.id) {
                $scope.data_api.list({id: $state.params.id}, function (clientResponse) {
                    $scope.item = clientResponse;
                    /*
                    if ($scope.item.job) {
                        $scope.jobApi.list({id: $scope.item.job}, function (response) {
                            $scope.item.job = response;
                        });
                    }
                    */
                    var currentFiles = $scope.item.files || [];

                    loadAccountingItems();
                    loadRepairFiles(currentFiles);
                });
            } else {
                if (REPAIR_CREATE_FROM_EMAIL_KEY in $sessionStorage) {
                    $scope.item = $sessionStorage[REPAIR_CREATE_FROM_EMAIL_KEY];
                    console.log("ITEM LOADED", $scope.item);
                    $scope.uploadedFiles = $scope.item.files || [];
                    delete $sessionStorage[REPAIR_CREATE_FROM_EMAIL_KEY];
                }
                $scope.refreshUpdateTable = true;
            }
        }

        function loadRepairFiles(files) {
            $scope.uploadedFilesDone = [];
            for (var i = 0; i < files.length; i++) {
                $scope.uploadedFilesDone.push({'id': files[i].id, 'done': false});
                dataAPIService.getDataApi("/api/", 'files').list({id: files[i].id}, function (response) {
                    if (!user.role.administrator && user.role.subcontractor) {
                        if ($scope.fileTypes_by_id[response.file_type]) {
                            $scope.uploadedFiles.push(response);
                        }
                    } else {
                        $scope.uploadedFiles.push(response);
                    }
                });
            }
        }

        $scope.uploadedJobFilesDone = [];
        function loadJobsFiles(files) {
            $scope.uploadedJobFilesDone = [];
            $scope.uploadedJobFiles = [];

            for (var i = 0; i < files.length; i++) {
                $scope.uploadedJobFilesDone.push({'id': files[i].id, 'done': false});
                dataAPIService.getDataApi("/api/", 'files').list({id: files[i].id}, function (response) {
                    if (!user.role.administrator && user.role.subcontractor) {
                        if ($scope.fileTypes_by_id[response.file_type]) {
                            $scope.uploadedJobFiles.push(response);
                        }
                    } else {
                        $scope.uploadedJobFiles.push(response);
                    }
                });
            }
        }


        function getIndexFromItem (item) {
            var index;

            if (typeof item.id === "undefined") {
                index = _.findIndex($scope.item.repair_costs, function (cost) {
                    return cost.new_count === item.new_count;
                });
            } else {
                index = _.findIndex($scope.item.repair_costs, function (cost) {
                    return cost.id === item.id;
                });
            }

            return index;
        }

        $scope.viewable = function (item) {
            return roleService.isAccessible($scope.modelName, $scope.route, 'view', item);
        };

        $scope.viewOnly = function (item) {

            //SW: This can cause all Inputs to be disabled if item.isActive == false
            if ("isActive" in $scope.item && !$scope.item.isActive) {
                return true;
            }

            if (roleService.isAccessible($scope.modelName, $scope.route, 'update', item)) {
                return formStateService.formState('saving') || formStateService.formState('loading');
            } else {
                return true;
            }
        };

        function filesEditable() {
            if (roleService.isAccessible($scope.modelName, $scope.route, 'update', 'repair_files')) {
                return true;
            }
            return roleService.isAccessible($scope.modelName, $scope.route, 'update', 'repair_files_limited');
        }

        var updateRoleInformation = function () {
            $scope.isAdmin = roleService.userHasThisRole('administrator');

            if ($scope.isAdmin) {
                // set this off so Admins can send email
                $scope.limitUser = null;
            }

            if (roleService.getRole("supervisor")) {
                $scope.supervisor_id = roleService.getRole("supervisor_id");
            }
            if (roleService.getRole("subcontractor")) {
                $scope.subbie_id = roleService.getRole("subbie_id");

            }
            loadItem(); // Load item now we know WHO it is
        };

        $scope.getTotal = function (item) {
            var index = getIndexFromItem(item);
            var total = $scope.item.repair_costs[index]['quantity'] *
                parseFloat($scope.item.repair_costs[index]['unit_price']);
            $scope.item.repair_costs[index]['total_price'] = total.toFixed(2);
        };

        $scope.compileEmails = function () {
            // compile list of emails
            var emails = [];

            return emails;
        };

        $scope.toggleShowNotes = function () {
            $scope.showNotesStatus = !$scope.showNotesStatus;
        };

        $scope.addNoteCount = function () {
            $scope.pendingNoteCount++;
        };

        $scope.changeSupervisor = function (supervisor_id) {
            var index = _.findIndex($scope.supervisors, function (instance) {
                return instance.id === supervisor_id;
            });

            if (angular.isDefined($scope.supervisors[index])) {
                $scope.item.supervisor_mobile_number = $scope.supervisors[index].phone_number;
                $scope.item.supervisor_email = $scope.supervisors[index].email;
            } else {
                $scope.item.supervisor_mobile_number = '';
                $scope.item.supervisor_email = '';
            }
        };

        /*
        $scope.isActiveDate = function (item) {
            if (angular.isDefined(item.active_end_date)) {
                return item.active_end_date === null || new Date().toJSON() <= item.active_end_date;
            }
            return true;    // must be new
        };

        $scope.editProduct = function (id) {
            if (angular.isDefined(allOpportunities[id])) {
                return allOpportunities[id].has_product;
            } else {
                return false;
            }
        };

        $scope.checkProduct = function (id, index) {
            if (angular.isDefined(allOpportunities[id])) {
                if (!allOpportunities[id].has_product) {
                    $scope.item.business_opportunity[index].product = '';
                }
            }
        };
        */

        /*
        $scope.fetch = function($select) {
            if ($select.search.trim() === "" || $scope.formState('loading')) {
                return;
            }

            // if you click on the controls too quickly, a race condition happens, so...
            if (loadJobsUntilExhausted) {
                $scope.cancelLoadJobs(false);
                return;
            }
            $scope.loading = true;
            loadJobsUntilExhausted = $interval(function () {
                if ($select.search.trim() === "") {
                    $scope.cancelLoadJobs(true);
                    return;
                }

                if ($scope.lastSearchTerm !== $select.search) {
                    $scope.lastSearchTerm = $select.search;
                    $scope.currentOffset = 0;
                }

                var params = {
                    filter: 'active',
                    q: $select.search,
                    fieldList: ['job_number', 'address'],
                    offset: $scope.currentOffset,
                    limit: $scope.offset
                };

                console.log("Search Term, Offset:", params['q'], $scope.currentOffset);
                $scope.jobApi.list(params, function (response) {
                    console.log("Found:", response);
                    angular.forEach(response.results, function(value) {
                        var found = false;

                        for (var i = 0; i < $scope.activeJobs.length; i++) {
                            if (value.id === $scope.activeJobs[i].id) {
                                found = true;
                                break;
                            }
                        }
                        if (!found) {
                            $scope.activeJobs.push(value);
                        }
                    });
                    if (response.results.length < $scope.offset) {
                        $scope.cancelLoadJobs(false);
                    } else {
                        $scope.loading = false;
                        $scope.currentOffset += $scope.offset;
                    }
                });
            }, 300);    // 250 milliseconds
        };
        */

        $scope.noJob = function (searchText) {
            $scope.item.no_job = true;
            $scope.item.address = searchText;
        }

        $scope.onJobChanged = function (item) {
            $scope.job = item;

            if (item)
                loadJobsFiles(item.files);
            else
                loadJobsFiles([]);
        };

        /*
        $scope.onOpenClose = function (isOpen, value, form) {
            $scope.currentOffset = 0;
            $scope.displayCurrentJob = isOpen;
            $scope.cancelLoadJobs(true);
            if (!isOpen) {
                form.job.$setTouched();
            }
        };

        var cancelIntervalJobs = function () {
            console.log("Clearing job interval...");
            if (loadJobsUntilExhausted !== null) {
                $interval.cancel(loadJobsUntilExhausted);
                loadJobsUntilExhausted = null;
            }
            $scope.loading = false;
        };

        $scope.selectJob = function (job) {
            $scope.cancelLoadJobs(false);
            if (job) {
                $scope.jobAvailable = true;
            }
        };

        $scope.cancelLoadJobs = function (clear) {
            console.log("Stopping job load...");
            cancelIntervalJobs();
            if (clear) {
                $scope.activeJobs = [{
                    id: 0
                }];
            }
        };

        function beforeSave(item) {
            if (item.job) {
                item.job = (item.job.id) ? item.job.id : null;
            }
            $scope.cancelLoadJobs(false);
            console.log("Before save:", item);
            return item;
        }
        */

        /* Override for default impls */
        $scope.validateItem = function (item) {
            return true;
        };

        $scope.$watch('item.rejected_date', function (value) {
            if ($scope.item.isActive && value) {
                $scope.item.back_charge = true;
            }
        });

        $scope.costItemChanged = function (row, selectedItem) {
            if (!row.invoiced) {
                row.unit_price = selectedItem.SalesDetails.UnitPrice;
                $scope.getTotal(row);

                if (!row.details)
                    row.details = selectedItem.Description;
            }
        };

        $scope.canGenerateInvoice = function() {
            if (!$scope.item.repair_costs)
                $scope.item.repair_costs = []; // init the array if it's empty

            return _.filter($scope.item.repair_costs, {"invoiced": true}).length != $scope.item.repair_costs.length; // Look for invoices rows and if they are all invoiced then disable
        };

        $scope.createInvoices = function() {
            dataAPIService.getDataApi("/api/", "repair").updateItem($scope.item.id, $scope.item, function (success) {
                dataAPIService.getDataApi("/api/", "create_repair_invoice").action({'id': $scope.item.id}, function (response) {
                    alerts.success("Generated Invoice: " + response.xero_code + " In Xero", false);

                    $scope.xero_entities.push (response);


                    console.log(response);

                    $scope.skipConfirm = true; // Skip confirm
                    $state.go($state.current, {}, {reload: true});
                });
            });
        };

        $scope.createPurchaseOrder = function() {
            if (!$scope.item.xero_purchase_order) {
                dataAPIService.getDataApi("/api/", "repair").updateItem($scope.item.id, $scope.item, function (success) {
                    dataAPIService.getDataApi("/api/", "create_repair_purchase_order").action({'id': $scope.item.id}, function (response) {
                        $scope.item.xero_purchase_order = response;

                        $scope.xero_entities.push(response);

                        alerts.success("Generated Purchase Order: " + response.xero_code + " In Xero", false);

                        console.log(response);

                        $scope.skipConfirm = true; // Skip confirm
                        $state.go($state.current, {}, {reload: true});
                    });
                });
            }
        };

        $scope.waitLoadAllApi = $interval(function() {
            if (models.length > 0 && formStateService.isLoaded(models)) {
                formStateService.setFormState({loading: false});
                $scope.filesEditable = filesEditable();
                if (user.role.can_see_plans_before_accept || $scope.filesEditable) {
                    $scope.item.isActive = ($state.params.id) ? $scope.item.is_active : true;
                } else {
                    $scope.item.isActive = $scope.item.accepted_date !== null;
                }
                $state.params.skip = true;
                $scope.jobLoaded = true;
                console.log("All Repair modules loaded.");
                $interval.cancel($scope.waitLoadAllApi);
            }
        }, SETTINGS.interval);

        roleService.subscribeAccessUpdate($scope, updateRoleInformation);
        // roleService.triggerPageLoaded($scope);
    }
})();
