from flask import Flask
from flask import request
from calculate.propose_timeline import ProposeTimeline


app = Flask(__name__)


@app.route('/health/')
def health():
    return 'OK'


@app.route('/propose_timeline/')
def propose_timeline():
    project_id = request.args.get('project_id')
    start_date = request.args.get('start_date')
    baseline_id = request.args.get('baseline_id')
    source_baseline_id = request.args.get('source_baseline_id') # TODO for now default baseline
    timeline = ProposeTimeline()
    baseline_id = timeline.basic_solver(project_id, start_date, baseline_id, source_baseline_id)
    return str(project_id) + ', ' + str(baseline_id) + ', ' + str(start_date)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


