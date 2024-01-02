# rscrape
Web scraping for amateur radio repeaters

Depends:
- python3
- python3-pandas

Install Pandas:
- Debian: apt install python3-pandas --no-install-recommends

USAGE:
```
webscrape.py [options]

Required Options
     -c --city       city to search from i.e. Boston...
                     must put in quotes if city is multi word i.e. "New Bedford"
     -s --state      state to search from, must be two letter postal abbreviation i.e. MA
     -r --radius     distance in miles to search from City, State i.e. 35
     -b --bands      bands to search valid values are 29, 50, 144, 222, 440, 902, 1296
                         must not have any spaces between commas when passing the option
                         i.e. 144,222,440 i.e. 144,440,1296

Optional:
     -o --outputfile name of csv file to write i.e. -o repeaters.csv
                         if not outputfile is selected writes to repeaters.csv
     -f --filter     filter output based on the type of repeater desired
                         valid modes are fm ysf dmr dstar nxdn p25
                         i.e. -f ysf,dmr i.e. nxdn,p2f,dstar, etc
                         if no filter is selected the default is to print all repeaters in radius
     -k --oneper     only output closest repeater per a given frequency')
     -p --chirp      prints an additional csv file that is CHIRP format The CHIRP file has
                         CHIRP_ added to the beginning of the file name. i.e. CHIRP_repeaters.csv
                         chirp option works with FM analog repeaters ONLY
     -z --search     search each repeater entry for the indicated text and only print matches, case sensitive
                         this feature is particularly useful when searching for linked networks using the notes,
                         callsign, sponsor, etc. *** Chirp output only contains a subset of data and results
                         will differ from the primary repeater CSV data file
                         i.e. -z "NB1RI"
```
