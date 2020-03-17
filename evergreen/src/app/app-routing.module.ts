import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { SlabScheduleComponent } from './slab-schedule/slab-schedule.component';


const routes: Routes = [
  { path: "slab-schedule", component: SlabScheduleComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
