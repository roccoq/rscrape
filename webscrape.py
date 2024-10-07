#!/usr/bin/python3

import sys, getopt
import requests
import pandas as pd
import re
import csv
from io import StringIO
from pprint import pprint

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
   print ('     -k --oneper     only output closest repeater per a given frequency')
   print ('     -p --chirp      prints an additional csv file that is CHIRP format The CHIRP file has')
   print ('                         CHIRP_ added to the beginning of the file name. i.e. CHIRP_repeaters.csv')
   print ('                         chirp option works with FM analog repeaters ONLY')
   print ('     -q --dbfilter   select which database to query the valid choices are :')
   print ('                         nerep -> New England Repeater Directory')
   print ('                         nesmc -> New England Spectrum Managment Council')
   print ('                         csma  -> Connecticut Spectrum Management Association')
   print ('                         nyrep -> New York Repeader Directory')
   print ('                         neny  -> New England and New York Repeater Directories combined (DEFAULT)')
   print ('     -x --xnotes     print extended notes in comments field, does not apply to chirp output')
   print ('     -z --search     search each repeater entry for the indicated text and only print matches, case sensitive ')
   print ('                         this feature is particularly useful when searching for linked networks using the notes,')
   print ('                         callsign, sponsor, etc. *** Chirp output only contains a subset of data and results')
   print ('                         will differ from the primary repeater csv data file')
   print ('                         i.e. -z "NB1RI"')

   sys.exit(exit_code)

def updatewebformdata(formdata, city,state,radius,bands, numperfreq, dbfilter):

    location = city + ", " + state
    bandlist = bands + ","

    formupdate = { "loca":location,
                   "radi":radius,
                   "band":bandlist,
                   "freq":numperfreq,
                   "dbfilter":dbfilter
                   }
    formdata.update(formupdate)

