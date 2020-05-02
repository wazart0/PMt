# %% init
import pandas as pd
from time import time

import psycopg2
con = psycopg2.connect(user='ad', password='pass', database='pmt')

av = pd.read_sql(open('../../pmt_calendar/sql_queries/calculate_availability.sql', 'r').read(), con)
lp = pd.read_sql(open('../../baseline/sql_queries/temp_lowest_level_projects.sql', 'r').read() + 'select * from lowest_level_projects;', con)
ld = pd.read_sql(open('../../baseline/sql_queries/temp_lowest_level_dependencies.sql', 'r').read() + 'select * from lowest_level_dependency;', con)

con.close()


lp['start'] = None
lp['end'] = None

av['project'] = None

av_original = av.copy(deep=True)
av['worker'] = 0
for i in range(1, 10):
    av_tmp = av_original.copy(deep=True)
    av_tmp['worker'] = i
    av = pd.concat([av, av_tmp], ignore_index=True)








def unassign_project_from_workers(project):
    global av, lp
    av.project.loc[(av.project == project)] = None



def assign_time_first_free(project, from_date = None, assignee = None, one_worker_per_project = False):
    global av, lp
    lp_index = lp[lp.project == project].index[0]
    if from_date is None:
        from_date = av.start.min()
    if assignee is None:
        assignee = av.worker.unique()
    if one_worker_per_project:
        assignee = [av[av.worker.isin(assignee) & av.project.isnull() & (from_date <= av.start)].sort_values(['start']).worker.iat[0]]
        # print(assignee)
    time_left = lp.at[lp_index, 'worktime_planned']
    first = False
    for index in av[av.worker.isin(assignee) & av.project.isnull() & (from_date <= av.start)].sort_values(['start']).index:
        worktime = av.at[index, 'end'] - av.at[index, 'start']
        av.at[index, 'project'] = lp.at[lp_index, 'project']
        if first == False:
            lp.at[lp_index, 'start'] = av.at[index, 'start']
            first = True
        if time_left == worktime:
            lp.at[lp_index, 'end'] = av.at[index, 'end']
            return
        elif time_left < worktime:
            new_row = av.loc[index]
            new_row['project'] = None
            av.at[index, 'end'] -= time_left
            new_row['start'] = av.at[index, 'end']
            av.loc[av.shape[0]] = new_row
            lp.at[lp_index, 'end'] = av.at[index, 'end']
            return
        time_left -= worktime
    raise Exception("No more available time in calendar.")


def fix_dependence_issues(one_worker_per_project = False):
    global av, lp, ld
    number_of_fixes = 0
    while True: # fix dependency issue
        update = ld[ld.dependence == 'FS'].merge(lp, left_on='predecessor', right_on='project')[['project_x', 'end']].groupby(['project_x']).max()
        update = update.merge(lp, left_on='project_x', right_on='project')
        update = update[update.start < update.end_x]

        if update.shape[0] == 0:
            return number_of_fixes

        unassign_project_from_workers(update.project.iat[0])
        assign_time_first_free(update.project.iat[0], update.end_x.iat[0], one_worker_per_project=one_worker_per_project)
        number_of_fixes += 1


def create_dependency_paths():
    global lp, ld
    # build dependency paths
    paths = [[i] for i in list(lp.project[~lp.project.isin(ld.project)])] # roots
    number_of_new_paths = len(paths)
    while number_of_new_paths:
        new_paths = []
        for path in paths[-number_of_new_paths:]:
            successors = list(ld[(ld.predecessor == path[-1])].project)
            for successor in successors:
                new_path = path.copy()
                new_path.append(successor)
                new_paths.append(new_path)
        number_of_new_paths = len(new_paths)
        paths += new_paths
    return paths


def assign_projects_to_resources_no_dependence(one_worker_per_project = False):
    global av, lp
    for project in lp.project: # assign first availble time to project
        assign_time_first_free(project, one_worker_per_project=one_worker_per_project)


