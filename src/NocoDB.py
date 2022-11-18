import configparser
import csv
import json
from fastapi import FastAPI
from loguru import logger
import requests
import pandas as pd

app = FastAPI(
    title = "Capacity Storage",
    description= "Downloads data from NocoDB as CSV"
)

config = configparser.ConfigParser()
config.read('config.ini')
url = config.get('noco', 'url')
API_TOKEN = config.get('noco', 'xc-auth')
CONTENT_TYPE = 'application/json'
URL = url + 'nc/eq_ast_be9y/api/v1/testTable'

header = {
    'xc-auth': API_TOKEN,
    "accept": CONTENT_TYPE
    }

@logger.catch
@app.get("/NocoDB/{id}")
async def get_One_Storage_Capacity_Reporting(id: int):
    getRowByID = f'{URL}/' + str(id)
    r = requests.get(getRowByID, headers=header)
    dictionary = json.loads(r.text)
    if dictionary:
        date = [dictionary['Date']]
        array = [dictionary['Array']]
        type = [dictionary['Type']]
        division = [dictionary['Division']]
        geo = [dictionary['Geo']]
        serialNum = [dictionary['SerialNumber']]
        used = [dictionary['Used']]
        failed = [dictionary['Failed']]
        free = [dictionary['Free']]
        totalCapacity = [dictionary['TotalCapacity']]
        percentUsed = [dictionary['PercentUsed']]
        percentUsedSymbol = [dictionary['PercentUsedString']]
        x = [dictionary['x']]

        csv_Headers = [
                        "Date",
                        "Array",
                        "Type",
                        "Division",
                        "Geo",
                        "Serial Number",
                        "Used",
                        "Failed",
                        "Free",
                        "Total Capacity",
                        "Percent Used",
                        "Percent Used (%)",
                        "x"
                    ]

        csv_Rows = list(zip(
                        date,
                        array,
                        type,
                        division,
                        geo,
                        serialNum,
                        used,
                        failed,
                        free,
                        totalCapacity,
                        percentUsed,
                        percentUsedSymbol,
                        x
                    ))

        name = dictionary['Name']
        with open(f'{name}.csv', 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)

            # write the headers
            writer.writerow(csv_Headers)
            # write the rows
            for data in csv_Rows:
                writer.writerow(data)
        return{
            "message": "Download successful!"
        }
    else:
        return{
            "message": "ID or data does not exist...try again."
        }

