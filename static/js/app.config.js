/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

var NAV_MENU = {
    'job': [
        {'link': 'job.list', 'name': 'Job List', 'stateName': 'job.list'},
        {'link': 'job.pour-schedule', 'name': 'Slab Schedule', 'stateName': 'job.pour-schedule'},
        {'link': 'job.paving_list', 'name': 'Paving Schedule', 'stateName': 'job.paving_list'},
        {'link': 'job.enumber_list', 'name': 'ENumber Schedule', 'stateName': 'job.enumber_list'},
        {'link': 'job.create', 'name': 'New Job', 'stateName': 'job.create'}
    ],
    'repair': [
        {'link': 'repair.list', 'name': 'Repair List', 'stateName': 'repair.list'},
        {'link': 'repair.create', 'name': 'New Repair', 'stateName': 'repair.create'}
    ],
    'email': [
        {'link': 'email.list', 'name': 'Email List', 'stateName': 'email.list'}
    ]
};

var DEFAULT_LIST_OPTIONS = {
    'total': 0,
    'currentPage': 1,
    'filter': "active",
    'order': "asc",
    'q': "",
    'searchField': "",
    'ordering': "",
    'limit': 20,
    'offset': 0
};

var DEFAULT_JOB_LIST_OPTIONS = angular.extend({}, DEFAULT_LIST_OPTIONS, {
    'sort': "date_received",
    'when': null,
    "job_type": null
});

var DEFAULT_POUR_JOB_LIST_OPTIONS = angular.extend({}, DEFAULT_LIST_OPTIONS, {
    'sort': "date_received",
    'when': null,
    "job_type": null,
    'limit': 20,
    'offset': 0
});

var DEFAULT_POUR_SCHEDULE_OPTIONS = angular.extend({}, DEFAULT_LIST_OPTIONS, {
    'sort': "pour_date",
    'when': null,
    "job_type": null,
    'limit': 20,
    'filter': "all",
});

var DEFAULT_REPAIR_LIST_OPTIONS = angular.extend({}, DEFAULT_LIST_OPTIONS, {
    'sort': "date_received"
});

var DEFAULT_SLAB_SCHEDULE_OPTIONS = angular.extend({}, DEFAULT_LIST_OPTIONS, {
    'limit': 50
});

var DEFAULT_PAVING_SCHEDULE_OPTIONS = {
    'limit': 50,
    'currentPage': 1,
    'filter': "called_up",
    'q': "",
    'searchField': "",
    'ordering': "call_up_date",
    "sort":"call_up_date",
    "order":"desc",
    'offset': 0
};

var DEFAULT_ENUMBER_SCHEDULE_OPTIONS = DEFAULT_PAVING_SCHEDULE_OPTIONS; //same same!

angular
    .module('cormack')
    .value('NAV_MENU', NAV_MENU)
    .value('DEFAULT_JOB_LIST_OPTIONS', DEFAULT_JOB_LIST_OPTIONS)
    .value('DEFAULT_POUR_JOB_LIST_OPTIONS', DEFAULT_POUR_JOB_LIST_OPTIONS)
    .value('DEFAULT_REPAIR_LIST_OPTIONS', DEFAULT_REPAIR_LIST_OPTIONS)
    .value('DEFAULT_SLAB_SCHEDULE_OPTIONS', DEFAULT_SLAB_SCHEDULE_OPTIONS)
    .value('DEFAULT_POUR_SCHEDULE_OPTIONS', DEFAULT_POUR_SCHEDULE_OPTIONS)
    .value('DEFAULT_PAVING_SCHEDULE_OPTIONS', DEFAULT_PAVING_SCHEDULE_OPTIONS)
    .value('DEFAULT_ENUMBER_SCHEDULE_OPTIONS', DEFAULT_ENUMBER_SCHEDULE_OPTIONS)
    .constant('APP_NAME', '<span style="color:#00a2d9;">Cormack</span> <span style="color:#545861;">JMS</span>')
    .config(jwtConfig)
    .run(run);


function jwtConfig ($httpProvider, $localStorageProvider, jwtOptionsProvider) {

    jwtOptionsProvider.config({
        tokenGetter: function () {
            return $localStorageProvider.get('token');
        },
        loginPath: '/login',
        unauthenticatedRedirectPath: '/login',
        whiteListedDomains: ['localhost', 'cormack.qa.ocom.com.au']
    });

    $httpProvider.interceptors.push('jwtInterceptor');
}

