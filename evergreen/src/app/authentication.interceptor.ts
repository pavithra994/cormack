import { Injectable } from '@angular/core';
import {
    HttpRequest,
    HttpHandler,
    HttpEvent,
    HttpInterceptor
} from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class AuthenticationInterceptor implements HttpInterceptor {

    constructor() {}

    intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {

        let token = localStorage.getItem("ngStorage-token");
        if (!token)
            return next.handle(request);
        
        token = token.substr(1, token.length - 2);
        
        const cloned = request.clone({
            headers: request.headers.set("Authorization", "Bearer " + token)
        })
        return next.handle(cloned);
    }
}
