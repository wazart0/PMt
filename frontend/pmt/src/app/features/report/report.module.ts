import { ReportRoutingModule } from './report-routing.module';
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AnychartTestComponent } from './anychart-test/anychart-test.component';
import { ReportPageComponent } from './report-page/report-page.component';

@NgModule({
  declarations: [AnychartTestComponent, ReportPageComponent],
  imports: [CommonModule, ReportRoutingModule],
})
export class ReportModule {}
