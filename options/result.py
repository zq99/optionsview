import logging
import os
from typing import Optional

import pandas as pd

log = logging.getLogger("options - result")
logging.basicConfig(level=logging.INFO)


class Result:
    """
    Track extraction status and metadata for straddle and stacked output files.
    """

    def __init__(self, is_complete: bool, straddle_file: "ResultFile", stacked_file: "ResultFile") -> None:
        """Store completion status and metadata for both output files."""
        self.is_complete = is_complete
        self.straddle_file = straddle_file
        self.stacked_file = stacked_file

    def to_string(self) -> str:
        """Return both output filenames and sizes as a single string."""
        label = "{}={} {}={}"
        return label.format(self.straddle_file.name, self.straddle_file.size, self.stacked_file.name, self.stacked_file.size)

    @staticmethod
    def get_empty_result() -> "Result":
        """Return an incomplete result with blank filenames and zero sizes."""
        return Result(False, ResultFile("", 0), ResultFile("", 0))

    def print_summary(self) -> None:
        """Print completion status and the output filenames and sizes."""
        print("is complete: {}".format(str(self.is_complete)))
        print("straddle file: {} | size: {}".format(self.straddle_file.name, self.straddle_file.size))
        print("stacked file: {} | size: {}".format(self.stacked_file.name, self.stacked_file.size))

    def get_straddle_df(self) -> Optional[pd.DataFrame]:
        """Read the exported straddle CSV if extraction is complete."""
        return self.__get_as_dataframe(self.straddle_file.name)

    def get_tabular_df(self) -> Optional[pd.DataFrame]:
        """Read the exported stacked CSV if extraction is complete."""
        return self.__get_as_dataframe(self.stacked_file.name)

    def __get_as_dataframe(self, file: Optional[str]) -> Optional[pd.DataFrame]:
        """Read a CSV if extraction is complete; otherwise log and return None.

        CSV reading errors propagate to the caller."""
        if self.is_complete:
            return pd.read_csv(file)
        else:
            self.__display_not_found(file)
            return None

    @staticmethod
    def __display_not_found(file: Optional[str]) -> None:
        """Log an unavailable file."""
        log.error("File not found: {}".format(file))


class ResultFile:
    """Metadata for an output file; its name may be None when unavailable."""

    def __init__(self, name: Optional[str], size: int) -> None:
        """Store the optional filename and file size in bytes."""
        self.name = name
        self.size = size

    def to_string(self) -> str:
        """Return the filename and size as name=size."""
        return "{}={}".format(self.name, self.size)


def __get_result_of_output_files(
    straddle_file_name: Optional[str], stacked_file_name: Optional[str]
) -> Result:
    """Build result metadata from output-file existence and byte sizes.

    Both files must exist for the result to be complete. Log inspection
    errors and return the incomplete default result if an error occurs."""
    result = Result.get_empty_result()
    try:
        is_straddle_file_exists = os.path.isfile(straddle_file_name) if (straddle_file_name is not None) else False
        is_stacked_file_exists = os.path.isfile(stacked_file_name) if (stacked_file_name is not None) else False
        is_files_exists = is_stacked_file_exists and is_straddle_file_exists
        straddle_size = __get_size(straddle_file_name) if is_straddle_file_exists else 0
        stacked_size = __get_size(stacked_file_name) if is_stacked_file_exists else 0
        straddle_result = ResultFile(straddle_file_name, straddle_size)
        tabular_result = ResultFile(stacked_file_name, stacked_size)
        result = Result(is_files_exists, straddle_result, tabular_result)
    except Exception as e:
        log.error(e)
        pass
    return result


def __get_size(filename: str) -> int:
    """Return the file size in bytes."""
    st = os.stat(filename)
    return st.st_size
