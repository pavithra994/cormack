

/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019 
 *
 */

function StepsController () {
    var ctrl = this;

    ctrl.setStep = function(step) {
        if (ctrl.formsCtrl) {
            ctrl.formsCtrl.$setDirty(true);
        }

        if (ctrl.item[step.field])
            ctrl.item[step.field] = null;
        else
            ctrl.item[step.field] = new Date();

        this.onChange({'item': ctrl.item, 'key':step.field});
    }
}
angular.module('app.job').component('steps', {
  templateUrl: 'js/job/components/StepsComponent.html',
  require: {
    formsCtrl: '?^form'
  },
  controller: StepsController,
  bindings: {
      item: '<',
      steps:'<',
      disabled: '=',
      onChange: "&"
  }
});
