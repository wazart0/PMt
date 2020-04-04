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
av3 = av.copy(deep=True)
av4 = av.copy(deep=True)
av5 = av.copy(deep=True)

av['worker_id'] = 1
av1['worker_id'] = 2
av2['worker_id'] = 3
av3['worker_id'] = 4
av4['worker_id'] = 5
av5['worker_id'] = 6

av = pd.concat([av, av1, av2, av3, av4, av5], ignore_index=True)




# %% 

def assign_time_first_free(lp_index, from_date = None, assignee = None):
    global av, lp
    if from_date is None:
        from_date = av.start.min()
    if assignee is None:
        assignee = av.worker_id.unique()
    time_left = lp.at[lp_index, 'worktime_planned']
    first = False
    for index in av[av.worker_id.isin(assignee) & av.project_id.isnull() & (from_date <= av.start)].sort_values(['start']).index:
        worktime = av.at[index, 'end'] - av.at[index, 'start']
        av.at[index, 'project_id'] = lp.at[lp_index, 'project_id']
        if first == False:
            lp.at[lp_index, 'start'] = av.at[index, 'start']
            first = True
        if time_left == worktime:
            lp.at[lp_index, 'end'] = av.at[index, 'end']
            return
        elif time_left < worktime:
            new_row = av.loc[index]
            new_row['project_id'] = None
            av.at[index, 'end'] -= time_left
            new_row['start'] = av.at[index, 'end']
            av.loc[av.shape[0]] = new_row
            lp.at[lp_index, 'end'] = av.at[index, 'end']
            return
        time_left -= worktime
    raise Exception("No more available time in calendar.")


def unassign_project_from_workers(project_id):
    global av, lp
    av.project_id.loc[(av.project_id == project_id)] = None

# lp.at[0, 'worktime_planned'] -= pd.Timedelta('4h')
# assign_time_first_free(0,[2,3])


def assign_projects_to_resources_no_dependance():
    global av, lp
    for index in lp.index: # assign first availble time to project
        assign_time_first_free(index)


def assign_projects_to_resources_first_free():
    global av, lp, ld
    for index in lp.index: # assign first availble time to project
        assign_time_first_free(index)
    # print("Start fixing...")
    while True: # fix dependancy issue
        update = ld[ld.dependance == 'FS'].merge(lp, left_on='predecessor_id', right_on='project_id')[['project_id_x', 'end']].groupby(['project_id_x']).max()
        update = update.merge(lp, left_on='project_id_x', right_on='project_id')
        update = update[update.start < update.end_x]

        if update.shape[0] == 0:
            return lp.end.max()

        unassign_project_from_workers(update.project_id.iat[0])
        assign_time_first_free(lp[lp.project_id == update.project_id.iat[0]].index[0], update.end_x.iat[0])


finish_date = assign_projects_to_resources_first_free()

av[av.project_id.isnull() & (av.start <= finish_date)].sort_values('start').start

# %%

def assign_projects_infinite_resources(start_date):
    global lp
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
        
    

assign_projects_infinite_resources('2020-02-01')


# %%





