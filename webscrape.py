#!/usr/bin/python3

import sys, getopt
import requests
import pandas as pd
import re
import csv

def helpmessage(exit_code):
   print ('webscrape.py [options]')
   print (' ')
   print ('Required Options')
   print ('     -c --city       city to search from i.e. Boston...')
   print ('                     must put in quotes if city is multi word i.e. "New Bedford"') 
   print ('     -s --state      state to search from, must be two letter postal abbreviation i.e. MA')
   print ('     -r --radius     distance in miles to search from City, State i.e. 35')
   print ('     -b --bands      bands to search valid values are 29, 50, 144, 222, 440, 902, 1296')
   print ('                         must not have any spaces between commas when passing the option')
   print ('                         i.e. 144,222,440 i.e. 144,440,1296')
   print (' ')
   print ('Optional:')
   print ('     -o --outputfile name of csv file to write i.e. -o repeaters.csv')
   print ('                         if not outputfile is selected writes to repeaters.csv')
   print ('     -f --filter     filter output based on the type of repeater desired')
   print ('                         valid modes are fm ysf dmr dstar nxdn p25')
   print ('                         i.e. -f ysf,dmr i.e. nxdn,p2f,dstar, etc')
   print ('                         if no filter is selected the default is to print all repeaters in radius')
   sys.exit(exit_code)

def updatewebformdata(formdata, city,state,radius,bands):

    location = city + ", " + state
    bandlist = bands + ","

    formupdate = { "loca":location,
                   "radi":radius,
                   "band":bandlist
                   }
    formdata.update(formupdate)
                   
def processrepeaterdata(rpters, repeater_list, rfilter):
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

        # Seperate City, State and populate variables
        location = re.search(r"([A-Z][A-Za-z\. ]+),\s([A-Z]{2})", rpters[i][0])
        city = location.group(1)
        state = location.group(2)

        # Get Frequency
        freq = rpters[i][1] 

        # Get Repeater Callsign
        call = rpters[i][3] 

        # Seperate Distance and Direction and populate variables
        distdir = re.search(r"([0-9]{1,3}.[0-9])([EWNS][EW]{0,1}|)", rpters[i][4])
        dist = distdir.group(1)
        direct = distdir.group(2)

        # Get Repeater Sponsor
        sponsor = rpters[i][5]

        # Get Repeater Notes
        notes = rpters[i][6] 

        # Determine if C4FM Capable        
        if re.search('fusion', notes, re.IGNORECASE):
            ysf_mode = "TRUE"

        # Determine if D-STAR Capable    
        if re.search('d-star', notes, re.IGNORECASE):
            dstar_mode = "TRUE"

        # Determine if NXDN Capable and set RAN    
        if re.search('nxdn', notes, re.IGNORECASE):
            nxdn_mode = "TRUE"
            code = re.search(r"NXDN\:(RAN[0-9]{1}|)", notes)
            if code:
                nxdn_ran = code.group(1)

        # Determine if DMR Capable and set CC        
        if re.search('dmr', notes, re.IGNORECASE):
            dmr_mode = "TRUE"
            code = re.search(r"DMR\:([C]{2,4}[0-9]{1,2}|)", notes)
            if code:
                dmr_cc = code.group(1)

        # Determine if P25 Capable and ser NAC        
        if re.search('p25', notes, re.IGNORECASE):
            p25_mode = "TRUE"
            code = re.search(r"P25\:NAC[:]{0,1}([0-9]{3}|)", notes)
            if code:
                p25_nac = code.group(1)

        # Determine if Analog FM capable and set PL Tone
        if 'nan' in str(rpters[i][2]):
            pltone = ""
        else:
            pltone = rpters[i][2]
            fm_mode = "TRUE"

        # Determine if FM Analog Capable and set DCS
        if re.search("DCS\(", notes, re.IGNORECASE):
            fm_mode = "TRUE"
            code = re.search(r"DCS\(([0-9]{1,3})\)", notes)
            if code:
                dcs_code = code.group(1)

        # Some stations are FM and dont have a PL or DCS
        # Adding logic for these stations
        if ysf_mode != "TRUE" and dstar_mode != "TRUE" and nxdn_mode != "TRUE" and p25_mode != "TRUE" and dmr_mode != "TRUE" and fm_mode != "TRUE":
            fm_mode = "TRUE"

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

        # Append filtered output
        filteroutput(rfilter, repeater, repeater_list)


