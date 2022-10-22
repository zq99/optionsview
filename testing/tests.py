import logging
import os
import unittest
import pandas as pd

from options.data import download_options_view, get_options_view_df
from options.data import View
from options.common import is_validated_file

log = logging.getLogger("optionsview test")
logging.basicConfig(level=logging.INFO)


class DataDownloadTestCase(unittest.TestCase):
    exports_folder_name = "exports"

    def __init__(self):
        super().__init__()
        self.setUp()

    def setUp(self):
        self.folder = os.path.dirname(os.path.realpath(__file__))
        self.check_folders_exist()
        self.delete_old_test_exports()

    def check_folders_exist(self):
        folders = [self.get_output_filepath(None)]
        for folder in folders:
            self.assertTrue(os.path.isdir(folder))

    def get_output_filepath(self, output_name):
        name_format = '{}/{}/{}' if output_name is not None else '{}/{}'
        return name_format.format(self.folder, self.exports_folder_name, output_name)

    def delete_old_test_exports(self):
        output_path = self.get_output_filepath(None)
        os.chdir(output_path)
        all_files = os.listdir()
        if len(all_files) > 0:
            for f in all_files:
                log.info("removing old export: {}".format(f))
                os.remove(f)
        self.assertTrue(len(os.listdir()) == 0)

    def run_tests(self):
        self.run_pandas_dataframe_test()
        self.run_file_creation_test()

    def run_file_creation_test(self):
        output = self.get_output_filepath(None)

        result = download_options_view('TSLA', View.STRADDLE, output)
        self.assertTrue(is_validated_file(result.straddle_file.name))

        output = self.get_output_filepath(None)
        result = download_options_view('TSLA', View.TABULAR, output)
        self.assertTrue(is_validated_file(result.tabular_file.name))

        output = self.get_output_filepath(None)
        result = download_options_view('AMZN', View.ALL, output)
        self.assertTrue(result.is_complete)

    def run_pandas_dataframe_test(self):
        straddle_df, tabular_df = get_options_view_df('TSLA')

        df_list = [straddle_df, tabular_df]
        for df in df_list:
            self.assertTrue(isinstance(df, pd.DataFrame))
            self.assertFalse(df.empty)
            self.assertFalse(len(df) == 0)
            self.assertFalse(len(df.columns) == 0)

        self.assertTrue(len(straddle_df.head(3)) == 3)
        self.assertTrue(len(tabular_df.head(5)) == 5)


def run_all_tests():
    """
    This is the main method to run to check the API output
    """
    log.info("Start testing")
    test_creation = DataDownloadTestCase()
    test_creation.run_tests()
    log.info("End testing")
