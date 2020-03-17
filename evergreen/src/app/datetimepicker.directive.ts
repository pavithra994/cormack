import { Directive, ElementRef, ChangeDetectorRef } from '@angular/core';

import * as moment from "moment";
import * as $ from "jquery";
import * as datetimepicker from "eonasdan-bootstrap-datetimepicker";

@Directive({
    selector: '[appDatetimepicker]'
})
export class DatetimepickerDirective {
    constructor(
        private element : ElementRef,
        private changeDetector : ChangeDetectorRef,
    ) {
        datetimepicker.call($(this.element.nativeElement), {
            format: "YYYY-MM-DD"
        });
        $(this.element.nativeElement).on("dp.change", (event) => {
            this.element.nativeElement.dispatchEvent(new Event("input"));
            this.changeDetector?.detectChanges();
        });
    }
}
