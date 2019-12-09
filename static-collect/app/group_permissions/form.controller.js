/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    'use strict';

    angular.module('app.group_permissions')
           .controller('GroupPermissionsController', ['$state', '$stateParams', '$scope', '$filter', 'alerts',
               'dataAPIService', 'formStateService', 'permissionService', 'SweetAlert', 'CodeTableCacheService', 'platform',
                '$http', '$anchorScroll', '$q',
    function ($state, $stateParams, $scope, $filter, alerts, dataAPIService, formStateService, permissionService, SweetAlert,
              CodeTableCacheService, platform, $http, $anchorScroll, $q) {
        alerts.clearMessages();

        $scope.platform = platform;
        $scope.modelName = 'group_permissions';
        $scope.route = $state.current.name;
        $scope.data_api = dataAPIService.getDataApi("/api/", $scope.modelName);
        $scope.formStateService = formStateService.formState;
        $scope.refreshUpdateTable = false;

        loadItem();
        loadOptions();

        $scope.search = {'filter_field': ""};

        function loadAllModelFields (item) {
            _.each(item.states, function (state){
                _.each(state.models, function (models_item){
                    $scope.loadModelOptions(models_item.base_uri, models_item.model_name);
                });
            });
        }

        function loadItem() {
            formStateService.setFormState({loading: true});
            $scope.item = {
                "group": null,
                "states": [{deny:false, _show:true}]
                }; //TODO Set Defaults for New Item here1

            if ($state.params.id) {
                $scope.data_api.getItem($state.params.id, function (response) {
                    formStateService.setFormState({loading: false});
                    $scope.item = _.extend($scope.item, response);
                    $scope.item.is_active = true; // cannot be deactivated.

                    loadAllModelFields($scope.item);

                    $scope.refreshUpdateTable = true;
                });
            } else {
                $scope.item.is_active = true;
                $scope.refreshUpdateTable = true;
                formStateService.setFormState({loading: false});
            }
        }

        function loadOptions() {
            var loadTables = [
                {
                    name: 'group_list',
                    uri : '/api/',
                    scope: 'group_List'
                },            ];

            $scope.options = {};

            CodeTableCacheService.processLoadTables(loadTables, $scope.options);
        }

        /* Override for default implementation */
        $scope.validateItem = function (item) {
            return true;
        };

        /* Override the following to change behaviour */
        $scope.allowDelete = function (model) {
            return $scope.item.is_active && !formStateService.formState('loading') && !formStateService.formState('saving') && permissionService.can_goto_state ({"name":model + ".delete"});
        };

        $scope.allowRestore = function (model) {
            return !$scope.item.is_active && !formStateService.formState('loading') && !formStateService.formState('saving') && permissionService.can_goto_state ({"name":model + ".restore"});
        };

        /* TODO: use the roleService - here for testing */
        $scope.editable = function (model, route) {
            return true; // hardcode
        };

        $scope.getExtraStates = function () {
            var currentStates = _.map($scope.item.states, function (state) {
               return state.state_name;
            });

            var all_states = $scope.getStates();

            _.remove(currentStates, function (obj) {
                return all_states.includes(obj);
            });

            return currentStates;
        };

        $scope.getStates = function () {
            return _.filter(_.map($state.get(), function (state) {
                return state.name;
            }), function (item) {
                return item;
            }); // filter out nulls/empty
        };

        $scope.modelOptions = {};

        $scope.loadModelOptions = function (uri, modelName) {
            modelName = modelName.toLowerCase();

            var options= $scope.modelOptions[modelName];

            if (!options) {
                return $http({'method':'OPTIONS', 'url': uri + modelName + "/"}).then (function (response) {
                    var modelData = response.data;

                    modelData.fields = _.filter(_.map(modelData.actions.POST, function (val, key) {
                        var label = val.label;

                        // label = label + "(" + key + ")";

                        return {id: key, label: label};
                    }), function (o) {
                       return o.id != 'pk';
                    });


                    $scope.modelOptions[modelName] = modelData;
                });
            }
            return $q(function(resolve, reject) {
                resolve(options);
            });
        };

        $scope.cleanUpFields = function(permission) {
            permission.fields = _.filter(permission.fields, function (field) {
                return (field.deny_read || field.deny_update);
            });

            if ($scope.form) {
                $scope.form.$setDirty(true);
            }
        };

        $scope.addMissingFields = function (permission) {
            var options = $scope.modelOptions[permission.model_name];

            _.each(options.fields, function (field) {
               var found = _.find (permission.fields, function (item) {
                  return field.id == item.field_name;
               });

               if (!found) {
                   if (!permission.fields)
                       permission.fields = [];

                   permission.fields.push ({field_name:field.id, deny_read:false, deny_update:false});
               }
            });

            if ($scope.form) {
                $scope.form.$setDirty(true);
            }
        };

        $scope.setStateName = function (states_item, o) {
            states_item.state_name = o;
        };

        $scope.hasStateName = function (o) {
            var found = _.find($scope.item.states, function (state) {
               return state.state_name == o;
            });

            return found;
        };

        $scope.missing = function (list, name) {
            if (_.find(list, {'id':name}))
                return false;
            else
                return true; // not found ie missing
        };

        $scope.showStateItem = function (item) {
            _.each($scope.item.states, function (state) {
               if (state != item)
                {
                    state._show = false;
                }
                else {
                    state._show = true;
               }
            });

            item._show = true;
        };

        $scope.addState = function (o) {
            var item = $scope.hasStateName(o);

            if (!item) {
                var item = {state_name: o, deny: true};
                $scope.item.states.push(item);
            }

            $scope.showStateItem(item);
        };

        $scope.setAll= function (list, fieldName, value) {
            _.each (list, function (item) {
                item[fieldName] = value;
            });

            if ($scope.form) {
                $scope.form.$setDirty(true);
            }
        };

        $scope.toggle = function (item, fieldName) {
            item[fieldName] = !(item[fieldName] || false);

            if ($scope.form) {
                $scope.form.$setDirty(true);
            }
        };

        $scope.duplicateState = function (list, item) {

            var newItem = angular.copy(item);

            // remove ids
            delete newItem.id;
            delete newItem.pk;
            _.each (newItem.models, function (model) {
                delete  model.id;
                delete  model.pk;

                _.each (model.fields, function (field) {
                    delete  field.id;
                    delete  field.pk;
                });
            });

            list.push (newItem);

            if ($scope.form) {
                $scope.form.$setDirty(true);
            }
        }

        $scope._showUpload = false;
        $scope.showUpload = function () {
            $scope._showUpload = !$scope._showUpload;
        };
        $scope.closeShowUpload = function () {
            $scope._showUpload = false;
        };

        $scope.uploadData = {json:""};

        $scope.uploadJSON = function (jsonText) {
            try {
                var data = JSON.parse(jsonText);
            } catch (e) {
                alerts.error ("Cannot parse the JSON. Please check and try again");
            }
            cleanUpJSON(data);

            // Look up group name - if found us that instead of the ID
            var group = _.find ($scope.options.group_List, function (group) {
                return group.name = data.group_name;
            });

            loadAllModelFields(data);

            if (group) {
                data.group = group.id;
            }
            delete data.group_name;

            $scope.item = data;

            $scope.uploadData.json = ""; // clear
            $scope._showUpload = false;
        };

        function cleanUpJSON(data) {
            delete data.id;
            delete data.pk;
            delete data.$hashKey;

            _.each(data.states, function (state) {
                delete state.id;
                delete state.pk;
                delete state.$hashKey;

                _.each(state.models, function (model) {
                    delete model.id;
                    delete model.pk;
                    delete model.$hashKey;

                    _.each(model.fields, function (field) {
                        delete field.id;
                        delete field.pk;
                        delete field.$hashKey;
                    });
                });
            });
        }

        $scope.download = function () {
            var group = _.find ($scope.options.group_List, function (group) {
                return group.id == $scope.item.group;
            });

            var data = angular.copy($scope.item);
            data.group_name = group.name;

            // clean up the data
            cleanUpJSON(data);

            var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data, null, 2));
            var dlAnchorElem = document.getElementById('downloadAnchorElem');
            dlAnchorElem.setAttribute("href",     dataStr     );
            dlAnchorElem.setAttribute("download", group.name + "_template.json");
            dlAnchorElem.click();
        }
    }]);

})();
