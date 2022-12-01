import configparser
import csv
from itertools import zip_longest
import os
import time
from fastapi import FastAPI
from loguru import logger
import pandas as pd
import requests


app = FastAPI(
    title = "Capacity Storage",
    description= "Downloads data from NocoDB as CSV"
)

config = configparser.ConfigParser()
config.read('config.ini')
url = config.get('noco', 'url')
API_TOKEN = config.get('noco', 'xc-auth')
CONTENT_TYPE = 'application/json'

@logger.catch
@app.get("/NocoDB/array/")
async def get_Array_Names(limit: int):
    URL = url + f"testTable/groupby?column_name=Array&limit={limit}&offset=0&shuffle=0"

    header = {
        'xc-auth': API_TOKEN,
        "accept": CONTENT_TYPE
        }

    response = requests.get(URL, headers=header)
    response = response.json()

    arrayList = []
    for dicts in response['list']:
        for keys, values in dicts.items():
            if keys == 'Array':
                arrayList.append(values)

    # returns list of all Arrays available
    return arrayList

@logger.catch
@app.get("/NocoDB/geo/")
async def get_Geo_Locations(limit: int):
    URL = url + f"testTable/groupby?column_name=Geo&limit={limit}&offset=0&shuffle=0"

    header = {
        'xc-auth': API_TOKEN,
        "accept": CONTENT_TYPE
        }

    response = requests.get(URL, headers=header)
    response = response.json()
    
    geoList = []
    for dicts in response['list']:
        for keys, values in dicts.items():
            if keys == 'Geo':
                geoList.append(values)

    # returns list of all Geo Locations available
    return geoList

@logger.catch
@app.get("/NocoDB/division/")
async def get_Divisions(limit: int):
    URL = url + f"testTable/groupby?column_name=Division&limit={limit}&offset=0&shuffle=0"

    header = {
        'xc-auth': API_TOKEN,
        "accept": CONTENT_TYPE
        }

    response = requests.get(URL, headers=header)
    response = response.json()
    
    divisionList = []
    for dicts in response['list']:
        for keys, values in dicts.items():
            if keys == 'Division':
                divisionList.append(values)

    # returns list of all Divisions available
    return divisionList

@logger.catch
@app.get("/NocoDB/type/")
async def get_Types(limit: int):
    URL = url + f"testTable/groupby?column_name=Type&limit={str(limit)}&offset=0&shuffle=0"

    header = {
        'xc-auth': API_TOKEN,
        "accept": CONTENT_TYPE
        }

    response = requests.get(URL, headers=header)
    response = response.json()
    
    typeList = []
    for dicts in response['list']:
        for keys, values in dicts.items():
            if keys == 'Type':
                typeList.append(values)

    # returns list of all Types available
    return typeList


@logger.catch
@app.get("/NocoDB/filter/")
async def get_Storage_Capacity_Reportings(array_name: str,
                                          start_date: str, 
                                          end_date: str,
                                          Array: bool = False,
                                          Type: bool = False,
                                          Division: bool = False,
                                          Geo: bool = False,
                                          Serial_Number: bool = False,
                                          Used: bool = False,
                                          Failed: bool = False,
                                          Free: bool = False,
                                          Total_Capacity: bool = False,
                                          Percent_Used: bool = False,
                                          Percentage_Used: bool = False,
                                          x: bool = False):
    
    fields = {'Array': 'Array', 'created_at': 'created_at', 'Type': 'Type', 'Division': 'Division',
              'Geo': 'Geo', 'SerialNumber': 'SerialNumber', 'Used': 'Used', 'Failed': 'Failed', 'Free': 'Free',
              'TotalCapacity': 'TotalCapacity', 'PercentUsed': 'PercentUsed', 'PercentUsedString': 'PercentUsedString', 'x': 'x'}

    # this dictionary holds respective string and boolean values. The key names are used as csv column names
    dict = {
        "created_at": start_date,
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

    csv_Headings = []
    for k in dict.keys():
        csv_Headings.append(k)

    
    table_url = url + 'testTable/?'
    table = f"&where=(Array,eq,{array_name})"
    table_url = table_url + table

    header = {
        'xc-auth': API_TOKEN,
        "accept": CONTENT_TYPE
        }
    try:
        response = requests.get(table_url, headers=header)
        response = response.json()

        
        df = pd.DataFrame(response['list'])

        start_date = start_date + " 00:00:00" # 00:00:00
        end_date = end_date + " 23:59:59"     # 23:59:59

        # Filters DataFrame rows between two dates
        data = (df['created_at'] >= start_date) & (df['created_at'] <= end_date)
        df = df.loc[data]

        Date_ = []
        Array_ = []
        Type_ = []
        Division_ = []
        Geo_ = []
        Serial_Number_ = []
        Used_ = []
        Failed_ = []
        Free_ = []
        Total_Capacity_ = []
        Percent_Used_ = []
        Percentage_Used_ = []
        x_ = []


        for columns in fields.values():
            for data_ofColumns in df[f'{columns}']:
                if columns == "created_at":
                    Date_.append(data_ofColumns)
                elif columns == "Array":
                    Array_.append(data_ofColumns)
                elif columns == "Type" and dict['Type'] is True:
                    Type_.append(data_ofColumns)
                elif columns == "Division" and dict['Division'] is True:
                    Division_.append(data_ofColumns)
                elif columns == "Geo" and dict['Geo'] is True:
                    Geo_.append(data_ofColumns)
                elif columns == "SerialNumber" and dict['Serial Number'] is True:
                    Serial_Number_.append(data_ofColumns)
                elif columns == "Used" and dict['Used'] is True:
                    Used_.append(data_ofColumns)
                elif columns == "Failed" and dict['Failed'] is True:
                    Failed_.append(data_ofColumns)
                elif columns == "Free" and dict['Free'] is True:
                    Free_.append(data_ofColumns)
                elif columns == "TotalCapacity" and dict['Total Capacity'] is True:
                    Total_Capacity_.append(data_ofColumns)
                elif columns == "PercentUsed" and dict['Percent Used'] is True:
                    Percent_Used_.append(data_ofColumns)
                elif columns == "PercentUsedString" and dict['Percent Used (%)'] is True:
                    Percentage_Used_.append(data_ofColumns)
                elif columns == "x" and dict['x'] is True:
                    x_.append(data_ofColumns)
        

        csv_Rows = list(zip_longest(
                            Date_,
                            Array_,
                            Type_,
                            Division_,
                            Geo_,
                            Serial_Number_,
                            Used_,
                            Failed_,
                            Free_,
                            Total_Capacity_,
                            Percent_Used_,
                            Percentage_Used_,
                            x_
                        ))

        DTIME = time.strftime("%Y_%m_%d_%H")
        with open(os.path.join(f'{DTIME}_report.csv'), 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)

            # write the headers
            writer.writerow(csv_Headings)
            # write the rows
            for write_data in csv_Rows:
                writer.writerow(write_data)

        # Removes all unnecessary chars/symbols from csv file
        # reading the CSV file
        text = open(os.path.join(f'{DTIME}_report.csv'), "r")

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
        x = open(os.path.join(f'{DTIME}_report.csv'),"w")

        # all the replaced text is written back to NeedsName.csv file
        x.writelines(text)
        x.close()
        return{
            "message": "CSV has been successfully downloaded!"
        }
    except:
        return{
            "message": "Failed to download data into CSV file, please try again. The data does not exist or the information received is incorrect..."
        }
