import os
import unittest
from pathlib import Path
from hashlib import sha1


from pickart import PickartFile
from pickart.converter import convert_to_pickart, convert_to_png

FILES_DIR = Path("tests", "converter")
OUTPUT_DIR = Path(FILES_DIR, "output")
INPUT_DIR = Path(FILES_DIR, "input")
NORMAL_PNG_FILE = Path(INPUT_DIR, "normal.png")
NORMAL_PICKART_FILE = Path(INPUT_DIR, "normal.pickart")
CONVERTED_NORMAL_PNG_FILE_HASH = "625dbe2dd88c1a293c3de87166f087036642cb2d"


class TestConverter(unittest.TestCase):
    def testPNGtoPickartConvertion(self):
        expected_name = Path(OUTPUT_DIR, "normal.pickart")
        convert_to_pickart(NORMAL_PNG_FILE, OUTPUT_DIR)
        self.assertTrue(expected_name.is_file())
        pickart_file = PickartFile(expected_name)
        self.assertTrue(pickart_file.valid)
        os.remove(expected_name)

    def testPNGtoPickartConvertionWithDifferentName(self):
        expected_name = Path(OUTPUT_DIR, "temp_res.pickart")
        convert_to_pickart(NORMAL_PNG_FILE, OUTPUT_DIR, "temp_res")
        self.assertTrue(expected_name.is_file())
        pickart_file = PickartFile(expected_name)
        self.assertTrue(pickart_file.valid)
        os.remove(expected_name)

    def testPickartToPNG(self):
        expected_name = Path(OUTPUT_DIR, "normal.png")
        convert_to_png(NORMAL_PICKART_FILE, OUTPUT_DIR)
        self.assertTrue(expected_name.is_file())
        self.assertEqual(
            sha1(expected_name.read_bytes()).hexdigest(), CONVERTED_NORMAL_PNG_FILE_HASH
        )
        os.remove(expected_name)

    def testPickartToPNGWithDifferentName(self):
        expected_name = Path(OUTPUT_DIR, "temp_res.png")
        convert_to_png(NORMAL_PICKART_FILE, OUTPUT_DIR, "temp_res")
        self.assertTrue(expected_name.is_file())
        self.assertEqual(
            sha1(expected_name.read_bytes()).hexdigest(), CONVERTED_NORMAL_PNG_FILE_HASH
        )
        os.remove(expected_name)


if __name__ == "__main__":
    unittest.main()
