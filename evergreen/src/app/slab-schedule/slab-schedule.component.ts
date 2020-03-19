import { Component, OnInit } from '@angular/core';
import { DataService } from "../data.service";
import { SlabScheduleRowComponent } from '../slab-schedule-row/slab-schedule-row.component';
import { NONE_TYPE } from '@angular/compiler';

/**
 * A component to show / edit the slab schedule.
 * 
 * NOTE: There are currently several outstanding issues with this component:
 * 
 * 1. _Search does not work._ The API ignores `search=` and `q=` in URLs.
 * 2. Filtering by "no slab date" does not work.
 * 3. When you change the value of a sort column, it should trigger a re-download.
 */
@Component({
    selector: 'app-slab-schedule',
    templateUrl: './slab-schedule.component.html',
    styleUrls: ['./slab-schedule.component.css']
})
export class SlabScheduleComponent implements OnInit {
    /**
     * An error to show.
     */
    error: any = null;

    /**
     * The data (jobs) downloaded from the Django server.
     */
    data = null;

    /**
     * The jobs, in array form, downloaded from the Django server.
     */
    jobs = [];

    /**
     * Whether to group by date.
     */
    group: boolean = true;

    /**
     * The groups of rows.
     */
    row_groups = [];

    /**
     * The page we are currently on.
     */
    page = 0;

    /**
     * The available set of page sizes.
     */
    page_sizes_available = [10, 30, 50, 100];

    /**
     * The default page size.
     */
    page_size = 30;

    /**
     * Set to the maximum number of pages based on the number of jobs.
     */
    page_maximum = 0;

    /**
     * Filter by having a set pour date.
     */
    pour_date_set = true;

    /**
     * The search terms, from the box at the top of the page.
     */
    search_terms = null;

    /**
     * A dictionary of available builders, indexed by their ID.
     */
    builders = {}

    /**
     * A dictionary of available supervisors, indexed by their ID.
     */
    supervisors = {}

    /**
     * A dictionary of available subcontractors, indexed by their ID.
     */
    subcontractors = {}

    /**
     * A dictionary of available suppliers, indexed by their ID.
     */
    suppliers = {}

    /**
     * Which column to sort by.
     */
    sort_column = "pour_date";

    /**
     * The order to sort in.
     */
    sort_order: "asc" | "desc" = "asc";

    /**
     * Set up the component.
     */
    constructor(private dataService: DataService) { }

    /**
     * Angular initializer.
     */
    ngOnInit(): void {
        this.downloadSupportingInformation();
        this.downloadJobs();
    }

    /**
     * Download supporting information such as builders from the server.
     */
    downloadSupportingInformation() {
        // Builders
        this.dataService.getBuilders()
            .subscribe(
                (builders: any[]) => {
                    this.builders = builders.reduce((map, obj) => {
                        map[obj.id] = obj;
                        return map;
                    }, {});
                },
                error => this.error = error);

        this.dataService.getSupervisors()
            .subscribe(
                (supervisors: any[]) => {
                    this.supervisors = supervisors.reduce((map, obj) => {
                        map[obj.id] = obj;
                        return map;
                    }, {});
                },
                error => this.error = error);

        this.dataService.getSubcontractors()
            .subscribe(
                (subcontractors: any[]) => {
                    this.subcontractors = subcontractors.reduce((map, obj) => {
                        map[obj.id] = obj;
                        return map;
                    }, {});
                },
                error => this.error = error);

        this.dataService.getSuppliers()
            .subscribe(
                (suppliers: any[]) => {
                    this.suppliers = suppliers.reduce((map, obj) => {
                        map[obj.id] = obj;
                        return map;
                    }, {});
                },
                error => this.error = error);
    }

    /**
     * Download the list of jobs from the server.
     */
    downloadJobs() {
        this.group = this.sort_column == "pour_date" && this.pour_date_set;
        this.dataService.getSlabSchedule(
            this.pour_date_set ? "all" : "null_pour_date",
            1,
            this.page_size,
            this.page * this.page_size,
            this.sort_order,
            this.sort_column,
            this.pour_date_set ? new Date().toISOString() : null,
            this.search_terms
        ).subscribe(
            (data: any) => {
                this.data = data;
                this.jobs = data["results"] ?? [];

                this.page_maximum = Math.ceil(this.data.count / this.page_size) - 1;

                const groups = {};
                this.jobs.forEach(job => {
                    groups[job.pour_date] = groups[job.pour_date] || [];
                    groups[job.pour_date].push(job);
                });
                const groups_list = Object.entries(groups);
                groups_list.sort((a, b) => a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0);
                this.row_groups = groups_list.map((value: [string, any[]], index) => {
                    return {
                        key: value[0],
                        jobs: value[1],
                        melbourne_jobs: value[1].filter(x => x.depot_type == 1),
                        torquay_jobs: value[1].filter(x => x.depot_type == 2)
                    }
                });
            },
            (error: any) => {
                this.error = error;
            });
    }

    /**
     * Called by buttons on the page to set the number of rows displayed on each page.
     * @param size The size of pages.
     */
    setPageSize(size: number): void {
        this.page_size = size;
        this.page_maximum = Math.ceil(this.data.count / this.page_size) - 1;
        this.downloadJobs();
    }

    /**
     * Set the page of results that the view is displaying.
     * @param page The page index, starting from 0.
     */
    setPage(page: number): void {
        this.page = Math.min(this.page_maximum, Math.max(0, page));
        this.downloadJobs();
    }

    /**
     * Set the current sort column.
     * 
     * NOTE: This will reload the jobs.
     * 
     * @param column The column to sort by.
     */
    sortBy(column: string): void {
        if (this.sort_column == column)
            this.sort_order = this.sort_order == "asc" ? "desc" : "asc";
        this.sort_column = column;

        this.group = this.sort_column == "pour_date" && this.pour_date_set;

        this.downloadJobs();
    }

    /**
     * Return an array of possible pages.
     */
    pageOptions(): number[] {
        return [...Array(this.page_maximum + 1).keys()];
    }

    /**
     * Reload the displayed jobs based on changed filters.
     */
    reloadFilters() {
        console.log("reloading filters...");
        this.downloadJobs();
    }

    /**
     * Reload the displayed jobs based on changed filters.
     */
    reloadFieldChanged(event) {
        console.log("reloading due to field change...", event);
        if (event == this.sort_column || event == "force_reload")
            this.downloadJobs();
    }
}
