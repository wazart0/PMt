# %% init
import pandas as pd
from time import time

import psycopg2
from sqlalchemy import create_engine

# class version seems to be significantly slower (or maybe not - to be confirmed)
class ProposeAssigment():

    def __init__(self, project_id, host='database', path=''):
        con = psycopg2.connect(host=host, user='ad', password='pass', database='pmt')

        # TODO those SQLs should be rewritten to python (DB should only provide significant data)
        cursor = con.cursor()
        cursor.execute(open(path + 'baseline/sql_queries/temp_projects_in_tree.sql', 'r').read().format(top_level_node_id=project_id))
        self.av = pd.read_sql(open(path + 'pmt_calendar/sql_queries/calculate_availability.sql', 'r').read(), con)
        self.lp = pd.read_sql(open(path + 'baseline/sql_queries/temp_lowest_level_projects.sql', 'r').read() + 'select * from lowest_level_projects;', con)
        self.ld = pd.read_sql(open(path + 'baseline/sql_queries/temp_lowest_level_dependencies.sql', 'r').read() + 'select * from lowest_level_dependency;', con)

        con.close()

        self.lp['begin'] = None
        self.lp['end'] = None

        self.av['project_id'] = None


    def to_db(self, baseline_id):
        # con = psycopg2.connect(host='database', user='ad', password='pass', database='pmt')

        engine = create_engine('postgresql://ad:pass@database:5432/pmt')

        self.ld['baseline_id'] = baseline_id
        self.av['baseline_id'] = baseline_id

        self.ld.rename(columns={'dependence': 'timeline_dependency'}, inplace=True)

        self.av.rename(columns={'start': 'begin'}, inplace=True)
        self.av.drop(['id'], axis=1, inplace=True)
        self.av = self.av[self.av.project_id.notnull()]
        self.av['project_id'] = self.av.project_id.astype(int)

        self.ld.to_sql('baseline_projectdependency', engine, index=False, if_exists='append')
        self.av.to_sql('baseline_timeline', engine, index=False, if_exists='append')

        # con.close()


    def unassign_project_from_workers(self, project_id):
        self.av.project_id.loc[(self.av.project_id == project_id)] = None


    def assign_time_first_free(self, project_id, from_date = None, assignee = None, one_worker_per_project = False):
        lp_index = self.lp[self.lp.project_id == project_id].index[0]
        if from_date is None:
            from_date = self.av.start.min()
        if assignee is None:
            assignee = self.av.user_id.unique()
        if one_worker_per_project:
            assignee = [self.av[self.av.user_id.isin(assignee) & self.av.project_id.isnull() & (from_date <= self.av.start)].sort_values(['start']).user_id.iat[0]]
            # print(assignee)
        time_left = self.lp.at[lp_index, 'worktime_planned']
        first = False
        for index in self.av[self.av.user_id.isin(assignee) & self.av.project_id.isnull() & (from_date <= self.av.start)].sort_values(['start']).index:
            worktime = self.av.at[index, 'end'] - self.av.at[index, 'start']
            self.av.at[index, 'project_id'] = self.lp.at[lp_index, 'project_id']
            if first == False:
                self.lp.at[lp_index, 'start'] = self.av.at[index, 'start']
                first = True
            if time_left == worktime:
                self.lp.at[lp_index, 'end'] = self.av.at[index, 'end']
                return
            elif time_left < worktime:
                new_row = self.av.loc[index]
                new_row['project_id'] = None
                self.av.at[index, 'end'] -= time_left
                new_row['start'] = self.av.at[index, 'end']
                self.av.loc[self.av.shape[0]] = new_row
                self.lp.at[lp_index, 'end'] = self.av.at[index, 'end']
                return
            time_left -= worktime
        raise Exception("No more available time in calendar.")


    def fix_dependence_issues(self, one_worker_per_project = False):
        number_of_fixes = 0
        while True: # fix dependency issue
            update = self.ld[self.ld.dependence == 'FS'].merge(self.lp, left_on='predecessor_id', right_on='project_id')[['project_id_x', 'end']].groupby(['project_id_x']).max()
            update = update.merge(self.lp, left_on='project_id_x', right_on='project_id')
            update = update[update.start < update.end_x]

            if update.shape[0] == 0:
                return number_of_fixes

            self.unassign_project_from_workers(update.project_id.iat[0])
            self.assign_time_first_free(update.project_id.iat[0], update.end_x.iat[0], one_worker_per_project=one_worker_per_project)
            number_of_fixes += 1


    def create_dependency_paths(self):
        # buiself.ld dependency paths
        paths = [[i] for i in list(self.lp.project_id[~self.lp.project_id.isin(self.ld.project_id)])] # roots
        number_of_new_paths = len(paths)
        while number_of_new_paths:
            new_paths = []
            for path in paths[-number_of_new_paths:]:
                successors = list(self.ld[(self.ld.predecessor_id == path[-1])].project_id)
                for successor in successors:
                    new_path = path.copy()
                    new_path.append(successor)
                    new_paths.append(new_path)
            number_of_new_paths = len(new_paths)
            paths += new_paths
        return paths


    def assign_projects_to_resources_no_dependence(self, one_worker_per_project = False):
        for project_id in self.lp.project_id: # assign first availble time to project
            self.assign_time_first_free(project_id, one_worker_per_project=one_worker_per_project)


    def assign_projects_to_resources_first_free(self, one_worker_per_project = False):
        for project_id in self.lp.project_id: # assign first availble time to project
            self.assign_time_first_free(project_id, one_worker_per_project=one_worker_per_project)
            
        # print("Start fixing...")
        number_of_fixes = self.fix_dependence_issues(one_worker_per_project=one_worker_per_project)
        print("Preliminary assignment quality: " + str(number_of_fixes))
        return self.lp.end.max()



    def assign_projects_to_resources_from_longest_path(self, one_worker_per_project = False):

        paths = self.create_dependency_paths()

        for path in paths:
            path.append(self.lp[self.lp.project_id.isin(path)].worktime_planned.sum())
        paths = sorted(paths, key=lambda path: path[-1], reverse=True)

        for path in paths:
            for project_id in path[:-1]:
                if self.av[(self.av.project_id == project_id)].shape[0] == 0:
                    self.assign_time_first_free(project_id, one_worker_per_project=one_worker_per_project)
                    # print('Project ' + str(project_id) + ' assigned.')
            # print(path)
            # break

        # print("Start fixing...")
            number_of_fixes = self.fix_dependence_issues(one_worker_per_project=one_worker_per_project)
            # print("Preliminary assignment quality (bigger -> worser): " + str(number_of_fixes))
        return self.lp[self.lp.end.notnull()].end.max()



    def assign_projects_to_resources_from_path_begin(self, one_worker_per_project = False):

        paths = self.create_dependency_paths()

        print('Assigning projects...')

        level = 0
        while True:
            projects_on_level = list(set([(i[level] if (len(i) > level) else None) for i in paths]))
            if (len(projects_on_level) <= 1) and (projects_on_level[0] is None):
                break
            # print(projects_on_level)
            for project_id in projects_on_level:
                if (self.av[(self.av.project_id == project_id)].shape[0] == 0) and (project_id is not None):
                    self.assign_time_first_free(project_id, one_worker_per_project=one_worker_per_project)
                    # print('Project ' + str(project_id) + ' assigned.')
            level += 1

        print('Unassigned projects: ' + str(self.lp[~self.lp.project_id.isin(self.av.project_id)].shape[0]))

        # print("Start fixing...")
        number_of_fixes = self.fix_dependence_issues(one_worker_per_project=one_worker_per_project)
        print("Preliminary assignment quality (bigger -> worser): " + str(number_of_fixes))
        return self.lp.end.max()



    def assign_projects_infinite_resources(self, start_date):
        self.lp['start'] = pd.Timestamp(start_date, tz='UTC')
        self.lp['end'] = self.lp['start'] + self.lp['worktime_planned']
        while True:
            update = self.ld[self.ld.dependence == 'FS'].merge(self.lp, left_on='predecessor_id', right_on='project_id')[['project_id_x', 'end']].groupby(['project_id_x']).max()
            update = update.merge(self.lp, left_on='project_id_x', right_on='project_id')
            update = update[update.start < update.end_x][['project_id', 'worktime_planned', 'end_x']].rename(columns={'end_x': 'start'})
            update['end'] = update.start + update.worktime_planned
            
            if update.shape[0] == 0:
                return self.lp.end.max()

            self.lp = pd.concat([self.lp[~self.lp.project_id.isin(update.project_id)], update], ignore_index=True)
            
        



# def generate_timeline(project_id):
# proposal = ProposeAssigment(project_id=55, host='localhost', path='../../')


# algo_time_start = time()

# finish_date = proposal.assign_projects_to_resources_first_free(one_worker_per_project=True)
# # finish_date = proposal.assign_projects_to_resources_from_longest_path(one_worker_per_project=False)
# # finish_date = proposal.assign_projects_to_resources_from_path_begin(one_worker_per_project=True)

# algo_time_end = time()

# print('Project finish timestamp: ' + str(finish_date))
# print('Calculation time [s]: ' + str(algo_time_end - algo_time_start))
# print('Unassigned workers time during project: ' + str((proposal.av[proposal.av.project_id.isnull() & (proposal.av.start <= finish_date)].end - proposal.av[proposal.av.project_id.isnull() & (proposal.av.start <= finish_date)].start).sum()))
# # proposal.av[proposal.av.project_id.isnull() & (proposal.av.start <= finish_date)].sort_values('start')


# generate_timeline(project_id)


# %%





