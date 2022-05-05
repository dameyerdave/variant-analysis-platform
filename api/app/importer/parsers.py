from os.path import isfile
import csv

class Parser():
    def parse(file):
        raise NotImplementedError("You must implement parse in Parser.")

class TsvParser(Parser):
    def parse(self, file):
        if isfile(file):
          with open(file, 'r') as f:
              reader = csv.DictReader(f, delimiter="\t")
              for row in reader:
                 yield row
        else:
            raise FileNotFoundError(f"File {file} not found.")