''' en placemark för varje event

events: arbete, underhållning, sportakrivitet
'''
import os
from xml.dom import minidom
import xml.etree.ElementTree as ET
import pandas as pd
import datetime
#import plotly.plotly as py
#import plotly.figure_factory as ff


file_name = 'Events.xml'

full_file =os.path.abspath(os.path.join('data',file_name))

tree = ET.parse(full_file)
events = tree.findall('Event')
df = pd.DataFrame(columns = ['Type','StartTime','EndTime','Reminder'])

for c in events:
    event_type = c.find('event_type').text
    event_length = c.find('time/event_length').text
    event_startTime = c.find('time/event_startTime').text
    year = int(event_startTime[0:4])
    month = int(event_startTime[5:7])
    day = int(event_startTime[8:10])
    hour = int(event_startTime[11:13])
    minute = int(event_startTime[14:16])
    event_startTime  = datetime.datetime(year,month,day,hour,minute)
    event_endTime = event_startTime + datetime.timedelta(minutes=int(event_length))
    reminder = c.find('reminder').text
    df = df.append({'Type': event_type,'StartTime':  event_startTime,'EndTime' : event_endTime, 'Reminder':reminder}, ignore_index=True)

def SchemaBuilder(data):
    #Create an empty dateframe to fill the events with
    Schema = pd.DataFrame(columns = ['Type','StartTime','EndTime','Reminder'])
    #insert work into the schedule
    for num in range(data.shape[0]):
        if data.iloc[num].Type  == "Work":
            Schema = Schema.append(data.iloc[num], ignore_index=True)

    #start insert other events
    for num in range(data.shape[0]):
        if data.iloc[num].Type == "Friends":
            for i in range(Schema.shape[0]):
                if data.iloc[num].StartTime >= Schema.iloc[i].StartTime and data.iloc[num].EndTime <= Schema.iloc[i].EndTime: #chec if time slot is occupied
                    if Schema.iloc[i].Type== "Work":
                        if Schema.iloc[i].EndTime <= data.iloc[num].EndTime:
                            df.set_value(num,'StartTime',Schema.iloc[i].EndTime )
                            Schema = Schema.append(data.iloc[num], ignore_index=True)
                            continue

                    elif Schema.iloc[i].Type == "Sport":
                        Schema.drop(Schema.index[i])
                        Schema = Schema.append(data.iloc[num], ignore_index=True)
                        continue



        elif data.iloc[num].Type == "Sport":
            for i in range(Schema.shape[0]):
                if data.iloc[num].StartTime >= Schema.iloc[i].StartTime and data.iloc[num].EndTime <= Schema.iloc[i].EndTime: #chec if time slot is occupied
                    pass
                else:
                    Schema = Schema.append(data.iloc[num], ignore_index=True)

    return Schema

Schema = SchemaBuilder(df)
print(Schema)

#
# def Visulize(self,Schema):
# #https://plot.ly/python/gantt/
#     for events in Schema:
#         df[events] = [dict(Tasnk = 'event.event_type', Start = 'event.startTime', Finish = 'event.finishTime']
#
#         # df = [
#         # dict(Task='Morning Sleep', Start='2016-01-01', Finish='2016-01-01 6:00:00', Resource='Sleep'),
#         # dict(Task='Breakfast', Start='2016-01-01 7:00:00', Finish='2016-01-01 7:30:00', Resource='Food'),
#         # dict(Task='Work', Start='2016-01-01 9:00:00', Finish='2016-01-01 11:25:00', Resource='Brain'),
#         # dict(Task='Break', Start='2016-01-01 11:30:00', Finish='2016-01-01 12:00:00', Resource='Rest'),
#         # dict(Task='Lunch', Start='2016-01-01 12:00:00', Finish='2016-01-01 13:00:00', Resource='Food'),
#         # dict(Task='Work', Start='2016-01-01 13:00:00', Finish='2016-01-01 17:00:00', Resource='Brain'),
#         # dict(Task='Exercise', Start='2016-01-01 17:30:00', Finish='2016-01-01 18:30:00', Resource='Cardio'),
#         # dict(Task='Post Workout Rest', Start='2016-01-01 18:30:00', Finish='2016-01-01 19:00:00', Resource='Rest'),
#         # dict(Task='Dinner', Start='2016-01-01 19:00:00', Finish='2016-01-01 20:00:00', Resource='Food'),
#         # dict(Task='Evening Sleep', Start='2016-01-01 21:00:00', Finish='2016-01-01 23:59:00', Resource='Sleep')
#         # ]
#
#     colors = dict(Work = 'rgb(46, 137, 205)',
#               Friends = 'rgb(114, 44, 121)',
#               Training = 'rgb(198, 47, 105)')
#
#     fig = ff.create_gantt(df, colors=colors, index_col='Resource', title='Daily Schedule',
#                       show_colorbar=True, bar_width=0.8, showgrid_x=True, showgrid_y=True)
#     py.iplot(fig, filename='gantt-hours-minutes', world_readable=True)