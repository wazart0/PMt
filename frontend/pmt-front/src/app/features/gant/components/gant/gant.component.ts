import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Task } from '../../models/task.model';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-gant',
  templateUrl: './gant.component.html',
  styleUrls: ['./gant.component.scss']
})
export class GantComponent implements OnInit {
  constructor(private httpClient: HttpClient) {}
  jobs$: Observable<Node>;
  jobs: Node;

  tasks: Task[];

  dividerPosition = 70;
  dividerSize = 1;
  ngOnInit() {
    this.getJobs().subscribe(x => console.log(x));
    this.tasks = this.getTasks();
  }

  taskClicked(index: number, task: Task) {
    if (!task.children) {
      return;
    }
    if (!task.expanded) {
      task.expanded = true;
      this.tasks.splice(index + 1, 0, ...task.children);
    } else {
      task.expanded = false;
      this.tasks.splice(index + 1, task.children.length);
    }
  }

  private getTasks() {
    return [
      new Task('Task no1', 'Resource no1', new Date(), new Date(), [
        new Task('Task no1a', 'Resource no1', new Date(), new Date(), null),
        new Task('Task no1b', 'Resource no1', new Date(), new Date(), null),
        new Task('Task no1c', 'Resource no1', new Date(), new Date(), [
          new Task('Task no1c1', 'Resource no1', new Date(), new Date(), null),
          new Task('Task no1c2', 'Resource no1', new Date(), new Date(), null),
          new Task('Task no1c3', 'Resource no1', new Date(), new Date(), null)
        ])
      ]),
      new Task('Task no2', 'Resource no1', new Date(), new Date(), null),
      new Task('Task no3', 'Resource no1', new Date(), new Date(), null)
    ];
  }

  getJobs() {
    return this.httpClient.get(`${environment.api}/jobs`);
  }
}