function run($state, $rootScope, $localStorage, authService, dataCacheService, editableOptions, editableThemes,
             roleService) {
    var access = {};
    // below is required to match routing with role authentication
    var routeMapping = {
        job: ['job.create', 'job.list', 'job.edit', 'job.slab-schedule', 'job.pour-schedule', 'job.paving_list', 'job.enumber_list'],
        repair: ['repair.create', 'repair.list', 'repair.edit'],
        email: ['email.list', 'email.assign'],
        report: ['reports'],
        mobile: ['mobile.list', 'mobile.edit']
    };

    roleService.updateRouteMapping(routeMapping);
    // TODO: rename allowRoles to groupRoles i,e,, Group Roles are to be retrieved from the user account
    authService.allowRoles = true;
    $rootScope.allow_access = false;
    $rootScope.$state = $state;

    var updatePermissions = function () {
        var user = authService.getCurrentUser();
        var permissions = {
            // ROLE: Administrator
            'administrator': {
                job: {
                    'job.create': {
                        view: true,
                        update: true
                    },
                    'job.list': true,
                    'job.edit': {
                        view: true,
                        update: true
                    },
                    'job.slab-schedule': true,
                    'job.pour-schedule': true,
                    'job.paving_list': true,
                    'job.enumber_list': true
                },
                repair: {
                    'repair.create': {
                        view: true,
                        update: true
                    },
                    'repair.list': true,
                    'repair.edit': {
                        view: true,
                        update: true
                    }
                },
                mobile: {
                    'mobile.list': true,
                    'mobile.edit': {
                        view: true,
                        update: true
                    },
                    'mobile.listtasks': true
                },
                email: {
                    'email.fetch': true,
                    'email.list': true,
                    'email.assign': {
                        view: true,
                        update: true
                    },
                    'email.delete': true
                },
                reports: true
            },
            'subbie': {
                job: {
                    'job.create': false,
                    'job.list': true,
                    'job.edit': {
                        view: ['address', 'suburb', 'job_type', 'job_number', 'comments', 'job_files', 'sqm', 'description', 'base_inspection_date', 'steel_inspection_date', 'rock_booked_date', 'materials', 'materials_time', 'has_part_a', 'part_a_date', 'part_a_booking_number', 'waste_date', 'piers_date', 'piers_inspection_date', 'piers_concrete_date', 'proposed_start_date', 'start_date', 'call_up_date', 'date_cancelled', 'mix', 'paving_colour', 'paving_type', 'has_conduit', 'job_drains', 'job_checklists', 'job_notes', 'tasks'],
                        update: ['job_files_limited']
                    },
                    'job.slab-schedule': false,
                    'job.pour-schedule': false,
                    'job.paving_list': false,
                    'job.enumber_list': false
                },
                repair: {
                    'repair.create': false,
                    'repair.list': true,
                    'repair.edit': {
                        view: ['job', 'supervisor', 'description', 'repair_files_limited'],
                        update: ['repair_files_limited']
                    }
                },
                mobile: {
                    'mobile.list': true,
                    'mobile.edit': {
                        view: true,
                        update: false
                    },
                    'mobile.listtasks': true
                },
                email: false,
                reports: false
            },
            'supervisor': {
                job: {
                    'job.create': false,
                    'job.list': true,
                    'job.edit': {
                        view: ['address', 'suburb', 'client', 'job_type', 'job_number', 'comments', 'job_files', 'sqm', 'description', 'supervisor', 'supervisor_mobile_number', 'supervisor_email', 'base_inspection_date', 'steel_inspection_date', 'rock_booked_date', 'materials', 'materials_time', 'waste_date', 'proposed_start_date', 'start_date', 'call_up_date', 'mix', 'paving_colour', 'paving_type', 'has_conduit', 'job_drains', 'job_checklists', 'job_notes', 'tasks'],
                        update: ['job_files_limited', 'job_notes']
                    },
                    'job.slab-schedule': false,
                    'job.pour-schedule': false,
                    'job.paving_list': false,
                    'job.enumber_list': false
                },
                repair: {
                    'repair.create': false,
                    'repair.list': true,
                    'repair.edit': {
                        view: true,
                        update: ['repair_files_limited', 'repair_notes']
                    }
                },
                mobile: false,
                email: false,
                reports: true
            },
            'client_manager': {
                job: {
                    'job.create': false,
                    'job.list': true,
                    'job.edit': {
                        view: ['address', 'suburb', 'client', 'job_type', 'job_number', 'comments', 'job_files', 'sqm', 'description', 'supervisor', 'supervisor_mobile_number', 'supervisor_email', 'base_inspection_date', 'steel_inspection_date', 'rock_booked_date', 'materials', 'materials_time', 'waste_date', 'proposed_start_date', 'start_date', 'call_up_date', 'mix', 'paving_colour', 'paving_type', 'has_conduit', 'job_drains', 'job_checklists', 'job_notes', 'tasks'],
                        update: ['job_files_limited']
                    },
                    'job.slab-schedule': false,
                    'job.pour-schedule': false,
                    'job.paving_list': false,
                    'job.enumber_list': false
                },
                repair: {
                    'repair.create': false,
                    'repair.list': true,
                    'repair.edit': {
                        view: true,
                        update: false
                    }
                },
                mobile: false,
                email: false,
                reports: true
            },
            'employee': {
                job: {
                    'job.create': false,
                    'job.list': true,
                    'job.edit': {
                        view: ["active_end_date","address","base_inspection_date","base_inspection_time_of_day",
                            "building_inspector_supplier","call_up_date","client","comments","date_cancelled",
                            "date_received","description","dollars_difference","excavation_allowance","has_conduit",
                            "has_part_a","has_part_a_date","job_checklists","job_costs","job_files",
                            "job_notes","job_number","job_type","mix","part_a_booking_number","paving_colour",
                            "paving_type","piers_date","piers_inspection_date","piers_inspection_time_of_day", "piers_concrete_time_of_day", "piers_concrete_date","piers_concrete_time_of_day",
                            "piers_time_of_day","pod_delivery_date","pod_supplier","pour_date","pour_date_time_of_day",
                            "rock_booked_date","rock_booked_time_of_day","rock_m3","rock_supplier","sqm","start_date",
                            "steel_delivery_date","steel_inspection_date","steel_inspection_time_of_day","steel_supplier",
                            "steps","sub_contractor","suburb","supervisor","take_off_sent","tasks","termite_supplier",
                            "waste_date","waste_time_of_day", 'job_files', 'steps',
                            "down_pipes_installed", "down_pipes_comment", "gas_line_installed", "gas_line_comment",
                            "rebates_brickwork", "rebates_brickwork_comment", "risers_correct_location", "risers_location_comment",
                            "good_access_rear_paving", "rear_paving_comment", "pacing_within_tolerance", "pacing_heights_comment"],
                        update: ['job_checklists', 'job_notes', 'job_files', 'steps', "down_pipes_installed", "down_pipes_comment", "gas_line_installed", "gas_line_comment", "rebates_brickwork", "rebates_brickwork_comment", "risers_correct_location", "risers_location_comment", "good_access_rear_paving", "rear_paving_comment", "pacing_within_tolerance", "pacing_heights_comment"]
                    },
                    'job.slab-schedule': true,
                    'job.pour-schedule': true,
                    'job.paving_list': {
                        view: true,
                        update: ['steps']
                    },
                    'job.enumber_list': {
                        view: true,
                        update: ['steps']
                    }
                },
                repair: {
                    'repair.create': false,
                    'repair.list': true,
                    'repair.edit': {
                        view: true,
                        update: false
                    }
                },
                mobile: false,
                email: false,
                reports: true
            },
            // ROLE: Default
            'default': {
                job: {
                    'job.create': false,
                    'job.list': true,
                    'job.edit': false,
                    'job.slab-schedule': false,
                    'job.pour-schedule': false,
                    'job.paving_list': false,
                    'job.enumber_list': false
                },
                subbie_views: false,
                repair: {
                    'repair.create': false,
                    'repair.list': true,
                    'repair.edit': false
                },
                mobile: false,
                email: false,
                reports: false
            }
        };
        roleService.updatePermissions(permissions);

        if (user.role && user.role.administrator) {    // ignore other roles
            access = roleService.getPermission('administrator');
        // TODO: Merge roles and permissions if user has two or more roles
        } else if (user.role && user.role.subcontractor) {
            access = roleService.getPermission('subbie');
        } else if (user.role && user.role.supervisor) {
            access = roleService.getPermission('supervisor');
        } else if (user.role && user.role.client_manager) {
            access = roleService.getPermission('client_manager');
        } else if (user.role && user.role.employee) {
            access = roleService.getPermission('employee');
        } else {
            if (!user.role)
                console.warn("Unable to access user rules. Permissions will be limited.");
            access = roleService.getPermission('default');
        }
        roleService.updateAccessSettings(access);

        // check NAV MENU accessibility: job
        angular.forEach(NAV_MENU.job, function (item, index) {
            if (!roleService.isAccessible('job', item.stateName)) {
                NAV_MENU.job[index].skip = true;
            } else if (angular.isDefined(NAV_MENU.job[index].skip)) {
                delete NAV_MENU.job[index].skip;
            }
        });

        // check NAV MENU accessibility: repair
        angular.forEach(NAV_MENU.repair, function (item, index) {
            if (!roleService.isAccessible('repair', item.stateName)) {
                NAV_MENU.repair[index].skip = true;
            } else if (angular.isDefined(NAV_MENU.repair[index].skip)) {
                delete NAV_MENU.repair[index].skip;
            }
        });

        // check NAV MENU accessibility: email
        angular.forEach(NAV_MENU.email, function (item, index) {
            if (!roleService.isAccessible('email', item.stateName)) {
                NAV_MENU.email[index].skip = true;
            } else if (angular.isDefined(NAV_MENU.email[index].skip)) {
                delete NAV_MENU.email[index].skip;
            }
        });
    };

    $rootScope.$on('$pageLoaded', function () {
        if ($localStorage.isAuthenticated) {
            //roleService.additionalRoles = ['administrator', 'subbie', 'supervisor', 'client_manager', 'default'];
            updatePermissions();
        }
    });

    editableOptions.theme = 'default';
    editableThemes['default'].submitTpl = '<button type="submit" class="btn btn-success">Save</button>';
    editableThemes['default'].cancelTpl = '<button type="button" class="btn btn-default" ng-click="$form.$cancel()">Cancel</button>';
}
