import csv
from itertools import zip_longest
import os
from pathlib import PurePath
import secrets
import time
import dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import APIKeyHeader
from loguru import logger
import pandas as pd
import requests
import pika
import configparser


# Title and description of 'Capacity Reporting'.
app = FastAPI(
    title = "Capacity Storage",
    description= "Downloads data from NocoDB as CSV"
)

# Load secrets from .env
dotenv.load_dotenv(PurePath(__file__).with_name('.env'))

# Set constant variables for the headers.
url = os.getenv('URL')
API_TOKEN = os.getenv('API_KEY_NOCO')
API_KEY = os.getenv('API_KEY')
CONTENT_TYPE = 'application/json'

# Authorization Token.
api_key = APIKeyHeader(name='X-API-Key')

# Will only allow end user to use the API if the Authorization Token matches.
# Otherwise, it will return 'Invalid Token' and response code.
def authorize(key: str = Depends(api_key)):
    if not secrets.compare_digest(key, API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token')


# [GET] Array name(s). Integer value taken to retrieve that many arrays if exists, otherwise, it will return up-to or the exact number.
@logger.catch
@app.get("/NocoDB/array/", dependencies=[Depends(authorize)])
async def get_Array_Names(limit: int):
    URL = url + f"testTable/groupby?column_name=Array&limit={limit}&offset=0&shuffle=0"

    header = {
        'xc-token': API_TOKEN,
        "accept": CONTENT_TYPE
        }

    # Will try to request the Array information with the header provided. If feasible, then the Array(s) will return.
    try:
        response = requests.get(URL, headers=header)
        response = response.json()
        
        # Appends all Array(s) found into the 'arrayList' and return the list to end user.
        arrayList = []
        for dicts in response['list']:
            for keys, values in dicts.items():
                if keys == 'Array':
                    arrayList.append(values)

        # Returns list of all Arrays available
        return arrayList

    # Otherwise, if the request for the Array information is invalid, then a return message will be provided to the end user.
    except:
        return{
            "message": "Failed to retrieve. The data does not exist or the information received is incorrect..."
        }


# [GET] Geo Location(s). Integer value taken to retrieve the Geo Location(s) if exist, otherwise, it will return up-to or the exact number.
@logger.catch
@app.get("/NocoDB/geo/", dependencies=[Depends(authorize)])
async def get_Geo_Locations(limit: int):
    URL = url + f"testTable/groupby?column_name=Geo&limit={limit}&offset=0&shuffle=0"

    header = {
        'xc-token': API_TOKEN,
        "accept": CONTENT_TYPE
        }

    # Will try to request the Geo Location information with the header provided. If feasible, then the Geo Location(s) will return.
    try:
        response = requests.get(URL, headers=header)
        response = response.json()
        
        # Appends all Geo Location(s) found into the 'geoList' and return the list to end user.
        geoList = []
        for dicts in response['list']:
            for keys, values in dicts.items():
                if keys == 'Geo':
                    geoList.append(values)

        # returns list of all Geo Locations available
        return geoList

    # Otherwise, if the request for the Geo Location information is invalid, then a return message will be provided to the end user.
    except:
        return{
            "message": "Failed to retrieve. The data does not exist or the information received is incorrect..."
        }
        

# [GET] Division(s). Integer value taken to retrieve the Division(s) if exist, otherwise, it will return up-to or the exact number.
@logger.catch
@app.get("/NocoDB/division/", dependencies=[Depends(authorize)])
async def get_Divisions(limit: int):
    URL = url + f"testTable/groupby?column_name=Division&limit={limit}&offset=0&shuffle=0"

    header = {
        'xc-token': API_TOKEN,
        "accept": CONTENT_TYPE
        }

    # Will try to request the Division information with the header provided. If feasible, then the Division(s) will return.
    try:
        response = requests.get(URL, headers=header)
        response = response.json()
        
        # Appends all Division(s) found into the 'divisionList' and return the list to end user.
        divisionList = []
        for dicts in response['list']:
            for keys, values in dicts.items():
                if keys == 'Division':
                    divisionList.append(values)

        # returns list of all Divisions available
        return divisionList

    # Otherwise, if the request for the Division information is invalid, then a return message will be provided to the end user.
    except:
        return{
            "message": "Failed to retrieve. The data does not exist or the information received is incorrect..."
        }


# [GET] Type(s). Integer value taken to retrieve the Type(s) if exist, otherwise, it will return up-to or the exact number.
@logger.catch
@app.get("/NocoDB/type/", dependencies=[Depends(authorize)])
async def get_Types(limit: int):
    URL = url + f"testTable/groupby?column_name=Type&limit={str(limit)}&offset=0&shuffle=0"

    header = {
        'xc-token': API_TOKEN,
        "accept": CONTENT_TYPE
        }

    # Will try to request the Type information with the header provided. If feasible, then the Type(s) will return.
    try:
        response = requests.get(URL, headers=header)
        response = response.json()
        
        # Appends all Type(s) found into the 'typeList' and return the list to end user.
        typeList = []
        for dicts in response['list']:
            for keys, values in dicts.items():
                if keys == 'Type':
                    typeList.append(values)

        # returns list of all Types available
        return typeList

    # Otherwise, if the request for the Type information is invalid, then a return message will be provided to the end user.
    except:
        return{
            "message": "Failed to retrieve. The data does not exist or the information received is incorrect..."
        }


# [GET] Allows end user to get all data, or filter column fields to retrieve only information wanted using an
#       Array name with a start/end date range.
@logger.catch
@app.get("/NocoDB/filter/", dependencies=[Depends(authorize)])
async def get_Storage_Capacity_Reportings(array_name: str,
                                          start_date: str, 
                                          end_date: str,
                                          Get_All_Data: bool = False,
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

    # Dictionary holds respective string and boolean values. The key names are used as csv column names
    dict = {
        "created_at": start_date,
        "Array": True,
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

    # Appends the column names into the list to be used in the CSV
    csv_Headings = []
    for k in dict.keys():
        csv_Headings.append(k)

    # URL endpoint to query the Array Name
    table_url = url + 'testTable/?'
    table = f"&where=(Array,eq,{array_name})"
    table_url = table_url + table

    header = {
        'xc-token': API_TOKEN,
        "accept": CONTENT_TYPE
        }

    # Will try to request the query with the header provided and initiate the process of getting data needed to produce a CSV file.
    try:
        response = requests.get(table_url, headers=header)
        response = response.json()

        # Stores the data into DataFrame
        df = pd.DataFrame(response['list'])

        start_date = start_date + " 00:00:00" # 00:00:00
        end_date = end_date + " 23:59:59"     # 23:59:59

        # Filters DataFrame rows between two dates
        data = (df['created_at'] >= start_date) & (df['created_at'] <= end_date)
        df = df.loc[data]

        # Lists are used to append content of each column
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


        # If True, all data for each column will be returned.
        if Get_All_Data is True:
            for keys in dict.keys():
                dict[keys] = True

        # Appends data into lists if the end user wants that specific column's data in the CSV file by selecting 'True'.
        # 'created_at' and 'Array' are always True, regardless if the entire CSV file is empty.
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
        

        # zip() function allows each list to pair next to each other in sequential order.
        # The lists become the rows for the columns.
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

        # Creates a CSV file and includes a timestamp for the file name.
        DTIME = time.strftime("%Y_%m_%d_%H")
        with open(os.path.join(f'{DTIME}_report.csv'), 'w', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)

            # Write the headers.
            writer.writerow(csv_Headings)

            # Write the rows.
            for write_data in csv_Rows:
                writer.writerow(write_data)

        # Reading the CSV file and placing inside 'text' variable.
        text = open(os.path.join(f'{DTIME}_report.csv'), "r")

        # join() method combines all contents of 
        # CSV file and formed as a string
        text = ''.join([i for i in text]) 

        # Search and replace the contents (unnecessary information).
        text = text.replace("[None]", "") 
        text = text.replace("None", "") 
        text = text.replace("[]", "") 
        text = text.replace("[", "") 
        text = text.replace("]", "") 
        text = text.replace(f"[\'", "")
        text = text.replace(f"\']", "")
        text = text.replace(f"\'", "")

        # Opens output file in write mode inside variable 'x'.
        x = open(os.path.join(f'{DTIME}_report.csv'),"w")

        # All the replaced text is written back to CSV file.
        x.writelines(text)
        x.close()

        # Allows end user to download CSV file
        headers = {'Content-Disposition': f'attachment; filename={DTIME}_report.csv'}
        return FileResponse(os.path.join(os.getcwd(), f'{DTIME}_report.csv'), media_type="text/csv", headers=headers)

    # Otherwise, if the request is invalid, then a return message will be provided to the end user.
    except:
        return{
            "message": "Failed to download data into CSV file, please try again. The data does not exist or the information received is incorrect..."
        }

@logger.catch
@app.post("/NocoDB/runReport/", dependencies=[Depends(authorize)])
async def run_report(report: str):
    #init config variabled - note this will move to vaults data soon
    cwd = os.path.dirname(__file__)
    configdir=os.path.join(cwd,'config')
    configpath=os.path.join(configdir,'config.ini')
    config = configparser.ConfigParser()
    config.read(configpath)
    rabbmquser = config.get('messageq', 'rmquser')
    rabbmqpass = config.get('messageq', 'rmqpass')
    rabbmqip = config.get('messageq', 'rmqip')
    rabbmqport = config.get('messageq', 'rmqport')

    #connect to mq pod
    creds = pika.PlainCredentials(rabbmquser, rabbmqpass)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbmqip, port=rabbmqport, credentials= creds))
    channel = connection.channel()

    #
    channel.queue_declare(queue=config.get('messageq', 'customer'))

    #send message to queue and close connection
    channel.basic_publish(exchange='', routing_key=config.get('messageq', 'customer'), body=f'Run {report} Report')
    print(f" [x] Sent {report} request to {config.get('messageq', 'customer')} queue")
    connection.close()