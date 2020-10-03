<template>
  <div>
    <div id="container" style="width: 1600px; height: 700px;"></div>
    <button @click="exportChart">export</button>
  </div>
</template>

<script>
import anychart from "anychart";
import axios from "axios";
export default {
  name: "AnyGantt",
  mounted: function () {
    this.gantt();
  },
  data() {
    return {
      chart: "abc",
    };
  },
  methods: {
    exportChart() {
      this.chart.saveAsPng();
    },
    // Declares the method
    gantt() {
      // create data

      let url = "http://51.83.129.102:8000/graphql/";
      // let url = 'http://localhost:8000/graphql/';
      // let url = 'http://backend:8000/graphql/';

      var data = [];
      // var vm = this;
      axios
        .post(url, {
          query: `
						{
							baseline (id:110) {
							id
							name
							belongsTo {
								id
							}
							projects {
								wbs
								project {
								id
								name
								}
								start
								finish
								belongsTo {
								id
								}
								predecessorsIdFS
							}
							}
						}
						`,
        })
        .then((response) => {
          let projects = response["data"]["data"]["baseline"]["projects"];
          // console.log(projects);

          for (let i = 0; i < projects.length; i++) {
            let task = {
              id: projects[i]["project"]["id"].toString(),
              name: projects[i]["project"]["name"],
              // user: '<a href="https://images.pexels.com/photos/423364/pexels-photo-423364.jpeg?auto=compress&cs=tinysrgb&h=650&w=940" target="_blank" style="color:#0077c0;">Awesome!</a>',
              actualStart: projects[i]["start"],
              actualEnd: projects[i]["finish"],
              // duration: moment(projects[i]['finish']).diff(moment(projects[i]['start'])),
              // percent: 0,
              // type: "task"
            };

            if (
              projects[i]["belongsTo"]["id"] !=
              response["data"]["data"]["baseline"]["belongsTo"]["id"]
            ) {
              task["parent"] = projects[i]["belongsTo"]["id"].toString();
            }

            // task['dependentOn'] = projects[i]['predecessorsIdFS']

            data.push(task);
          }

          // create a data tree
          var treeData = anychart.data.tree(data, "as-tree");
          // create a chart
          var chart = anychart.ganttProject();
          this.chart = chart;
          // set the data
          this.chart.data(treeData);
          // set the container id
          this.chart.container("container");
          // initiate drawing the chart
          this.chart.draw();
          // fit elements to the width of the timeline
          this.chart.fitAll();
        });
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss"></style>
