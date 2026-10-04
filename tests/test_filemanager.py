import json
import tempfile
import unittest
from pathlib import Path

from services.filemanager import FileDataError, FileManager


class FileManagerTests(unittest.TestCase):
    def test_corrupt_file_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notatki.json"
            path.write_text("to nie jest json", encoding="utf-8")
            manager = FileManager("notatki", data_dir=Path(directory))

            with self.assertRaises(FileDataError):
                manager.add("test", "opis")

            self.assertEqual(path.read_text(encoding="utf-8"), "to nie jest json")

    def test_save_and_case_insensitive_remove(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = FileManager("notatki", data_dir=Path(directory))
            manager.add("Altdorf", "opis")
            manager.remove("altdorf")

            data = json.loads((Path(directory) / "notatki.json").read_text(encoding="utf-8"))
            self.assertEqual(data, [])


if __name__ == "__main__":
    unittest.main()
