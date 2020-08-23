from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sys
from collections import defaultdict

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# USA Zones only at the moment
ZONES = {'-04:00':'EST', '-05:00':'CST', '-06:00':'MDT', '-07:00':'PST'}

#busy times 
times = defaultdict(list)


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            try:
                creds = pickle.load(token)
            except:
                print('No Token Found')

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    if not events:
        print('No upcoming events found.')

    
    #convertToTuples
    #print(events[0].keys())
    

    for event in events:
        start, end = event.get('start').get('dateTime'), event.get('end').get('dateTime')

        start_date, start_time, zone = convertTimeString(start)
        end_date, end_time, zone = convertTimeString(end)
        

        if start_date == end_date:
            times[start_date].append([convertTimeToIntegers(start_time), convertTimeToIntegers(end_time)])

    
    final_free_times = getFreeTime(times['2020-09-01'])
    print('2020-09-01', end = ': ')
    finalPrintStatement(final_free_times)



#Returns all the times available on your calendar between these two dates
def getFreeTime(busy_times):
    start_time = [4, 0]
    end_time = [18, 0]

    if len(times) == 0:
        return 'Free Schedule'

    free_times = []
    curr_hour, curr_minute = 4, 0
    
    for busy_time in busy_times:
        starting_hour, starting_minutes = busy_time[0]
        ending_hour, ending_minutes = busy_time[1]

        if starting_hour > curr_hour:
            free_times.append([(curr_hour, curr_minute), (starting_hour, starting_minutes)])
            curr_hour, curr_minute = ending_hour, ending_minutes

    if curr_hour <= end_time[0]:
        free_times.append([(curr_hour, curr_minute), (end_time[0], end_time[1])])
    
    return free_times


def finalPrintStatement(array):
    for interval in array:
        print(convertIntToString(interval[0], interval[1]), end=' ')


def convertIntToString(start, end):
    return str(start[0])+':'+str(start[1]) + '-' + str(end[0])+':'+str(end[1])

def convertTimeToIntegers(time_string):
    time = time_string.split(':')
    return (int(time[0]), int(time[1]))

#print time in format: XX hours, YY minutes and ZZ seconds.
def printDifference(difference):
    print(str(difference[0]) + ' hours,', str(difference[1]) + ' minutes and', str(difference[2]) + ' seconds.')


#calculates the differences between two times
def timeDuration(start_time, end_time):
    
    s_hour, s_min, s_second = list(map(int, start_time.split(':')))
    e_hour, e_min, e_second = list(map(int, end_time.split(':')))

    difference = [(e_hour - s_hour), (e_min - s_min), (e_second - s_second)]
    #printDifference(difference)

#convert Google Formatted Time&Date string to string array of [date, time, zone]
def convertTimeString(curr_time):
    date, t = curr_time.split('T')
    negative = False
    try:
        time, zone = t.split('-')
        negative = True 
    except:
        time, zone = t.split('+')
    
    zone = ZONES['-'+zone] if negative else ZONES['+'+zone]
    return date, time, zone

    
    
    

    
    


if __name__ == '__main__':
    main()