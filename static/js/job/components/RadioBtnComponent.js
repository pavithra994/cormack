

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
        if (ctrl.item[ctrl.field] != null) { //if already set then make null.
            ctrl.item[ctrl.field] = null;
        }
        else {
            ctrl.item[ctrl.field] = new Date();
        }

        if (ctrl.formsCtrl) {
            ctrl.formsCtrl.$setDirty(true);
        };

        this.onChange({'item': ctrl.item, 'key':ctrl.field});
    };
}
angular.module('app.job').component('radioBtn', {
  templateUrl: 'js/job/components/RadioBtnComponent.html',
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
