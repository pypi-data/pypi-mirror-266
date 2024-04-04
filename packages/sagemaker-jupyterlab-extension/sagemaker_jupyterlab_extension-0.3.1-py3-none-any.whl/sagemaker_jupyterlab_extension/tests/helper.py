import os
import json
import tempfile


logfile = tempfile.mkstemp()[1]
os.environ["SAGEMAKER_LOG_FILE"] = logfile
log_file_name = logfile.split("/")[2]

"""Read the last entry from the temporary logfile"""


def get_last_entry(file_name):
    actual_file = os.path.join("/tmp", "jupyterlab/", file_name)
    with open(actual_file) as fid:
        lines = fid.readlines()
    return json.loads(lines[-1])
