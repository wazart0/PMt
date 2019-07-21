import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GantComponent } from './components/gant/gant.component';
import { TaskComponent } from './components/task/task.component';
import { MDBBootstrapModule } from 'angular-bootstrap-md';

@NgModule({
  declarations: [GantComponent, TaskComponent],
  imports: [CommonModule, MDBBootstrapModule],
  exports: [GantComponent]
})
export class GantModule {}
