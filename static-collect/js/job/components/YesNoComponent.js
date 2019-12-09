

/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019 
 *
 */

function YesNoController () {
    var ctrl = this;

    ctrl.setValue = function (value) {
        if (ctrl.item[ctrl.field] === value) { //if already set then make null.
            ctrl.item[ctrl.field] = null;
        }
        else {
            ctrl.item[ctrl.field] = value;
        }

        if (ctrl.formsCtrl) {
            ctrl.formsCtrl.$setDirty(true);
        };

        this.onChange({'item': ctrl.item, 'key':ctrl.field});
    };
}
angular.module('app.job').component('yesNo', {
  templateUrl: 'js/job/components/YesNoComponent.html',
  require: {
    formsCtrl: '?^form'
  },
  controller: YesNoController,
  bindings: {
      item: '<',
      field: '<',
      disabled: '=',
      onChange: "&"
  }
});
