#!/usr/bin/python3

"""Web scraping tool for amateur radio repeaters.

Fetches data from regional directories, processes modes/tones, outputs to CSV/CHIRP.
"""

import argparse
import csv
import logging
import re
import sys
from io import StringIO
from typing import Any

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Version info
__version__ = "0.90.2"  # Formatting


def updatewebformdata(
    formdata: dict[str, str],
    city: str,
    state: str,
    radius: str,
    bands: str,
    numperfreq: str,
    dbfilter: str,
) -> None:
    # def updatewebformdata(formdata, city, state, radius, bands, numperfreq, dbfilter):
    """Update the web form data dictionary with search parameters.

    Args:
        formdata (dict): The form data dictionary to update.
        city (str): The city to search from.
        state (str): The two-letter state abbreviation.
        radius (str): The search radius in miles.
        bands (str): Comma-separated list of bands to search.
        numperfreq (str): Option for number of repeaters per frequency.
        dbfilter (str): The database filter to use.

    Returns:
        None: Updates the formdata in place.
    """

    location = city + ", " + state
    bandlist = bands + ","

    formupdate = {
        "loca": location,
        "radi": radius,
        "band": bandlist,
        "freq": numperfreq,
        "dbfilter": dbfilter,
    }
    formdata.update(formupdate)