def assign_projects_to_resources_first_free(one_worker_per_project = False):
    global av, lp, ld
    for project in lp.project: # assign first availble time to project
        assign_time_first_free(project, one_worker_per_project=one_worker_per_project)
        
    # print("Start fixing...")
    number_of_fixes = fix_dependence_issues(one_worker_per_project=one_worker_per_project)
    print("Preliminary assignment quality: " + str(number_of_fixes))
    return lp.end.max()



def assign_projects_to_resources_from_longest_path(one_worker_per_project = False):
    global av, lp, ld

    paths = create_dependency_paths()

    for path in paths:
        path.append(lp[lp.project.isin(path)].worktime_planned.sum())
    paths = sorted(paths, key=lambda path: path[-1], reverse=True)

    for path in paths:
        for project in path[:-1]:
            if av[(av.project == project)].shape[0] == 0:
                assign_time_first_free(project, one_worker_per_project=one_worker_per_project)
                # print('Project ' + str(project) + ' assigned.')
        # print(path)
        # break

    # print("Start fixing...")
        number_of_fixes = fix_dependence_issues(one_worker_per_project=one_worker_per_project)
        # print("Preliminary assignment quality (bigger -> worser): " + str(number_of_fixes))
    return lp[lp.end.notnull()].end.max()



def assign_projects_to_resources_from_path_start(one_worker_per_project = False):
    global av, lp, ld

    paths = create_dependency_paths()

    print('Assigning projects...')

    level = 0
    while True:
        projects_on_level = list(set([(i[level] if (len(i) > level) else None) for i in paths]))
        if (len(projects_on_level) <= 1) and (projects_on_level[0] is None):
            break
        # print(projects_on_level)
        for project in projects_on_level:
            if (av[(av.project == project)].shape[0] == 0) and (project is not None):
                assign_time_first_free(project, one_worker_per_project=one_worker_per_project)
                # print('Project ' + str(project) + ' assigned.')
        level += 1

    print('Unassigned projects: ' + str(lp[~lp.project.isin(av.project)].shape[0]))

    # print("Start fixing...")
    number_of_fixes = fix_dependence_issues(one_worker_per_project=one_worker_per_project)
    print("Preliminary assignment quality (bigger -> worser): " + str(number_of_fixes))
    return lp.end.max()


        
algo_time_start = time()

finish_date = assign_projects_to_resources_first_free(one_worker_per_project=True)
# finish_date = assign_projects_to_resources_from_longest_path(one_worker_per_project=False)
# finish_date = assign_projects_to_resources_from_path_start(one_worker_per_project=True)

algo_time_end = time()

print('Project finish timestamp: ' + str(finish_date))
print('Calculation time [s]: ' + str(algo_time_end - algo_time_start))
print('Unassigned workers time during project: ' + str((av[av.project.isnull() & (av.start <= finish_date)].end - av[av.project.isnull() & (av.start <= finish_date)].start).sum()))
# av[av.project.isnull() & (av.start <= finish_date)].sort_values('start')

# %%

def assign_projects_infinite_resources(start_date):
    global lp
    lp['start'] = pd.Timestamp(start_date, tz='UTC')
    lp['end'] = lp['start'] + lp['worktime_planned']
    while True:
        update = ld[ld.dependence == 'FS'].merge(lp, left_on='predecessor', right_on='project')[['project_x', 'end']].groupby(['project_x']).max()
        update = update.merge(lp, left_on='project_x', right_on='project')
        update = update[update.start < update.end_x][['project', 'worktime_planned', 'end_x']].rename(columns={'end_x': 'start'})
        update['end'] = update.start + update.worktime_planned
        
        if update.shape[0] == 0:
            return lp.end.max()

        lp = pd.concat([lp[~lp.project.isin(update.project)], update], ignore_index=True)
        
    

# assign_projects_infinite_resources('2020-02-01')


# %%




