import requests
import json
import xlsxwriter
from copy import deepcopy
import pandas

def read_file(filename):
  return open(str(filename), 'r').read()

def cross_join(left, right):
    new_rows = []
    for left_row in left:
        for right_row in right:
            temp_row = deepcopy(left_row)
            for key, value in right_row.items():
                temp_row[key] = value
            new_rows.append(deepcopy(temp_row))
    return new_rows


def flatten_list(data):
    for elem in data:
        if isinstance(elem, list):
            yield from flatten_list(elem)
        else:
            yield elem


def json_to_dataframe(data_in):
    def flatten_json(data, prev_heading=''):
        if isinstance(data, dict):
            rows = [{}]
            for key, value in data.items():
                rows = cross_join(rows, flatten_json(value, prev_heading + '.' + key))
        elif isinstance(data, list):
            rows = []
            for i in range(len(data)):
                [rows.append(elem) for elem in flatten_list(flatten_json(data[i], prev_heading))]
        else:
            rows = [{prev_heading[1:]: data}]
        return rows

    return pandas.DataFrame(flatten_json(data_in))

json_query = read_file("GitHub_activity.graphql")
url = 'https://api.github.com/graphql'
headers = {"Authorization": "Bearer 3b477ada5a779a8b8567861418ae57e19d68b53f"}
r = requests.post(url, json={'query': json_query}, headers=headers)

json_data = json.loads(r.text)
print(json_data)
AJ_data = json_data['data']['nodes']
spreadsheet = json_to_dataframe(AJ_data)
spreadsheet.to_csv('test_Pandaspreadsheet2.csv')
print(spreadsheet)

