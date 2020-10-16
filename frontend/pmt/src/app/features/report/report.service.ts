import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class ReportService {
  constructor(private readonly httpClient: HttpClient) {}

  get(name = 'default') {
    let url = 'http://51.83.129.102:8090/v1/graphql/';
    // let url = 'http://localhost:8000/graphql/';
    // let url = 'http://backend:8000/graphql/';
    return this.httpClient.post(url, {
      query: `
        query projects_for_baseline {
          baseline(where: {name: {_eq: "${name}"}, base_project: {name: {_eq: "test_FS_only.csv"}}}) {
            projects(order_by: {project: {created_at: asc}}) {
              finish
              parent_id
              project_id
              start
              project {
                name
                label
              }
            }
          }
        }
        `,
    });
  }
}
