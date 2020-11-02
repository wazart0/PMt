import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzGridModule } from 'ng-zorro-antd/grid';
import { NzLayoutModule } from 'ng-zorro-antd/layout';
import { NzSelectModule } from 'ng-zorro-antd/select';
import { FormsModule } from '@angular/forms';
import { NzDropDownModule } from 'ng-zorro-antd/dropdown';

@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    NzInputModule,
    NzButtonModule,
    NzGridModule,
    NzLayoutModule,
    NzSelectModule,
    NzDropDownModule,
    FormsModule,
  ],
  exports: [
    NzInputModule,
    NzButtonModule,
    NzGridModule,
    NzGridModule,
    NzLayoutModule,
    NzSelectModule,
    NzDropDownModule,
    FormsModule,
  ],
})
export class SharedModule {}
