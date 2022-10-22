import logging
import pandas as pd
import os

log = logging.getLogger("options - result")
logging.basicConfig(level=logging.INFO)


class Result:
    """
    results of the extract are tracked here
    games_file and moves_file are ResultFile objects
    """

    def __init__(self, is_complete, straddle_file, tabular_file):
        self.is_complete = is_complete
        self.straddle_file = straddle_file
        self.tabular_file = tabular_file

    def to_string(self):
        label = "{}={} {}={}"
        return label.format(self.straddle_file.name, self.straddle_file.size, self.tabular_file.name, self.tabular_file.size)

    @staticmethod
    def get_empty_result():
        return Result(False, ResultFile("", 0), ResultFile("", 0))

    def print_summary(self):
        """
        return a summary to console
        """
        print("is complete: {}".format(str(self.is_complete)))
        print("straddle file: {} | size: {}".format(self.straddle_file.name, self.straddle_file.size))
        print("tabular file: {} | size: {}".format(self.tabular_file.name, self.tabular_file.size))

    def get_straddle_df(self):
        return self.__get_as_dataframe(self.straddle_file.name)

    def get_tabular_df(self):
        return self.__get_as_dataframe(self.tabular_file.name)

    def __get_as_dataframe(self, file):
        if self.is_complete:
            return pd.read_csv(file)
        else:
            self.__display_not_found(file)
            return None

    @staticmethod
    def __display_not_found(file):
        log.error("File not found: {}".format(file))


class ResultFile:
    def __init__(self, name, size):
        self.name = name
        self.size = size

    def to_string(self):
        return "{}={}".format(self.name, self.size)


def __get_result_of_output_files(straddle_file_name, tabular_file_name):
    result = Result.get_empty_result()
    try:
        is_straddle_file_exists = os.path.isfile(straddle_file_name) if (straddle_file_name is not None) else False
        is_tabular_file_exists = os.path.isfile(tabular_file_name) if (tabular_file_name is not None) else False
        is_files_exists = is_tabular_file_exists and is_straddle_file_exists
        straddle_size = __get_size(straddle_file_name) if is_straddle_file_exists else 0
        tabular_size = __get_size(tabular_file_name) if is_tabular_file_exists else 0
        straddle_result = ResultFile(straddle_file_name, straddle_size)
        tabular_result = ResultFile(tabular_file_name, tabular_size)
        result = Result(is_files_exists, straddle_result, tabular_result)
    except Exception as e:
        log.error(e)
        pass
    return result


def __get_size(filename):
    st = os.stat(filename)
    return st.st_size
