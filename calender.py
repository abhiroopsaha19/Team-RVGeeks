#!/usr/bin/python3

# https://developers.google.com/calendar/quickstart/python
# https://developers.google.com/calendar/create-events#python

import traceback

from contest import get_contest

import logging

import datetime 
import pytz
from pytz import timezone
from dateutil import tz


logger=logging.getLogger() 

logger.setLevel(logging.INFO) 


def make_event(contest):
    date = datetime.datetime.utcfromtimestamp(int(contest['timestamp']))
    # date = datetime.datetime.utcfromtimestamp(1594564500)
    date = pytz.UTC.localize(date)
    ist = pytz.timezone('Asia/Kolkata')
    date = date.astimezone(ist)

    if 'endtimestamp' in contest.keys():
      dateend = datetime.datetime.utcfromtimestamp(int(contest['endtimestamp']))
      dateend = pytz.UTC.localize(dateend)
      ist = pytz.timezone('Asia/Kolkata')
      dateend = dateend.astimezone(ist)
      
      desc  = "{} \n {} \n START: {} {} IST \nEND: {} {} IST \nURL: {} \n\n src: {}".format(
        contest['platform'],
        contest['name'],
        contest['date'],
        contest['time'],

        contest['enddate'],
        contest['endtime'],

        contest['url'],

        'https://contestcal.herokuapp.com/'

        )

    else:
      dateend = date + datetime.timedelta(hours = 2)
      desc  = "{}\n{}\nSTART: {} {} IST\nURL: {} ".format(
        contest['platform'],
        contest['name'],
        contest['date'],
        contest['time'],

        contest['url']

        )

    # print(desc)
    # print("------------------------")
    event = {
      'id':'contestid'+str(int(contest['timestamp'])),
      'summary': contest['platform'].lower() + " contest, "+ contest['name'],
      
      'description': desc,
      'start': {
        'dateTime': date.isoformat()   ,
        # 'timeZone': 'Asia/Kolkata',
      },
      'end': {
        'dateTime': dateend.isoformat()   ,
        # 'timeZone': 'Asia/Kolkata',
      },
    
      
      'reminders': {
        'useDefault': False,
        'overrides': [
          {'method': 'popup', 'minutes': 10 * 60},
          {'method': 'popup', 'minutes': 2 * 60},
          {'method': 'popup', 'minutes': 15},
        ],
      },
    }
    return event


def create_event(contest, service):

    eventData = make_event(contest)
    event = service.events().insert(calendarId='primary', body=eventData).execute()
    logger.info('Event created: %s' % (event.get('htmlLink')))


