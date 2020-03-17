import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule, HTTP_INTERCEPTORS } from "@angular/common/http";

import { AuthenticationService } from "./authentication.service";
import { AuthenticationInterceptor } from "./authentication.interceptor";

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { SlabScheduleComponent } from './slab-schedule/slab-schedule.component';
import { SlabScheduleRowComponent } from './slab-schedule-row/slab-schedule-row.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';

import { DatetimepickerDirective } from './datetimepicker.directive';

@NgModule({
    declarations: [
        AppComponent,
        SlabScheduleComponent,
        SlabScheduleRowComponent,
        DatetimepickerDirective
    ],
    imports: [
        BrowserModule,
        AppRoutingModule,
        HttpClientModule,
        FormsModule,
        BrowserAnimationsModule,
    ],
    providers: [
        { provide: HTTP_INTERCEPTORS, useClass: AuthenticationInterceptor, multi: true }
    ],
    bootstrap: [AppComponent]
})
export class AppModule { }
