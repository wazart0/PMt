import pandas as pd

import datetime
import dateutil.parser





def replaceTime(timestamp, time): # TODO improve, not so efficient method
    return dateutil.parser.parse(str(timestamp).split(' ')[0] + time)




class CalendarExpander():

    def __init__(self, start_timestamp = None, calendar = None):
        self.calendar = calendar
        self.start = start_timestamp
        self.expanded_calendar = None


    def generate_weekly_availability(self, solver, calendar_row, finish):
        isoweekday = {'Monday': 1, 'Tuesday': 2, 'Wednesday': 3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6, 'Sunday': 7}
        initial_start_finish = []
        for weekday in calendar_row['calculation_details']['weekdays']:
            tmp_timestamp = self.start
            while tmp_timestamp.isoweekday() != isoweekday[weekday]:
                tmp_timestamp += datetime.timedelta(days=1)
            initial_start_finish.append({
                'start': replaceTime(tmp_timestamp, calendar_row['calculation_details']['start_hour']), 
                'finish': replaceTime(tmp_timestamp, calendar_row['calculation_details']['finish_hour'])})

        weeks = 0
        while True:
            for i in initial_start_finish:
                if i['finish'] + datetime.timedelta(weeks=weeks) > finish: 
                    return
                self.expanded_calendar.loc[self.expanded_calendar.shape[0]] = [
                    calendar_row['id'], 
                    i['start'] + datetime.timedelta(weeks=weeks), 
                    i['finish'] + datetime.timedelta(weeks=weeks)]
            weeks += 1


    def solver_runner(self, solver, calendar_row):
        # TODO calculate finish on the fly or create some estimators - now its about 3 years
        finish = self.start + datetime.timedelta(weeks=150)
        if solver == 'weekly_repetition_solver':
            self.generate_weekly_availability(solver, calendar_row, finish)


    def check_schema_of_calculation_details(self, calculation_details):
        if 'weekdays' in calculation_details.keys() \
            and 'start_hour' in calculation_details.keys() \
            and 'finish_hour' in calculation_details.keys():
            return 'weekly_repetition_solver'
        return None

    
    def expand_calendars(self):
        self.expanded_calendar = pd.DataFrame(columns=['calendar_id', 'start', 'finish']) # init

        for row in self.calendar.iterrows():
            self.solver_runner(self.check_schema_of_calculation_details(row[1]['calculation_details']), row[1])





class UserCalendarExpander(CalendarExpander):
    
    def __init__(self, start_timestamp, user_calendar = None, calendar = None):
        self.user_calendar = user_calendar
        self.calendar = calendar
        self.start = start_timestamp


    def create_availability_frame(self):
        self.expand_calendars()

        availability = self.user_calendar.merge(self.expanded_calendar, how='inner', on='calendar_id', suffixes=('_user_calendar', ''))
        self.expanded_calendar = None # free some RAM
        # TODO if start_user_calendar is between start and finish then start_y = start_user_calendar (the same for finish_user_calendar)
        availability = availability[
            (availability.start_user_calendar < availability.start) & 
            (availability.finish_user_calendar.isnull() | (availability.finish_user_calendar > availability.finish)) & 
            (availability.in_office == True)]
        # TODO include out of office intervals

        return availability[['user_id', 'start', 'finish']]





