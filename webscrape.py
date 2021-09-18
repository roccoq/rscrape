#!/usr/bin/python3

import requests
import pandas as pd
import re
import csv

# Two Dimensional List
repeater_list = []

# Repeater Entry
repeater = []

# Repeater Header
repeater_header = ['City','State','Frequency','Callsign','Distance','Direction','Sponsor','FM','PL Tone','DCS','DMR','DMR CC','NXDN','NXDN RAN','P25','P25 NAC','D-STAR','YSF','Notes']

# Append Header to List
repeater_list.append(repeater_header)

# Repeater Query URL
nesmc_url = "https://rptr.amateur-radio.net/cgi-bin/exec.cgi"

# Web Form Data... to be implemented as options
formdata = {
        "task":"rsearch",
        "template":"nesmc",
        "dbfilter":"nesmc",
        "band":"144,222,440,",
        "sortby":"freq",
        "meth":"RPList",
        "radi":"120",
        "loca":"Providence, RI",
        "final": "Go!"
        }

# POST Form Request
nesmc_rptrs = requests.post(nesmc_url, data=formdata)

# Read HTML response and parse table
tables = pd.read_html(nesmc_rptrs.text)

# Print Table in Pandas Data Frame Format
#print(tables[2])

# Select 4th Table as its sorted by distance... to be selectable in the future
df=tables[3]

# Write Data Frame to two dimensional list
rpters = df.values.tolist()

# Remove Header from list
rpters.pop(0)

# Iterate through repater list to write in preferred format
for i in range(len(rpters)):
    
    # Initialize/clear variables
    ysf_mode = ""
    dstar_mode = ""
    nxdn_mode = ""
    nxdn_ran = ""
    dmr_mode = ""
    dmr_cc = ""
    p25_mode = ""
    p25_nac = ""
    dcs_code = ""
    fm_mode = ""

    #Seperate City State
    location = re.search(r"([A-Z][A-Za-z\. ]+),\s([A-Z]{2})", rpters[i][0])
    city = location.group(1)
    state = location.group(2)

    freq = rpters[i][1] 

    if 'nan' in str(rpters[i][2]):
        pltone = ""
    else:
        pltone = rpters[i][2]
        fm_mode = "TRUE"

    call = rpters[i][3] 

    distdir = re.search(r"([0-9]{1,3}.[0-9])([EWNS][EW]{0,1}|)", rpters[i][4])
    dist = distdir.group(1)
    direct = distdir.group(2)

    sponsor = rpters[i][5]
    notes = rpters[i][6] 

    if re.search("DCS\(", notes, re.IGNORECASE):
        fm_mode = "TRUE"
        code = re.search(r"DCS\(([0-9]{1,3})\)", notes)
        if code:
            dcs_code = code.group(1)
    if re.search('fusion', notes, re.IGNORECASE):
        ysf_mode = "TRUE"
    if re.search('d-star', notes, re.IGNORECASE):
        dstar_mode = "TRUE"
    if re.search('nxdn', notes, re.IGNORECASE):
        nxdn_mode = "TRUE"
        code = re.search(r"NXDN\:(RAN[0-9]{1}|)", notes)
        if code:
            nxdn_ran = code.group(1)
    if re.search('dmr', notes, re.IGNORECASE):
        dmr_mode = "TRUE"
        code = re.search(r"DMR\:([C]{2,4}[0-9]{1,2}|)", notes)
        if code:
            dmr_cc = code.group(1)
    if re.search('p25', notes, re.IGNORECASE):
        p25_mode = "TRUE"
        code = re.search(r"P25\:NAC[:]{0,1}([0-9]{3}|)", notes)
        if code:
            p25_nac = code.group(1)

    # Build Repeater Entry
    repeater = []
    repeater.append(city)
    repeater.append(state)
    repeater.append(freq)
    repeater.append(call)
    repeater.append(dist)
    repeater.append(direct)
    repeater.append(sponsor)
    repeater.append(fm_mode)
    repeater.append(pltone)
    repeater.append(dcs_code)
    repeater.append(dmr_mode)
    repeater.append(dmr_cc)
    repeater.append(nxdn_mode)
    repeater.append(nxdn_ran)
    repeater.append(p25_mode)
    repeater.append(p25_nac)
    repeater.append(dstar_mode)
    repeater.append(ysf_mode)
    repeater.append(notes)

    # Append Repeater Entry to List
    repeater_list.append(repeater)

# Print Repeaters
#print(*repeater_list, sep='\n')

# Write repeater list to csv
with open('nesmc.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)

    # write multiple rows
    writer.writerows(repeater_list)