def filteroutput(rfilter, repeater, repeater_list):
    print (rfilter)
    if "all" in rfilter:
        repeater_list.append(repeater)
        return
    if "fm" in rfilter:
        if repeater[7] == "TRUE":
            repeater_list.append(repeater)
            return
    if "ysf" in rfilter:
        if repeater[17] == "TRUE":
            repeater_list.append(repeater)
            return
    if "dmr" in rfilter:
        if repeater[10] == "TRUE":
            repeater_list.append(repeater)
            return
    if "dstar" in rfilter:
        if repeater[16] == "TRUE":
            repeater_list.append(repeater)
            return
    if "p25" in rfilter:
        if repeater[14] == "TRUE":
            repeater_list.append(repeater)
            return
    if "nxdn" in rfilter:
        if repeater[12] == "TRUE":
            repeater_list.append(repeater)
            return


def main(argv):

   DEBUG = False

   # Default Values
   city = 'Providence'
   state = 'RI'
   radius = '50'
   bands = '144,440'
   rfilter = ["all"]
   rfilterlist = []
   outputfile ="repeaters.csv"

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

   # Web Form Data
   formdata = {
           "task":"rsearch",
           "template":"nesmc",
           "dbfilter":"nesmc",
           "band":"",
           "sortby":"freq",
           "meth":"RPList",
           "radi":"",
           "loca":"",
           "final": "Go!"   
        }

   # Process options
   try:
       opts, args = getopt.getopt(argv,"hdc:s:r:b:f:o:",["DEBUG=","city=","state=","radius=","bands=","filter=","outputfile="])
   except getopt.GetoptError:
      helpmessage(2)
   for opt, arg in opts:
      if opt == '-h':
          helpmessage(0)
      elif opt in ("-d", "--debug"):
            DEBUG = True
      elif opt in ("-c", "--city"):
            city = arg
      elif opt in ("-s", "--state"):
         state = arg
      elif opt in ("-r", "--radius"):
         radius = arg
      elif opt in ("-b", "--bands"):
         bands = arg
      elif opt in ("-f", "--filter"):
         rfilter.pop(0)
         rfilterlist = list(arg.split(","))
         rfilter = rfilterlist
         print (rfilter)
      elif opt in ("-o", "--outputfile"):
         outputfile = arg

   if DEBUG == True:         
      print ('City is "', city)
      print ('State is "', state)
      print ('Radius is "', radius)
      print ('Band(s) is/are "', bands)
      print ('Output file is "', outputfile)
      print ('Filter(s) is/are"', rfilter)

   # Create Webform Data
   updatewebformdata(formdata, city, state, radius, bands)

   if DEBUG == True:
      print (formdata)

   # POST Form Request
   nesmc_rptrs = requests.post(nesmc_url, data=formdata)

   # Read HTML response and parse table
   tables = pd.read_html(nesmc_rptrs.text)

   # Print Table in Pandas Data Frame Format
   if DEBUG == True:
      print(tables[2])

   # Select 4th Table as its sorted by distance... to be selectable in the future
   df=tables[3]

   # Write Data Frame to two dimensional list
   rpters = df.values.tolist()
  
   # Process Repeater Data
   processrepeaterdata(rpters, repeater_list, rfilter)

   # Print Repeaters
   if DEBUG == True:
       print(*repeater_list, sep='\n')

   # Write repeater list to csv
   with open(outputfile, 'w', encoding='UTF8', newline='') as f:
       writer = csv.writer(f)

       # write multiple rows
       writer.writerows(repeater_list)

if __name__ == "__main__":
   main(sys.argv[1:])


