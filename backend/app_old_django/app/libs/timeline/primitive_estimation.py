# %% init
import pandas as pd
from time import time

import psycopg2
from sqlalchemy import create_engine

# class version seems to be significantly slower (or maybe not - to be confirmed)
class ProposeAssigment():

    def __init__(self, project_id, start, path='', host='database', user='ad', password='pass', database='pmt'):
        
        self.host = host
        self.user = user
        self.password = password
        self.database = database

        self.root_project_id = project_id
        self.start = start
        
        con = psycopg2.connect(host=host, user=user, password=password, database=database)

        cursor = con.cursor()
        # TODO those SQLs should be rewritten to python (DB should only provide significant data)
        cursor.execute(open(path + 'baseline/sql_queries/temp_projects_in_tree.sql', 'r').read().format(top_level_vertex_id=project_id)) # TODO create WBS in pandas
        cursor.execute(open(path + 'baseline/sql_queries/temp_timeline_dependence.sql', 'r').read())
        cursor.execute(open(path + 'pmt_calendar/sql_queries/calculate_availability.sql', 'r').read().format(start=str(start))) # TODO retrieve only assigned users

        cursor.execute(open(path + 'baseline/sql_queries/temp_lowest_level_dependencies.sql', 'r').read()) # TODO calculate in pandas

        self.projects = pd.read_sql('select * from projects_in_tree;', con)
        self.dependencies = pd.read_sql('select * from timeline_dependency;', con)
        self.av = pd.read_sql('select * from availability;', con)

        self.ld = pd.read_sql('select * from lowest_level_dependency;', con) # TODO calculate in pandas

        con.close()

        # self.validate_schema()

        self.lp = self.create_lowest_level_projects()
        self.lp['start'] = None
        self.lp['finish'] = None

        self.av['project_id'] = None


    def to_db(self, baseline_id):
        engine = create_engine('postgresql://' + self.user + ':' + self.password + '@' + self.host + ':5432/' + self.database)

        self.update_projects()
        self.projects['baseline_id'] = baseline_id
        self.projects['llp'] = False
        self.projects.llp.loc[self.projects.project_id.isin(self.lp.project_id)] = True
        self.projects.worktime_planned = self.projects.worktime_planned.astype(str) # TODO do we really need to convert?

        self.ld['baseline_id'] = baseline_id
        self.ld['llp'] = True
        self.ld.rename(columns={'dependence': 'timeline_dependency'}, inplace=True)

        self.dependencies['baseline_id'] = baseline_id
        self.dependencies['llp'] = False
        self.dependencies.rename(columns={'dependence': 'timeline_dependency'}, inplace=True)

        self.av = self.av[self.av.project_id.notnull()]
        self.av.drop(['id'], axis=1, inplace=True)
        self.av['baseline_id'] = baseline_id
        self.av['project_id'] = self.av.project_id.astype(int)

        self.projects.to_sql('baseline_project', engine, index=False, if_exists='append')
        self.ld.to_sql('baseline_projectdependency', engine, index=False, if_exists='append')
        self.dependencies.to_sql('baseline_projectdependency', engine, index=False, if_exists='append')
        self.av.to_sql('baseline_timeline', engine, index=False, if_exists='append')


    # def create_wbs(self): TODO

    def validate_schema(self):
        self.projects.astype(dtype={'project_id': 'int64', 'belongs_to': 'int64', 'worktime_planned': 'timedelta64', 'start': 'datetime64[ns]', 'finish': 'datetime64[ns]'})
        self.dependencies.astype(dtype={'project_id': 'int64', 'predecessor_id': 'int64', 'dependence': 'str'})
        self.av.astype(dtype={'user_id': 'int64', 'start': 'datetime64[ns]', 'finish': 'datetime64[ns]'})


    def create_lowest_level_projects(self):
        return self.projects[~self.projects.project_id.isin(self.projects.belongs_to)][['project_id', 'worktime_planned']]
        # self.projects.worktime_planned.loc[self.projects.project_id.isin(self.projects.belongs_to)] = None
        # self.projects.drop(['worktime_planned'], axis=1, inplace=True)


    # def create_lowest_level_dependencies(self):
    #     pass


    def update_projects(self):
        self.projects.drop(['start', 'finish', 'worktime_planned'], axis=1, inplace=True)
        self.projects = self.projects.merge(self.lp, how='left', on='project_id')
        while True:
            tmp = self.projects.groupby('belongs_to').count()
            tmp = tmp[tmp.project_id == tmp.worktime_planned]
            update = self.projects[self.projects.belongs_to.isin(tmp.index)].groupby('belongs_to').agg({'worktime_planned':'sum', 'start':'min', 'finish':'max'})

            if self.projects[self.projects.worktime_planned.isnull()].shape[0] == 0:
                return

            for index, row in update.iterrows():
                self.projects.loc[self.projects.project_id == index, 'worktime_planned'] = row.worktime_planned
                self.projects.loc[self.projects.project_id == index, 'start'] = row.start
                self.projects.loc[self.projects.project_id == index, 'finish'] = row.finish


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
            worktime = self.av.at[index, 'finish'] - self.av.at[index, 'start']
            self.av.at[index, 'project_id'] = self.lp.at[lp_index, 'project_id']
            if first == False:
                self.lp.at[lp_index, 'start'] = self.av.at[index, 'start']
                first = True
            if time_left == worktime:
                self.lp.at[lp_index, 'finish'] = self.av.at[index, 'finish']
                return
            elif time_left < worktime:
                new_row = self.av.loc[index]
                new_row['project_id'] = None
                self.av.at[index, 'finish'] -= time_left
                new_row['start'] = self.av.at[index, 'finish']
                self.av.loc[self.av.shape[0]] = new_row
                self.lp.at[lp_index, 'finish'] = self.av.at[index, 'finish']
                return
            time_left -= worktime
        raise Exception("No more available time in calendar.")


    def find_incorrect_dependencies_FS(self, partial_update = False):
        update = self.ld[self.ld.dependence == 'FS'].merge(self.lp, left_on='predecessor_id', right_on='project_id')[['project_id_x', 'finish']].groupby(['project_id_x']).max()
        update = update.merge(self.lp, left_on='project_id_x', right_on='project_id')
        update = update[update.start < update.finish_x]
        if partial_update == True:
            update = update[update.project_id.isin(self.projects[self.projects.finish.isnull()].project_id)]
        return update



    def fix_dependence_issues(self, partial_update = False, one_worker_per_project = False):
        number_of_fixes = 0
        while True: # fix dependency issue
            update = self.find_incorrect_dependencies_FS(partial_update=partial_update)

            if update.shape[0] == 0:
                return number_of_fixes

            self.unassign_project_from_workers(update.project_id.iat[0])
            self.assign_time_first_free(update.project_id.iat[0], update.finish_x.iat[0], one_worker_per_project=one_worker_per_project)
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
            
        number_of_fixes = self.fix_dependence_issues(one_worker_per_project=one_worker_per_project)
        print("Preliminary assignment quality: " + str(number_of_fixes))
        return self.lp.finish.max()


    def update_lp_based_on_projects(self):
        for index, row in self.lp.iterrows(): # TODO: find better way to update
            self.lp.loc[self.lp.project_id == row['project_id'], 'start'] = self.projects[self.projects.project_id == row['project_id']].start.iloc[0]
            self.lp.loc[self.lp.project_id == row['project_id'], 'finish'] = self.projects[self.projects.project_id == row['project_id']].finish.iloc[0]


    def assign_projects_by_start_based_on_infinite_resources(self, partial_update = False, partial_update_from = None, one_worker_per_project = False):
        if partial_update == True and partial_update_from is None:
            partial_update_from = pd.Timestamp.utcnow()

        self.assign_projects_infinite_resources(partial_update=partial_update, partial_update_from=partial_update_from)
        temp_df = self.lp.copy(deep=True)
        temp_df.sort_values(['start'], inplace=True)
        self.lp.start = None
        self.lp.finish = None
        self.update_lp_based_on_projects()

        for project_id in temp_df.project_id:
            if partial_update == True:
                if self.projects[self.projects.project_id == project_id].finish.iloc[0] is pd.NaT:
                    self.assign_time_first_free(project_id, one_worker_per_project=one_worker_per_project)
            else:
                self.assign_time_first_free(project_id, one_worker_per_project=one_worker_per_project)
            
        number_of_fixes = self.fix_dependence_issues(partial_update=partial_update, one_worker_per_project=one_worker_per_project)
        print("Preliminary assignment quality: " + str(number_of_fixes))
        return self.lp.finish.max()


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



    def assign_projects_to_resources_from_path_start(self, one_worker_per_project = False):
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
        return self.lp.finish.max()



    def assign_projects_infinite_resources(self, partial_update = False, partial_update_from = None):
        if partial_update == True:
            if partial_update_from is None:
                partial_update_from = pd.Timestamp.utcnow()
            self.update_lp_based_on_projects()
            self.lp.start[self.lp.start.isnull()] = partial_update_from
            self.lp.finish = self.lp.apply(lambda row: (row['start'] + row['worktime_planned']) if row['finish'] is pd.NaT else row['finish'], axis=1)
        else:
            self.lp['start'] = self.start
            self.lp['finish'] = self.lp['start'] + self.lp['worktime_planned']

        while True:
            update = self.find_incorrect_dependencies_FS()
            #1 update = update[['project_id', 'worktime_planned', 'finish_x']].rename(columns={'finish_x': 'start'})
            #1 update['finish'] = update.start + update.worktime_planned
            
            if update.shape[0] == 0:
                return self.lp.finish.max()

            #1 self.lp = pd.concat([self.lp[~self.lp.project_id.isin(update.project_id)], update], ignore_index=True)
            
            for index, row in update.iterrows(): # TODO: find better way to update
                self.lp.loc[self.lp.project_id == row['project_id'], 'start'] = row.finish_x
                self.lp.loc[self.lp.project_id == row['project_id'], 'finish'] = row.finish_x + row.worktime_planned

            
        



