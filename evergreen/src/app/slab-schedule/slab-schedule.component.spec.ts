import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SlabScheduleComponent } from './slab-schedule.component';

describe('SlabScheduleComponent', () => {
  let component: SlabScheduleComponent;
  let fixture: ComponentFixture<SlabScheduleComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SlabScheduleComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SlabScheduleComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
