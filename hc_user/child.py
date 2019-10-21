#from ..csv_utils.csv_modifier import CSVModifier, InputDelim
import sys

print("sys.path")
[print(path) for path in sys.path]

print("{} __name__: {}".format(__file__,__name__))
print("{} __package__: {}".format(__file__,__package__))

#from csv_utils.csv_modifier import CSVModifier, InputDelim

from csv_utils.csv_handler import CSVHandler
print(CSVHandler)