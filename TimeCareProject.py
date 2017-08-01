import os
import xml.etree.ElementTree as ET
import pandas as pd
import datetime



def loadEvents():
    file_name = 'Events.xml'
    full_file = os.path.abspath(os.path.join('data',file_name))
    tree = ET.parse(full_file)
    events = tree.findall('Event')
    df = pd.DataFrame(columns = ['Type','StartTime','EndTime','Reminder'])

    for event in events:
        df = appendEvent(df, event)

    return df

def appendEvent(df, event):
    event_type = event.find('event_type').text
    event_length = event.find('time/event_length').text
    event_startTime = event.find('time/event_startTime').text
    year = int(event_startTime[0:4])
    month = int(event_startTime[5:7])
    day = int(event_startTime[8:10])
    hour = int(event_startTime[11:13])
    minute = int(event_startTime[14:16])
    event_startTime  = datetime.datetime(year,month,day,hour,minute)
    event_endTime = event_startTime + datetime.timedelta(minutes=int(event_length))
    reminder = event.find('reminder').text

    if event_type == "Sport":
        event_startTime = adjustSportStartTime(event, event_startTime)
        event_endTime = adjustSportEndTime(event, event_endTime)

    return df.append({'Type': event_type,'StartTime':  event_startTime,'EndTime' : event_endTime, 'Reminder':reminder}, ignore_index=True)

def adjustSportStartTime(event, event_startTime):
        changing_time = event.find('time/changing_time').text
        event_startTime -= datetime.timedelta(minutes=int(changing_time))
        return event_startTime

def adjustSportEndTime(event, event_endTime):
        shower_time = event.find('time/shower_time').text
        event_endTime += datetime.timedelta(minutes=int(shower_time))
        return event_endTime


def filterEventsOfType(data, eventType):
    events = []
    for n in range(data.shape[0]):
        if data.iloc[n].Type == eventType:
            events.append(data.iloc[n])

    return events

def insertWork(data,Schema):

    for num in range(data.shape[0]):
        if data.iloc[num].Type  == "Work":
            Schema = Schema.append(data.iloc[num], ignore_index=True)
    return Schema

def insertFriends(data,Schema):
    friendEvents = filterEventsOfType(data, "Friends")
    workEvents = filterEventsOfType(data, "Work")
    sportEvents = filterEventsOfType(data, "Sport")

    for friendEvent in friendEvents:
        result = EnougthSpace(friendEvent,Schema)
        if not result[0] and result[1]:
            friendEvent = friendEvent.set_value('StartTime',result[1])
            Schema = Schema.append(friendEvent, ignore_index=True)

        elif result[0]:
            Schema = Schema.append(friendEvent, ignore_index=True)

    return Schema


def insertSport(data, Schema):
    friendEvents = filterEventsOfType(data, "Friends")
    workEvents = filterEventsOfType(data, "Work")
    sportEvents = filterEventsOfType(data, "Sport")

    for sportEvent in sportEvents:
        result = EnougthSpace(sportEvent,Schema)
        if result[0]:
            Schema = Schema.append(sportEvent, ignore_index=True)

    return Schema

def SameDay(event,Schema):
    if event.StartTime.day == Schema.StartTime.day and event.StartTime.month == Schema.StartTime.month and event.StartTime.year == Schema.StartTime.year:
        return True

def startOverlap(event,Schema):
    if event.StartTime >= Schema.StartTime  and  Schema.EndTime >= event.StartTime  and event.StartTime < Schema.EndTime and SameDay(event,Schema):
        return True


def endOverlap(event,Schema):
    if event.StartTime <= Schema.StartTime  and  event.EndTime >= Schema.StartTime  and SameDay(event,Schema):
        return True


def startAndEndOverlap(event,Schema):
    if event.StartTime >= Schema.StartTime  and  event.EndTime <= Schema.EndTime  and SameDay(event,Schema):
        return True


def totalOverlap(event,Schema):
    if event.StartTime > Schema.StartTime  and  event.EndTime <= Schema.EndTime  and event.StartTime< Schema.EndTime and SameDay(event,Schema):
        return True

def EnougthSpace(event,Schema):
    for i in range(Schema.shape[0]):
        if totalOverlap(event,Schema.iloc[i]):
            return[False, False]

        elif startOverlap(event,Schema.iloc[i]):
            if Schema.iloc[i].Type== "Work" and event.Type == "Friends":
                if Schema.iloc[i].EndTime < event.EndTime:
                    return [False, Schema.iloc[i].EndTime]
            else:
                return [False, False]

        elif endOverlap(event,Schema.iloc[i]):
            return [False, False]

        elif startAndEndOverlap(event,Schema.iloc[i]):
            return[False, False]

    return [True, False]


def SchemaBuilder(data):
    Schema = pd.DataFrame(columns = ['Type','StartTime','EndTime','Reminder'])
    Schema = insertWork(data,Schema)
    Schema = insertFriends(data,Schema)
    Schema = insertSport(data,Schema)

    Schema = Schema.sort_values(by="StartTime")

    return Schema

df = loadEvents()
Schema = SchemaBuilder(df)
print(Schema)
#
# ''' Kvar att göra:
#     Olika typer av träningspass'''
