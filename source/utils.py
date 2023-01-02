import csv
import gzip
import re

re_num   = re.compile(r"^([1-9][0-9]*)")
re_point = re.compile(r"^POINT \(([\-\.\d]+) ([\-\.\d]+)\)$")

def open_files(filenames, header):
    files = {}
    writers = {}
    for filename in filenames:
        zip2 = os.path.basename(filename).partition(".")[0]
        files[zip2] = gzip.open(filename, "wt", encoding="ascii")
        writers[zip2] = csv.writer(filename[zip2])
        writers[zip2].writerow(header)
    return files, writers

def close_files(files):
    for f in files.values():
        f.close()
