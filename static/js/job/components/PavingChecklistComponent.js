

/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019 
 *
 */

function PavingChecklistController () {
    var ctrl = this;

    ctrl.setStep = function(step) {
        if (ctrl.formsCtrl) {
            ctrl.formsCtrl.$setDirty(true);
        }

        if (ctrl.item[step.field] == null)
            ctrl.item[step.field] = true;
        else {
            if (ctrl.item[step.field])
                ctrl.item[step.field] = false; // Second Time = False
            else
                ctrl.item[step.field] = null; // Third time = Null
        }

        this.onChange({'item': ctrl.item, 'key':step.field});
    }
}
angular.module('app.job').component('pavingChecklist', {
  templateUrl: 'js/job/components/PavingChecklistComponent.html',
  require: {
    formsCtrl: '?^form'
  },
  controller: PavingChecklistController,
  bindings: {
      item: '<',
      fields:'<',
      disabled: '=',
      onChange: "&"
  }
});
