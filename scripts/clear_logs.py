#!venv/bin/python3

import os
import glob

logs_dir = os.path.join(os.path.dirname(__file__), '../logs')

log_files = sorted(glob.glob(os.path.join(logs_dir, '*.log')), key=os.path.getctime)

files_to_delete = log_files[:-30]

for file_path in files_to_delete:
    try:
        os.remove(file_path)
    except Exception as e:
        pass