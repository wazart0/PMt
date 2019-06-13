import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { PublicRoutingModule } from './public-routing.module';
import { SharedModule } from '../shared/shared.module';
import { MainComponent } from './layouts/main/main.component';

@NgModule({
  declarations: [MainComponent],
  imports: [CommonModule, PublicRoutingModule, SharedModule]
})
export class PublicModule {}
