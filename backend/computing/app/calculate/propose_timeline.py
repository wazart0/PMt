import pandas as pd

from libs.db_access.pg_connect import PGconnection
from libs.algorithms.primitive_estimation import ProposeAssigment



class ProposeTimeline():

    def __init__(self, root_project_id, start, solver = None):

        self.db = PGconnection(host='database', user='ad', password='pass', database='pmt')

        self.root_project_id = root_project_id
        self.start = start
        

    def basic_solver(self):

        baseline_id = None # TODO must have
        partial_update = False
        partial_update_from = '' # some date for partial update

        solver = ProposeAssigment()



        # Get data from DB
        path = './calculate/sql/'
        cursor = db.connect()

        # TODO those SQLs should be rewritten to python (DB should only provide significant data)
        cursor.execute(open(path + 'temp_projects_in_tree.sql', 'r').read().format(top_level_vertex_id=self.root_project_id)) # TODO create WBS in pandas
        cursor.execute(open(path + 'temp_timeline_dependence.sql', 'r').read())
        cursor.execute(open(path + 'calculate_availability.sql', 'r').read().format(start=str(self.start))) # TODO retrieve only assigned users

        cursor.execute(open(path + 'temp_lowest_level_dependencies.sql', 'r').read()) # TODO calculate in pandas

        solver.projects = pd.read_sql('select * from projects_in_tree;', self.db.con)
        solver.dependencies = pd.read_sql('select * from timeline_dependency;', self.db.con)
        solver.av = pd.read_sql('select * from availability;', self.db.con)

        solver.ld = pd.read_sql('select * from lowest_level_dependency;', self.db.con) # TODO calculate in pandas

        db.disconnect()



        # Calculation part

        solver.initialize()

        from time import time
        algo_time_start = time()
        # finish_date = solver.assign_projects_infinite_resources(baseline.start)
        # finish_date = solver.assign_projects_to_resources_first_free(one_worker_per_project=True)
        # finish_date = solver.assign_projects_by_start_based_on_infinite_resources(one_worker_per_project=True)
        finish_date = solver.assign_projects_by_start_based_on_infinite_resources(partial_update=partial_update, partial_update_from=partial_update_from, one_worker_per_project=True)
        algo_time_finish = time()

        print('Project finish timestamp: ' + str(finish_date))
        print('Calculation time [s]: ' + str(algo_time_finish - algo_time_start))
        print('Unassigned workers time during project: ' + str((solver.av[solver.av.project_id.isnull() & (solver.av.start <= finish_date)].finish - solver.av[solver.av.project_id.isnull() & (solver.av.start <= finish_date)].start).sum()))



        # adjust data to DB

        solver.update_projects()
        solver.projects['baseline_id'] = baseline_id
        solver.projects['llp'] = False
        solver.projects.llp.loc[solver.projects.project_id.isin(solver.lp.project_id)] = True
        solver.projects.worktime_planned = solver.projects.worktime_planned.astype(str) # TODO do we really need to convert?

        solver.ld['baseline_id'] = baseline_id
        solver.ld['llp'] = True
        solver.ld.rename(columns={'dependence': 'timeline_dependency'}, inplace=True)

        solver.dependencies['baseline_id'] = baseline_id
        solver.dependencies['llp'] = False
        solver.dependencies.rename(columns={'dependence': 'timeline_dependency'}, inplace=True)

        solver.av = solver.av[solver.av.project_id.notnull()]
        solver.av.drop(['id'], axis=1, inplace=True)
        solver.av['baseline_id'] = baseline_id
        solver.av['project_id'] = solver.av.project_id.astype(int)



        # insert or update data in DB

        engine = self.db.get_engine()

        # solver.projects.to_sql('baseline_project', engine, index=False, if_exists='append')
        # solver.av.to_sql('baseline_timeline', engine, index=False, if_exists='append')
        # # dependencies probably not needed in new version
        # solver.ld.to_sql('baseline_projectdependency', engine, index=False, if_exists='append')
        # solver.dependencies.to_sql('baseline_projectdependency', engine, index=False, if_exists='append')




