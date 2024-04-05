# Importing the read_json function from the json_utils module of the ignutils package
from ignutils import json_utils

# Reading data from a JSON file named "file.json" using the read_json function
# The returned data will be stored in the variable named 'fil'
fil = json_utils.read_json("file.json")

# Printing the content of the variable 'fil
print(fil)