# def processrepeaterdata(
#    rpters,
#    repeater_list,
#    rfilter,
#    chirp,
#    chirpcount,
#    chirprepeater,
#    chirprepeaterlist,
#    searchfilter,
#    exnotes,
#    DEBUG,
#    tx_power,
#    ams_mode,
# ):
def processrepeaterdata(
    rpters: list[list[Any]],
    repeater_list: list[list[Any]],
    rfilter: list[str],
    chirp: bool,
    chirpcount: int,
    chirprepeater: list[Any],
    chirprepeaterlist: list[list[Any]],
    searchfilter: str,
    exnotes: bool,
    DEBUG: bool,
    tx_power: str,
    ams_mode: str,
) -> None:
    """Process raw repeater data into formatted entries for output.

    Args:
        rpters (list): List of raw repeater data entries.
        repeater_list (list): List to append processed repeater entries.
        rfilter (list): List of mode filters (e.g., ['fm', 'ysf']).
        chirp (bool): Flag to generate CHIRP format output.
        chirpcount (int): Counter for CHIRP location indexing.
        chirprepeater (list): Temporary list for building CHIRP entry.
        chirprepeaterlist (list): List to append CHIRP entries.
        searchfilter (str): Text to search for in repeater entries.
        exnotes (bool): Flag to include extended notes.
        DEBUG (bool): Flag for debug printing.
        tx_power (str): Transmit power level.
        ams_mode (str): AMS mode version ('v1' or 'v2').

    Returns:
        None: Modifies repeater_list and chirprepeaterlist in place.
    """
    valid_pls = [
        "67.0",
        "69.3",
        "71.9",
        "74.4",
        "77.0",
        "79.7",
        "82.5",
        "85.4",
        "88.5",
        "91.5",
        "94.8",
        "97.4",
        "100.0",
        "103.5",
        "107.2",
        "110.9",
        "114.8",
        "118.8",
        "123.0",
        "127.3",
        "131.8",
        "136.5",
        "141.3",
        "146.2",
        "151.4",
        "156.7",
        "162.2",
        "167.9",
        "173.8",
        "179.9",
        "186.2",
        "192.8",
        "203.5",
        "206.5",
        "210.7",
        "218.1",
        "225.7",
        "229.1",
        "233.6",
        "241.8",
        "250.3",
        "254.1",
    ]

    valid_dcs = [
        "006",
        "007",
        "015",
        "017",
        "023",
        "025",
        "026",
        "031",
        "032",
        "036",
        "043",
        "047",
        "051",
        "053",
        "054",
        "065",
        "071",
        "072",
        "073",
        "074",
        "114",
        "115",
        "116",
        "122",
        "125",
        "131",
        "132",
        "134",
        "143",
        "145",
        "152",
        "155",
        "156",
        "162",
        "165",
        "172",
        "174",
        "205",
        "212",
        "223",
        "225",
        "226",
        "243",
        "244",
        "245",
        "246",
        "251",
        "252",
        "255",
        "261",
        "263",
        "265",
        "266",
        "271",
        "274",
        "306",
        "311",
        "315",
        "325",
        "331",
        "332",
        "343",
        "346",
        "351",
        "356",
        "364",
        "365",
        "371",
        "411",
        "412",
        "413",
        "423",
        "431",
        "432",
        "445",
        "446",
        "452",
        "454",
        "455",
        "462",
        "464",
        "465",
        "466",
        "503",
        "506",
        "516",
        "523",
        "526",
        "532",
        "546",
        "565",
        "606",
        "612",
        "624",
        "627",
        "631",
        "632",
        "654",
        "662",
        "664",
        "703",
        "712",
        "723",
        "731",
        "732",
        "734",
        "743",
        "754",
    ]

    # Iterate through repater list to write in preferred format
    for i in range(len(rpters)):
        if DEBUG:
            logging.debug(rpters[i])

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
        operating_mode = ""
        ams = "N"

        # Separate City, State and populate variables
        if "nan" in str(rpters[i][0]):
            city = "EMPTY"
            state = "EMPTY"
        else:
            location = re.search(r"([A-Z][A-Za-z\.\/ ]+),\s([A-Za-z]{2})", rpters[i][0])
            if location:
                city = location.group(1)
                state = location.group(2)
            else:
                city = state = "UNKNOWN"

        # Get Frequency
        if "nan" in str(rpters[i][1]):
            freq = "EMPTY"
        else:
            freq = rpters[i][1]

        # Get offset and offset direction
        # offsetinfo = []
        offsetinfo: dict[str, float | str] = determineoffset(freq)
        offset = offsetinfo["offset"]
        offset_dir = offsetinfo["offset_dir"]

        # Get Repeater Callsign
        if "nan" in str(rpters[i][3]):
            call = "EMPTY"
        else:
            call = rpters[i][3]

        # Separate Distance and Direction and populate variables
        distdir = re.search(r"([0-9]{1,3}.[0-9])([EWNS][EW]{0,1}|)", rpters[i][4])
        if distdir:
            dist = distdir.group(1)
            direct = distdir.group(2)
        else:
            dist = direct = "UNKNOWN"

        # Get Repeater Sponsor
        if "nan" in str(rpters[i][5]):
            sponsor = "EMPTY"
        else:
            sponsor = rpters[i][5]

        if "nan" not in str(rpters[i][2]):
            # Determine if NXDN Capable in PL Section
            if re.search("nxdn", rpters[i][2], re.IGNORECASE):
                nxdn_mode = "TRUE"

            # Determine if YSF Capable in PL Section
            if re.search("ysf", rpters[i][2], re.IGNORECASE):
                ysf_mode = "TRUE"

            # Determine if D-Star Capable in PL Section
            if re.search("d-star", rpters[i][2], re.IGNORECASE):
                dstar_mode = "TRUE"

            # Determine if DMR Capable in PL Section
            if re.search("dmr", rpters[i][2], re.IGNORECASE):
                dmr_mode = "TRUE"

            # Determine if DMR Capable in PL Section
            if re.search("p25", rpters[i][2], re.IGNORECASE):
                p25_mode = "TRUE"

        # Get Repeater Notes
        notes = rpters[i][6]
        if "nan" in str(notes):
            notes = "EMPTY"
        else:
            # Determine if C4FM Capable
            ysf_match = re.search(r"ysf|fusion", notes, re.IGNORECASE)
            if ysf_match:
                ysf_mode = "TRUE"

            # Determine if D-STAR Capable
            dstar_match = re.search("d-star", notes, re.IGNORECASE)
            if dstar_match:
                dstar_mode = "TRUE"

            # Get NXDN RAN if defined
            nxdn_match = re.search("nxdn", notes, re.IGNORECASE)
            if nxdn_match:
                nxdn_mode = "TRUE"
                code = re.search(r"RAN[0-9]{1,2}", notes)
                if code:
                    nxdn_ran = code.group(0)

            # Determine if DMR Capable and set CC
            dmr_match = re.search("dmr", notes, re.IGNORECASE)
            if dmr_match:
                dmr_mode = "TRUE"
                code = re.search(r"[C]{2,4}[0-9]{1,2}", notes)
                if code:
                    dmr_cc = code.group(0)

            # Determine if P25 Capable and set NAC
            p25_match = re.search(r"(NAC\:|NAC)([0-9]{3,4}|)", notes)

            if p25_match:
                p25_mode = "TRUE"
                if p25_match.group(2) == "":
                    nac_number = "UNKNOWN"
                else:
                    nac_number = p25_match.group(2)
                p25_nac = p25_match.group(1) + " " + nac_number

        # Determine if Analog FM capable and set PL Tone from table and then tries notes
        pltone = ""
        if "nan" in str(rpters[i][2]):
            pltone = ""
        else:
            pl_match = re.search(
                r"[6-9]{1}[0-9]{1}\.[0-9]{1}|[1-2]{1}[0-9]{2}\.[0-9]{1}",
                rpters[i][2],
                re.IGNORECASE,
            )
            if pl_match and pl_match.group(0) in valid_pls:
                pltone = pl_match.group(0)
                fm_mode = "TRUE"
                fm_tone_mode = "Tone"
            elif pltone == "":
                pl_match = re.search(
                    r"[6-9]{1}[0-9]{1}\.[0-9]{1}|[1-2]{1}[0-9]{2}\.[0-9]{1}",
                    notes,
                    re.IGNORECASE,
                )
                if pl_match and pl_match.group(0) in valid_pls:
                    fm_mode = "TRUE"
                    pltone = pl_match.group(0)
                    fm_tone_mode = "Tone"
                else:
                    pltone = ""

        # Determine if FM Analog Capable and set DCS
        if notes != "EMPTY":
            if re.search(r"DCS\(", notes, re.IGNORECASE):
                fm_mode = "TRUE"
                code = re.search(
                    r"DCS\(([0-9]{1,3})\)", notes, re.IGNORECASE
                )  # Added IGNORECASE for consistency
                if code:
                    captured = code.group(1).zfill(
                        3
                    )  # Pad to 3 digits (handles e.g., '23' -> '023')
                    if captured in valid_dcs:
                        dcs_code = captured
                        fm_tone_mode = "DCS"

            if re.search(r"D[0-9][0-9]{2}", notes, re.IGNORECASE):
                fm_mode = "TRUE"
                code = re.search(
                    r"D([0-9]{3})", notes, re.IGNORECASE
                )  # Fixed to [0-9]{3}, added IGNORECASE
                if code:
                    # Already 3 digits, no padding needed
                    captured = code.group(1)
                    if captured in valid_dcs:
                        dcs_code = captured
                        fm_tone_mode = "DCS"

        # Some stations are FM and dont have a PL or DCS
        # Adding logic for these stations
        if (
            ysf_mode != "TRUE"
            and dstar_mode != "TRUE"
            and nxdn_mode != "TRUE"
            and p25_mode != "TRUE"
            and dmr_mode != "TRUE"
            and fm_mode != "TRUE"
        ):
            fm_mode = "TRUE"

        # YSF Operating Mode
        if fm_mode:
            operating_mode = "FM"
            ams = "N"

        if ysf_mode:
            if ams_mode == "v1":
                operating_mode = "Auto"
                ams = ""
            elif ams_mode == "v2":
                operating_mode = "FM"
                ams = "Y"

        # Extended Notes
        if DEBUG:
            logging.debug(call)
        if notes != "EMPTY":
            ex_notes = city + "," + state + "," + call + "," + notes

        # Build Repeater Entry
        repeater = []
        repeater.append(city)
        repeater.append(state)
        repeater.append(freq)
        repeater.append(str(offset))
        repeater.append(str(offset_dir))
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
        repeater.append(operating_mode)
        repeater.append(ams)

        if exnotes:
            repeater.append(ex_notes)
        else:
            repeater.append(notes)

        # If chirp option is true build chirp list
        if chirp and fm_mode:
            chirprepeater = []
            # chirprepeater: list[Any] = []
            chirprepeater.append(str(chirpcount))
            chirprepeater.append(call)
            # chirprepeater.append(freq)
            chirprepeater.append(str(freq))
            chirprepeater.append(offset_dir)
            chirprepeater.append(f"{abs(float(offset)):.6f}")
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
            chirprepeater.append(
                dist + " :: " + call + " :: " + city + " " + state + " :: " + notes
            )
            chirprepeater.append("")
            chirprepeater.append("")
            chirprepeater.append("")
            chirprepeater.append("")

        # Build Chirp list
        if chirp and fm_mode:
            if searchfilter != "":
                if any(searchfilter in s for s in chirprepeater):
                    chirpbuild(chirprepeater, chirprepeaterlist)
                    chirpcount += 1
            else:
                chirpbuild(chirprepeater, chirprepeaterlist)
                chirpcount += 1

        # Append filtered output
        if searchfilter != "":
            if any(searchfilter in s for s in repeater):
                filteroutput(rfilter, repeater, repeater_list)
        else:
            filteroutput(rfilter, repeater, repeater_list)