@logger.catch
@app.get("/NocoDB/filter/")
async def get_Multiple_Storage_Capacity_Reportings(start_date: str, 
                                                   end_date: str, 
                                                   #fieldNames: str, 
                                                   Date: bool,
                                                   Array: bool,
                                                   Type: bool,
                                                   Division: bool,
                                                   Geo: bool,
                                                   Serial_Number: bool,
                                                   Used: bool,
                                                   Failed: bool,
                                                   Free: bool,
                                                   Total_Capacity: bool,
                                                   Percent_Used: bool,
                                                   Percentage_Used: bool,
                                                   x: bool):

    r = requests.get(URL, headers=header)
    dictionary = json.loads(r.text)

    df = pd.DataFrame(dictionary) # works for more than one row (which is what we need)
    
    dict = {
    "created_at": start_date,
    "Date": Date,
    "Array": Array,
    "Type": Type,
    "Division": Division,
    "Geo": Geo,
    "Serial Number": Serial_Number,
    "Used": Used,
    "Failed": Failed,
    "Free": Free,
    "Total Capacity": Total_Capacity,
    "Percent Used": Percent_Used,
    "Percent Used (%)": Percentage_Used,
    "x": x
    }
    
    csv_Headings = ["Name"]
    for key, value in dict.items():
            csv_Headings.append(key)
    
    csv_Headings.remove("created_at")
    # take string date as parameter and concatenate the date with the time starting at 00:00:00 and ending 23:59:59. that way you won't need to strip
    start_date = start_date + " 00:00" # 00:00:00
    end_date = end_date + " 23:59"     # 23:59:59
    # Select DataFrame rows between two dates
    data = (df['created_at'] >= start_date) & (df['created_at'] <= end_date)
    df2 = df.loc[data]
    df3 = df.loc[data]
    df4 = df.loc[data]
    df5 = df.loc[data]
    df6 = df.loc[data]
    df7 = df.loc[data]
    df8 = df.loc[data]
    df9 = df.loc[data]
    df10 = df.loc[data]
    df11 = df.loc[data]
    df12 = df.loc[data]
    df13 = df.loc[data]
    df14 = df.loc[data]
    df15 = df.loc[data]
    dfNames = df.loc[data]

    count = 0
    devices = []
    for deviceNames in list(dfNames):
        if deviceNames == "Array":
            dfNames = list(dfNames[deviceNames].items())
            while count < len(dfNames):
                devices.append(dfNames[count][1])
                count = count+1
    #reset count
    count = 0
    
    if Date is False:
        Date = []
        index = 0
        i = 0
        while index < len(df2):
            Date.append(None)
            index = index+1
    elif Date is True:
        Date = []
        index = 0
        i = 0
        for column in list(df2):
            if column == "Date":
                df2 = list(df2[column].items())
                while index < len(df2):
                    Date.append(df2[index][1])
                    index = index+1
            # reset index
            index = 0
            i = i+1

    if start_date is False:
        start_date = []
        index = 0
        i = 0
        while index < len(df2):
            start_date.append(None)
            index = index+1
    elif start_date is True:
        index = 0
        i = 0
        start_date = []
        for column in list(df3):
            if column == "created_at":
                df3 = list(df3[column].items())
                while index < len(df3):
                    start_date.append(df3[index][1])
                    index = index+1
            # reset index
            index = 0
            i = i+1

    if Array is False:
        Array = []
        index = 0
        i = 0
        while index < len(df4):
            Array.append(None)
            index = index+1
    elif Array is True:
        index = 0
        i = 0
        Array = []
        for column in list(df4):
            if column == "Array":
                df4 = list(df4[column].items())
                while index < len(df4):
                    Array.append(df4[index][1])
                    index = index+1
            # reset index
            index = 0
            i = i+1

    if Type is False:
        Type = []
        index = 0
        i = 0
        while index < len(df5):
            Type.append(None)
            index = index+1
    elif Type is True:
        index = 0
        i = 0
        Type = []
        for column in list(df5):
            if column == "Type":
                df5 = list(df5[column].items())
                while index < len(df5):
                    Type.append(df5[index][1])
                    index = index+1
            # reset index
            index = 0
            i = i+1

    if Division is False:
        Division = []
        index = 0
        i = 0
        while index < len(df6):
            Division.append(None)
            index = index+1
    elif Division is True:
        Division = []
        index = 0
        i = 0
        Division = []
        for column in list(df6):
            if column == "Division":
                df6 = list(df6[column].items())
                while index < len(df6):
                    Division.append(df6[index][1])
                    index = index+1
            # reset index
            index = 0
            i = i+1

    if Geo is False:
        Geo = []
        index = 0
        i = 0
        while index < len(df7):
            Geo.append(None)
            index = index+1
    elif Geo is True:
        index = 0
        i = 0
        Geo = []
        for column in list(df7):
            if column == "Geo":
                df7 = list(df7[column].items())
                while index < len(df7):
                    Geo.append(df7[index][1])
                    index = index+1
            # reset index
            index = 0
            i = i+1

    if Serial_Number is False:
        Serial_Number = []
        index = 0
        i = 0
        while index < len(df8):
            Serial_Number.append(None)
            index = index+1
    elif Serial_Number is True:
        index = 0
        i = 0
        Serial_Number = []
        for column in list(df8):
            if column == "SerialNumber":
                df8 = list(df8[column].items())
                while index < len(df8):
                    Serial_Number.append(df8[index][1])
                    index = index+1
            # reset index
            index = 0
            i = i+1
    
    if Used is False:
        Used = []
        index = 0
        i = 0
        while index < len(df9):
            Used.append(None)
            index = index+1
    elif Used is True:
        index = 0
        i = 0
        Used = []
        for column in list(df9):
            if column == "Used":
                df9 = list(df9[column].items())
                while index < len(df9):
                    Used.append(df9[index][1])
                    index = index+1
            # reset index
            index = 0
            i = i+1

    if Failed is False:
        Failed = []
        index = 0
        i = 0
        while index < len(df10):
            Failed.append(None)
            index = index+1
    elif Failed is True:
        index = 0
        i = 0
        Failed = []
        for column in list(df10):
            if column == "Failed":
                df10 = list(df10[column].items())
                while index < len(df10):
                    Failed.append(df10[index][1])
                    index = index+1
            # reset index
            index = 0
            i = i+1

    if Free is False:
        Free = []
        index = 0
        i = 0
        while index < len(df11):
            Free.append(None)
            index = index+1
    elif Free is True:
        index = 0
        i = 0
        Free = []
        for column in list(df11):
            if column == "Free":
                df11 = list(df11[column].items())
                while index < len(df11):
                    Free.append(df11[index][1])
                    index = index+1
            # reset index
            index = 0
            i = i+1

    if Total_Capacity is False:
        Total_Capacity = []
        index = 0
        i = 0
        while index < len(df12):
            Total_Capacity.append(None)
            index = index+1
    elif Total_Capacity is True:
        index = 0
        i = 0
        Total_Capacity = []
        for column in list(df12):
            if column == "TotalCapacity":
                df12 = list(df12[column].items())
                while index < len(df12):
                    Total_Capacity.append(df12[index][1])
                    index = index+1
            # reset index
            index = 0
            i = i+1

    if Percent_Used is False:
        Percent_Used = []
        index = 0
        i = 0
        while index < len(df13):
            Percent_Used.append(None)
            index = index+1
    elif Percent_Used is True:
        index = 0
        i = 0
        Percent_Used = []
        for column in list(df13):
            if column == "PercentUsed":
                df13 = list(df13[column].items())
                while index < len(df13):
                    Percent_Used.append(df13[index][1])
                    index = index+1
            # reset index
            index = 0
            i = i+1

    if Percentage_Used is False:
        Percentage_Used = []
        index = 0
        i = 0
        while index < len(df14):
            Percentage_Used.append(None)
            index = index+1
    elif Percentage_Used is True:
        index = 0
        i = 0
        Percentage_Used = []
        for column in list(df14):
            if column == "PercentUsedString":
                df14 = list(df14[column].items())
                while index < len(df14):
                    Percentage_Used.append(df14[index][1])
                    index = index+1
            # reset index
            index = 0
            i = i+1

    if x is False:
        x = []
        index = 0
        i = 0
        while index < len(df15):
            x.append(None)
            index = index+1
    elif x is True:
        index = 0
        i = 0
        x = []
        for column in list(df15):
            if column == "x":
                df15 = list(df15[column].items())
                while index < len(df15):
                    x.append(df15[index][1])
                    index = index+1
            # reset index
            index = 0
            i = i+1
    
    csv_Rows = list(zip(
                    devices,    # Names of devices. Currently using "Array" for name
                    Date,
                    Array,
                    Type,
                    Division,
                    Geo,
                    Serial_Number,
                    Used,
                    Failed,
                    Free,
                    Total_Capacity,
                    Percent_Used,
                    Percentage_Used,
                    x
                ))

    with open(f'NeedsName-FastAPI-Test.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)

        # write the headers
        writer.writerow(csv_Headings)
        # write the rows
        for data in csv_Rows:
            writer.writerow(data)

    # Removes all unnecessary chars/symbols from csv file
    # reading the CSV file
    text = open("NeedsName-FastAPI-Test.csv", "r")

    #join() method combines all contents of 
    # csv file and formed as a string
    text = ''.join([i for i in text]) 

    # search and replace the contents
    text = text.replace("[None]", "") 
    text = text.replace("None", "") 
    text = text.replace("[]", "") 
    text = text.replace("[", "") 
    text = text.replace("]", "") 
    text = text.replace(f"[\'", "")
    text = text.replace(f"\']", "")
    text = text.replace(f"\'", "")

    # NeedsName.csv is the output file opened in write mode
    x = open("NeedsName-FastAPI-Test.csv","w")

    # all the replaced text is written back to NeedsName.csv file
    x.writelines(text)
    x.close()
