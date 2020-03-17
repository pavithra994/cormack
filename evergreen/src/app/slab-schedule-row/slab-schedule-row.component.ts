import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import { DataService } from "../data.service";

/**
 * A class to display one line of the slab schedule.
 */
@Component({
    selector: '[slab-schedule-row]',
    templateUrl: './slab-schedule-row.component.html',
    styleUrls: ['./slab-schedule-row.component.css']
})
export class SlabScheduleRowComponent implements OnInit {

    /**
     * A dictionary of which fields are currently being updated.
     */
    update = {};

    /**
     * The job that this row is displaying.
     */
    @Input() job : any;

    /**
     * A dictionary of builder names to match up to codes.
     */
    @Input() builders : {};

    /**
     * A dictionary of supervisor names to match up to codes.
     */
    @Input() supervisors : {};

    /**
     * A dictionary of supervisor names to match up to codes.
     */
    @Input() subcontractors : {};

    /**
     * A dictionary of supplier names to match up to codes.
     */
    @Input() suppliers : {};

    /**
     * Whether to show a label for which depot on the rows.
     */
    @Input() showLabel : boolean = false;

    /**
     * An event to trigger reloading all of the data.
     */
    @Output() reload : EventEmitter<any> = new EventEmitter();

    /**
     * Set up a new instance of this component.
     */
    constructor(private dataService : DataService) {}

    /**
     * Initialize this component.
     */
    ngOnInit(): void {}

    /**
     * Mark a given field as being updated (which should show the update form).
     * @param field The field to set as being updated.
     */
    setUpdate(field : string) {
        Object.keys(this.update).forEach(key => this.update[key] = (key == field));
        if (!(field in this.update))
            this.update[field] = true;
    }

    /**
     * Update this record in the database.
     */
    patch(field : string) {
        this.dataService.patchJob(this.job).subscribe(
            (result) => {
                console.log("PATCH result", result)
                // TODO: Update sort order.
                this.reload.emit(field);
            },
            (error) => console.log("PATCH error", error));
    }

    getPumpInspectors() {
        return Object.entries(this.subcontractors)
            .filter(([key, value]) => value["type"]["code"] == "Pumping")
            .reduce((map, [key, value]) => {
                map[key] = value;
                return map;
            }, {});
    }

    getSubcontractors() {
        return Object.entries(this.subcontractors)
            .filter(([key, value]) => value["type"]["id"] == 6)
            .reduce((map, [key, value]) => {
                map[key] = value;
                return map;
            }, {});
    }

    /**
     * Required for comparing IDs in select tags, because otherwise Angular is particular about exact matching
     * references.
     * @param n1 
     * @param n2 
     */
    numberEquals(n1, n2) {
        return n1 == n2
    }
}
