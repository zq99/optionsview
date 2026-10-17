import logging
import os
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional, Tuple, Union

if TYPE_CHECKING:
    import pandas as pd

log = logging.getLogger("options - common")
logging.basicConfig(level=logging.INFO)


def get_date_stamp() -> str:
    """Return the current local date in YYYYMMDD format."""
    return datetime.today().strftime('%Y%m%d')


def get_file_name(
    file_name: str,
    timestamp: bool = True,
    file_path: Optional[str] = None,
    file_ext: str = '.csv',
) -> str:
    """Build a filename with an optional directory and local-date suffix.

    Include the leading dot in file_ext. This does not create directories.
    """
    full_file = (file_path + "/" + file_name) if file_path is not None else file_name
    full_file += "_" + get_date_stamp() + file_ext if timestamp else file_ext
    return full_file


def is_validated_file(
    file_name: Union[str, List[str]], log_results: bool = True
) -> bool:
    """Return whether every supplied file exists and has a nonzero size."""
    result, file = validate_file(file_name, log_results)
    return result


def validate_file(
    file_name: Union[str, List[str]], log_result: bool = True
) -> Tuple[bool, Optional[Union[str, List[str]]]]:
    """Return validation status and the original input, or None on failure.

    Validation checks file existence and nonzero size, not file contents.
    """
    if check_files_exist(file_name, log_result):
        if log_result:
            log.info("file [{}] exists!".format(file_name))
        return True, file_name
    else:
        if log_result:
            log.error("file [{}] does NOT exist!".format(file_name))
        return False, None


def check_files_exist(
    files: Union[str, List[str]], log_results: bool = True
) -> bool:
    """Check that every supplied path is a nonempty file.

    Return False at the first missing or zero-byte file. An empty list
    returns True, preserving the existing behaviour.
    """
    if log_results:
        log.info("checking files exist...")

    file_list = files if type(files) == list else [files]
    for f in file_list:
        if not os.path.isfile(f):
            if log_results:
                log.info("Expected file : " + f + " not found")
            return False
        else:
            if get_size(f) == 0:
                if log_results:
                    log.info("Expected file : " + f + " has no data!")
                return False
    if log_results:
        log.info("check complete")
    return True


def get_size(filename: str) -> int:
    """Return the file size in bytes, or zero if the path is not a file."""
    if os.path.isfile(filename):
        st = os.stat(filename)
        return st.st_size
    else:
        return 0


def export_df(
    data_df: "pd.DataFrame", file_name: str, index_required: bool = True
) -> bool:
    """Export a DataFrame to CSV using UTF-8 with a byte-order mark.

    Include the index by default. Log export errors and return False;
    return True when to_csv completes successfully.
    """
    try:
        data_df.to_csv(file_name, index=index_required, encoding='utf-8-sig')
        return True
    except PermissionError:
        log.error("unable to access existing file {}".format(file_name))
        return False
    except Exception as e:
        log.error(e)
        return False
