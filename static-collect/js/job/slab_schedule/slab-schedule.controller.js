/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

/***
 * Job Slab Schedule Controller
 */
(function () {
    'use strict';

    angular
        .module('app.job')
        .controller('JobSlabScheduleController', ['$filter', '$interval', '$state', '$scope', 'authService',
            'dataCacheService', 'dataAPIService', 'formStateService', 'roleService', 'SweetAlert', 'stateStorage',
            'widgetService', 'SETTINGS', 'DEFAULT_SLAB_SCHEDULE_OPTIONS', '$uibModal', '$document',
            function ($filter, $interval, $state, $scope, authService, dataCacheService,
                                       dataAPIService, formStateService, roleService, SweetAlert, stateStorage,
                                       widgetService, SETTINGS, DEFAULT_SLAB_SCHEDULE_OPTIONS, $uibModal, $document) {

            var models = []; // Used to check for loading - TODO:remove this

            $scope.listOptions = {
                emptyWantedDateFilter: $state.params.emptyWantedDateFilter === 'true'
            };
            $scope.listOptions.wantedDateFilter = $scope.listOptions.emptyWantedDateFilter ? null : $state.params.wantedDateFilter || new Date();

            $scope.dateHeaders = [];
            function organizeDateBoxes() {
                var daysOfWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
                var i = 0, days = 0;

                while (i < 18) {
                    var date = new Date(widgetService.normalizedDate($scope.listOptions.wantedDateFilter));
                    var addDate = new Date(date.setDate(date.getDate() + days));
                    var actualDate = addDate.getDate();
                    var dayOfWeek = addDate.getDay();

                    if (dayOfWeek !== 0) {
                        var month = date.getMonth() + 1;

                        $scope.dateHeaders.push({
                            index: i,
                            date_scheduled: widgetService.normalizedDate(addDate),
                            dayOfWeek: daysOfWeek[dayOfWeek],
                            dayOfWeekAbbr: daysOfWeek[dayOfWeek].substring(0, 3).toUpperCase(),
                            date: actualDate.toString().padStart(2, "0"),
                            month: month.toString().padStart(2, "0")
                        });
                        i++;
                    }
                    days++;
                }
            }
            organizeDateBoxes();


            $scope.allJobs = [];
            $scope.all_task_type = {};
            $scope.currentSelectedBox = null; // The Current Task Box that has been Clicked.
            $scope.clipboardBox = null; // The Box in the Clipboard
            $scope.currentClientJob = null; // The "Job" Selected in the Client Table selected
            $scope.selectedTaskType = null; // Current "default" Task.

            $scope.subbieSlots = {}; // Data for Task table at top
            $scope.customerTable = []; // Customer Table at the bottom

            // Load Lookups etc..
            function loadLookUps() {
                var baseFilter = {
                    filter: 'active'
                };


                function getTaskTypeData(data, params) {
                    var result = dataAPIService.applyFilters(data, params);
                    $scope.all_task_type = _.keyBy(result, 'id');
                    return result;
                }

                var loadTables = [
                    {
                        name: 'subbie',
                        params: {
                            filter: [
                                'active'
                            ]
                        },
                        callback: dataAPIService.applyFilters,
                        scope: 'subcontractors'
                    },
                    {
                        name: 'code_task_type',
                        params: baseFilter,
                        callback: getTaskTypeData,
                        scope: 'task_types'
                    },
                    {
                        name: 'client',
                        params: baseFilter,
                        callback: dataAPIService.applyFilters,
                        scope: 'clients'
                    }
                ];
                models = _.map(loadTables, 'name');
                models.push('job', 'tasks');
                dataCacheService.processLoadTables(loadTables, $scope, 'query');
            }

            loadLookUps();

            function loadList() {
                var startDateBase = new Date($scope.listOptions.wantedDateFilter);
                // set back fourteen days
                var startDate = moment(startDateBase.setDate(startDateBase.getDate() - 14)).format("YYYY-MM-DD");
                var endDateBase = new Date($scope.dateHeaders[$scope.dateHeaders.length - 1].date_scheduled);
                // forward 7 days
                var endDate = moment(endDateBase.setDate(endDateBase.getDate() + 7)).format("YYYY-MM-DD");

                var tasksOptions = angular.copy($scope.listOptions);

                //tasksOptions.filter = "active"; // Just get active
                tasksOptions.filter = "active"; // Just get active
                tasksOptions.limit= 10000; // try and get them all

                // Just tasks in the Date Range.
                tasksOptions.query = {"logic":"and", "criteria":[
                        {"operation":"between","name":"date_scheduled","params":[startDate, endDate]},
                        {"operation":"is_null", "name":"job__date_cancelled"}
                    ]};

                dataAPIService.getDataApi("/api/", "tasks").list(tasksOptions, function (data) {
                    $scope.jobTasks = data.results;
                    $scope.listOptions.total = data.count;
                    $scope.listOptions.currentPage = Math.ceil($scope.listOptions.offset / $scope.listOptions.limit) + 1;

                    buildSupplierLines(); // recalc this!
                    // TODO Load if there is more..
                });


                $scope.jobs = [];

                var jobOptions = angular.copy($scope.listOptions);
                jobOptions.filter = "slab_schedule";
                jobOptions.limit= 10000; // try and get them all
                jobOptions.slab_date_start = startDate;
                jobOptions.slab_date_end = endDate;

                dataAPIService.getDataApi("/api/", "job").list(jobOptions,  function (data) {
                    $scope.jobs = data.results;

                    $scope.allJobs = _.keyBy($scope.jobs, 'id');
                }, function (err) {
                    err = _.cloneDeep(err);
                    err.config.headers['Authorization'] = null;

                    alert ("Cannot Get Pour Jobs - Please refresh:" + JSON.stringify(err));
                });


            }
            loadList();

            /* Look up in subbieSlots and update data */
            function setSubbieSlotsProperty(index, channel, sked, property, value) {
                $scope.subbieSlots[index].channels[channel].dateBox[sked][property] = value;
            }

            /* Look up in subbieSlots and update data */
            function setSubbieSlotsSubProperty(index, channel, sked, property, sub, value) {
                $scope.subbieSlots[index].channels[channel].dateBox[sked][property][sub] = value;
            }

            /* Build data for Contractors table at the top*/
            function buildSupplierLines() {
                var boxId = 1;
                var jobTasks = angular.copy($scope.jobTasks);

                $scope.currentSelectedBox = null;

                // Sort by display_order..
                $scope.subcontractors = _.sortBy($scope.subcontractors, [function(o) {
                    return o.display_order;
                }]);

                // noinspection JSUnresolvedVariable
                angular.forEach($scope.subcontractors, function (subbie) {
                    $scope.subbieSlots[subbie.id] = {
                        name: subbie.name,
                        display_order: subbie.display_order,
                        capacity: subbie.jobs_per_day,
                        channels: []
                    };
                    for (var slot_order = 0; slot_order < subbie.jobs_per_day; slot_order++) {
                        $scope.subbieSlots[subbie.id].channels[slot_order] = {
                            dateBox: [],
                            index: slot_order
                        };
                        angular.forEach($scope.dateHeaders, function (sked) {
                            $scope.subbieSlots[subbie.id].channels[slot_order].dateBox[sked.index] = {
                                skedIndex: sked.index,
                                date_scheduled: sked.date_scheduled,
                                slot_order: slot_order,
                                boxId: boxId,
                                supplier: subbie.id,
                                empty: true,
                                moving: false,
                                job: null,
                                task: null
                            };
                            if (jobTasks) {
                                _.each (jobTasks, function (theJobTask, taskIndex) {
                                    var job = $scope.allJobs[theJobTask.job];

                                    // noinspection JSUnresolvedVariable
                                    if (theJobTask.supplier === subbie.id
                                        && theJobTask.date_scheduled === sked.date_scheduled
                                        && slot_order === theJobTask.slot_order) {

                                        // create a monitoring array of task types used in an assigned job task

                                        if ($scope.allJobs[theJobTask.job]) {
                                            if (!angular.isDefined($scope.allJobs[theJobTask.job].filledTypes)) {
                                                $scope.allJobs[theJobTask.job].filledTypes = [];
                                            }
                                            $scope.allJobs[theJobTask.job].filledTypes.push(theJobTask.task_type);
                                        }
                                        setSubbieSlotsProperty(subbie.id, slot_order, sked.index, 'job', angular.copy(job));
                                        setSubbieSlotsProperty(subbie.id, slot_order, sked.index, 'task',
                                            angular.copy(theJobTask));
                                        setSubbieSlotsSubProperty(subbie.id, slot_order, sked.index, 'task', 'task_type',
                                            theJobTask.task_type);
                                        setSubbieSlotsSubProperty(subbie.id, slot_order, sked.index, 'task', 'task_type',
                                            theJobTask.task_type);
                                        setSubbieSlotsProperty(subbie.id, slot_order, sked.index, 'empty', false);
                                        // jobTasks.splice(taskIndex, 1); // SW: Not sure why you would do this??
                                        return;
                                    }
                                });
                            }
                            boxId++;
                        });
                    }
                });
                // doing this below will invalidate supplier id as an index to access the subbie slot so we
                // use toArray | orderBy:'name' in the template instead
                //$scope.subbieSlots = _.sortBy($scope.subbieSlots, ['name']); // Sort by Contractor Name
            }

            /* Build data for Clients table at the Bottom*/
            // noinspection JSUnresolvedVariable
            function buildClientLines() {
                var lastIndex = $scope.dateHeaders.length - 1;

                var jobsByClient = _.groupBy($scope.jobs, 'client');
                var background = '#fff';
                var foreground = '#000';

                // get pour date background and foreground colour
                var pour_taskType = _.find ($scope.task_types, {'code':"POUR"});
                if (!pour_taskType) { // Default JUST in case..
                    pour_taskType = {
                        'background_colour':'white',
                        'foreground_colour':'black'
                    }
                }

                var pier_taskType = _.find ($scope.task_types, {'code':"PIERS"});
                if (!pour_taskType) { // Default JUST in case..
                    pour_taskType = {
                        'background_colour':'white',
                        'foreground_colour':'black'
                    }
                }

                var task_types = [{"code":"pour_date", "task_type":pour_taskType}, {"code":"piers_date", "task_type":pier_taskType}];

                var clientJobs = {}; // Dict index by Date+Client.id. has Array. Array Index = 0 is
                var clientCount = {}; // Dict of Key=Client.id. Value is Max rows for this client in ONE day

                var start_date = moment($scope.dateHeaders[0].date_scheduled);
                var end_date =   moment($scope.dateHeaders[lastIndex].date_scheduled);

                function includeJob (theDate, startDate, endDate) {
                    if (!theDate.isValid())
                        return false;// Invalid date. forget it.

                    return theDate.isBetween(startDate, endDate, null, "[]");
                }
                _.each ($scope.jobs, function (job) {
                    _.each (task_types, function (taskType) {
                        var theDate = moment(job[taskType.code]);
                        if (includeJob(theDate, start_date, end_date)) {
                            var key = theDate.format("YYYY-MM-DD") + ":" + job.client;

                            var maxRows = 0;

                            var clientJobsEntry = {"job": job, "task_type": taskType.task_type};

                            if (key in clientJobs) {
                                clientJobs[key].push(clientJobsEntry);

                                maxRows = clientJobs[key].length;
                            }
                            else {
                                clientJobs[key] = [clientJobsEntry]; // Create New Array entry for Date + Client.
                                maxRows = 1;
                            }

                            if (clientCount[job.client]) {
                                if (maxRows > clientCount[job.client]) {
                                    clientCount[job.client] = maxRows;
                                }
                            }
                            else {
                                clientCount[job.client] = maxRows; // init to max So far
                            }
                        }
                    });

                });

                var rows = [];
                _.each (_.sortBy($scope.clients, "name"), function (client) {
                    var rowsForClient = clientCount[client.id];

                    // SW: Uncomment to Show ALL Customers if required
                    // if (!rowsForClient)
                    //     rowsForClient = 1; // Always do a Row Per Client even an empty one

                    for (var client_row = 0; client_row < rowsForClient; client_row++) {
                        var row = [];

                        // Header Cell
                        row[0] = {
                            "key": null,
                            "text": client.name,
                            "id": client.id,
                            "row_span": clientCount[client.id],
                            "client_row": client_row, // NOTE if > 0 don't show
                            "empty":true
                        };

                        _.each($scope.dateHeaders, function (dateHeader) {
                            var key = moment(dateHeader.date_scheduled).format("YYYY-MM-DD") + ":" + client.id;

                            var entry = clientJobs[key];
                            var box = {
                                "key": key,
                                "row_span":1,
                                "client_row": client_row,
                                "task_type": null,
                                "job": null,
                                "empty":true
                            };

                            if (entry && entry[client_row] && entry[client_row].job) {
                                if (client_row < entry.length) {
                                    box.task_type = entry[client_row].task_type; // for Colors
                                    box.job = entry[client_row].job;
                                }
                            }

                            row.push(box)
                        });

                        rows.push(row);
                    }

                });
                $scope.customerTable = rows;
            }

            // When the user clicks a Task Type
            $scope.selectTaskType = function (tasktype) {
                $scope.selectedTaskType = tasktype;
            };

            /* Clicks on the Tables */
            // When User clicks a Client Box on Bottom
            $scope.clickAtClientBox = function (box) {
                if (box.job) {
                    $scope.currentClientJob = box.job;
                    $scope.currentSelectedBox = null;// Unselect
                }
            };

            // When User Clicks a Task Box on Top
            $scope.clickAtTaskBox = function (box) {
                $scope.currentSelectedBox = box;
                if (box.job) { // If this box has a job use it
                    $scope.currentClientJob = box.job; // Make the same job
                }
            };

            $scope.isClickedAt = function (box, action) {
                var clicked = $scope.currentSelectedBox === box;

                if (angular.isUndefined(action)) {
                    return clicked;
                }

                switch (action) {
                    case 'add':
                        return clicked && box.empty && $scope.clipboardBox === null;
                    case 'edit':
                        return clicked && !box.empty && $scope.clipboardBox === null;
                    case 'remove':
                        return clicked && !box.empty && $scope.clipboardBox === null;
                    case 'cut':
                        return clicked && !box.empty;
                    case 'cancel':
                        return clicked && $scope.clipboardBox !== null;
                    case 'paste':
                        return clicked && $scope.clipboardBox !== null && $scope.clipboardBox !== box && (box.job == null);
                    default:
                        return clicked;
                }
            };


            /*
             * Actions on the Tasks
             */

            var dateTimeFields = {'pour_date':true, 'base_inspection_date':true,
                'steel_inspection_date':true, 'rock_booked_date':true, 'part_a_date':true,
                'waste_date':true, 'piers_date':true, 'piers_inspection_date':true, 'piers_concrete_date':true}

             // Update the Date fields ie pourDate of the Job
            function updateJobDateField(box, successCallback) {
                var job = box.job;
                var task_type= box.task.task_type;
                var date_scheduled = box.date_scheduled;
                var subbie = box.task.supplier;

                // noinspection JSUnresolvedVariable
                var jobDateField = $scope.all_task_type[task_type].job_date_field;
                var subbieField = $scope.all_task_type[task_type].subbie_field;

                if ((jobDateField  && job.hasOwnProperty(jobDateField)) || (subbieField && job.hasOwnProperty(subbieField))) {
                    var api = dataAPIService.getDataApi("/api/", "job");

                    // TODO "PATCH" the Job
                    api.getItem(job.id, function (jobData) { // Load Fresh job so no data is lost.

                        // Update Date field
                        if (jobDateField && job.hasOwnProperty(jobDateField)) {

                            // we re-cast as a JS Date object as field can be of type datetime
                            if (dateTimeFields[jobDateField]) {// only dateTime for Pour not others..
                                jobData[jobDateField] = new Date(date_scheduled);// Date and Time
                            }
                            else {
                                jobData[jobDateField] = moment(new Date(date_scheduled)).format("YYYY-MM-DD");
                            }
                        }

                        // Update Subbie Field
                        if (subbieField  && job.hasOwnProperty(subbieField)) {
                            jobData[subbieField] = subbie;
                        }

                        api.updateItem(jobData.id, jobData, function (response) {
                            $scope.allJobs[jobData.id] = angular.copy(response);

                            successCallback();
                        }, apiError);
                    }, apiError);
                }
                else {
                    successCallback();
                }
            }

            $scope.undoOperationHandler = null; // A function to run when the operation is to be Undone because of an error
            function undoOperation () {
                if ($scope.undoOperationHandler) {

                    $scope.undoOperationHandler();
                }
            }

            function apiError(error) {
                var message;

                if (angular.isDefined(error.data) && angular.isDefined(error.data.non_field_errors)) {
                    message = error.data.non_field_errors[0];
                } else {
                    message = "An error occurred while updating the Item. Try again later.";
                }

                undoOperation();

                SweetAlert.swal({
                        title: "Error",
                        text: message,
                        type: "error",
                        showCancelButton: false,
                        confirmButtonColor: "#DD6B55",
                        confirmButtonText: "Ok",
                        closeOnConfirm: true
                    },
                    function (isConfirm) {

                    });
            }

            // Call API to Save the Task
            function apiSaveTask(task, successCallBack) {
                var taskForApi = {
                    description: task.description,
                    task_type: task.task_type,
                    supplier: task.supplier,
                    date_scheduled: task.date_scheduled,
                    slot_order: task.slot_order,
                    job: task.job
                };


                if (task.id) {
                    taskForApi.id = task.id;
                    dataAPIService.getDataApi("/api/", "tasks").updateItem(task.id, taskForApi, function(savedTask) {
                        task.id = savedTask.id;

                        successCallBack(savedTask);
                    }, apiError);
                }
                else {
                    dataAPIService.getDataApi("/api/", "tasks").createItem(taskForApi, function (savedTask) {
                        task.id = savedTask.id;

                        successCallBack(savedTask);
                    }, apiError);
                }
            }
            // Set a BOX to Empty/Cleared
            function resetBox(box) {
                if ($scope.clipboardBox == box) {
                    $scope.clipboardBox = null; // Remove from Clipboard if this was the Clipboard
                }

                box.job = null;
                box.task = null;
                box.empty = true;
            }

            // Make sure value in Task as the same as the box. - Might be New or Moved.
            function alignBoxTask (box) {
                box.task.date_scheduled = box.date_scheduled;
                box.task.supplier = box.supplier;
                box.task.slot_order = box.slot_order;

                if (box.task.job) {
                    box.job = $scope.allJobs[box.task.job];
                }
            }

            // Move "Paste" an item
            function moveBoxItem(box) {
                box.job = $scope.clipboardBox.job;
                box.task = $scope.clipboardBox.task;
                box.empty = false;

                alignBoxTask(box);

                $scope.undoOperationHandler = function () {
                    box.job = null;
                    box.task = null;
                    box.empty = true;

                    $scope.undoOperationHandler  = null;
                };

                apiSaveTask(box.task, function () {
                    updateJobDateField(box, function (){
                        $scope.undoOperationHandler = null;

                        resetBox($scope.clipboardBox); // reset the clipboard box to empty.
                    });
                });
            }

            function removeBoxItem(box, tellAPItoDelete) {
                if (tellAPItoDelete) { // Actually let API Know. Not sure why we would not...
                    if (box.task.id) {
                        dataAPIService.getDataApi("/api/", "tasks").delete(box.task, function (task) {
                            resetBox(box);
                        });
                    }
                }
                else { // was from moveBoxItem
                    resetBox(box);
                }
            }

            // When Add Button Clicked
            $scope.btnAddTaskBoxItem = function (box) {
                if ($scope.currentClientJob) {
                    box.job = $scope.currentClientJob;
                }
                box.task = {};

                if ($scope.selectedTaskType) { // set to the selected Type..
                    box.task.task_type = $scope.selectedTaskType.id;
                }

                alignBoxTask(box);

                $scope.editTaskBoxItem(box, true);
            };

            // When Edit Button Clicked
            $scope.editTaskBoxItem = function (box, add) {
                var dialogData = {}; // New Object
                dialogData.task_type = box.task.task_type;
                dialogData.description = box.task.description;

                if (add) {
                    $scope.undoOperationHandler = function () {
                        box.job = null;
                        box.task = null;
                        box.empty = true;
                    };
                }
                else {
                    var original_Task = angular.copy(box.task);

                    $scope.undoOperationHandler = function () {
                        _.each (original_Task, function (val, key) {
                            box.task[key] = val; // restore value;
                        });

                        $scope.editTaskBoxItem(box, add);
                    };
                }

                if (box.job && box.job.id)
                    dialogData.job_id = box.job.id;

                var modalInstance = $uibModal.open({
                    animation: true,
                    ariaLabelledBy: 'modal-title',
                    ariaDescribedBy: 'modal-body',
                    templateUrl: 'EditTaskModalContent.html',
                    controller: 'ModalTaskInstanceCtrl',
                    controllerAs: '$ctrl',
                    size: "md",
                    appendTo: angular.element($document[0].querySelector("#modal-location")),
                    resolve: {
                        dialogData: function () {
                            return dialogData;
                        },
                        task_types: function() {
                            return $scope.task_types;
                        },
                        jobsList : function () {
                            return $scope.jobs;
                        }
                    }
                });

                modalInstance.result.then(function (dialogData) {
                    box.task.task_type = dialogData.task_type;
                    box.task.description  = dialogData.description;
                    box.task.job = dialogData.job_id;

                    alignBoxTask(box);

                    apiSaveTask(box.task, function (newTask) {
                        box.task = newTask; // Update Task

                        //SW: NOT SURE WE NEED THIS: setSubbieSlotsProperty(box.supplier, box.slot_order, box.skedIndex, 'job', dialogData.job);

                        updateJobDateField(box, function () {
                            $scope.undoOperationHandler = null;

                            box.empty = false;
                        });
                    });
                }, function () {
                    if (add) {
                        undoOperation();
                    }
                    else {
                        $scope.undoOperationHandler = null;
                    }
                });
            };


            $scope.btnEditTaskBoxItem = function (box) {
                $scope.editTaskBoxItem(box, false);
            }

            // When Remove Button Clicked
            $scope.btnRemoveBoxItem = function (box) {
                SweetAlert.swal({
                        title: "Are you sure?",
                        text: "Are you sure you want to remove this task?",
                        type: "warning",
                        showCancelButton: true,
                        confirmButtonColor: "#DD6B55",
                        confirmButtonText: "Yes, delete it!",
                        closeOnConfirm: true
                    },
                    function (isConfirm) {
                        if (isConfirm) {
                            removeBoxItem(box, true);
                        }
                    });
            };

            // When Cut Button Clicked
            $scope.btnCutTaskBoxItem = function (box) {
                $scope.clipboardBox = box;

                box.moving = true;
            };

            // When Paste button Clicked
            $scope.btnPasteTaskBoxItem = function (box) {
                if (angular.isDefined($scope.clipboardBox)) {
                    if (!box.task) {
                        moveBoxItem(box);
                    } else {
                        SweetAlert.swal({
                                title: "Are you sure?",
                                text: "Are you sure you want to move the paste the task here and replace this one?",
                                type: "warning",
                                showCancelButton: true,
                                confirmButtonColor: "#DD6B55",
                                confirmButtonText: "Yes, move it!",
                                closeOnConfirm: true
                            },
                            function (isConfirm) {
                                if (isConfirm) {
                                    // TODO DELETE the Current Task Then
                                    moveBoxItem(box);
                                }
                            });
                    }
                }
            };
            // When Cancel Button Clicked
            $scope.btnCancelCutTaskBoxItem = function (box) {
                box.moving = true;
                $scope.clipboardBox = null;
            };

            /*
             * For The Filter Box at the Top.
             */
            // Set Filter Date to Today
            $scope.setToday = function () {
                $scope.listOptions.emptyWantedDateFilter = false;
                $scope.listOptions.wantedDateFilter = new Date();
                $scope.refreshList();
            };

            // Adjust Filter Date by 'days' Days
            $scope.setFromLastDate = function (days, strict) {
                var date;

                $scope.listOptions.emptyWantedDateFilter = false;
                //clearSearchControls();
                if (angular.isDefined($scope.listOptions.wantedDateFilter) &&
                    $scope.listOptions.wantedDateFilter !== null) {

                    date = new Date(widgetService.normalizedDate($scope.listOptions.wantedDateFilter));
                } else {
                    if (strict) {
                        return;
                    }
                    date = new Date();
                }
                if (days !== 0) {
                    $scope.listOptions.wantedDateFilter = new Date(date.setDate(date.getDate() + days));
                    $scope.refreshList();
                }
            };

            // Clear the Filter Date
            $scope.clearDate = function () {
                $scope.listOptions.emptyWantedDateFilter = true;
                $scope.refreshList();
            };


            // Works out the Colors for a Box/Cell based on the Type
            $scope.cellCSS = function (type) {
                if (type) {
                    return {
                        "background": "linear-gradient(" + type.background_colour + ", white)",
                        "color": type.foreground_colour,
                        "cursor": "pointer",
                    }
                }
                else
                    return {"background":"white", "color":"black"};
            };

            // Work out Class naames for Task Box
            $scope.taskBoxClasses = function(box) {
                var result = [];

                if ($scope.currentSelectedBox === box) {
                    result.push ("stateActive");

                    if (box.job && box.job.id) {
                        result.push ("stateActiveJob"); // Has a Job
                    }
                    else {
                        result.push ("stateActiveEmpty"); // Is Empty
                    }
                }

                if (box == $scope.clipboardBox) { // Was box.boxId === clipboardBox.boxId
                    result.push("stateCut");
                }

                if (box.job && box.job.id) {
                    var selected = false;

                    if ($scope.currentSelectedBox && $scope.currentSelectedBox.job ) {
                        if($scope.currentSelectedBox === box) {
                            selected = true;
                            result.push("stateSelectedBox");
                        }
                    }

                    if ($scope.currentClientJob && $scope.currentClientJob.id) {
                        if (box.job.id === $scope.currentClientJob.id) {
                            result.push("stateMatchingBox");

                            selected = true;
                        }
                    }

                    if (!selected) {
                        result.push("stateUnSelectedBox");
                    }
                }
                return result;
            };

            // Work out Class Names for Client Job Box
            $scope.clientBoxClasses = function(box) {
                var result = [];

                if (box.job && $scope.currentClientJob) {
                    if (box.job.id == $scope.currentClientJob.id) {
                        result.push("stateCurrentJob");
                    }
                }

                return result;
            };

            // Reload the list
            $scope.refreshList = function (except) {
                var options = angular.copy($scope.listOptions);
                var destination = "job.slab-schedule";
                // noinspection JSUnresolvedVariable
                var finalExcept = angular.isDefined(except) ?
                    angular.copy(except) : (angular.isDefined($scope.exceptSearch) ? $scope.exceptSearch : []);

                finalExcept = _.union(finalExcept, ['total', 'currentPage']);
                for (var i = 0; i < finalExcept.length; i++) {
                    delete options[finalExcept[i]];
                }
                stateStorage.storeStateThenGo(destination, options, true);
            };

            $scope.waitLoadAllApi = $interval(function () {
                // noinspection JSUnresolvedVariable
                if (models.length > 0 && formStateService.isLoaded(models) && angular.isDefined($scope.subcontractors)) {
                    formStateService.setFormState({loading: false});
                    buildSupplierLines();
                    buildClientLines();
                    console.log("All Job modules loaded.", models, $scope.subbieSlots, $scope.customerTable);
                    $interval.cancel($scope.waitLoadAllApi);
                }
            }, SETTINGS.interval);

            roleService.triggerPageLoaded($scope);

    }])

    /* Controller for the Dialog */
    .controller('ModalTaskInstanceCtrl', function ($uibModalInstance, dialogData, task_types, dataAPIService, $interval, SETTINGS, jobsList) {
        var $ctrl = this;
        $ctrl.dialogData = dialogData;
        $ctrl.task_types = task_types;
        $ctrl.jobsList = jobsList;

        $ctrl.currentOffset = 0;
        $ctrl.limit = 30;

        $ctrl.validateJob = function (form) {
            var result = $ctrl.dialogData.job !== null;

            form.job.$setValidity('required', result);

            return result;
        };

        $ctrl.ok = function (form) {
            if ($ctrl.validateJob(form)) {
                $uibModalInstance.close($ctrl.dialogData);
            }
        };

        $ctrl.cancel = function () {
            $uibModalInstance.dismiss('cancel');
        };
    });

})();
