import csv
import gzip
import os
import pickle
import rtree
import shapefile
from shapely import geometry


def open_files(targets, header):
    files = {}
    writers = {}
    for target in targets:
        zip2 = os.path.basename(target.path).partition(".")[0]
        files[zip2] = gzip.open(target.path, "wt", encoding="ascii")
        writers[zip2] = csv.writer(files[zip2])
        writers[zip2].writerow(header)
    return files, writers


def close_files(files):
    for f in files.values():
        f.close()


class BlockGroupIndex:
    def __init__(self, filename):
        self.filename = filename
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                data = pickle.load(f)
            self.blkgrp = data["blkgrp"]
            self.shape = data["shape"]
            assert len(self.blkgrp) == len(self.shape)
            self.n = len(self.blkgrp)
        else:
            self.blkgrp = []
            self.shape = []
            self.n = 0
        self.index = rtree.index.Index(os.path.splitext(filename)[0])
    def close(self):
        self.index.close()
        with open(self.filename, "wb") as f:
            pickle.dump({
                "blkgrp": self.blkgrp,
                "shape": self.shape
            }, f)
    def add_shapefile(self, filename):
        blkgrp = shapefile.Reader(filename)
        for i in range(len(blkgrp)):
            s = geometry.shape(blkgrp.shape(i))
            self.index.insert(self.n, s.bounds)
            self.blkgrp.append(blkgrp.record(i)["GEOID"])
            self.shape.append(s)
            self.n += 1
            assert len(self.blkgrp) == len(self.shape) == self.n
    def locate(self, x, y):
        if x and y:
            p = geometry.Point(float(x), float(y))
            for i in self.index.intersection(p.bounds):
                if p.intersects(self.shape[i]):
                    return self.blkgrp[i]
        return ""