# def determineoffset(freq_string):
def determineoffset(freq_string: str) -> dict[str, float | str]:
    """Calculate repeater offset based on frequency.

    Args:
        freq_string (str): Frequency as string.

    Returns:
        dict: {'offset': float, 'offset_dir': str}
    """

    # Convert String to Float for comparison
    try:
        # Attempt to convert freq_string to float
        freq = float(freq_string)
    except ValueError:
        # Handle the case where freq_string is not convertible to float
        logging.error(f"Error: '{freq_string}' is not a valid float string")
        return {"offset": 0, "offset_dir": "off"}

    if freq >= 51 and freq <= 51.99:
        offset = -0.500000
        offset_dir = "-"
        return {"offset": offset, "offset_dir": offset_dir}

    if freq >= 52 and freq <= 54:
        offset = -1.000000
        offset_dir = "-"
        return {"offset": offset, "offset_dir": offset_dir}

    if freq >= 144.51 and freq <= 144.89:
        offset = 0.600000
        offset_dir = "+"
        return {"offset": offset, "offset_dir": offset_dir}

    if freq >= 145.11 and freq <= 145.49:
        offset = -0.600000
        offset_dir = "-"
        return {"offset": offset, "offset_dir": offset_dir}

    if freq >= 146.0 and freq <= 146.39:
        offset = 0.600000
        offset_dir = "+"
        return {"offset": offset, "offset_dir": offset_dir}

    if freq >= 146.4 and freq <= 146.5:
        offset = -1.500000
        offset_dir = "-"
        return {"offset": offset, "offset_dir": offset_dir}

    if freq >= 146.61 and freq <= 146.99:
        offset = -0.600000
        offset_dir = "-"
        return {"offset": offset, "offset_dir": offset_dir}

    if freq >= 147.0 and freq <= 147.39:
        offset = 0.600000
        offset_dir = "+"
        return {"offset": offset, "offset_dir": offset_dir}

    if freq >= 147.6 and freq <= 147.99:
        offset = -0.600000
        offset_dir = "-"
        return {"offset": offset, "offset_dir": offset_dir}

    if freq >= 223 and freq <= 225:
        offset = -1.600000
        offset_dir = "-"
        return {"offset": offset, "offset_dir": offset_dir}

    if freq >= 440 and freq <= 444.99:
        offset = 5.000000
        offset_dir = "+"
        return {"offset": offset, "offset_dir": offset_dir}

    if freq >= 445 and freq <= 450:
        offset = -5.000000
        offset_dir = "-"
        return {"offset": offset, "offset_dir": offset_dir}

    if freq >= 918 and freq <= 922:
        offset = -12.000000
        offset_dir = "-"
        return {"offset": offset, "offset_dir": offset_dir}

    if freq >= 927 and freq <= 928:
        offset = -25.000000
        offset_dir = "-"
        return {"offset": offset, "offset_dir": offset_dir}

    # If not in list return 0
    return {"offset": 0, "offset_dir": "off"}


