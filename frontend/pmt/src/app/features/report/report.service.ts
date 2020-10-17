import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class ReportService {
  constructor(private readonly httpClient: HttpClient) {}

  get(name = '') {
    let url = 'http://51.83.129.102:8090/v1/graphql/';
    // let url = 'http://localhost:8000/graphql/';
    // let url = 'http://backend:8000/graphql/';
    return this.httpClient.post(url, {
      query: `
        query projectWithDefaultBaselineAndParentWhere ($strFrag: String = "%${name}%") {
          project(where: {name: {_ilike: $strFrag}}) {
            id
            label
            name
            created_at
            description
            default_baseline_project {
              start
              finish
              worktime
              parent_id
              parent {
                label
                name
                created_at
              }
            }
          }
        }
        `,
    });
  }
}
