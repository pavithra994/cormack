import { Injectable } from '@angular/core';

/**
 * Service to provide authentication.
 * 
 * This class is a bit messy because it needs to interface with the authentication system from the previous version of
 * the app.
 */
@Injectable({ providedIn: 'root' })
export class AuthenticationService {

    /**
     * Set up a new instance of this class.
     */
    constructor() {}

    /**
     * Gets the JWT token for the current user.
     */
    getToken() {
        return localStorage.getItem("ngStorage-token");
    }

    /**
     * Get the user information from local storage.
     */
    getUser() {
        let str = localStorage.getItem("ngStorage-user");
        if (!str)
            return null;
        return JSON.parse(str);
    }
}
