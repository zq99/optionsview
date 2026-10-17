import logging
import os
import unittest
from typing import Optional

import pandas as pd

from options.data import download_options_view, get_options_view_df
from options.data import View
from options.common import is_validated_file

log = logging.getLogger("options - test")
logging.basicConfig(level=logging.INFO)


class DataDownloadTestCase(unittest.TestCase):
    """Integration checks for options downloads and exported CSV files."""

    exports_folder_name = "exports"

    def __init__(self) -> None:
        """Initialize the test case and prepare the exports folder."""
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
        """Return an export path, or the exports directory when no name is supplied."""
        name_format = '{}/{}/{}' if output_name is not None else '{}/{}'
        return name_format.format(self.folder, self.exports_folder_name, output_name)

    def delete_old_test_exports(self) -> None:
        """Change to the exports directory and delete all existing files in it."""
        output_path = self.get_output_filepath(None)
        os.chdir(output_path)
        all_files = os.listdir()
        if len(all_files) > 0:
            for f in all_files:
                log.info("removing old export: {}".format(f))
                os.remove(f)
        self.assertTrue(len(os.listdir()) == 0)

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
        straddle_df, stacked_df = get_options_view_df('TSLA')

        df_list = [straddle_df, stacked_df]
        for df in df_list:
            self.assertTrue(isinstance(df, pd.DataFrame))
            self.assertFalse(df.empty)
            self.assertFalse(len(df) == 0)
            self.assertFalse(len(df.columns) == 0)

        self.assertTrue(len(straddle_df.head(3)) == 3)
        self.assertTrue(len(stacked_df.head(5)) == 5)


def run_all_tests() -> None:
    """
    Run all options download integration checks.

    These checks use the configured data source and require download access.
    Setup deletes existing files in the exports directory beside this module
    and changes the current working directory to that directory.
    """
    log.info("Start testing")
    test_creation = DataDownloadTestCase()
    test_creation.run_tests()
    log.info("End testing")