# proposal = ProposeAssigment(project_id=56, start=pd.Timestamp('2020-02-01', tz='UTC'), host='localhost', path='../../')
# algo_time_start = time()

# # finish_date = proposal.assign_projects_infinite_resources()
# # finish_date = proposal.assign_projects_infinite_resources(partial_update=True, partial_update_from=pd.Timestamp('2021-01-01', tz='UTC'))
# # finish_date = proposal.assign_projects_by_start_based_on_infinite_resources(one_worker_per_project=True)
# finish_date = proposal.assign_projects_by_start_based_on_infinite_resources(partial_update=True, partial_update_from=pd.Timestamp('2021-01-01', tz='UTC'), one_worker_per_project=True)

# # # not so good methods (probably some logic has to be reviewed):
# # finish_date = proposal.assign_projects_to_resources_first_free(one_worker_per_project=True)
# # finish_date = proposal.assign_projects_to_resources_from_longest_path(one_worker_per_project=False)
# # finish_date = proposal.assign_projects_to_resources_from_path_start(one_worker_per_project=True)

# algo_time_finish = time()

# # proposal.update_projects()
# print('Project finish timestamp: ' + str(finish_date))
# print('Calculation time [s]: ' + str(algo_time_finish - algo_time_start))
# print('Unassigned workers time during project: ' + str((proposal.av[proposal.av.project_id.isnull() & (proposal.av.start <= finish_date)].finish - proposal.av[proposal.av.project_id.isnull() & (proposal.av.start <= finish_date)].start).sum()))
# # proposal.av[proposal.av.project_id.isnull() & (proposal.av.start <= finish_date)].sort_values('start')



# %%





