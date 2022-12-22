<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
<!-- Unsure how to link
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/CC-Digital-Innovation/Capacity-Reporting">
    <img src="images/CC_Logo.PNG" alt="Logo" width="250" height="100">
  </a>

<h3 align="center">Capacity Reporting</h3>

  <p align="center">
    Pulls Storage Capacity information from all customer storage arrays and creates a CSV
    <br />
    <a href="https://github.com/CC-Digital-Innovation/Capacity-Reporting"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/CC-Digital-Innovation/Capacity-Reporting">View Demo Presentation TBD</a>
    ·
    <a href="https://github.com/CC-Digital-Innovation/Capacity-Reporting/issues">Report Bug</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#usage">Usage</a>
      <ul>
        <li><a href="#how">How</a></li>
      </ul>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#report">Report Script</a></li>
    <li><a href="#endpoints">API Endpoints</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#history">History</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
    <li><a href="#license">License</a></li>
    </li>
  </ol>
</details>

---

<!-- ABOUT THE PROJECT -->
## Usage

Utilizes the report script to gather capacity reporting for XtremIO, Pure Storage, Vmax and Data Domain devices. This is configurable with lookup.json edits and config.ini edits. The data gathered from the script can be saved to a local file, a fileshare folder, and is also saved to [NocoDB](https://www.nocodb.com/). With the database, the end user can retrieve device data as a CSV file using the API endpoints and also allows the end user to lookup device information.

---
## How
<center>
<a href="https://github.com/CC-Digital-Innovation/Capacity-Reporting">
    <img src="images/Diagram.PNG" alt="Logo" width="650" height="750">
  </a>
</center>

---

### Built With

[![Python][Python]][Python-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>


---
<!-- GETTING STARTED -->
## Getting Started

### Prerequisites
1. [Python version 3.7.14+](https://www.python.org/downloads/)
2. Install `requirements.txt`
3. NocoDB Authorization Token

---

## Installation
### Clone the repository
   ```sh
   git clone https://github.com/CC-Digital-Innovation/Capacity-Reporting.git
  ```

### Install `requirements.txt`
```sh
pip install -r requirements.txt
```
`NOTE:` The following will be installed
* [FastAPI version 0.88.0](https://fastapi.tiangolo.com/)
* [loguru version 0.6.0](https://pypi.org/project/loguru/)
* [Pandas version 1.5.2](https://pandas.pydata.org/)
* [requests version 2.28.1](https://pypi.org/project/requests/2.8.1/)
* [Uvicorn 0.20.0](https://www.uvicorn.org/)
* [python-dotenv](https://pypi.org/project/python-dotenv/)

---

## Report
### <b>Automation</b>
Report.py can be scheduled via a task manager service (Windows Task Manager, cronjob etc). The script iterates over devices outlined in lookup.json and depending on device type, will do the following:

- Gather capcity information for the given device
- calculate percentages and normalize all data to gigabytes
- Gather drive status for given arrays drives
- write data to a csv file and put that file in either a netshare folder, local folder, both or niether
- Sends all data to NoCo DB for history retrieval

### <b>XtremIO devices</b>
report.py calls on xtremio api to gather information about the devices capacity. user name and password authentication is used and credentials are in lookup.json

### <b>Pure Storage devices</b>
report.py calls on Pure storage api to gather information about the devices capacity. user name and password is used to get a token to authorize a session and credentials are outlined in lookup.json
### <b>VMAX devices</b>
VMAX devices require symcli setup on the machine that report is running from. The symcli interface has a configuration file that each device will need to be configured for. SAMPLE CONFIG PENDING
report.py uses subproccess calls to symcli which is set up to run connections to vmax machines. the sym cli call uses an sid and a device name configured in the symcli configuration. thse are outlined in lookup.json for vmax devices only

### <b>Data Domain Devices</b>
similarly to Pure and XtremIO devices, the data doman api is leveraged to get capacity data. STILL IN PROGRESS: failed drives from data domain is not easliy found in the data domain api. user name and password are used to generate an api token and token is used to authenticate api calls. credentials are found in lookup.json

---

## Endpoints
### <b>/NocoDB/array/</b>

This endpoint takes in an integer value and will return the amount of Arrays stored in the database.
 Note: It will only return as many Arrays available, so exceeding the number can return a smaller count since there may not be that many Arrays available (which would ultimately result in returning every available Array).

### <b>/NocoDB/geo/</b>

This endpoint takes in an integer value and will return the amount of Geo locations stored in the database.
 Note: It will only return as many Geo locations available, so exceeding the number can return a smaller count since there may not be that many Geo locations available (which would ultimately result in returning every available Geo location).

### <b>/NocoDB/division/</b>

This endpoint takes in an integer value and will return the amount of Divisions stored in the database.
 Note: It will only return as many Divisions available, so exceeding the number can return a smaller count since there may not be that many Divisions available (which would ultimately result in returning every available Division).

### <b>/NocoDB/type/</b>

This endpoint takes in an integer value and will return the amount of Types stored in the database.
 Note: It will only return as many Types available, so exceeding the number can return a smaller count since there may not be that many Types available (which would ultimately result in returning every available Type).

### <b>/NocoDB/filter</b>

This endpoint requires an Array name (can be found by running the Array 'GET' endpoint), a start/end date range for a specified data set retrieval. Each column field is optional to include in the CSV file. Select true if the data is to be included or select false to ignore the data:

<b>Example:</b>

* start_date and end_date set to 2022-11-17
* choose true for columns wanted in the CSV file (but can also be set to false if the column is not needed)
* An added bonus is the Get_All_Data option, where if set to true, then the rest of the columns can be skipped, and the CSV file will contain every column with all the data for that device's start/end date range

---

<!-- ROADMAP -->
## Roadmap
<p> 1. TBD
</p>
<p>
2. TBD
</p>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---
<!-- HISTORY -->
## History
<p>version 0.1 (info) - 2022/MM/DD</p>
<p>version 0.2 (info) - 2022/MM/DD</p>
<p>version 0.3 (info) - 2022/MM/DD</p>

---
<!-- CONTACT -->
## Contact

Alex Barraza - [@sabarraz](https://github.com/sabarraz) - alex.barraza@computacenter.com

Ben Verley - [@bverley92](https://github.com/@bverley92) - ben.verley@computacenter.com

Project Link: [https://github.com/CC-Digital-Innovation/Capacity-Reporting](https://github.com/CC-Digital-Innovation/Capacity-Reporting)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments
[Jonny Le](jonny.le@computacenter.com)

[Richard Bocchinfuso](richard.bocchinfuso@computacenter.com)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---
<!-- LICENSE -->
## License

MIT License

Copyright (c) [2022] [Computacenter]

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/CC-Digital-Innovation/D42.svg?style=for-the-badge
[contributors-url]: https://github.com/CC-Digital-Innovation/D42/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/CC-Digital-Innovation/D42.svg?style=for-the-badge
[forks-url]: https://github.com/CC-Digital-Innovation/D42/network/members
[stars-shield]: https://img.shields.io/github/stars/CC-Digital-Innovation/D42.svg?style=for-the-badge
[stars-url]: https://github.com/CC-Digital-Innovation/D42/stargazers
[issues-shield]: https://img.shields.io/github/issues/CC-Digital-Innovation/D42.svg?style=for-the-badge
[issues-url]: https://github.com/CC-Digital-Innovation/D42/issues
[license-shield]: https://img.shields.io/github/license/CC-Digital-Innovation/D42.svg?style=for-the-badge
[license-url]: https://github.com/CC-Digital-Innovation/D42/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/alex-barraza-474289192
[product-screenshot]: images/screenshot.png
[Python]: https://img.shields.io/badge/python-000000?style=for-the-badge&logo=python&logoColor=green
[Python-url]: https://www.python.org/
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB