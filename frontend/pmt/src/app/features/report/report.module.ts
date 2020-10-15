import { ReportRoutingModule } from './report-routing.module';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AnychartTestComponent } from './anychart-test/anychart-test.component';

@NgModule({
  declarations: [AnychartTestComponent],
  imports: [CommonModule, ReportRoutingModule],
})
export class ReportModule {}
