import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { SlabScheduleRowComponent } from './slab-schedule-row.component';

describe('SlabScheduleRowComponent', () => {
  let component: SlabScheduleRowComponent;
  let fixture: ComponentFixture<SlabScheduleRowComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ SlabScheduleRowComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(SlabScheduleRowComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
