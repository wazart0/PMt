import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { NotFoundComponent } from '../shared/components/not-found/not-found.component';
import { MainComponent } from './layouts/main/main.component';

const routes: Routes = [
  { path: '', component: MainComponent /* TODO: or module ??*/ },
  { path: '**', component: NotFoundComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class PublicRoutingModule {}
