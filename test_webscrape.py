import unittest
from webscrape import determineoffset, filteroutput


class TestWebscrape(unittest.TestCase):
    def test_determineoffset(self):
        self.assertEqual(determineoffset("145.2")["offset"], -0.6)
        self.assertEqual(determineoffset("EMPTY")["offset"], 0)

    def test_filteroutput(self):
        rfilter = ["fm", "ysf"]
        repeater = [""] * 25
        repeater[9] = "TRUE"
        repeater[20] = "TRUE"
        repeater_list = []
        filteroutput(rfilter, repeater, repeater_list)
        self.assertEqual(len(repeater_list), 1)


if __name__ == "__main__":
    unittest.main()