# def filteroutput(rfilter, repeater, repeater_list):
def filteroutput(
    rfilter: list[str], repeater: list[Any], repeater_list: list[list[Any]]
) -> None:
    """Filter and append repeater entry based on mode filters.

    Args:
        rfilter (list): List of mode filters.
        repeater (list): The repeater entry to filter.
        repeater_list (list): List to append filtered entries.

    Returns:
        None: Appends to repeater_list if matched.
    """
    matched = False
    if "fm" in rfilter and repeater[9] == "TRUE":
        matched = True
    if "ysf" in rfilter and repeater[20] == "TRUE":
        matched = True
    if "dmr" in rfilter and repeater[13] == "TRUE":
        matched = True
    if "dstar" in rfilter and repeater[19] == "TRUE":
        matched = True
    if "p25" in rfilter and repeater[17] == "TRUE":
        matched = True
    if "nxdn" in rfilter and repeater[15] == "TRUE":
        matched = True
    if "all" in rfilter or matched:
        repeater_list.append(repeater)


# def chirpbuild(chirprepeater, chirprepeaterlist):
def chirpbuild(chirprepeater: list[Any], chirprepeaterlist: list[list[Any]]) -> None:
    """Append a CHIRP-formatted repeater entry to the list.

    Args:
        chirprepeater (list): The CHIRP entry to append.
        chirprepeaterlist (list): List to append the entry.

    Returns:
        None: Appends to chirprepeaterlist.
    """
    chirprepeaterlist.append(chirprepeater)


