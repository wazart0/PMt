# %% init
import pandas as pd
from time import time

import psycopg2
from sqlalchemy import create_engine

# class version seems to be significantly slower (or maybe not - to be confirmed)
class ProposeAssigment():

    def __init__(self, project, path='', host='database', user='ad', password='pass', database='pmt'):
        
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        
        con = psycopg2.connect(host=host, user=user, password=password, database=database)

        # TODO those SQLs should be rewritten to python (DB should only provide significant data)
        cursor = con.cursor()
        cursor.execute(open(path + 'baseline/sql_queries/temp_projects_in_tree.sql', 'r').read().format(top_level_node=project))
        cursor.execute(open(path + 'pmt_calendar/sql_queries/calculate_availability.sql', 'r').read())
        cursor.execute(open(path + 'baseline/sql_queries/temp_lowest_level_projects.sql', 'r').read())
        cursor.execute(open(path + 'baseline/sql_queries/temp_lowest_level_dependencies.sql', 'r').read())

        self.projects = pd.read_sql('select * from projects_in_tree;', con)
        self.av = pd.read_sql('select * from availability;', con)
        self.lp = pd.read_sql('select * from lowest_level_projects;', con)
        self.ld = pd.read_sql('select * from lowest_level_dependency;', con)

        con.close()

        self.lp['start'] = None
        self.lp['finish'] = None

        self.av['project'] = None


    def to_db(self, baseline):
        # con = psycopg2.connect(host='database', user='ad', password='pass', database='pmt')
        engine = create_engine('postgresql://' + self.user + ':' + self.password + '@' + self.host + ':5432/' + self.database)

        self.update_projects()

        self.ld['baseline'] = baseline
        self.av['baseline'] = baseline
        self.projects['baseline'] = baseline

        self.ld.rename(columns={'dependence': 'timeline_dependency'}, inplace=True)

        self.av.drop(['id'], axis=1, inplace=True)
        self.av = self.av[self.av.project.notnull()]
        self.av['project'] = self.av.project.astype(int)

        self.projects.worktime_planned = self.projects.worktime_planned.astype(str) # TODO do we really need to convert?

        self.projects.to_sql('baseline_project', engine, index=False, if_exists='append')
        self.ld.to_sql('baseline_projectdependency', engine, index=False, if_exists='append')
        self.av.to_sql('baseline_timeline', engine, index=False, if_exists='append')

        # con.close()


    def update_projects(self):
        self.projects = self.projects.merge(self.lp, how='left', on='project')
        while True:
            tmp = self.projects.groupby('belongs_to').count()
            tmp = tmp[tmp.project == tmp.worktime_planned]
            update = self.projects[self.projects.belongs_to.isin(tmp.index)].groupby('belongs_to').agg({'worktime_planned':'sum', 'start':'min', 'finish':'max'})
            if self.projects[self.projects.worktime_planned.isnull()].shape[0] == 0:
                return
            for index, row in update.iterrows():
                self.projects.loc[self.projects.project == index, 'worktime_planned'] = row.worktime_planned
                self.projects.loc[self.projects.project == index, 'start'] = row.start
                self.projects.loc[self.projects.project == index, 'finish'] = row.finish


    def unassign_project_from_workers(self, project):
        self.av.project.loc[(self.av.project == project)] = None


    def assign_time_first_free(self, project, from_date = None, assignee = None, one_worker_per_project = False):
        lp_index = self.lp[self.lp.project == project].index[0]
        if from_date is None:
            from_date = self.av.start.min()
        if assignee is None:
            assignee = self.av.user.unique()
        if one_worker_per_project:
            assignee = [self.av[self.av.user.isin(assignee) & self.av.project.isnull() & (from_date <= self.av.start)].sort_values(['start']).user.iat[0]]
            # print(assignee)
        time_left = self.lp.at[lp_index, 'worktime_planned']
        first = False
        for index in self.av[self.av.user.isin(assignee) & self.av.project.isnull() & (from_date <= self.av.start)].sort_values(['start']).index:
            worktime = self.av.at[index, 'finish'] - self.av.at[index, 'start']
            self.av.at[index, 'project'] = self.lp.at[lp_index, 'project']
            if first == False:
                self.lp.at[lp_index, 'start'] = self.av.at[index, 'start']
                first = True
            if time_left == worktime:
                self.lp.at[lp_index, 'finish'] = self.av.at[index, 'finish']
                return
            elif time_left < worktime:
                new_row = self.av.loc[index]
                new_row['project'] = None
                self.av.at[index, 'finish'] -= time_left
                new_row['start'] = self.av.at[index, 'finish']
                self.av.loc[self.av.shape[0]] = new_row
                self.lp.at[lp_index, 'finish'] = self.av.at[index, 'finish']
                return
            time_left -= worktime
        raise Exception("No more available time in calendar.")


    def fix_dependence_issues(self, one_worker_per_project = False):
        number_of_fixes = 0
        while True: # fix dependency issue
            update = self.ld[self.ld.dependence == 'FS'].merge(self.lp, left_on='predecessor', right_on='project')[['project_x', 'finish']].groupby(['project_x']).max()
            update = update.merge(self.lp, left_on='project_x', right_on='project')
            update = update[update.start < update.finish_x]

            if update.shape[0] == 0:
                return number_of_fixes

            self.unassign_project_from_workers(update.project.iat[0])
            self.assign_time_first_free(update.project.iat[0], update.finish_x.iat[0], one_worker_per_project=one_worker_per_project)
            number_of_fixes += 1


    def create_dependency_paths(self):
        # buiself.ld dependency paths
        paths = [[i] for i in list(self.lp.project[~self.lp.project.isin(self.ld.project)])] # roots
        number_of_new_paths = len(paths)
        while number_of_new_paths:
            new_paths = []
            for path in paths[-number_of_new_paths:]:
                successors = list(self.ld[(self.ld.predecessor == path[-1])].project)
                for successor in successors:
                    new_path = path.copy()
                    new_path.append(successor)
                    new_paths.append(new_path)
            number_of_new_paths = len(new_paths)
            paths += new_paths
        return paths


    def assign_projects_to_resources_no_dependence(self, one_worker_per_project = False):
        for project in self.lp.project: # assign first availble time to project
            self.assign_time_first_free(project, one_worker_per_project=one_worker_per_project)


    def assign_projects_to_resources_first_free(self, one_worker_per_project = False):
        for project in self.lp.project: # assign first availble time to project
            self.assign_time_first_free(project, one_worker_per_project=one_worker_per_project)
            
        # print("Start fixing...")
        number_of_fixes = self.fix_dependence_issues(one_worker_per_project=one_worker_per_project)
        print("Preliminary assignment quality: " + str(number_of_fixes))
        return self.lp.finish.max()



    def assign_projects_to_resources_from_longest_path(self, one_worker_per_project = False):

        paths = self.create_dependency_paths()

        for path in paths:
            path.append(self.lp[self.lp.project.isin(path)].worktime_planned.sum())
        paths = sorted(paths, key=lambda path: path[-1], reverse=True)

        for path in paths:
            for project in path[:-1]:
                if self.av[(self.av.project == project)].shape[0] == 0:
                    self.assign_time_first_free(project, one_worker_per_project=one_worker_per_project)
                    # print('Project ' + str(project) + ' assigned.')
            # print(path)
            # break

        # print("Start fixing...")
            number_of_fixes = self.fix_dependence_issues(one_worker_per_project=one_worker_per_project)
            # print("Preliminary assignment quality (bigger -> worser): " + str(number_of_fixes))
        return self.lp[self.lp.end.notnull()].end.max()



    def assign_projects_to_resources_from_path_start(self, one_worker_per_project = False):

        paths = self.create_dependency_paths()

        print('Assigning projects...')

        level = 0
        while True:
            projects_on_level = list(set([(i[level] if (len(i) > level) else None) for i in paths]))
            if (len(projects_on_level) <= 1) and (projects_on_level[0] is None):
                break
            # print(projects_on_level)
            for project in projects_on_level:
                if (self.av[(self.av.project == project)].shape[0] == 0) and (project is not None):
                    self.assign_time_first_free(project, one_worker_per_project=one_worker_per_project)
                    # print('Project ' + str(project) + ' assigned.')
            level += 1

        print('Unassigned projects: ' + str(self.lp[~self.lp.project.isin(self.av.project)].shape[0]))

        # print("Start fixing...")
        number_of_fixes = self.fix_dependence_issues(one_worker_per_project=one_worker_per_project)
        print("Preliminary assignment quality (bigger -> worser): " + str(number_of_fixes))
        return self.lp.finish.max()



    def assign_projects_infinite_resources(self, start_date):
        self.lp['start'] = pd.Timestamp(start_date, tz='UTC')
        self.lp['finish'] = self.lp['start'] + self.lp['worktime_planned']
        while True:
            update = self.ld[self.ld.dependence == 'FS'].merge(self.lp, left_on='predecessor', right_on='project')[['project_x', 'finish']].groupby(['project_x']).max()
            update = update.merge(self.lp, left_on='project_x', right_on='project')
            update = update[update.start < update.finish_x][['project', 'worktime_planned', 'finish_x']].rename(columns={'finish_x': 'start'})
            update['finish'] = update.start + update.worktime_planned
            
            if update.shape[0] == 0:
                return self.lp.finish.max()

            self.lp = pd.concat([self.lp[~self.lp.project.isin(update.project)], update], ignore_index=True)
            
        



# proposal = ProposeAssigment(project=55, host='localhost', path='../../')
# algo_time_start = time()

# finish_date = proposal.assign_projects_to_resources_first_free(one_worker_per_project=True)
# # finish_date = proposal.assign_projects_to_resources_from_longest_path(one_worker_per_project=False)
# # finish_date = proposal.assign_projects_to_resources_from_path_start(one_worker_per_project=True)

# algo_time_finish = time()

# # proposal.update_projects()
# print('Project finish timestamp: ' + str(finish_date))
# print('Calculation time [s]: ' + str(algo_time_finish - algo_time_start))
# print('Unassigned workers time during project: ' + str((proposal.av[proposal.av.project.isnull() & (proposal.av.start <= finish_date)].finish - proposal.av[proposal.av.project.isnull() & (proposal.av.start <= finish_date)].start).sum()))
# # proposal.av[proposal.av.project.isnull() & (proposal.av.start <= finish_date)].sort_values('start')



# %%