def processrepeaterdata(rpters, repeater_list, rfilter, chirp, chirpcount, chirprepeater, chirprepeaterlist, searchfilter, exnotes, DEBUG):
    
    valid_pls = ['67.0', '69.3', '71.9', '74.4', '77.0', '79.7', '82.5', '85.4', '88.5', '91.5', '94.8', '97.4', '100.0', '103.5', '107.2', '110.9', '114.8', '118.8', '123.0', '127.3', '131.8', '136.5', '141.3', '146.2', '151.4', '156.7', '162.2', '167.9', '173.8', '179.9', '186.2', '192.8', '203.5', '206.5', '210.7', '218.1', '225.7', '229.1', '233.6', '241.8', '250.3', '254.1']
    valid_dcs = []

    # Iterate through repater list to write in preferred format
    for i in range(len(rpters)):

        if DEBUG == True:
           print(rpters[i])

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
        ex_notes = ""
        fm_tone_mode = ""
        tx_power = "Low"

        # Seperate City, State and populate variables
        location = re.search(r"([A-Z][A-Za-z\.\/ ]+),\s([A-Z]{2})", rpters[i][0])
        city = location.group(1)
        state = location.group(2)

        # Get Frequency
        freq = rpters[i][1]

        # Get offset and offset direction
        offsetinfo = []
        offsetinfo = determineoffset(freq)
        offset = offsetinfo['offset']
        offset_dir = offsetinfo['offset_dir']

        # Get Repeater Callsign
        if 'nan' in str(rpters[i][3]):
            call="EMPTY"
        else:
            call = rpters[i][3]

        # Seperate Distance and Direction and populate variables
        distdir = re.search(r"([0-9]{1,3}.[0-9])([EWNS][EW]{0,1}|)", rpters[i][4])
        dist = distdir.group(1)
        direct = distdir.group(2)

        # Get Repeater Sponsor
        sponsor = rpters[i][5]

        if 'nan' not in str(rpters[i][2]):
            # Determine if NXDN Capable in PL Section
            if re.search('nxdn', rpters[i][2], re.IGNORECASE):
                nxdn_mode = "TRUE"

            # Determine if YSF Capable in PL Section
            if re.search('ysf', rpters[i][2], re.IGNORECASE):
                ysf_mode = "TRUE"
        
            # Determine if D-Star Capable in PL Section
            if re.search('d-star', rpters[i][2], re.IGNORECASE):
                ysf_mode = "TRUE"

            # Determine if DMR Capable in PL Section
            if re.search('dmr', rpters[i][2], re.IGNORECASE):
                dmr_mode = "TRUE"

            # Determine if DMR Capable in PL Section
            if re.search('p25', rpters[i][2], re.IGNORECASE):
                p25_mode = "TRUE"
                
        # Get Repeater Notes
        notes = rpters[i][6]
        if 'nan' in str(notes):
            notes="EMPTY"
        else:
            # Determine if C4FM Capable
            if re.search('fusion', notes, re.IGNORECASE):
                ysf_mode = "TRUE"

            if re.search('ysf', notes, re.IGNORECASE):
                ysf_mode = "TRUE"

            # Determine if D-STAR Capable
            if re.search('d-star', notes, re.IGNORECASE):
                dstar_mode = "TRUE"
           
            # Get NXDN RAN if defined
            if re.search('nxdn', notes, re.IGNORECASE):
                nxdn_mode = "TRUE"

            if nxdn_mode == "TRUE":
                code = re.search(r"RAN[0-9]{1,2}", notes)
                if code:
                    nxdn_ran = code.group(0)
                    

            # Determine if DMR Capable and set CC
            if re.search('dmr', notes, re.IGNORECASE):
                dmr_mode = "TRUE"
            
            if dmr_mode == "TRUE":  
                code = re.search(r"[C]{2,4}[0-9]{1,2}", notes)
                if code:
                    dmr_cc = code.group(0)

            # Determine if P25 Capable and ser NAC
            if re.search('p25', notes, re.IGNORECASE):
                p25_mode = "TRUE"

            if p25_mode == "TRUE": 
                code = re.search(r"(NAC\:|NAC)([0-9]{3,4}|)", notes)
                if code:
                    p25_nac = code.group(1) + " " + code.group(2)

        # Determine if Analog FM capable and set PL Tone
        if 'nan' in str(rpters[i][2]):
            pltone = ""
        else:
            if re.search(r"[6-9]{1}[0-9]{1}\.[0-9]{1}|[1-2]{1}[0-9]{2}\.[0-9]{1}", rpters[i][2], re.IGNORECASE):
               code = re.search(r"[6-9]{1}[0-9]{1}\.[0-9]{1}|[1-2]{1}[0-9]{2}\.[0-9]{1}", rpters[i][2], re.IGNORECASE)
               pltone = code.group(0)
               fm_mode = "TRUE"
               fm_tone_mode = "Tone" 
            else:
                pltone = ""

        # Find PL in notes
        if notes != "EMPTY":    
            if re.search(r"[6-9]{1}[0-9]{1}\.[0-9]{1}|[1-2]{1}[0-9]{2}\.[0-9]{1}", notes, re.IGNORECASE):
                code = re.search(r"[6-9]{1}[0-9]{1}\.[0-9]{1}|[1-2]{1}[0-9]{2}\.[0-9]{1}", notes, re.IGNORECASE)
                if code:
                    if code.group(0) in valid_pls:
                        fm_mode = "TRUE"
                        pltone = code.group(0)
                        fm_tone_mode = "Tone"
        

        # Determine if FM Analog Capable and set DCS
        if notes != "EMPTY":    
            if re.search(r"DCS\(", notes, re.IGNORECASE):
                fm_mode = "TRUE"
                code = re.search(r"DCS\(([0-9]{1,3})\)", notes)
                if code:
                    dcs_code = code.group(1)
                    fm_tone_mode = "DCS"

            if re.search(r"D[1-9][0-9]{2}", notes, re.IGNORECASE):
                fm_mode = "TRUE"
                code = re.search(r"D([1-9][0-9]{2})", notes)
                if code:
                    dcs_code = code.group(1)
                    fm_tone_mode = "DCS"

        # Some stations are FM and dont have a PL or DCS
        # Adding logic for these stations
        if ysf_mode != "TRUE" and dstar_mode != "TRUE" and nxdn_mode != "TRUE" and p25_mode != "TRUE" and dmr_mode != "TRUE" and fm_mode != "TRUE":
            fm_mode = "TRUE"

        # Extended Notes
        if DEBUG == True:
           print(call)
        if notes != "EMPTY":
            ex_notes = city + "," + state + "," + call + "," + notes

        # Build Repeater Entry
        repeater = []
        repeater.append(city)
        repeater.append(state)
        repeater.append(freq)
        repeater.append(str(offset))
        repeater.append(offset_dir)
        repeater.append(call)
        repeater.append(dist)
        repeater.append(direct)
        repeater.append(sponsor)
        repeater.append(fm_mode)
        repeater.append(pltone)
        repeater.append(dcs_code)
        repeater.append(fm_tone_mode)
        repeater.append(dmr_mode)
        repeater.append(dmr_cc)
        repeater.append(nxdn_mode)
        repeater.append(nxdn_ran)
        repeater.append(p25_mode)
        repeater.append(p25_nac)
        repeater.append(dstar_mode)
        repeater.append(ysf_mode)
        repeater.append(tx_power)

        if exnotes == True:
            repeater.append(ex_notes)
        else:
            repeater.append(notes)

        # If chirp option is ture build chirp list
        if chirp == True and fm_mode == "TRUE":
            chirprepeater = []
            chirprepeater.append(str(chirpcount))
            chirprepeater.append(call)
            chirprepeater.append(freq)
            chirprepeater.append(offset_dir)
            chirprepeater.append("%.6f" % abs(float(offset)))
            if dcs_code and not dcs_code.isspace():
                chirprepeater.append("DTCS")
            else:
                chirprepeater.append("Tone")
            if pltone and not pltone.isspace():
                chirprepeater.append(pltone)
                chirprepeater.append(pltone)
            else:
                chirprepeater.append("88.5")
                chirprepeater.append("88.5")
            if dcs_code and not dcs_code.isspace():
                chirprepeater.append(dcs_code)
            else:
                chirprepeater.append("023")
            chirprepeater.append("NN")
            chirprepeater.append("FM")
            chirprepeater.append("5.00")
            chirprepeater.append("")
            chirprepeater.append(dist + " :: " + call + " :: " + city + " " + state + " :: " + notes)
            chirprepeater.append("")
            chirprepeater.append("")
            chirprepeater.append("")
            chirprepeater.append("")

        # Build Chirp list
        if chirp == True and fm_mode == "TRUE":
            if searchfilter != '':
                if any(searchfilter in s for s in chirprepeater):
                    chirpbuild(chirprepeater, chirprepeaterlist)
            else:
                chirpbuild(chirprepeater, chirprepeaterlist)
                chirpcount += 1


        # Append filtered output
        if searchfilter != '':
            if any(searchfilter in s for s in repeater):
                filteroutput(rfilter, repeater, repeater_list)
        else:
            filteroutput(rfilter, repeater, repeater_list)