# def main(argv):
def main(argv: list[str]) -> None:
    """Main entry point for the script, handling options and data processing.

    Args:
     argv (list): Command-line arguments.

     Returns:
         None: Processes data and writes output files.
    """

    DEBUG = False

    # Default Values
    city = "Providence"
    state = "RI"
    radius = "50"
    bands = "144,440"
    rfilter = ["all"]
    outputfile = "repeaters.csv"
    searchfilter = ""
    numperfreq = ""
    dbfilter = "neny"
    tx_power = "Low"
    ams_mode = "v1"

    # extended notes
    exnotes = False

    # chirp
    chirp = False

    # Chirp list index
    chirpcount = 0

    # Two Dimensional List
    repeater_list = []

    # Chirp Repeater list
    chirprepeaterlist = []

    # Chirp Repeaters
    chirprepeater: list[str | float] = []

    # Repeater Header
    repeater_header = [
        "City",
        "State",
        "Frequency",
        "Offset",
        "Offset Direction",
        "Name",
        "Distance",
        "Direction",
        "Sponsor",
        "FM",
        "CTCSS",
        "DCS",
        "Tone Mode",
        "DMR",
        "DMR CC",
        "NXDN",
        "NXDN RAN",
        "P25",
        "P25 NAC",
        "D-STAR",
        "YSF",
        "TX Power",
        "Operating Mode",
        "AMS",
        "Comment",
    ]

    # Chirp Repeater repeater_header
    chirprepeaterlist_header = [
        "Location",
        "Name",
        "Frequency",
        "Duplex",
        "Offset",
        "Tone",
        "rToneFreq",
        "cToneFreq",
        "DtcsCode",
        "DtcsPolarity",
        "Mode",
        "TStep",
        "Skip",
        "Comment",
        "URCALL",
        "RPT1CALL",
        "RPT2CALL",
        "DVCODE",
    ]

    # Append Header to List
    repeater_list.append(repeater_header)

    # Append Chrp Header to list
    chirprepeaterlist.append(chirprepeaterlist_header)

    # Repeater Query URL
    nesmc_url = "https://rptr.amateur-radio.net/cgi-bin/exec.cgi"

    # Web Form Data
    formdata = {
        "task": "rsearch",
        "template": "nesmc",
        "band": "",
        "sortby": "freq",
        "meth": "RPList",
        "radi": "",
        "loca": "",
        "freq": "",
        "final": "Go!",
    }

    # Process options
    parser = argparse.ArgumentParser(
        description="Web scraping for amateur radio repeaters",
        epilog="Valid bands: 29, 50, 144, 222, 440, 902, 1296. Valid filters: fm, ysf, dmr, dstar, nxdn, p25. Valid dbfilters: nerep, nesmc, csma, nyrep, nesct, neny (default). Valid amsmodes: v1 (default), v2.",
    )

    # Arguments with defaults (no required=True)
    parser.add_argument(
        "-c",
        "--city",
        default="Providence",
        help='City to search from (e.g., Boston or "New Bedford"; default: Providence)',
    )
    parser.add_argument(
        "-s",
        "--state",
        default="RI",
        help="State (two-letter postal abbreviation, e.g., MA; default: RI)",
    )
    parser.add_argument(
        "-r",
        "--radius",
        default=50,
        type=int,
        help="Search radius in miles (e.g., 35; default: 50)",
    )
    parser.add_argument(
        "-b",
        "--bands",
        default="144,440",
        help="Bands to search (comma-separated, no spaces, e.g., 144,440; default: 144,440)",
    )

    # Optional arguments
    parser.add_argument(
        "-o",
        "--outputfile",
        default="repeaters.csv",
        help="Output CSV file (default: repeaters.csv)",
    )
    parser.add_argument(
        "-f",
        "--filter",
        help="Filter by repeater type (comma-separated, e.g., ysf,dmr; default: all)",
    )
    parser.add_argument(
        "-k",
        "--oneper",
        action="store_true",
        help="Output only the closest repeater per frequency",
    )
    parser.add_argument(
        "-p",
        "--chirp",
        action="store_true",
        help="Output additional CHIRP-format CSV (for FM analog only)",
    )
    parser.add_argument(
        "-q",
        "--dbfilter",
        default="neny",
        choices=["nerep", "nesmc", "csma", "nyrep", "nesct", "neny"],
        help="Database to query (default: neny)",
    )
    parser.add_argument(
        "-x",
        "--xnotes",
        action="store_true",
        help="Print extended notes in comments field (not for CHIRP)",
    )
    parser.add_argument(
        "-z",
        "--search",
        default="",
        help='Search repeater entries for text (case-sensitive, e.g., "NB1RI"; default: "")',
    )
    parser.add_argument(
        "-a",
        "--amsmode",
        default="v1",
        choices=["v1", "v2"],
        help="AMS/Operating mode for C4FM radios i.e. FT3DR (default: v1)",
    )
    parser.add_argument(
        "-w", "--power", default="Low", help="TX power level (default: Low)"
    )
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")

    # Parse the arguments
    args = parser.parse_args()

    # Map parsed args to your existing variables
    DEBUG = args.debug
    city = args.city
    state = args.state
    radius = str(args.radius)  # Convert to str for form data
    bands = args.bands
    outputfile = args.outputfile
    rfilter = ["all"] if not args.filter else args.filter.lower().split(",")
    chirp = args.chirp
    searchfilter = args.search
    numperfreq = "1per" if args.oneper else ""
    dbfilter = args.dbfilter
    exnotes = args.xnotes
    tx_power = args.power
    ams_mode = args.amsmode

    # Configure logging at the beginning -- NEW: Setup logging
    logging.basicConfig(
        filename="webscrape.log",  # Log to file
        level=(
            logging.DEBUG if DEBUG else logging.INFO
        ),  # DEBUG level if --debug, else INFO
        # Timestamp - Level - Message
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Log debug info instead of print
    if DEBUG:
        logging.debug(f"City is {city}")
        logging.debug(f"State is {state}")
        logging.debug(f"Radius is {radius}")
        logging.debug(f"Band(s) is/are {bands}")
        logging.debug(f"Output file is {outputfile}")
        logging.debug(f"Filter(s) is/are {rfilter}")
        logging.debug(f"OnePer is {numperfreq}")
        logging.debug(f"dbfilter is {dbfilter}")
        logging.debug(f"power {tx_power}")
        logging.debug(f"amsmode {ams_mode}")

    # Radius positive
    if args.radius <= 0:
        parser.error("Radius must be positive")

    # Validate Bands
    valid_bands = {"29", "50", "144", "222", "440", "902", "1296"}
    if not all(b in valid_bands for b in bands.split(",")):
        parser.error("Invalid bands")

    # Two Leter State Abbreviation
    if not re.match(r"^[A-Z]{2}$", state):
        parser.error("State must be a two-letter code")

    # Validate Radius
    try:
        int(radius)
    except ValueError:
        logging.error("Radius must be numeric")
        sys.exit(1)

    # Validate DB Filters
    valid_dbfilters = {"nerep", "nesmc", "csma", "nyrep", "nesct", "neny"}
    if dbfilter not in valid_dbfilters:
        logging.error("Invalid dbfilter")
        sys.exit(1)

    # Validate AMS Mode
    if ams_mode not in {"v1", "v2"}:
        logging.error("amsmode must be v1 or v2")
        sys.exit(1)

    # Create a session with retry logic -- NEW: Retries added here
    session = requests.Session()
    # 3 retries, exponential backoff
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Create Webform Data
    if dbfilter == "neny":
        updatewebformdata(formdata, city, state, radius, bands, numperfreq, "nerep")
        try:
            nerep_rptrs = session.post(nesmc_url, data=formdata, timeout=10)
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            sys.exit(1)
        updatewebformdata(formdata, city, state, radius, bands, numperfreq, "nyrep")
        try:
            nyrep_rptrs = session.post(nesmc_url, data=formdata, timeout=10)
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            sys.exit(1)

        # Read HTML response and parse table
        try:
            tables_nerep = pd.read_html(StringIO(nerep_rptrs.text))
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            sys.exit(1)

        try:
            tables_nyrep = pd.read_html(StringIO(nyrep_rptrs.text))
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            sys.exit(1)

        # Print Table in Pandas Data Frame Format
        if DEBUG:
            logging.debug("TABLES NEREP")
            logging.debug(tables_nerep)
            logging.debug("TABLES NYEP")
            logging.debug(tables_nyrep)

        # Select 4th Table as its sorted by distance... to be selectable in the future

        # df_nerep=tables_nerep[1]
        # df_nyrep=tables_nyrep[1]

        if len(tables_nerep) > 1:
            df_nerep = tables_nerep[1]
        else:
            logging.error("Data changed, less tables")
            sys.exit(1)

        if len(tables_nyrep) > 1:
            df_nyrep = tables_nyrep[1]
        else:
            logging.error("Data changed, less tables")
            sys.exit(1)

        # Dynamically set columns from first row and drop it
        df_nerep.columns = df_nerep.iloc[0]
        df_nerep = df_nerep.drop(index=0).reset_index(drop=True)

        df_nyrep.columns = df_nyrep.iloc[0]
        df_nyrep = df_nyrep.drop(index=0).reset_index(drop=True)

        frames = [df_nerep, df_nyrep]
        df = pd.concat(frames)

        # Now sorts by actual 'FREQ' column name from source
        df_sorted = df.sort_values(by=["FREQ"])

        # Drop Dupes
        df_sorted = df_sorted.drop_duplicates(subset=["CALL", "FREQ"])

        # Write Data Frame to two dimensional list
        rpters = df_sorted.values.tolist()

    # Create Webform Data
    elif dbfilter == "nesct":
        updatewebformdata(formdata, city, state, radius, bands, numperfreq, "nesmc")
        try:
            nerep_rptrs = session.post(nesmc_url, data=formdata, timeout=10)
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            sys.exit(1)
        updatewebformdata(formdata, city, state, radius, bands, numperfreq, "csma")
        try:
            nyrep_rptrs = session.post(nesmc_url, data=formdata, timeout=10)
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            sys.exit(1)

        # Read HTML response and parse table
        try:
            tables_nerep = pd.read_html(StringIO(nerep_rptrs.text))
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            sys.exit(1)

        try:
            tables_nyrep = pd.read_html(StringIO(nyrep_rptrs.text))
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            sys.exit(1)

        # Print Table in Pandas Data Frame Format
        if DEBUG:
            logging.debug("TABLES NEREP")
            logging.debug(tables_nerep)
            logging.debug("TABLES NYEP")
            logging.debug(tables_nyrep)

        # Select table as its sorted by distance... to be selectable in the future
        if len(tables_nerep) > 1:
            df_nerep = tables_nerep[1]
        else:
            logging.error("Data changed, less tables")
            sys.exit(1)

        if len(tables_nyrep) > 1:
            df_nyrep = tables_nyrep[1]
        else:
            logging.error("Data changed, less tables")
            sys.exit(1)

        # Dynamically set columns from first row and drop it
        df_nerep.columns = df_nerep.iloc[0]
        df_nerep = df_nerep.drop(index=0).reset_index(drop=True)

        df_nyrep.columns = df_nyrep.iloc[0]
        df_nyrep = df_nyrep.drop(index=0).reset_index(drop=True)

        frames = [df_nerep, df_nyrep]
        df = pd.concat(frames)

        # Now sorts by actual 'FREQ' column name from source
        df_sorted = df.sort_values(by=["FREQ"])

        # Drop Dupes
        df_sorted = df_sorted.drop_duplicates(subset=["CALL", "FREQ"])

        # Write Data Frame to two dimensional list
        rpters = df_sorted.values.tolist()

    else:
        updatewebformdata(formdata, city, state, radius, bands, numperfreq, dbfilter)

        if DEBUG:
            logging.debug(formdata)

        # POST Form Request
        try:
            nesmc_rptrs = session.post(nesmc_url, data=formdata, timeout=10)
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            sys.exit(1)

        # Read HTML response and parse table
        try:
            tables = pd.read_html(StringIO(nesmc_rptrs.text))
        except Exception as e:
            logging.error(f"Error fetching data: {e}")
            sys.exit(1)

        # Print Table in Pandas Data Frame Format
        if DEBUG and tables:
            logging.debug(tables)

        # Select table as its sorted by distance... to be selectable in the future
        if len(tables) > 1:
            df = tables[1]
        else:
            logging.debug("Data changed, less tables")
            sys.exit(1)

        # Dynamically set columns from first row and drop it
        df.columns = df.iloc[0]
        df = df.drop(index=0).reset_index(drop=True)

        df_sorted = df.sort_values(
            by=["FREQ"]
        )  # Now sorts by actual 'FREQ' column name from source

        # If needed, sort or process further (script doesn't sort here currently)
        rpters = df_sorted.values.tolist()

    # Process Repeater Data
    processrepeaterdata(
        rpters,
        repeater_list,
        rfilter,
        chirp,
        chirpcount,
        chirprepeater,
        chirprepeaterlist,
        searchfilter,
        exnotes,
        DEBUG,
        tx_power,
        ams_mode,
    )

    # Print Repeaters
    # if DEBUG == True:
    # logging.debug(*repeater_list, sep="\n")

    # Write repeater list to csv
    with open(outputfile, "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)

        # write multiple rows
        writer.writerows(repeater_list)

    # Chirp Repeater list
    if chirp:
        # Write chirp list to csv
        with open("CHIRP_" + outputfile, "w", encoding="UTF8", newline="") as g:
            writerchirp = csv.writer(g)

            # write multiple rows
            writerchirp.writerows(chirprepeaterlist)


if __name__ == "__main__":
    main(sys.argv[1:])
