import { ReportService } from './../report.service';
import { Component, Input, OnInit, SimpleChanges } from '@angular/core';
import 'anychart';

@Component({
  selector: 'app-anychart-test',
  templateUrl: './anychart-test.component.html',
  styleUrls: ['./anychart-test.component.scss'],
})
export class AnychartTestComponent implements OnInit {
  chart: anychart.charts.Gantt;

  @Input()
  search: string;
  constructor(private reportService: ReportService) {}

  ngOnInit() {
    console.log(anychart);
    this.gantt();
  }

  ngOnChanges(changes: SimpleChanges) {
    if (changes.search?.currentValue) {
      this.gantt(this.search);
    }
  }
  gantt(search?: string) {
    // create data

    let url = 'http://51.83.129.102:8000/graphql/';
    // let url = 'http://localhost:8000/graphql/';
    // let url = 'http://backend:8000/graphql/';

    var data = [];
    // var vm = this;

    this.reportService.get(search).subscribe((response: any) => {
      console.log(response);
      if (response.data.project.length == 0) {
        this.chart.dispose();
        return;
      }
      let projects = response['data']['project'];
      // console.log(projects);

      for (let i = 0; i < projects.length; i++) {
        let task = {
          id: projects[i]['id'].toString(),
          name: projects[i]['name'],
          // user: '<a href="https://images.pexels.com/photos/423364/pexels-photo-423364.jpeg?auto=compress&cs=tinysrgb&h=650&w=940" target="_blank" style="color:#0077c0;">Awesome!</a>',
          actualStart: projects[i]['default_baseline_project']['start'],
          actualEnd: projects[i]['default_baseline_project']['finish'],
          // duration: moment(projects[i]['finish']).diff(moment(projects[i]['start'])),
          // percent: 0,
          // type: "task"
          parent: projects[i]['default_baseline_project']['parent_id'],
        };

        // if (
        //   projects[i]["belongsTo"]["id"] !=
        //   response["data"]["data"]["baseline"]["belongsTo"]["id"]
        // ) {
        //   task["parent"] = projects[i]["belongsTo"]["id"].toString();
        // }

        // task['dependentOn'] = projects[i]['predecessorsIdFS']

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
