import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HeaderComponent } from './components/header/header.component';
import { MDBBootstrapModule } from 'angular-bootstrap-md';
import { NotFoundComponent } from './components/not-found/not-found.component';

@NgModule({
  declarations: [HeaderComponent, NotFoundComponent],
  imports: [CommonModule, MDBBootstrapModule.forRoot()],
  exports: [NotFoundComponent, HeaderComponent]
})
export class SharedModule {}
