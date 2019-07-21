import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { GantComponent } from './gant.component';

describe('GantComponent', () => {
  let component: GantComponent;
  let fixture: ComponentFixture<GantComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ GantComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(GantComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
