import csv
import logging
import os

log = logging.getLogger('edx.celery.task')


def store_row(data, abs_filepath):
    """
    Store data row in an indicated csv file.
    """
    with open(abs_filepath, "a+") as csv_file:
        writer = csv.writer(csv_file, dialect='excel', quotechar='"',
                            quoting=csv.QUOTE_ALL)
        if not data:
            log.info("No data provided to store.")
            return
        try:
            writer.writerow(data)
        except UnicodeEncodeError as e:
            log.error("UnicodeEncodeError occurred trying to store the row {!s}, "
                      "error: {!s}".format(data, e))


def cleanup_directory_user_files(dir_path, user_id, filename_user_id_getter):
    """
    Cleanup directory files by user id.
    """
    for the_file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, the_file)
        try:
            file_user_id = filename_user_id_getter(the_file)
            if int(file_user_id) == user_id:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
        except Exception as e:
            # NOTE: can't risk failing the flow for just cleanup,
            #  have to narrow down though e.g. https://stackoverflow.com/a/15452633/4942473
            log.error("An error occurred while cleaning up dir {!s} "
                      "for user_id {!s}".format(dir_path, e))


def fetch_csv_data(filepath):
    """
    Read data from a file.
    """
    with open(filepath, "r+") as csv_file:
        csv_file.seek(0)
        data = csv_file.read()
        yield data


def get_latest_user_file(user_id, dir_path, filename_user_id_getter, extension="csv"):
    """
    Get latest file in a dir provided a user id in a file name.
    """
    latest_file = None
    user_files_paths = None
    dirpath = os.path.join(dir_path)
    if os.path.isdir(dirpath):
        user_files_paths = [
            os.path.join(dirpath, f)
            for f in os.listdir(dirpath)
            if os.path.isfile(os.path.join(dirpath, f))
            and int(filename_user_id_getter(f)) == int(user_id)
            and os.path.join(dirpath, f).split(".")[-1] == extension
        ]
    if user_files_paths:
        latest_file = max(user_files_paths, key=os.path.getctime)
    return latest_file
