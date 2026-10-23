import logging
import os
import unittest
from typing import Optional

import pandas as pd

from optionsview.data import download_options_view, get_options_view
from optionsview.data import View
from optionsview.common import is_validated_file
from optionsview.result import OptionsViewResult
import tempfile
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path

from optionsview import data

log = logging.getLogger("optionsview - test")
logging.basicConfig(level=logging.INFO)


class DataDownloadTestCase(unittest.TestCase):
    """Integration checks for optionsview downloads and exported CSV files."""

    exports_folder_name = "exports"

    def __init__(self) -> None:
        """Initialize the test case and prepare the export folder."""
        super().__init__()
        self.setUp()

    def setUp(self) -> None:
        """Locate the test folder, check the exports directory and clear old exports."""
        self.folder = os.path.dirname(os.path.realpath(__file__))
        self.check_folders_exist()
        self.delete_old_test_exports()

    def check_folders_exist(self) -> None:
        """Check that the exports directory exists."""
        folders = [self.get_output_filepath(None)]
        for folder in folders:
            self.assertTrue(os.path.isdir(folder))

    def get_output_filepath(self, output_name: Optional[str]) -> str:
        """Return an export path, or the exports directory if no name is supplied."""
        path = Path(self.folder) / self.exports_folder_name

        if output_name is not None:
            path = path / output_name

        return str(path)

    def delete_old_test_exports(self) -> None:
        """Delete old exports while preserving .gitkeep."""
        output_path = self.get_output_filepath(None)
        os.chdir(output_path)

        for filename in os.listdir():
            if filename == ".gitkeep":
                continue

            log.info("removing old export: %s", filename)
            os.remove(filename)

        remaining = [
            filename
            for filename in os.listdir()
            if filename != ".gitkeep"
        ]
        self.assertEqual(remaining, [])

    def run_tests(self) -> None:
        """Run the DataFrame and file-download checks in their existing order."""
        self.run_pandas_dataframe_test()
        self.run_file_creation_test()

    def run_file_creation_test(self) -> None:
        """Download straddle, stacked and combined views and check their outputs."""
        output = self.get_output_filepath(None)

        result = download_options_view('TSLA', View.STRADDLE, output)
        self.assertTrue(is_validated_file(result.straddle_file.name))

        output = self.get_output_filepath(None)
        result = download_options_view('TSLA', View.STACKED, output)
        self.assertTrue(is_validated_file(result.stacked_file.name))

        output = self.get_output_filepath(None)
        result = download_options_view('AMZN', View.ALL, output)
        self.assertTrue(result.is_complete)

    def run_pandas_dataframe_test(self) -> None:
        """Check that both downloaded views contain tabular data."""
        result : OptionsViewResult = get_options_view('TSLA')

        df_list = [result.straddle, result.stacked]
        for df in df_list:
            self.assertTrue(isinstance(df, pd.DataFrame))
            self.assertFalse(df.empty)
            self.assertFalse(len(df) == 0)
            self.assertFalse(len(df.columns) == 0)

        self.assertTrue(len(result.straddle.head(3)) == 3)
        self.assertTrue(len(result.stacked.head(5)) == 5)

class OptionsViewRegressionTests(unittest.TestCase):
    """Check exports and missing-data handling without live downloads."""

    def setUp(self) -> None:
        self.views = OptionsViewResult(
            straddle=pd.DataFrame({"straddle_value": [1]}),
            stacked=pd.DataFrame({"stacked_value": [2]}),
        )

    def test_all_exports_have_distinct_paths_and_correct_contents(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(
                data, "get_options_view", return_value=self.views
            ):
                result = download_options_view("TEST", View.ALL, folder)

            self.assertTrue(result.is_complete)
            self.assertNotEqual(
                result.straddle_file.name,
                result.stacked_file.name,
            )

            pd.testing.assert_frame_equal(
                pd.read_csv(result.straddle_file.name),
                self.views.straddle,
            )
            pd.testing.assert_frame_equal(
                pd.read_csv(result.stacked_file.name),
                self.views.stacked,
            )

    def test_single_view_exports_are_complete(self):
        for view, field, expected in (
            (View.STRADDLE, "straddle_file", self.views.straddle),
            (View.STACKED, "stacked_file", self.views.stacked),
        ):
            with self.subTest(view=view):
                with tempfile.TemporaryDirectory() as folder:
                    with patch.object(
                        data, "get_options_view", return_value=self.views
                    ):
                        result = download_options_view("TEST", view, folder)

                    self.assertTrue(result.is_complete)
                    filename = getattr(result, field).name
                    pd.testing.assert_frame_equal(
                        pd.read_csv(filename), expected
                    )

    def test_missing_result_does_not_export(self):
        with patch.object(data, "get_options_view", return_value=None):
            with patch.object(data, "export_df") as export:
                result = download_options_view("TEST")

        self.assertFalse(result.is_complete)
        export.assert_not_called()

    def test_no_expirations_returns_empty_dataframes(self):

        ticker = SimpleNamespace(
            options=[],
            get_info=lambda: {
                "regularMarketPrice": 375.00,
                "regularMarketTime": 1761004800,
            },
        )

        with patch.object(data, "get_ticker", return_value=ticker):
            result = get_options_view("TEST")

        self.assertIsNotNone(result)
        self.assertIsInstance(result.straddle, pd.DataFrame)
        self.assertIsInstance(result.stacked, pd.DataFrame)
        self.assertTrue(result.straddle.empty)
        self.assertTrue(result.stacked.empty)

def run_all_tests() -> None:
    """Run regression checks, followed by live download checks."""
    log.info("Start testing")

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        OptionsViewRegressionTests
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    if not result.wasSuccessful():
        raise AssertionError("Regression tests failed")

    test_creation = DataDownloadTestCase()
    test_creation.run_tests()

    log.info("End testing")

if __name__ == "__main__":
    run_all_tests()