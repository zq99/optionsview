import logging
import os
from datetime import datetime

log = logging.getLogger("options - common")
logging.basicConfig(level=logging.INFO)


def get_date_stamp():
    return datetime.today().strftime('%Y%m%d')


def get_file_name(file_name, timestamp=True, file_path=None, file_ext='.csv'):
    full_file = (file_path + "/" + file_name) if file_path is not None else file_name
    full_file += "_" + get_date_stamp() + file_ext if timestamp else file_ext
    return full_file


def is_validated_file(file_name, log_results=True):
    result, file = validate_file(file_name, log_results)
    return result


def validate_file(file_name, log_result=True):
    if check_files_exist(file_name, log_result):
        if log_result:
            log.info("file [{}] exists!".format(file_name))
        return True, file_name
    else:
        if log_result:
            log.error("file [{}] does NOT exist!".format(file_name))
        return False, None


def check_files_exist(files, log_results=True):
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


def get_size(filename):
    if os.path.isfile(filename):
        st = os.stat(filename)
        return st.st_size
    else:
        return 0


def export_df(data_df, file_name, index_required=True):
    try:
        data_df.to_csv(file_name, index=index_required, encoding='utf-8-sig')
        return True
    except PermissionError:
        log.error("unable to access existing file {}".format(file_name))
        return False
    except Exception as e:
        log.error(e)
        return False
