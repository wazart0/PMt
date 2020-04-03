# %% init
import pandas as pd

import psycopg2
con = psycopg2.connect(user='ad', password='pass', database='pmt')

av = pd.read_sql(open('../../pmt_calendar/sql_queries/calculate_availability.sql', 'r').read(), con)
lp = pd.read_sql(open('../../baseline/sql_queries/temp_lowest_level_projects.sql', 'r').read() + 'select * from lowest_level_projects;', con)
ld = pd.read_sql(open('../../baseline/sql_queries/temp_lowest_level_dependancies.sql', 'r').read() + 'select * from lowest_level_dependancy;', con)

con.close()


lp['start'] = None
lp['end'] = None

av['project_id'] = None



av1 = av.copy(deep=True)
av2 = av.copy(deep=True)

av['worker_id'] = 2
av1['worker_id'] = 1
av2['worker_id'] = 3

av = pd.concat([av, av1, av2], ignore_index=True)




# %% 

def assign_time_first_free(project_id, assignee = None):
    global av, lp
    if assignee is None:
        assignee = av.worker_id.unique()
    time_left = lp.at[project_id, 'worktime_planned']
    first = False
    for index in av[av.worker_id.isin(assignee) & av.project_id.isnull()].sort_values(['start']).index:
        worktime = av.at[index, 'end'] - av.at[index, 'start']
        av.at[index, 'project_id'] = lp.at[project_id, 'project_id']
        if first == False:
            lp.at[project_id, 'start'] = av.at[index, 'start']
            first = True
        if time_left == worktime:
            lp.at[project_id, 'end'] = av.at[index, 'end']
            return
        elif time_left < worktime:
            new_row = av.loc[index]
            new_row['project_id'] = None
            av.at[index, 'end'] -= time_left
            new_row['start'] = av.at[index, 'end']
            av.loc[av.shape[0]] = new_row
            lp.at[project_id, 'end'] = av.at[index, 'end']
            return
        time_left -= worktime


def unassign_project_from_workers(project_id):
    global av, lp
    av.project_id.replace(project_id, inplace=True)

# lp.at[0, 'worktime_planned'] -= pd.Timedelta('4h')
# assign_time_first_free(0,[2,3])



# %%

def assign_tasks_infinite_resources(start_date):
    global av, lp
    lp['start'] = pd.Timestamp(start_date, tz='UTC')
    lp['end'] = lp['start'] + lp['worktime_planned']
    while True:
        update = ld[ld.dependance == 'FS'].merge(lp, left_on='predecessor_id', right_on='project_id')[['project_id_x', 'end']].groupby(['project_id_x']).max()
        update = update.merge(lp, left_on='project_id_x', right_on='project_id')
        update = update[update.start < update.end_x][['project_id', 'worktime_planned', 'end_x']].rename(columns={'end_x': 'start'})
        update['end'] = update.start + update.worktime_planned
        
        if update.shape[0] == 0:
            return lp.end.max()

        lp = pd.concat([lp[~lp.project_id.isin(update.project_id)], update], ignore_index=True)
        
    

assign_tasks_infinite_resources('2020-02-01')


# %%





