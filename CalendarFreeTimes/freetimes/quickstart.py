from __future__ import print_function
import datetime
import pickle
import os.path
from os import path
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from collections import defaultdict


class CalendarFreeTimes():
    def __init__(self):
        self.from_date = '' # Start Date
        self.to_date = ''   # End Date
        self.SCOPES = ['https://www.googleapis.com/auth/calendar.readonly'] # If modifying these scopes, delete the file token.pickle.
        self.ZONES = {'-04:00':'EST', '-05:00':'CST', '-06:00':'MDT', '-07:00':'PST'} # USA Zones only at the moment
        self.times = defaultdict(list) #All the busy times in your calendar
        self.service = None
        self.freeTimes = defaultdict(list)

    def main(self):

        date_1 = self.from_date
        self.from_date += 'T00:00:00.000000Z'

        date_2 = self.to_date
        self.to_date += 'T23:59:59.599999Z'

        #get the service
        self.initializeToken()

        if not self.service:
            print('Service is not available')
            return

        #get all the events from Google Calendar
        all_events = self.getEvents()

        #getAllBusyTimes using the events. Busy times will be added to self.times 
        self.getBusyTime(all_events)

        '''
        So far, I have got all the busy times in the calendar appended to dictionary against the date
        Now I am about to get for each date mentioned between start_date and to_date, 
        '''

        #main logic
        all_dates = self.findDateRange(date_1, date_2)

        for each_date in all_dates:
            final_free_times = self.getFreeTime(self.times[each_date])
            print('[Daniyal]', final_free_times)

            if not final_free_times: continue
            self.freeTimes[each_date].append(final_free_times[:])
            


    def initializeToken(self):
        """
        Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        CREDENTIALS_FILE = './credentials.json'
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)


        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, self.SCOPES, redirect_uri = 'http://localhost:8000/index/callback')
                creds = flow.run_local_server(port=8001)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

    def setFromDate(self, from_date):
        self.from_date = from_date

    def setToDate(self, to_date):
        self.to_date = to_date

    def getEvents(self):
        events_result = self.service.events().list(calendarId='primary', timeMin=self.from_date, timeMax=self.to_date, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])
        if not events:
            print('No upcoming events found.')
            return []
        return events

    def getBusyTime(self, events):

        for event in events:
            start, end = event.get('start').get('dateTime'), event.get('end').get('dateTime')

            start_date, start_time, zone = self.convertTimeString(start)
            end_date, end_time, zone = self.convertTimeString(end)
            
            if start_date == end_date:
                self.times[start_date].append([self.convertTimeToIntegers(start_time), self.convertTimeToIntegers(end_time)])

    def printFreeTimes(self):
        #for current date print the free times 
        for current_date in findDateRange(date_1, date_2):

            print(current_date, end = ': ')
            #pass all busy times for the current date
            #get all free times for the current date
            final_free_times = self.getFreeTime(self.times[current_date])
            finalPrintStatement(final_free_times)
            print()

    def getFreeTime(self, busy_times):

        if not busy_times:
            return []

        start_time = [0, 0]
        end_time = [23, 59]

        free_times = []
        curr_hour, curr_minute = 0, 0

        for busy_time in busy_times:
            starting_hour, starting_minutes = busy_time[0]
            ending_hour, ending_minutes = busy_time[1]

            if starting_hour > curr_hour:
                free_times.append([(curr_hour, curr_minute), (starting_hour, starting_minutes)])
                curr_hour, curr_minute = ending_hour, ending_minutes

        if curr_hour <= end_time[0]:
            free_times.append([(curr_hour, curr_minute), (end_time[0], end_time[1])])
    
        return free_times

    #convert time intervals to string
    def finalPrintStatement(self, array):
        for i, interval in enumerate(array):
            last = ','
            print(self.convertIntToString(interval[0], interval[1]), end='')
            if i != len(array) - 1:
                print(last, end = ' ')

    #convert time to string from integers
    def convertIntToString(self, start, end):
        first_am_pm = 'am' if start[0] < 12 else 'pm'
        second_am_pm = 'am' if end[0] < 12 else 'pm'
        
        first_hour = '0'+str(start[0]) if start[0] <= 9 else str(start[0]) if start[0] <= 12 else str(start[0]-12)
        first_min = '0'+str(start[1]) if start[1] <= 9 else str(start[1])

        end_hour = '0'+str(end[0]) if end[0] <= 9 else str(end[0]) if end[0] <= 12 else str(end[0]-12)
        end_min = '0'+str(end[1]) if end[1] <= 9 else str(end[1])

        return first_hour+':'+first_min + first_am_pm + ' - ' + end_hour+':'+end_min+second_am_pm

    #convert time to int from string
    def convertTimeToIntegers(self, time_string):
        time = time_string.split(':')
        return (int(time[0]), int(time[1]))

    #print time in format: XX hours, YY minutes and ZZ seconds.
    def printDifference(self, difference):
        print(str(difference[0]) + ' hours,', str(difference[1]) + ' minutes and', str(difference[2]) + ' seconds.')

    #calculates the differences between two times
    def timeDuration(self, start_time, end_time):
        
        s_hour, s_min, s_second = list(map(int, start_time.split(':')))
        e_hour, e_min, e_second = list(map(int, end_time.split(':')))

        difference = [(e_hour - s_hour), (e_min - s_min), (e_second - s_second)]
        #printDifference(difference)

    #convert Google Formatted Time&Date string to string array of [date, time, zone]
    def convertTimeString(self, curr_time):
        date, t = curr_time.split('T')
        negative = False
        try:
            time, zone = t.split('-')
            negative = True 
        except:
            time, zone = t.split('+')
        
        zone = self.ZONES['-'+zone] if negative else self.ZONES['+'+zone]
        return date, time, zone

    #convert date
    def findDateRange(self, start, end):
        arr = []
        start = list(map(int, start.split('-')))
        end = list(map(int, end.split('-')))
        start_year, start_month, start_date = start
        end_year, end_month, end_date = end

        curr_year, curr_month, curr_date = int(start_year), int(start_month), int(start_date)
        string_formatted_curr_date = ''
        i = 0

        while [curr_year, curr_month, curr_date] != end:

            formatted_curr_year = str(curr_year)
            formatted_curr_month = '0' + str(curr_month) if curr_month < 10 else str(curr_month)
            formatted_curr_date = '0' + str(curr_date) if curr_date < 10 else str(curr_date)

            string_formatted_curr_date = formatted_curr_year + '-' + formatted_curr_month + '-' + formatted_curr_date
            arr.append(string_formatted_curr_date)

            if (curr_date == 30 and curr_month % 2 == 0) or curr_date == 31:
                curr_date = 1
                curr_month += 1
                if curr_month > 12:
                    curr_month = 1
                    curr_year += 1
 
            else:
                curr_date += 1

        return arr


