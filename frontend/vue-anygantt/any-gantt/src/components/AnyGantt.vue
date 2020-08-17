<template>
	<div id="container" style="width: 1600px; height: 700px;"></div>
</template>

<script>
import anychart from 'anychart';
export default {
	name: 'AnyGantt',
	mounted: function() {
		this.gantt();
	},
	methods: {
		// Declares the method
		gantt: function() {
			// create data
			var data = [
				{
					id: '1',
					name: 'Development1',
					actualStart: '2018-01-15',
					actualEnd: '2018-03-10',
					children: [
						{
							id: '1_1',
							name: 'Analysis',
							actualStart: '2018-01-15',
							actualEnd: '2018-01-25',
						},
						{
							id: '1_2',
							name: 'Design',
							actualStart: '2018-01-20',
							actualEnd: '2018-02-04',
						},
						{
							id: '1_3',
							name: 'Meeting',
							actualStart: '2018-02-05',
							actualEnd: '2018-02-05',
						},
						{
							id: '1_4',
							name: 'Implementation',
							actualStart: '2018-02-05',
							actualEnd: '2018-02-24',
						},
						{
							id: '1_5',
							name: 'Testing',
							actualStart: '2018-02-25',
							actualEnd: '2018-03-10',
						},
					],
				},
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
		},
	},
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss"></style>
