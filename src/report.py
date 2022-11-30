import requests
import json
import subprocess
import csv
import io
import os
import configparser
import datetime

#GLOBALS
CWD = os.path.dirname(__file__)
CONFIGDIR=os.path.join(CWD,'config')
CONFIGPATH=os.path.join(CONFIGDIR,'config.ini')
MODULESPATH = os.path.join(CWD,'modules')
GB = ((1/1024)/1024)
time = datetime.datetime.now()
DTIME = time.strftime("%Y%m%d%H")
config = configparser.ConfigParser()
config.read(CONFIGPATH)
NOCOKEY = config.get('noco', 'api_key')
NOCOURL = config.get('noco', 'urlbulk')
CSVPATH = config.get('datapath', 'netpath')

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

#fucntion to write single device csvs
def csvfunc(content, filename):
    with open(filename, 'w', newline = '') as file:
        write = csv.DictWriter(file, content.keys())
        write.writeheader()
        write.writerow(content)

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

            #Get list of disks and then iterate over them to get failed disks
            rdisks = requests.get(f'https://{ip}/api/json/v3/types/local-disks', auth=(usr, passw), headers=headers, verify =False)
            count = 0
            for disk in rdisks.json()['local-disks']:
                r2 = requests.get(disk['href'], auth=(usr, passw), headers=headers, verify =False)
                if r2.json()['content']['fru-lifecycle-state'] == 'failed':
                    count = count +1

            #calls helper function to make dictionary and adds to running list
            xtremiodict = makedict(device, round(used*GB, 3), count, round(freespace*GB, 3), round(float(totcap)*GB, 3), rawpercent, percentuse)
            alldata.append(xtremiodict)

            #write singlecsv
            csvfunc(xtremiodict['csvdict'], os.path.join(CSVPATH, f"{device['Name']}.csv"))


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
            puredict = makedict(device, usedspace*1024, 0, freespace*1024, totalspace*1024, float(puredata['PercUsed']), float(puredata['Used(%)']))
            alldata.append(puredict)
            #write singlecsv
            csvfunc(puredict['csvdict'], os.path.join(CSVPATH, f"{device['Name']}.csv"))

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
                        vmaxdict = makedict(device, float(split[3])*1024, 0, float(split[2])*1024, float(split[1])*1024, percused, percused*100)
                        
                        #write singlecsv
                        csvfunc(vmaxdict['csvdict'], os.path.join(CSVPATH, f"{device['Name']}.csv"))

            #Get Failed drives
            symdisk = subprocess.run(["symdisk", "-sid", f"{device['sid']}", "list", "-failed"], capture_output=True)
            symdiskout = symcli.stdout.decode()
            for line in io.StringIO(symdiskout):
                if "Disks Selected" in line:
                    split = line.split()
                    driveno = split[-1]
                else:
                    driveno = "0"

            vmaxdict['csvdict']['Failed'] = driveno
            vmaxdict['nocodict']['Failed'] = driveno
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
            usedDD = (float(system.json()['physical_capacity']['used'])*GB)/1024
            totalDD = (float(system.json()['physical_capacity']['total'])*GB)/1024
            freespaceDD = (float(system.json()['physical_capacity']['available'])*GB)/1024
            rawpercentDD=round(1-(freespaceDD/totalDD), 4)
            percentuseDD = rawpercentDD*100

            DDdict =  makedict(device, round(usedDD, 3), 0, round(freespaceDD, 3), round(totalDD, 3), rawpercentDD, percentuseDD)
            alldata.append(DDdict)

            #write singlecsv
            csvfunc(DDdict['csvdict'], os.path.join(CSVPATH, f"{device['Name']}.csv"))

    #Writes csv data based on data added to csv list
    nocodata=[]
    with open(os.path.join(CSVPATH, f'report.csv'), "w", newline = '') as f:
        writer = csv.DictWriter(f, alldata[0]['csvdict'].keys())
        writer.writeheader()
        for row in alldata:
            nocodata.append(row['nocodict'])
            writer.writerow(row['csvdict'])
    
    #post data to noco in bulk
    header = {
        'xc-token' : NOCOKEY,
        'Content-Type' : 'application/json'
    }

    response = requests.post(NOCOURL + 'testTable', headers=header, data = json.dumps(nocodata))
    print(response)


    

if __name__== "__main__":
        main()
