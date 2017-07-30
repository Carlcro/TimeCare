import os
import xml.etree.ElementTree as ET
import pandas as pd
import datetime



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

    if event_type == "Sport":
            changing_time = c.find('time/changing_time').text
            event_startTime -= datetime.timedelta(minutes=int(changing_time))
            event_endTime += datetime.timedelta(minutes=int(changing_time))

    df = df.append({'Type': event_type,'StartTime':  event_startTime,'EndTime' : event_endTime, 'Reminder':reminder}, ignore_index=True)

def SchemaBuilder(data):
    Schema = pd.DataFrame(columns = ['Type','StartTime','EndTime','Reminder'])
    for num in range(data.shape[0]):
        if data.iloc[num].Type  == "Work":
            Schema = Schema.append(data.iloc[num], ignore_index=True)

    for num in range(data.shape[0]):
        inserted = False
        if data.iloc[num].Type == "Friends":
            print(data.iloc[num].Type)
            for i in range(Schema.shape[0]):
                if data.iloc[num].StartTime >= Schema.iloc[i].StartTime  and  data.iloc[num].StartTime <= Schema.iloc[i].EndTime: #chec if time slot is occupied
                    if Schema.iloc[i].Type== "Work":
                        if Schema.iloc[i].EndTime < data.iloc[num].EndTime:
                            print(Schema.iloc[i].EndTime)
                            data.set_value(num,'StartTime',Schema.iloc[i].EndTime)
                            Schema = Schema.append(data.iloc[num], ignore_index=True)
                            inserted = True
                            continue

                    elif Schema.iloc[i].Type == "Friends":
                            inserted = True

                    elif Schema.iloc[i].Type == "Sport":
                        Schema.drop(Schema.index[i])
                        Schema = Schema.append(data.iloc[num], ignore_index=True)
                        inserted = True
                        continue

        elif data.iloc[num].Type == "Sport" or data.iloc[num].Type == "Work":
            for i in range(Schema.shape[0]):
                if data.iloc[num].StartTime >= Schema.iloc[i].StartTime and data.iloc[num].EndTime <= Schema.iloc[i].EndTime: #chec if time slot is occupied
                    inserted = True

        if inserted == False:
            Schema = Schema.append(data.iloc[num], ignore_index=True)

    Schema = Schema.sort_values(by="StartTime")
    return Schema

Schema = SchemaBuilder(df)
print(Schema)
