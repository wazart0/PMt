import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HeaderComponent } from './components/header/header.component';
import { MDBBootstrapModule } from 'angular-bootstrap-md';
import { NotFoundComponent } from './components/not-found/not-found.component';
import { MainLayoutComponent } from './layouts/main-layout/main-layout.component';
import { RouterModule } from '@angular/router';

@NgModule({
  declarations: [HeaderComponent, NotFoundComponent, MainLayoutComponent],
  imports: [CommonModule, RouterModule, MDBBootstrapModule.forRoot()],
  exports: [NotFoundComponent, HeaderComponent, MainLayoutComponent]
})
export class SharedModule {}
