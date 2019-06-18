import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { GantComponent } from './gant/gant.component';

@NgModule({
  declarations: [GantComponent],
  imports: [CommonModule],
  exports: [GantComponent]
})
export class GantModule {}
