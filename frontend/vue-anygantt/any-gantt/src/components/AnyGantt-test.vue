<template>
	<div id="container" style="width: 1400px; height: 700px;"></div>
</template>

<script>
import anychart from 'anychart';
// import axios from 'axios';
export default {
	name: 'AnyGantt_test',
	mounted: function() {
		this.gantt();
	},
	methods: {
		// Declares the method
		gantt: function() {
			// create data
			var data = [
				{
					id: "1",
					name: "Development",
					baselineStart: "2018-01-12",
					baselineEnd: "2018-03-04",
					actualStart: "2018-01-15",
					actualEnd: "2018-03-10",
					children: [
						{
							id: "1_1",
							name: "Analysis",
							baselineStart: "2018-01-12",
							baselineEnd: "2018-01-25",
							// actualStart: "2018-01-15",
							// actualEnd: "2018-01-25"
						},
						{
							id: "1_2",
							name: "Design",
							// baselineStart: "2018-01-20",
							// baselineEnd: "2018-01-31",
							actualStart: "2018-01-20",
							actualEnd: "2018-02-04"
						},
						{
							id: "1_3",
							name: "Meeting",
							actualStart: "2018-02-05",
							actualEnd: "2018-02-05"
						},
						{
							id: "1_4",
							name: "Implementation",
							// baselineStart: "2018-02-01",
							// baselineEnd: "2018-02-19",
							// actualStart: "2018-02-05",
							// actualEnd: "2018-02-24"
						},
						{
							id: "1_5",
							name: "Testing",
							// baselineStart: "2018-02-20",
							// baselineEnd: "2018-03-05",
							actualStart: "2018-02-25",
							actualEnd: "2018-03-10"
						},
						{
							id: "1_6",
							name: "small task",
							// baselineStart: "2018-02-20",
							// baselineEnd: "2018-03-05",
							actualStart: "2018-01-20T08:00",
							actualEnd: "2018-01-20T16:00"
						}
					]
				}
			];


			// create a data tree
			var treeData = anychart.data.tree(data, 'as-tree');
			// create a chart
			var chart = anychart.ganttProject();
			// set the data
			chart.data(treeData);
			// set the container id
			chart.container('container');
			// initiate drawing the chart
			chart.draw();
			// fit elements to the width of the timeline
			chart.fitAll();
			// chart.fitToTask("1_6")
		},
	},
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss"></style>