def determineoffset(freq_string):

    # Convert String to Float for comparison
    freq=float(freq_string)

    if freq >= 51 and freq <= 51.99:
        offset = -0.500000
        offset_dir = "-"
        return {'offset': offset, 'offset_dir': offset_dir}

    if freq >= 52 and freq <= 54:
        offset = -1.000000
        offset_dir = "-"
        return {'offset': offset, 'offset_dir': offset_dir}

    if freq >= 144.51 and freq <= 144.89:
        offset = 0.600000
        offset_dir = "+"
        return {'offset': offset, 'offset_dir': offset_dir}

    if freq >= 145.11 and freq <= 145.49:
        offset = -0.600000
        offset_dir = "-"
        return {'offset': offset, 'offset_dir': offset_dir}

    if freq >= 146.0 and freq <= 146.39:
        offset = 0.600000
        offset_dir = "+"
        return {'offset': offset, 'offset_dir': offset_dir}

    if freq >= 146.4 and freq <= 146.5:
        offset = -1.500000
        offset_dir = "-"
        return {'offset': offset, 'offset_dir': offset_dir}

    if freq >= 146.61 and freq <= 146.99:
        offset = -0.600000
        offset_dir = "-"
        return {'offset': offset, 'offset_dir': offset_dir}

    if freq >= 147.0 and freq <= 147.39:
        offset = 0.600000
        offset_dir = "+"
        return {'offset': offset, 'offset_dir': offset_dir}

    if freq >= 147.6 and freq <= 147.99:
        offset = -0.600000
        offset_dir = "-"
        return {'offset': offset, 'offset_dir': offset_dir}

    if freq >= 223 and freq <= 225:
        offset = -1.600000
        offset_dir = "-"
        return {'offset': offset, 'offset_dir': offset_dir}

    if freq >= 440 and freq <= 444.99:
        offset = 5.000000
        offset_dir = "+"
        return {'offset': offset, 'offset_dir': offset_dir}

    if freq >= 445 and freq <= 450:
        offset = -5.000000
        offset_dir = "-"
        return {'offset': offset, 'offset_dir': offset_dir}

    if freq >= 918 and freq <= 922:
        offset = -12.000000
        offset_dir = "-"
        return {'offset': offset, 'offset_dir': offset_dir}

    if freq >= 927 and freq <= 928:
        offset = -25.000000
        offset_dir = "-"
        return {'offset': offset, 'offset_dir': offset_dir}

    # If not in list return 0
    return {'offset': 0, 'offset_dir': "off"}

