import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
@Injectable({
    providedIn: 'root'
})

/**
 * Handles interaction with the Django backend.
 * 
 * This replaces the previous component that was based on $resource.
 */
export class DataService {

    /**
     * Set up a new DataService with the given injected services.
     * 
     * @param http An HttpClient from dependency injection.
     */
    constructor(
        private http: HttpClient
    ) {}

    /**
     * Download the slab schedule from the server.
     */
    getSlabSchedule(
        filter : string = "all",
        job_type : number | null = null,
        limit : number | null = 20,
        offset : number | null = 0,
        order : "asc" | "desc" = "asc",
        sort : string | null = null,
        pour_date__ge : string | null = null,
        search : string | null = null
    ) {
        let url = "/api/job/?" + [
            "filter=" + filter,
            job_type != null ? `job_type=${job_type}` : null,
            limit != null ? `limit=${limit}` : null,
            offset != null ? `offset=${offset}` : null,
            `order=${order}`,
            sort ? `sort=${sort}` : null,
            pour_date__ge != null ? `pour_date__ge=${pour_date__ge}` : null,
            search ? `q=${search}` : null
        ].filter(x => x != null).join("&");
        console.debug("API " + url);
        return this.http.get(url);
    }

    /**
     * Downloads all builders from the Django app.
     */
    getBuilders(filter : "active" | "all" = "active") {
        return this.http.get("/api/client/?" + [
            "filter=" + filter
        ].filter(x => x != null).join("&"));
    }

    /**
     * Downloads all supervisors from the Django app.
     */
    getSupervisors(filter : "active" | "all" = "active") {
        return this.http.get("/api/supervisor/?" + [
            "filter=" + filter
        ].filter(x => x != null).join("&"));
    }

    /**
     * Downloads all subcontractors from the Django app.
     */
    getSubcontractors(filter : "active" | "all" = "active") {
        return this.http.get("/api/subbie/?" + [
            "filter=" + filter
        ].filter(x => x != null).join("&"));
    }

    /**
     * Downloads all suppliers from the Django app.
     */
    getSuppliers(filter : "active" | "all" = "active") {
        return this.http.get("/api/code_supplier/?" + [
            "filter=" + filter
        ].filter(x => x != null).join("&"));
    }

    /**
     * Patch a job existing in the database.
     * @param job The job to patch.
     */
    patchJob(job : any) {
        console.log(`patching job ${job.id}`)
        return this.http.patch(
            `/api/job/${job.id}/`,
            JSON.stringify(job),
            {
                headers: {
                    "Content-Type": "application/json"
                }
            });
    }
}
