import unittest
import pickle
from pathlib import Path
from hashlib import sha1
from shutil import copyfile
from gzip import GzipFile

from pickart import PickartFile, PickartFileData
from pickart.errors import BadPickartFile, BadPixelFormat
from pickart.pickart_file import set_stdo


FILES_DIR = Path("tests", "pickart")
SAVING_TESTS_DIR = Path(FILES_DIR, "saving_tests")
PICKART_FILE_WITH_EXTERNAL_OBJ = Path(FILES_DIR, "with_external_obj.pickart")
PICKART_FILE_WITH_WRONG_FORMAT = Path(FILES_DIR, "with_wrong_format.pickart")
PICKART_FILE_WITH_WRONG_VERSION = Path(FILES_DIR, "with_wrong_version.pickart")
PICKART_FILE_WITH_WRONG_SIZE = Path(FILES_DIR, "with_wrong_size.pickart")
PICKART_FILE_WITH_WRONG_PIXEL_FORMAT = Path(
    FILES_DIR, "with_wrong_pixel_format.pickart"
)
NORMAL_PICKART_FILE = Path(FILES_DIR, "normal_file.pickart")
FILE_FOR_SAVING_TESTS = Path(SAVING_TESTS_DIR, "save_test.pickart")


set_stdo(lambda x: None)
"""Standtart output for file loader. It is empty function that is used instead of standart `print`."""


def get_gzip_file_hash(file_path: Path) -> str:
    with GzipFile(file_path, "rb") as file:
        return sha1(file.read()).hexdigest()


class TestPickartFile(unittest.TestCase):
    def test_loading_pickart_file_with_external_obj(self):
        pickart_file = PickartFile(PICKART_FILE_WITH_EXTERNAL_OBJ)
        self.assertEqual(len(pickart_file.errors), 1)
        self.assertIsInstance(pickart_file.errors[0], pickle.UnpicklingError)
        self.assertEqual(pickart_file.filepath, PICKART_FILE_WITH_EXTERNAL_OBJ)
        self.assertFalse(pickart_file.valid)

    def test_loading_pickart_file_with_wrong_format(self):
        pickart_file = PickartFile(PICKART_FILE_WITH_WRONG_FORMAT)
        self.assertEqual(len(pickart_file.errors), 1)
        self.assertIsInstance(pickart_file.errors[0], TypeError)
        self.assertEqual(pickart_file.filepath, PICKART_FILE_WITH_WRONG_FORMAT)
        self.assertFalse(pickart_file.valid)

    def test_loading_pickart_file_with_wrong_version(self):
        pickart_file = PickartFile(PICKART_FILE_WITH_WRONG_VERSION)
        self.assertEqual(len(pickart_file.errors), 1)
        self.assertIsInstance(pickart_file.errors[0], BadPickartFile)
        self.assertEqual(pickart_file.filepath, PICKART_FILE_WITH_WRONG_VERSION)
        self.assertFalse(pickart_file.valid)

    def test_loading_pickart_file_with_wrong_size(self):
        pickart_file = PickartFile(PICKART_FILE_WITH_WRONG_SIZE)
        self.assertEqual(len(pickart_file.errors), 1)
        self.assertIsInstance(pickart_file.errors[0], BadPickartFile)
        self.assertEqual(pickart_file.filepath, PICKART_FILE_WITH_WRONG_SIZE)
        self.assertFalse(pickart_file.valid)

    def test_loading_pickart_file_with_wrong_pixel_format(self):
        pickart_file = PickartFile(PICKART_FILE_WITH_WRONG_PIXEL_FORMAT)
        self.assertEqual(len(pickart_file.errors), 1)
        self.assertIsInstance(pickart_file.errors[0], BadPixelFormat)
        self.assertEqual(pickart_file.filepath, PICKART_FILE_WITH_WRONG_PIXEL_FORMAT)
        self.assertFalse(pickart_file.valid)

    def test_loading_normal_file(self):
        pickart_file = PickartFile()
        self.assertIs(pickart_file.filepath, None)
        self.assertFalse(pickart_file.valid)
        pickart_file.load(NORMAL_PICKART_FILE)
        self.assertEqual(pickart_file.filepath, NORMAL_PICKART_FILE)
        self.assertTrue(pickart_file.valid)

    def test_saving_file_from_file_data(self):
        file_data = PickartFileData({"size": (1, 1), "version": 1})
        pickart_file = PickartFile(file_data=file_data)
        self.assertIs(pickart_file.filepath, None)
        self.assertFalse(pickart_file.valid)
        pickart_file.save(FILE_FOR_SAVING_TESTS)
        self.assertEqual(pickart_file.filepath, FILE_FOR_SAVING_TESTS)
        self.assertTrue(pickart_file.valid)

    def test_saving_file(self):
        NORMAL_PICKART_FILE_FOR_SAVING = Path(
            SAVING_TESTS_DIR, NORMAL_PICKART_FILE.name
        )

        copyfile(NORMAL_PICKART_FILE, NORMAL_PICKART_FILE_FOR_SAVING)

        pickart_file = PickartFile(NORMAL_PICKART_FILE_FOR_SAVING)
        pickart_file.save(FILE_FOR_SAVING_TESTS)
        self.assertEqual(pickart_file.filepath, FILE_FOR_SAVING_TESTS)
        self.assertTrue(pickart_file.valid)
        self.assertEqual(
            get_gzip_file_hash(FILE_FOR_SAVING_TESTS),
            get_gzip_file_hash(NORMAL_PICKART_FILE_FOR_SAVING),
        )
        saved_pickart_file = PickartFile(FILE_FOR_SAVING_TESTS)
        self.assertEqual(len(saved_pickart_file.errors), 0)
        self.assertEqual(saved_pickart_file._data, pickart_file._data)


if __name__ == "__main__":
    unittest.main()
