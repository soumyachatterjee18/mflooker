import os, time, sys

folder_path = "/home/ubuntu/venv"
log_file = ".log"
how_many_days_old_logs_to_remove = 15

now = time.time()
only_files = []

for file in os.listdir(folder_path):
    file_full_path = os.path.join(folder_path,file)
    if os.path.isfile(file_full_path) and file.endswith(log_file):
        #Delete files older than x days
        if os.stat(file_full_path).st_mtime < now - how_many_days_old_logs_to_remove * 86400: 
             os.remove(file_full_path)
             print "\n File Removed : " , file_full_path
