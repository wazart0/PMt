import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { TasksRoutingModule } from './tasks-routing.module';
import { GantModule } from 'src/app/features/gant/gant.module';

@NgModule({
  declarations: [],
  imports: [CommonModule, TasksRoutingModule, GantModule]
})
export class TasksModule {}
