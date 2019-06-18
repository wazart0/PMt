import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-gant',
  templateUrl: './gant.component.html',
  styleUrls: ['./gant.component.scss']
})
export class GantComponent implements OnInit {
  constructor(private httpClient: HttpClient) {}
  jobs$;
  getJobs() {
    return this.httpClient.get(`${environment.api}/jobs`);
  }
  ngOnInit() {
    this.jobs$ = this.getJobs();
  }
}
