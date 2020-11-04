from flask import Flask
from flask import request
from calculate.propose_timeline import ProposeTimeline
import dateutil.parser



app = Flask(__name__)


@app.route('/health/')
def health():
	return 'OK'


@app.route('/generate_baseline_proposal/', methods=['POST'])
def generate_baseline_proposalHandler():
	project_id = request.get_json().get('input').get('project_id')
	start_date = request.get_json().get('input').get('start_date')
	baseline_id = request.get_json().get('input').get('baseline_id')
	source_baseline_id = request.get_json().get('input').get('source_baseline_id') # TODO for now default baseline

	start_date = dateutil.parser.parse(start_date)
	timeline = ProposeTimeline()
	baseline_id = timeline.basic_solver(project_id, start_date, baseline_id, source_baseline_id)
	return '{  "baseline_id": "' + baseline_id + '" }'



if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0')


