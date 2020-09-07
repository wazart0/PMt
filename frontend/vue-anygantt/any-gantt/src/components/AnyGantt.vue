<template>
	<div id="container" style="width: 1600px; height: 700px;"></div>
</template>

<script>
import anychart from 'anychart';
import axios from 'axios';
export default {
	name: 'AnyGantt',
	mounted: function() {
		this.gantt();
	},
	methods: {
		// Declares the method
		gantt: function() {
			// create data
			// var data = [
			// 	{
			// 		id: '1',
			// 		name: 'Development1',
			// 		actualStart: '2018-01-15',
			// 		actualEnd: '2018-03-10',
			// 		children: [
			// 			{
			// 				id: '1_1',
			// 				name: 'Analysis',
			// 				actualStart: '2018-01-15',
			// 				actualEnd: '2018-01-25',
			// 			},
			// 			{
			// 				id: '1_2',
			// 				name: 'Design',
			// 				actualStart: '2018-01-20',
			// 				actualEnd: '2018-02-04',
			// 			},
			// 			{
			// 				id: '1_3',
			// 				name: 'Meeting',
			// 				actualStart: '2018-02-05',
			// 				actualEnd: '2018-02-05',
			// 			},
			// 			{
			// 				id: '1_4',
			// 				name: 'Implementation',
			// 				actualStart: '2018-02-05',
			// 				actualEnd: '2018-02-24',
			// 			},
			// 			{
			// 				id: '1_5',
			// 				name: 'Testing',
			// 				actualStart: '2018-02-25',
			// 				actualEnd: '2018-03-10',
			// 			},
			// 		],
			// 	},
			// ];

			// let url = 'http://51.83.129.102:8000/graphql/';
			let url = 'http://51.83.129.102:8000/graphql/';
			var data = [];
			// let url = 'http://backend:8000/graphql/';
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
					let projects = response['data']['data']['baseline']['projects'];
					console.log(projects);

					for (let i = 0; i < projects.length; i++) {
						let task = {
							id: projects[i]['project']['id'].toString(),
							name: projects[i]['project']['name'],
							// user: '<a href="https://images.pexels.com/photos/423364/pexels-photo-423364.jpeg?auto=compress&cs=tinysrgb&h=650&w=940" target="_blank" style="color:#0077c0;">Awesome!</a>',
							actualStart: projects[i]['start'],
							actualEnd: projects[i]['finish'],
							// duration: moment(projects[i]['finish']).diff(moment(projects[i]['start'])),
							// percent: 0,
							// type: "task"
						};

						if (projects[i]['belongsTo']['id'] != response['data']['data']['baseline']['belongsTo']['id']) {
							task['parent'] = projects[i]['belongsTo']['id'].toString();
						}

						// task['dependentOn'] = projects[i]['predecessorsIdFS']

						data.push(task);
					}

					console.log(data);

					// create a data tree
					var treeData = anychart.data.tree(data, 'as-table');
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
				});
		},
	},
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss"></style>
