import logging
import os
from dataclasses import dataclass
from typing import Optional

import pandas as pd

log = logging.getLogger("optionsview - result")
logging.basicConfig(level=logging.INFO)


@dataclass
class OptionsViewResult:
    straddle: pd.DataFrame
    stacked: pd.DataFrame


class Result:
    """
    Track extraction status and metadata for straddle and stacked output files.
    """

    def __init__(
            self,
            is_complete: bool,
            straddle_file: "ResultFile",
            stacked_file: "ResultFile"
    ) -> None:
        """Store completion status and metadata for both output files."""
        self.is_complete = is_complete
        self.straddle_file = straddle_file
        self.stacked_file = stacked_file

    def to_string(self) -> str:
        """Return both output filenames and sizes as a single string."""
        return (
            f"{self.straddle_file.name}={self.straddle_file.size} "
            f"{self.stacked_file.name}={self.stacked_file.size}"
        )

    @staticmethod
    def get_empty_result() -> "Result":
        """Return an incomplete result with blank filenames and zero sizes."""
        return Result(
            is_complete=False,
            straddle_file=ResultFile("", 0),
            stacked_file=ResultFile("", 0)
        )

    def print_summary(self) -> None:
        """Print completion status and the output filenames and sizes."""
        print(f"is complete: {self.is_complete}")
        print(f"straddle file: {self.straddle_file.name} | size: {self.straddle_file.size}")
        print(f"stacked file: {self.stacked_file.name} | size: {self.stacked_file.size}")

    def get_straddle_df(self) -> Optional[pd.DataFrame]:
        """Read the exported straddle CSV if extraction is complete."""
        return self.__get_as_dataframe(file=self.straddle_file.name)

    def get_stacked_df(self) -> Optional[pd.DataFrame]:
        """Read the exported stacked CSV if extraction is complete."""
        return self.__get_as_dataframe(file=self.stacked_file.name)

    def __get_as_dataframe(self, file: Optional[str]) -> Optional[pd.DataFrame]:
        """Read an available CSV when extraction is complete."""
        if self.is_complete and file and os.path.isfile(file):
            return pd.read_csv(file)

        self.__display_not_found(file)
        return None

    @staticmethod
    def __display_not_found(file: Optional[str]) -> None:
        """Log an unavailable file."""
        log.error(f"File not found: {file}")


class ResultFile:
    """Metadata for an output file; its name may be None when unavailable."""

    def __init__(self, name: Optional[str], size: int) -> None:
        """Store the optional filename and file size in bytes."""
        self.name = name
        self.size = size

    def to_string(self) -> str:
        """Return the filename and size as name=size."""
        return f"{self.name}={self.size}"


def __get_result_of_output_files(
        straddle_file_name: Optional[str],
        stacked_file_name: Optional[str]
) -> Result:
    """Build result metadata from output-file existence and byte sizes.

    Every requested file must exist for the result to be complete.
    Log inspection errors and return the incomplete default result if an error occurs."""

    result = Result.get_empty_result()
    try:
        is_straddle_file_exists = os.path.isfile(straddle_file_name) if (straddle_file_name is not None) else False
        is_stacked_file_exists = os.path.isfile(stacked_file_name) if (stacked_file_name is not None) else False

        requested_files = [
            filename
            for filename in (straddle_file_name, stacked_file_name)
            if filename is not None
        ]

        is_files_exists = bool(requested_files) and all(
            os.path.isfile(filename) for filename in requested_files
        )

        straddle_size = __get_size(filename=straddle_file_name) if is_straddle_file_exists else 0
        stacked_size = __get_size(filename=stacked_file_name) if is_stacked_file_exists else 0
        straddle_result = ResultFile(straddle_file_name, straddle_size)
        stacked_result = ResultFile(stacked_file_name, stacked_size)
        result = Result(is_files_exists, straddle_result, stacked_result)
    except Exception as e:
        log.error(e)
        pass
    return result


def __get_size(filename: str) -> int:
    """Return the file size in bytes."""
    st = os.stat(filename)
    return st.st_size
