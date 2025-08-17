import sys
import unittest
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd

from webscrape import (
    chirpbuild,
    determineoffset,
    filteroutput,
    main,
    processrepeaterdata,
    updatewebformdata,
)


class TestWebscrape(unittest.TestCase):
    def test_updatewebformdata(self) -> None:
        """Test updating form data with search parameters."""
        formdata = {"existing_key": "value"}
        city = "TestCity"
        state = "TS"
        radius = "100"
        bands = "144,440"
        numperfreq = "1per"
        dbfilter = "neny"

        updatewebformdata(formdata, city, state, radius, bands, numperfreq, dbfilter)

        expected = {
            "existing_key": "value",
            "loca": "TestCity, TS",
            "radi": "100",
            "band": "144,440,",
            "freq": "1per",
            "dbfilter": "neny",
        }
        self.assertEqual(formdata, expected)

    def test_updatewebformdata_empty_inputs(self) -> None:
        """Test updating form data with empty or minimal inputs."""
        formdata: dict[str, str] = {}
        city = ""
        state = ""
        radius = ""
        bands = ""
        numperfreq = ""
        dbfilter = ""

        updatewebformdata(formdata, city, state, radius, bands, numperfreq, dbfilter)

        expected = {"loca": ", ", "radi": "", "band": ",", "freq": "", "dbfilter": ""}
        self.assertEqual(formdata, expected)

    def test_processrepeaterdata_basic_fm(self) -> None:
        """Test processing a basic FM repeater entry."""
        rpters = [["City, ST", 145.0, "100.0", "CALL", "10.0N", "Sponsor", "Notes"]]
        repeater_list: list[list[Any]] = []
        rfilter = ["all"]
        chirp = False
        chirpcount = 0
        chirprepeater = [list[Any]]
        chirprepeaterlist: list[list[Any]] = []
        searchfilter = ""
        exnotes = False
        DEBUG = False
        tx_power = "Low"
        ams_mode = "v1"

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

        self.assertEqual(len(repeater_list), 1)
        repeater = repeater_list[0]
        self.assertEqual(repeater[0], "City")  # City
        self.assertEqual(repeater[1], "ST")  # State
        self.assertEqual(repeater[2], 145.0)  # Freq
        self.assertEqual(repeater[5], "CALL")  # Call
        self.assertEqual(repeater[9], "TRUE")  # FM mode
        self.assertEqual(repeater[10], "100.0")  # CTCSS

    def test_processrepeaterdata_ysf_mode(self) -> None:
        """Test processing a YSF-capable repeater."""
        rpters = [["City, ST", 145.0, "YSF", "CALL", "10.0N", "Sponsor", "Fusion"]]
        repeater_list: list[list[Any]] = []
        rfilter = ["ysf"]
        chirp = False
        chirpcount = 0
        chirprepeater = [list[Any]]
        chirprepeaterlist: list[list[Any]] = []
        searchfilter = ""
        exnotes = False
        DEBUG = False
        tx_power = "Low"
        ams_mode = "v2"  # Test v2 mode

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

        self.assertEqual(len(repeater_list), 1)
        repeater = repeater_list[0]
        self.assertEqual(repeater[20], "TRUE")  # YSF
        self.assertEqual(repeater[22], "FM")  # Operating Mode for v2
        self.assertEqual(repeater[23], "Y")  # AMS for v2

    def test_processrepeaterdata_chirp_output(self) -> None:
        """Test generating CHIRP output for FM repeater."""
        rpters = [["City, ST", 145.0, "100.0", "CALL", "10.0N", "Sponsor", "Notes"]]
        repeater_list: list[list[Any]] = []
        rfilter = ["fm"]
        chirp = True
        chirpcount = 0
        chirprepeater = [list[Any]]
        chirprepeaterlist: list[list[Any]] = []
        searchfilter = ""
        exnotes = False
        DEBUG = False
        tx_power = "Low"
        ams_mode = "v1"

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

        self.assertEqual(len(chirprepeaterlist), 1)
        chirp_entry = chirprepeaterlist[0]
        self.assertEqual(chirp_entry[0], "0")  # Location
        self.assertEqual(chirp_entry[1], "CALL")  # Name
        self.assertEqual(chirp_entry[2], "145.0")  # Frequency
        self.assertEqual(chirp_entry[5], "Tone")  # Tone
        self.assertEqual(chirp_entry[6], "100.0")  # rToneFreq

    def test_processrepeaterdata_search_filter(self) -> None:
        """Test search filter to include only matching entries."""
        rpters = [
            ["City, ST", "145.0", "100.0", "CALL", "10.0N", "Sponsor", "NB1RI Notes"]
        ]  # freq as str to avoid type error
        repeater_list: list[list[Any]] = []
        rfilter = ["all"]
        chirp = False
        chirpcount = 0
        chirprepeater = [list[Any]]
        chirprepeaterlist: list[list[Any]] = []
        searchfilter = "NB1RI"
        exnotes = False
        DEBUG = False
        tx_power = "Low"
        ams_mode = "v1"

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

        self.assertEqual(len(repeater_list), 1)  # Should match

        # Test non-matching
        repeater_list = []
        searchfilter = "NoMatch"
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
        self.assertEqual(len(repeater_list), 0)  # No match

    def test_processrepeaterdata_nan_handling(self) -> None:
        """Test handling of 'nan' in raw data."""
        rpters = [
            [
                float("nan"),
                float("nan"),
                float("nan"),
                float("nan"),
                "10.0N",
                "Sponsor",
                float("nan"),
            ]
        ]
        repeater_list: list[list[Any]] = []
        rfilter = ["all"]
        chirp = False
        chirpcount = 0
        chirprepeater = [list[Any]]
        chirprepeaterlist: list[list[Any]] = []
        searchfilter = ""
        exnotes = False
        DEBUG = False
        tx_power = "Low"
        ams_mode = "v1"

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

        self.assertEqual(len(repeater_list), 1)
        repeater = repeater_list[0]
        self.assertEqual(repeater[0], "EMPTY")  # City
        self.assertEqual(repeater[1], "EMPTY")  # State
        self.assertEqual(repeater[2], "EMPTY")  # Freq
        self.assertEqual(repeater[5], "EMPTY")  # Call

    def test_processrepeaterdata_dcs_code(self) -> None:
        """Test detection of DCS codes."""
        rpters = [["City, ST", 145.0, "", "CALL", "10.0N", "Sponsor", "DCS(023)"]]
        repeater_list: list[list[Any]] = []
        rfilter = ["fm"]
        chirp = False
        chirpcount = 0
        chirprepeater = [list[Any]]
        chirprepeaterlist: list[list[Any]] = []
        searchfilter = ""
        exnotes = False
        DEBUG = False
        tx_power = "Low"
        ams_mode = "v1"

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

        self.assertEqual(len(repeater_list), 1)
        repeater = repeater_list[0]
        self.assertEqual(repeater[9], "TRUE")  # FM
        self.assertEqual(repeater[11], "023")  # DCS
        self.assertEqual(repeater[12], "DCS")  # Tone Mode

    def test_processrepeaterdata_extended_notes(self) -> None:
        """Test inclusion of extended notes."""
        rpters = [
            ["City, ST", 145.0, "100.0", "CALL", "10.0N", "Sponsor", "Extra Notes"]
        ]
        repeater_list: list[list[Any]] = []
        rfilter = ["all"]
        chirp = False
        chirpcount = 0
        chirprepeater = [list[Any]]
        chirprepeaterlist: list[list[Any]] = []
        searchfilter = ""
        exnotes = True
        DEBUG = False
        tx_power = "Low"
        ams_mode = "v1"

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

        self.assertEqual(len(repeater_list), 1)
        repeater = repeater_list[0]
        self.assertEqual(repeater[24], "City,ST,CALL,Extra Notes")  # Extended notes

    def test_determineoffset_various_bands(self) -> None:
        """Test offset calculation for different frequency bands."""
        self.assertEqual(determineoffset("51.5")["offset"], -0.5)
        self.assertEqual(determineoffset("51.5")["offset_dir"], "-")

        self.assertEqual(determineoffset("53.0")["offset"], -1.0)
        self.assertEqual(determineoffset("53.0")["offset_dir"], "-")

        self.assertEqual(determineoffset("145.2")["offset"], -0.6)
        self.assertEqual(determineoffset("145.2")["offset_dir"], "-")

        self.assertEqual(determineoffset("146.8")["offset"], -0.6)
        self.assertEqual(determineoffset("146.8")["offset_dir"], "-")

        self.assertEqual(determineoffset("147.1")["offset"], 0.6)
        self.assertEqual(determineoffset("147.1")["offset_dir"], "+")

        self.assertEqual(determineoffset("224.0")["offset"], -1.6)
        self.assertEqual(determineoffset("224.0")["offset_dir"], "-")

        self.assertEqual(determineoffset("442.0")["offset"], 5.0)
        self.assertEqual(determineoffset("442.0")["offset_dir"], "+")

        self.assertEqual(determineoffset("447.0")["offset"], -5.0)
        self.assertEqual(determineoffset("447.0")["offset_dir"], "-")

        self.assertEqual(determineoffset("920.0")["offset"], -12.0)
        self.assertEqual(determineoffset("920.0")["offset_dir"], "-")

        self.assertEqual(determineoffset("927.5")["offset"], -25.0)
        self.assertEqual(determineoffset("927.5")["offset_dir"], "-")

    def test_determineoffset_invalid(self) -> None:
        """Test invalid or out-of-range frequencies."""
        self.assertEqual(determineoffset("EMPTY")["offset"], 0)
        self.assertEqual(determineoffset("EMPTY")["offset_dir"], "off")

        self.assertEqual(determineoffset("0.0")["offset"], 0)
        self.assertEqual(determineoffset("0.0")["offset_dir"], "off")

        self.assertEqual(determineoffset("1000.0")["offset"], 0)
        self.assertEqual(determineoffset("1000.0")["offset_dir"], "off")

        with self.assertLogs(level="ERROR") as cm:
            determineoffset("invalid")
        self.assertIn("Error: 'invalid' is not a valid float string", cm.output[0])

    def test_filteroutput_multiple_modes(self) -> None:
        """Test filtering for various modes."""
        rfilter = ["fm", "ysf"]
        repeater = [""] * 25
        repeater[9] = "TRUE"  # FM
        repeater[20] = "TRUE"  # YSF
        repeater_list: list[list[Any]] = []
        filteroutput(rfilter, repeater, repeater_list)
        self.assertEqual(len(repeater_list), 1)

        # Test no match
        repeater_list = []
        repeater[9] = ""  # No FM
        repeater[20] = ""  # No YSF
        filteroutput(rfilter, repeater, repeater_list)
        self.assertEqual(len(repeater_list), 0)

        # Test 'all'
        repeater_list = []
        rfilter = ["all"]
        filteroutput(rfilter, repeater, repeater_list)
        self.assertEqual(len(repeater_list), 1)

    def test_filteroutput_single_mode(self) -> None:
        """Test filtering for single mode like DMR."""
        rfilter = ["dmr"]
        repeater = [""] * 25
        repeater[13] = "TRUE"  # DMR
        repeater_list: list[list[Any]] = []
        filteroutput(rfilter, repeater, repeater_list)
        self.assertEqual(len(repeater_list), 1)

        repeater_list = []
        repeater[13] = ""
        filteroutput(rfilter, repeater, repeater_list)
        self.assertEqual(len(repeater_list), 0)

    def test_chirpbuild(self) -> None:
        """Test appending CHIRP entry."""
        chirprepeater = [
            "0",
            "CALL",
            145.0,
            "-",
            "0.600000",
            "Tone",
            "100.0",
            "100.0",
            "023",
            "NN",
            "FM",
            "5.00",
            "",
            "Comment",
            "",
            "",
            "",
            "",
        ]
        chirprepeaterlist: list[list[Any]] = []
        chirpbuild(chirprepeater, chirprepeaterlist)
        self.assertEqual(len(chirprepeaterlist), 1)
        self.assertEqual(chirprepeaterlist[0], chirprepeater)

    @patch("requests.Session.post")
    @patch("pandas.read_html")
    @patch("builtins.open", new_callable=mock_open)
    @patch(
        "sys.argv",
        ["webscrape.py", "-c", "TestCity", "-s", "TS", "-r", "10", "-b", "144"],
    )
    @patch("logging.basicConfig")
    def test_main_basic(
        self,
        mock_logging: MagicMock,
        mock_open: MagicMock,
        mock_read_html: MagicMock,
        mock_post: MagicMock,
    ) -> None:
        """Test main function with minimal inputs and mocks."""
        # Mock requests response
        mock_response = MagicMock()
        mock_response.text = "<html><table><tr><th>LOC</th><th>FREQ</th><th>PL</th><th>CALL</th><th>DIST/DIR</th><th>SPONSOR</th><th>NOTES</th></tr><tr><td>City, ST</td><td>145.0</td><td>100.0</td><td>CALL</td><td>5.0N</td><td>Sponsor</td><td>Notes</td></tr></table></html>"
        mock_post.return_value = mock_response

        # Define header and data for mock_df
        header = ["LOC", "FREQ", "PL", "CALL", "DIST/DIR", "SPONSOR", "NOTES"]
        data_row = ["City, ST", 145.0, "100.0", "CALL", "5.0N", "Sponsor", "Notes"]
        mock_df = pd.DataFrame([header, data_row])

        mock_read_html.return_value = [
            pd.DataFrame(),
            mock_df,
        ]  # Simulate tables[0], tables[1]

        main(sys.argv[1:])  # Call main without expecting SystemExit

        mock_open.assert_called_with("repeaters.csv", "w", encoding="UTF8", newline="")

    @patch("requests.Session.post")
    @patch("pandas.read_html")
    @patch("sys.argv", ["webscrape.py", "-d"])  # Debug mode
    def test_main_debug_logging(
        self, mock_read_html: MagicMock, mock_post: MagicMock
    ) -> None:
        """Test main with debug mode enables detailed logging."""
        # Mock requests response
        mock_response = MagicMock()
        mock_response.text = "<html><table><tr><th>LOC</th><th>FREQ</th><th>PL</th><th>CALL</th><th>DIST/DIR</th><th>SPONSOR</th><th>NOTES</th></tr><tr><td>City, ST</td><td>145.0</td><td>100.0</td><td>CALL</td><td>5.0N</td><td>Sponsor</td><td>Notes</td></tr></table></html>"
        mock_post.return_value = mock_response

        # Define header and data for mock_df
        header = ["LOC", "FREQ", "PL", "CALL", "DIST/DIR", "SPONSOR", "NOTES"]
        data_row = ["City, ST", 145.0, "100.0", "CALL", "5.0N", "Sponsor", "Notes"]
        mock_df = pd.DataFrame([header, data_row])

        mock_read_html.return_value = [
            pd.DataFrame(),
            mock_df,
        ]  # For both nerep and nyrep

        main(sys.argv[1:])


if __name__ == "__main__":
    unittest.main()