def filteroutput(rfilter, repeater, repeater_list):
    #print (rfilter)
    if "all" in rfilter:
        repeater_list.append(repeater)
        return
    if "fm" in rfilter:
        if repeater[9] == "TRUE":
            repeater_list.append(repeater)
            return
    if "ysf" in rfilter:
        if repeater[19] == "TRUE":
            repeater_list.append(repeater)
            return
    if "dmr" in rfilter:
        if repeater[12] == "TRUE":
            repeater_list.append(repeater)
            return
    if "dstar" in rfilter:
        if repeater[18] == "TRUE":
            repeater_list.append(repeater)
            return
    if "p25" in rfilter:
        if repeater[16] == "TRUE":
            repeater_list.append(repeater)
            return
    if "nxdn" in rfilter:
        if repeater[14] == "TRUE":
            repeater_list.append(repeater)
            return

def chirpbuild(chirprepeater, chirprepeaterlist):
    chirprepeaterlist.append(chirprepeater)

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
   searchfilter = ''
   numperfreq = ''
   dbfilter = 'neny'

   # extended notes
   exnotes = False

   # chirp
   chirp = False

   # Chirp list index
   chirpcount=0

   # Two Dimensional List
   repeater_list = []

   # Chirp Repeater list
   chirprepeaterlist = []

   # Repeater Entry
   repeater = []

   # Chirp Repeaters
   chirprepeater = []

   # Repeater Header
   repeater_header = ['City','State','Frequency','Offset','OffsetDir','Callsign','Distance','Direction','Sponsor','FM','PL Tone','Tone Mode','DCS','DMR','DMR CC','NXDN','NXDN RAN','P25','P25 NAC','D-STAR','YSF','TX Power','Notes']

   # Chirp Repeater repeater_header
   chirprepeaterlist_header = ['Location','Name','Frequency','Duplex','Offset','Tone','rToneFreq','cToneFreq','DtcsCode','DtcsPolarity','Mode','TStep','Skip','Comment','URCALL','RPT1CALL','RPT2CALL','DVCODE']

   # Append Header to List
   repeater_list.append(repeater_header)

   # Append Chrp Header to list
   chirprepeaterlist.append(chirprepeaterlist_header)

   # Repeater Query URL
   nesmc_url = "https://rptr.amateur-radio.net/cgi-bin/exec.cgi"

   # Web Form Data
   formdata = {
           "task":"rsearch",
           "template":"nesmc",
           "band":"",
           "sortby":"freq",
           "meth":"RPList",
           "radi":"",
           "loca":"",
           "freq":"",
           "final": "Go!"
        }

   # Process options
   try:
       opts, args = getopt.getopt(argv,"hdc:s:r:b:f:po:z:kxq:",["debug=","city=","state=","radius=","bands=","filter=","chirp","outputfile=","search=","oneper","xnotes","dbfilter"])
   except getopt.GetoptError:
      print("SYNTAX ERROR!")
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
         #print (rfilter)
      elif opt in ("-p", "--chirp"):
         chirp = True
      elif opt in ("-o", "--outputfile"):
         outputfile = arg
      elif opt in ("-z", "--search"):
         searchfilter = arg
      elif opt in ("-k", "--oneper"):
         numperfreq = "1per"
      elif opt in ("-x", "--xnotes"):
         exnotes = True
      elif opt in ("-q", "--dbfilter"):
         dbfilter = arg

   if DEBUG == True:
      print ('City is "', city)
      print ('State is "', state)
      print ('Radius is "', radius)
      print ('Band(s) is/are "', bands)
      print ('Output file is "', outputfile)
      print ('Filter(s) is/are"', rfilter)
      print ('OnePer is "', numperfreq)
      print ('dbfilter is"', dbfilter)

   # Create Webform Data
   if dbfilter == "neny":
      updatewebformdata(formdata, city, state, radius, bands, numperfreq, "nerep")
      nerep_rptrs = requests.post(nesmc_url, data=formdata)
      updatewebformdata(formdata, city, state, radius, bands, numperfreq, "nyrep")
      nyrep_rptrs = requests.post(nesmc_url, data=formdata)

      # Read HTML response and parse table
      tables_nerep = pd.read_html(StringIO(nerep_rptrs.text))
      tables_nyrep = pd.read_html(StringIO(nyrep_rptrs.text))

      # Print Table in Pandas Data Frame Format
      if DEBUG == True:
         print("TABLES NEREP")
         print(tables_nerep)
         print("TABLES NYEP")
         print(tables_nyrep[1])

      # Select 4th Table as its sorted by distance... to be selectable in the future
      df_nerep=tables_nerep[1]
      df_nyrep=tables_nyrep[1]

      # Drop first row which is header information
      df_nerep = df_nerep.drop(index=0)
      df_nyrep = df_nyrep.drop(index=0)

      frames = [df_nerep, df_nyrep]
      df = pd.concat(frames)
      df.columns = ["CITY", "FREQ", "PL", "CALL", "DIST", "SPONSOR", "NOTES"]
      df_sorted = (df.sort_values(by=['FREQ']))
      pprint(df_sorted)

      # Write Data Frame to two dimensional list
      rpters = df_sorted.values.tolist()
   else:
      updatewebformdata(formdata, city, state, radius, bands, numperfreq, dbfilter)

      if DEBUG == True:
         print (formdata)

      # POST Form Request
      nesmc_rptrs = requests.post(nesmc_url, data=formdata)

      # Read HTML response and parse table
      tables = pd.read_html(StringIO(nesmc_rptrs.text))

      # Print Table in Pandas Data Frame Format
      if DEBUG == True:
         print(tables[2])

      # Select 4th Table as its sorted by distance... to be selectable in the future
      df=tables[1]

      # Write Data Frame to two dimensional list
      rpters = df.values.tolist()

      # Remove Header from list
      rpters.pop(0)

   # Process Repeater Data
   processrepeaterdata(rpters, repeater_list, rfilter, chirp, chirpcount, chirprepeater, chirprepeaterlist, searchfilter, exnotes, DEBUG)

   # Print Repeaters
   if DEBUG == True:
       print(*repeater_list, sep='\n')

   # Write repeater list to csv
   with open(outputfile, 'w', encoding='UTF8', newline='') as f:
       writer = csv.writer(f)

       # write multiple rows
       writer.writerows(repeater_list)

   # Chirp Repeater list
   if chirp == True:
          # Write chirp list to csv
          with open("CHIRP_" + outputfile, 'w', encoding='UTF8', newline='') as g:
              writerchirp = csv.writer(g)

              # write multiple rows
              writerchirp.writerows(chirprepeaterlist)


if __name__ == "__main__":
   main(sys.argv[1:])
