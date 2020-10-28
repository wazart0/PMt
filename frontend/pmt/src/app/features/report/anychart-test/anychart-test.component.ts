import { ReportService } from './../report.service';
import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import 'anychart';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-anychart-test',
  templateUrl: './anychart-test.component.html',
  styleUrls: ['./anychart-test.component.scss'],
})
export class AnychartTestComponent implements OnChanges {
  chart: anychart.charts.Gantt;
  ganttDataSubscription: Subscription;

  @Input()
  search: string;
  constructor(private reportService: ReportService) {}

  ngOnChanges(changes: SimpleChanges) {
    if (changes.search) {
      console.log(changes.search);
      this.gantt(this.search);
    }
  }

  gantt(search?: string) {
    let data = [];

    if (this.chart) {
      this.chart.dispose();
    }

    if (this.ganttDataSubscription) {
      this.ganttDataSubscription.unsubscribe();
    }

    this.ganttDataSubscription = this.reportService
      .get(search)
      .subscribe((response: any) => {
        if (response.data.project.length == 0) {
          return;
        }
        let projects = response['data']['project'];

        for (let i = 0; i < projects.length; i++) {
          let task = {
            id: projects[i]['id'].toString(),
            name: projects[i]['name'],
            actualStart: projects[i]['default_baseline_project']['start'],
            actualEnd: projects[i]['default_baseline_project']['finish'],
            parent: projects[i]['default_baseline_project']['parent_id'],
          };
          data.push(task);
        }

        // create a data tree
        var treeData = anychart.data.tree(data, 'as-tree');
        // create a chart
        var chart = anychart.ganttProject();
        this.chart = chart;

        const timeline = chart.getTimeline();
        timeline.enabled(false);

        chart.splitterPosition('150%');

        const name = chart.dataGrid().column(1);
        name.width(150);

        const start = chart.dataGrid().column(2);
        start.width(150);
        start.title('Start');
        start.labels().format('{%start}{dateTimeFormat:dd MMM}');
        start.depthPaddingMultiplier(20);
        start.collapseExpandButtons(true);

        const end = chart.dataGrid().column(3);
        end.width(150);
        end.title('End');
        end.labels().format('{%end}{dateTimeFormat:dd MMM}');
        end.depthPaddingMultiplier(20);
        end.collapseExpandButtons(true);

        // set the data
        this.chart.data(treeData);
        // set the container id
        this.chart.container('container');
        // initiate drawing the chart
        this.chart.draw();
        // fit elements to the width of the timeline
        this.chart.fitAll();
      });
  }
}
