/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    'use strict';

    var JOB_CREATE_TEMPLATE_KEY = "job.create.template";
    var JOB_CREATE_FROM_EMAIL_KEY = "job.create.email";

    angular
        .module('app.job')
        .controller('JobController', ['$filter', '$interval', '$state', '$scope', 'alerts', 'authService',
            'dataAPIService', 'CodeTableCacheService', 'formStateService', 'roleService', 'SETTINGS',
            '$sessionStorage', '$localStorage',
            JobController]);

    /* @ngAnnotate */
    function JobController($filter, $interval, $state, $scope, alerts, authService, dataAPIService, CodeTableCacheService,
                           formStateService, roleService, SETTINGS, $sessionStorage, $localStorage) {
        var models = [];
        var tasksByJob = []; // this does not go thru code table cache so we manually do keyBy
        var user = $scope.limitUser = authService.getCurrentUser();

        $scope.allowDelete = roleService.allowDelete;
        $scope.allowRestore = roleService.allowRestore;
        $scope.editable = roleService.isEditable;
        $scope.route = $state.current.name;
        $scope.refreshUpdateTable = false;
        $scope.pendingNoteCount = 0;
        $scope.showNotesStatus = false;
        $scope.ongoingRevenue = [];
        $scope.datePaid = [];
        $scope.stagesLoaded = false;
        $scope.employeesLoaded = false;
        $scope.filesEditable = false;
        $scope.editorName = user.username;
        $scope.modelName = 'job';
        $scope.data_api = dataAPIService.getDataApi("/api/", 'job');
        $scope.uploadedFiles = [];
        $scope.accessible = roleService.isAccessible;
        $scope.formState = formStateService.formState;
        $scope.lastPurchaseOrderNumber = "";
        $scope.item = {
            files: [],
            part_a_date: null,
            date_received: new Date(),
            estimated_cost: '0.00'
        };

        $scope.token = function () {
            return  $localStorage.token;
        };

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
                    scope: 'subcontractors',
                    keyBy: 'id'
                },
                {
                    uri: '/api/',
                    name: 'code_supplier',
                    params: baseFilter,
                    scope: 'supplier',
                    keyBy: 'id'
                },
                {
                    uri: '/api/',
                    name: 'code_job_type',
                    params: baseFilter,
                    callback: dataAPIService.applyFilters,
                    scope: 'jobTypes',
                    keyBy: 'code'
                },
                {
                    uri: '/api/',
                    name: 'code_depot_type',
                    params: baseFilter,
                    callback: dataAPIService.applyFilters,
                    scope: 'depotTypes',
                    keyBy: 'code'
                },
                {
                    uri: '/api/',
                    name: 'code_mix',
                    params: baseFilter,
                    callback: dataAPIService.applyFilters,
                    scope: 'pavingMixes'
                },
                {
                    uri: '/api/',
                    name: 'code_purchase_order_type',
                    params: baseFilter,
                    callback: dataAPIService.applyFilters,
                    scope: 'orderTypes'
                },
                {
                    uri: '/api/',
                    name: 'code_paving_colour',
                    params: baseFilter,
                    callback: dataAPIService.applyFilters,
                    scope: 'pavingColours'
                },
                {
                    uri: '/api/',
                    name: 'code_paving_type',
                    params: baseFilter,
                    callback: dataAPIService.applyFilters,
                    scope: 'pavingTypes'
                },
                {
                    uri: '/api/',
                    name: 'code_drain_type',
                    params: baseFilter,
                    callback: dataAPIService.applyFilters,
                    scope: 'drainTypes'
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
                    name: 'client',
                    params: baseFilter,
                    callback: dataAPIService.applyFilters,
                    scope: 'clients',
                    keyBy: 'id'
                },
                {
                    uri: '/api/',
                    name: 'supervisor',
                    params: baseFilter,
                    callback: dataAPIService.applyFilters,
                    scope: 'supervisors',
                    keyBy: 'id'
                },
                {
                    uri: '/api/',
                    name: 'code_task_type',
                    params: baseFilter,
                    callback: dataAPIService.applyFilters,
                    scope: 'code_task_type',
                    keyBy: 'id'
                },
                {
                    uri: '/api/',
                    name: 'code_time_of_day',
                    params: baseFilter,
                    callback: dataAPIService.applyFilters,
                    scope: 'time_of_day_List',
                    keyBy: 'id'
                }
            ];

            models = _.map(loadTables, 'name');
            if ($state.params.id) {
                models.push('job');
            }
            models.push('tasks');
            CodeTableCacheService.processLoadTables(loadTables, $scope);
        }

        function loadAccountingItems() {
            $scope.xero_entities = []; // have an empty array

            var query = {"logic":"and", "criteria":[{"operation":"eq","name":"other_id","params":[$scope.item.id]},
                    {"operation":"eq","name":"other_name","params":["job"]}]};

            dataAPIService.getDataApi("/xero/", "xero_entity").list({query:query, offset:0, limit:10000}, function (data) {
                $scope.xero_entities = data.results;
            });
        }

        function loadItem() {
            formStateService.setFormState({loading: true});
            if ($state.params.id) {
                $scope.data_api.list({id: $state.params.id}, function (clientResponse) {
                    $scope.item = clientResponse;
                    $scope.refreshUpdateTable = true;
                    var currentFiles = $scope.item.files || [];

                    loadJobFiles(currentFiles);
                    if (!$scope.item.purchase_orders)
                        $scope.item.purchase_orders = []; // Ensure it's an array

                    // Migration Code. If there are NO items in array assume it needs to be migrated.
                    if (!$scope.item.purchase_orders.length) {
                        $scope.item.purchase_orders.push({"number": $scope.item.purchase_order_number,
                            "value": $scope.item.purchase_order_value,
                            "order_type": null,
                            "details":"Copied from original data"});
                    }

                    if (!$scope.item.job_drains) {
                        $scope.item.job_drains = []; // Ensure it's an array
                    }

                    // Migration Code. If there are NO items in array assume it needs to be migrated.
                    if (!$scope.item.job_drains.length && $scope.item.drain_type && $scope.isJobType('Paving')) {
                        $scope.item.job_drains.push({
                            "drain_type": $scope.item.drain_type,
                            "metres": $scope.item.drains,
                            "active_end_date": null,
                            "active_start_date": new Date()
                        });
                    }

                    loadAccountingItems();

                    var query = [{logic:'and', 'criteria':[{operation:"eq", name:'job__id', params:[$scope.item.id]}]}];

                    dataAPIService.getDataApi("/api/", "tasks").list({'query':query, limit:1000, offset:0}, function (response) {
                        $scope.item_tasks = response.results;
                        tasksByJob = _.keyBy($scope.item_tasks, 'job');
                    })
                });
            } else {
                formStateService.setFormState({loading: false}); // Loaded already for CREATE
                //if we have a JOB_CREATE_TEMPLATE_KEY in the sessionStorage use that as the basis of this new Job
                if (JOB_CREATE_TEMPLATE_KEY in $sessionStorage) {
                    $scope.item = $sessionStorage[JOB_CREATE_TEMPLATE_KEY];
                    delete $scope.item.id; // Ensure it's a different ID

                    delete $sessionStorage[JOB_CREATE_TEMPLATE_KEY]
                }
                if (JOB_CREATE_FROM_EMAIL_KEY in $sessionStorage) {
                    $scope.item = $sessionStorage[JOB_CREATE_FROM_EMAIL_KEY];
                    $scope.uploadedFiles = $scope.item.files || [];
                    //delete $scope.item.id; // Ensure it's a different ID
                    delete $sessionStorage[JOB_CREATE_FROM_EMAIL_KEY];
                }
                $scope.refreshUpdateTable = true;
            }
        }

        function loadJobFiles(files) {
            $scope.uploadedFilesDone = [];

            for (var i = 0; i < files.length; i++) {
                $scope.uploadedFilesDone.push({'id': files[i].id, 'done': false});
                dataAPIService.getDataApi("/api/", 'files').list({id: files[i].id}, function (response) {
                    $scope.uploadedFiles.push(response);
                });
            }
        }

        function getActiveCostsTotal() {
            var total = 0;

            var active_job_costs = $filter('activeOnly')($scope.item.job_costs);

            for (var i = 0; i < active_job_costs.length; i++) {
                total += parseFloat(active_job_costs[i]['total_price']);
            }

            return total;
        }

        function updateDollarsDifference() {
            $scope.item.dollars_difference = (parseFloat($scope.item.purchase_order_value)
                - parseFloat($scope.item.estimated_cost) - getActiveCostsTotal()).toFixed(2);
        }

        $scope.updateDollarsDifference = updateDollarsDifference;

        function filesEditable() {
            if (roleService.isAccessible($scope.modelName, $scope.route, 'update', 'job_files')) {
                return true;
            }
            return roleService.isAccessible($scope.modelName, $scope.route, 'update', 'job_files_limited');
        }

        $scope.isJobType = function (jobType) {
            if ($scope.jobTypes_by_code && angular.isDefined($scope.jobTypes_by_code[jobType])) {
                return $scope.jobTypes_by_code[jobType].id === $scope.item.job_type;
            } else {
                return false;
            }
        };
        
        // $scope.isDepotType = function (depotType) {
        //     console.log(' isDepotType ');
        //     if ($scope.depotTypes_by_code && angular.isDefined($scope.depotTypes_by_code[depotType])) {
        //         return $scope.depotTypes_by_code[depotType].id === $scope.item.depot_type;
        //     } else {
        //         return false;
        //     }
        // };
        

        $scope.getTotal = function (item) {
            var total = item['quantity'] * parseFloat(item['unit_price']);
            item['total_price'] = total.toFixed(2);
            updateDollarsDifference();
        };

        $scope.compileEmails = function () {
            // compile list of emails
            var emails = [];

            var item = $scope.item;

            if (item.sub_contractor) {
                var subbie = $scope.subcontractors_by_id[item.sub_contractor]
                if (subbie) {
                    emails.push({
                        "name": "Sub Contractor:" + subbie.name,
                        email: subbie.email
                    });
                }
            }

            if (item.supervisor) {
                var superV = $scope.supervisors_by_id[item.supervisor]
                if (superV) {
                    emails.push({"name": "Supervisor:" + superV.name, email: superV.email});
                }
            }
            // if (item.building_inspector_supplier) {
            //     emails.push({"name": "Inspector:" + $scope.supplier_by_id[item.building_inspector_supplier].description, email:$scope.supplier_by_id[item.building_inspector_supplier].email});
            // }
            // if (item.termite_supplier) {
            //     emails.push({"name": "Termite:" + $scope.supplier_by_id[item.termite_supplier].description, email:$scope.supplier_by_id[item.termite_supplier].email});
            // }
            // if (item.rock_supplier) {
            //     emails.push({"name": "Rock:" + $scope.supplier_by_id[item.rock_supplier].description, email:$scope.supplier_by_id[item.rock_supplier].email});
            // }
            // if (item.pod_supplier) {
            //     emails.push({"name": "Pod:" + $scope.supplier_by_id[item.pod_supplier].description, email:$scope.supplier_by_id[item.pod_supplier].email});
            // }
            // if (item.steel_supplier) {
            //     emails.push({"name": "Steel:" + $scope.supplier_by_id[item.steel_supplier].description, email:$scope.supplier_by_id[item.steel_supplier].email});
            // }

            return emails;
        };

        $scope.toggleShowNotes = function () {
            $scope.showNotesStatus = !$scope.showNotesStatus;
        };

        $scope.addNoteCount = function () {
            $scope.pendingNoteCount++;
        };

        $scope.changeSubcontractorRate = function (subcontractor_id) {
            if (subcontractor_id in $scope.subcontractors_by_id && $scope.item.sqm) {
                $scope.item.estimated_cost =
                    ($scope.subcontractors_by_id[subcontractor_id].rate_per_m * $scope.item.sqm).toFixed(2);
            } else {
                $scope.item.estimated_cost = '0.00';
            }
            updateDollarsDifference();
        };

        $scope.changeRockM3 = function (value) {
            if (angular.isDefined(value) && value !== null) {
                $scope.item.rock_m3 = (value * 0.05).toFixed(4);
                $scope.changeSubcontractorRate($scope.item.sub_contractor);
            }
        };

        $scope.stepsConfigENumber = [
            {label:"Dug", field:"dug_date"},
            {label:"Prepared", field:"prepared_date"},
            {label:"Poured", field:"poured_date"}
        ];

        $scope.stepsConfigPaving = [
            {label:"Dug", field:"dug_date"},
            {label:"Prepared", field:"prepared_date"},
            {label:"Poured", field:"poured_date"},
            {label:"Cut", field:"cut_date"},
            {label:"Sealed", field:"sealed_date"}
        ];

        $scope.changeSupervisor = function (value) {

            var superMan = null;
            if (value) {
                superMan = _.find($scope.supervisors, function (instance) {
                    return instance.id === value;
                });
            }

            if (superMan) {
                $scope.item.supervisor_mobile_number = superMan.phone_number;
                $scope.item.supervisor_email = superMan.email;
            } else {
                $scope.item.supervisor_mobile_number = '';
                $scope.item.supervisor_email = '';
            }
        };

        $scope.removeGeneralValidationMessages = function (element) {
            if (angular.isDefined(element)) {
                element.$setValidity('general', true);
            }
        };

        $scope.canShowMap = function () {
            return typeof($scope.item.address)!=="undefined" && typeof($scope.item.suburb)!=="undefined"
        };
        $scope.openMap = function() {
             window.open("https://www.google.com/maps/search/?api=1&query="+ $scope.item.address + " " + $scope.item.suburb);
        };

        $scope.canGenerateInvoice = function() {
            if (!$scope.item.job_costs)
                $scope.item.job_costs = []; // init the array if it's empty

            return _.filter($scope.item.job_costs, {"invoiced": true}).length != $scope.item.job_costs.length; // Look for invoices rows and if they are all invoiced then disable
        };

        $scope.createInvoices = function() {
            dataAPIService.getDataApi("/api/", "job").updateItem($scope.item.id, $scope.item, function (success) {
                dataAPIService.getDataApi("/api/", "create_job_invoice").action({'id': $scope.item.id}, function (response) {
                    alerts.success("Generated Invoice: " + response.xero_code + " In Xero", false);

                    $scope.xero_entities.push (response);

                    $scope.skipConfirm = true; // Skip confirm
                    $state.go($state.current, {}, {reload: true});
                });
            });
        };

        $scope.createPurchaseOrder = function() {
            if (!$scope.item.xero_purchase_order) {
                dataAPIService.getDataApi("/api/", "job").updateItem($scope.item.id, $scope.item, function (success) {
                    dataAPIService.getDataApi("/api/", "create_job_purchase_order").action({'id': $scope.item.id}, function (response) {
                        $scope.item.xero_purchase_order = response;

                        $scope.xero_entities.push (response);

                        alerts.success("Generated Purchase Order: " + response.xero_code + " In Xero", false);

                        $scope.skipConfirm = true; // Skip confirm
                        $state.go($state.current, {}, {reload: true});
                    });
                });
            }
        };

        // Update total Value of Purchase Orders
        $scope.updateTotalValue = function() {
            var value = 0;

            // get last Purchase Order number selected (we need to refresh this if ever an item is added or removed)
            angular.forEach($scope.item.job_costs, function (cost) {
                if (cost.purchase_order_number) {
                    $scope.lastPurchaseOrderNumber = cost.purchase_order_number;
                }
            });

            _.sumBy($scope.item.purchase_orders, function (po) {
                if (_.isFinite(parseFloat(po.value))) {
                    value = value + parseFloat(po.value);
                }
            });

            $scope.item.purchase_order_value = value.toFixed(2);
            updateDollarsDifference();
        };

        $scope.onPurchaseOrderNumberChanged = function (item) {
            if (angular.isDefined(item.purchase_order_number)) {
                $scope.lastPurchaseOrderNumber = item.purchase_order_number;
            }
        };

        $scope.costItemChanged = function (row, selectedItem) {
            if (!row.invoiced) {
                row.unit_price = selectedItem.SalesDetails.UnitPrice;
                $scope.getTotal(row);

                row.details = selectedItem.Description;
            }
        };

        $scope.selectClient = function (clientID) {
            if (clientID && clientID in $scope.clients_by_id) {
                if ($scope.clients_by_id[clientID].suppliers.length) {
                    $scope.filteredSubcontractors = $scope.clients_by_id[clientID].suppliers;

                    if ($scope.item.sub_contractor) {
                        var found = _.find($scope.clients_by_id[clientID].suppliers, {id: $scope.item.sub_contractor});

                        if (!found && $scope.item.sub_contractor in $scope.subcontractors_by_id) {
                            $scope.filteredSubcontractors.push($scope.subcontractors_by_id[$scope.item.sub_contractor]);
                        }
                    }

                } else {
                    $scope.filteredSubcontractors = [];
                }

                if ($scope.filteredSubcontractors.length === 1) {
                    $scope.item.sub_contractor = $scope.filteredSubcontractors[0].id;
                }

                if (!$scope.item.purchase_orders) {
                    $scope.item.purchase_orders = [];// init Array
                }

                // we need to check if user has permission in adding PO's first
                if (roleService.isAccessible($scope.modelName, $scope.route, 'update', 'purchase_orders')) {
                    while ($scope.item.purchase_orders.length < $scope.clients_by_id[clientID].number_of_purchase_orders) {
                        $scope.item.purchase_orders.push({});
                    }
                }
            } else {
                $scope.filteredSubcontractors = [];
            }
            $scope.showAllSubcontractors = $scope.filteredSubcontractors.length === 0;
        };

        $scope.createEnumber = function () {
            var newJob = {};

            // Copy the fields listed below into the New job.
            _.each(['client', 'job_number', 'sub_contractor', 'supervisor',
                'comments', 'address', 'job_type', 'suburb', 'sqm', 'description', 'files', 'depot_type'], function (key) {
                newJob[key] = $scope.item[key];
            });


            newJob.part_a_date = null;
            newJob.date_received = new Date();

            var jobTypeForENumber = _.find($scope.jobTypes, {'code':'enumber'});
            if (jobTypeForENumber)
                newJob.job_type = jobTypeForENumber.id;

            $sessionStorage[JOB_CREATE_TEMPLATE_KEY] = newJob;

            $state.go("job.create");
        };

        // When the PO Numbers changes update the summary for searching
        $scope.updatePoNumbers = function () {
            var all_poNumbers = _.map($scope.item.purchase_orders, function (po) {
                return po.number;
            });

            $scope.item.purchase_order_number = _.join(all_poNumbers, ", ").trim()
        };

        $scope.validateItem = function (item) {
            $scope.updatePoNumbers();
            // convert end date to datetime format
            if (item.active_end_date) {
                item.active_end_date = moment(item.active_end_date).format('YYYY-MM-DD HH:mm:ss');
            }
            return true;
        };

        $scope.fields_list = [];

        $scope.viewOnly = function (item) {
            $scope.fields_list.push (item);
            $scope.fields_list = _.sortBy(_.uniq($scope.fields_list));

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

        $scope.viewable = function (item) {
            $scope.fields_list.push (item);
            $scope.fields_list = _.sortBy(_.uniq($scope.fields_list));

            return roleService.isAccessible('job', $scope.route, 'view', item);
        };

        $scope.waitLoadAllApi = $interval(function() {
            if (models.length > 0 && formStateService.isLoaded(models)) {
                formStateService.setFormState({loading: false});
                $scope.filesEditable = filesEditable();
                if (user.role.can_see_plans_before_accept || $scope.filesEditable || user.role.employee) {
                    $scope.item.isActive = true;
                } else {
                    // we need to check if this is a task related to the user and if task is accepted first
                    $scope.item.isActive = (tasksByJob[$scope.item.id]) ? tasksByJob[$scope.item.id].accepted_date !== null : false;
                }
                $state.params.skip = true;
                $scope.selectClient($scope.item.client);
                // below will update estimated cost
                //$scope.changeSubcontractorRate($scope.item.sub_contractor);
                if ($state.params.id) {
                    $scope.updateTotalValue();
                }
                $interval.cancel($scope.waitLoadAllApi);
            }
        }, SETTINGS.interval);

        $scope.showOnError = function (form, field) {
            var formField = form[field];

            if (formField) {
                return (formField.$invalid && formField.$touched) ||
                    (form.$submitted && $scope.item._errors && $scope.item._errors[field]);
            }
            return false;
        };

        var updateRoleInformation = function () {
            $scope.isAdmin = roleService.userHasThisRole('administrator');
            $scope.isClientView = roleService.userHasThisRole('supervisor') ||  roleService.userHasThisRole('client_manager');

            if ($scope.isAdmin) {
                // set this off so Admins can send email
                $scope.limitUser = null;
            }

            if (roleService.getRole("employee")) {
                $scope.limitUser = null; // Can send email (confusing name)
            }

            if (roleService.getRole("supervisor")) {
                $scope.supervisor_id = roleService.getRole("supervisor_id");
            }
            if (roleService.getRole("subcontractor")) {
                $scope.subbie_id = roleService.getRole("subbie_id");

            }
            loadItem(); // Load item now we know WHO it is
        };

        roleService.subscribeAccessUpdate($scope, updateRoleInformation);
    }
})();
