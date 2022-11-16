import requests
import json
import subprocess
import csv
import io
import os
import configparser
import datetime

#GLOBALS
CWD = os.getcwd()
CONFIGDIR=os.path.join(CWD,'config')
CONFIGPATH=os.path.join(CONFIGDIR,'config.ini')
CSVPATH = os.path.join(CWD,'CSVData')
MODULESPATH = os.path.join(CWD,'modules')
TB = ((1/1024)/1024)/1024
time = datetime.datetime.now()
DTIME = time.strftime("%Y_%m_%d_%H")
config = configparser.ConfigParser()
config.read(CONFIGPATH)
NOCOKEY = config.get('noco', 'api_key')
NOCOURL = config.get('noco', 'url')

#Helper function to define dictionary after getting each data set from a device
def makedict(device, used, failed, freespace, totalcap, rawpercent, percentage):
    fulldict = {
            'csvdict': {
                'Date'           : DTIME,
                'Array'          : device['Name'],
                'Type'           : device['type'],
                'Division'       : device['Division'],
                'Geo'            : device['Geo'],
                'Serial Number'  : device['SN'],
                'Used'           : used,
                'Failed'         : failed,
                'Free'           : freespace,
                'Total Capacity' : totalcap,
                'Percent Used'   : round(rawpercent, 4),
                'Percent Used(%)': round(percentage, 2)
        },
            'nocodict' : {
                'Date'              : f"{DTIME}",
                'Array'             : device['Name'],
                'Type'              : device['type'],
                'Division'          : device['Division'],
                'Geo'               : device['Geo'],
                'SerialNumber'      : device['SN'],
                'Used'              : used,
                'Failed'            : failed,
                'Free'              : freespace,
                'TotalCapacity'     : totalcap,
                'PercentUsed'       : round(rawpercent, 4),
                'PercentUsedString' : round(percentage, 2)
        }
    }

    return fulldict

#Main code
def main():
    #Read lookup file and initialize csvdata array
    alldata = []
    with open(os.path.join(CONFIGDIR, 'lookup.json'), "r") as lookupfile:
        lookup = json.load(lookupfile)

    #iterate over all the devices in the lookup
    for ip in lookup['IPS'].keys():
        device = lookup['IPS'][ip]

        #XtremIO Devices
        if device['type'] == "XtremIO":
            #initialize REST header and device data
            headers = {
                'Content-Type': 'application/json'
            }
            ipaddr = ip
            usr = device['username']
            passw = device['password']

            #Get and parse results from xtremio clusters endpoint
            r = requests.get(f'https://{ip}/api/json/v3/types/clusters/1', auth=(usr, passw), headers=headers, verify =False)
            totcap = r.json()['content']['ud-ssd-space']
            totuse = r.json()['content']['logical-space-in-use']
            reduc  = r.json()['content']['data-reduction-ratio']

            #calc percentages and free space
            used = float(totuse)/float(reduc)
            freespace=float(totcap)-used
            rawpercent=1-(freespace/float(totcap))
            percentuse = rawpercent*100

            #calls helper function to make dictionary and adds to running list
            xtremiodict = makedict(device, round(used*TB, 3), 0, round(freespace*TB, 3), round(float(totcap)*TB, 3), rawpercent, percentuse)
            alldata.append(xtremiodict)
            #xtremiodict={}

        #Pure Storage Devices
        elif device['type']=="Pure":
            #initialize device data
            ipaddr = ip
            username = device['username']
            password = device['password']
            #Run ps script to get pure device capacity metrics. Rounds data retrieved NOTE: This will likely move to a REST call in the future
            pureps1 =subprocess.run(["Powershell.exe", "-File", f'{os.path.join(MODULESPATH, "pure.ps1")}', f"{ip}", f"{username}", f"{password}"], capture_output=True)
            pureps1out= pureps1.stdout.decode('utf-8')
            data = list(csv.DictReader(io.StringIO(pureps1out)))
            puredata=data[0]
            usedspace  = round(float(puredata['Used']), 3)
            freespace  = round(float(puredata['Free']), 3)
            totalspace = round(float(puredata['Capacity']), 3)
            
            #Calls helper function to make dict and adds to running list
            puredict = makedict(device, usedspace, 0, freespace, totalspace, float(puredata['PercUsed']), float(puredata['Used(%)']))
            alldata.append(puredict)

        #VMAX
        elif device['type']=="VMAX":
            #Runs symcli commands to retrieve data. NO IP, USER/PASS REQUIRED HERE
            os.environ[f"SYMCLI_CONNECT"] =device['symcli']
            subprocess.run(["symcfg", "discover"])
            symcli = subprocess.run(["symcfg", "-sid", f"{device['sid']}", "list", "-pool", "-thin",  "-TB"], capture_output=True)
            symcliout = symcli.stdout.decode()

            #Searches output of symcli for the line that starts with TBs (has capacity totals)
            #Splits TBs line for required data
            #Sends data to helper function and adds dictionary to running list
            for line in io.StringIO(symcliout):
                split = line.split()
                if split:
                    if split[0] == 'TBs':
                        percused=1-(float(split[2])/float(split[1]))
                        vmaxdict = makedict(device, float(split[3]), 0, float(split[2]), float(split[1]), percused, percused*100)
                        alldata.append(vmaxdict)

        #Data Domain
        elif device['type']=="DataDomain":
            #Needs to get API key to give to subsequent endpoints from auth endpoint
            headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
            }
            creds = {
                "username" : f"{device['username']}",
                "password" : f"{device['password']}"
            }
            auth = requests.post(f'https://{ip}:3009/rest/v1.0/auth' , headers=headers, data = json.dumps(creds), verify =False)
            headers['X-DD-AUTH-TOKEN']=auth.headers['X-DD-AUTH-TOKEN']
            system = requests.get(f'https://{ip}:3009/rest/v1.0/system' , headers=headers, verify =False)
            
            #calc percentages
            usedDD = (float(system.json()['physical_capacity']['used'])*TB)/1024
            totalDD = (float(system.json()['physical_capacity']['total'])*TB)/1024
            freespaceDD = (float(system.json()['physical_capacity']['available'])*TB)/1024
            rawpercentDD=round(1-(freespaceDD/totalDD), 4)
            percentuseDD = rawpercentDD*100

            DDdict = makedict(device, round(usedDD, 3), 0, round(freespaceDD, 3), round(totalDD, 3), rawpercentDD, percentuseDD)
            alldata.append(DDdict)

    #Writes csv data based on data added to csv list
    nocodata=[]
    with open(os.path.join(CSVPATH, f'{DTIME}_report.csv'), "w") as f:
        writer = csv.DictWriter(f, alldata[0]['csvdict'].keys())
        writer.writeheader()
        for row in alldata:
            nocodata.append(row['nocodict'])
            writer.writerow(row['csvdict'])
    
    #post data to noco in bulk
    header = {
        'xc-auth' : NOCOKEY,
        'Content-Type' : 'application/json'
    }

    #response = requests.post(NOCOURL, headers=header, data = json.dumps(nocodata))



    

if __name__== "__main__":
        main()
