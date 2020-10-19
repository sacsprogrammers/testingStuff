import requests
import json
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

def insert_space(word, index):
  return word[:index] + ' ' + word[index:]

def capitalize_headers(headers):
  return headers[:1].capitalize() + headers[1:]

def clean_headers(prev_heading):
  filter_heading = prev_heading.rindex('.')
  prev_heading = prev_heading[filter_heading + 1:]
  for i in prev_heading:
    if i.isupper() == True:
      num = prev_heading.index(i)
      prev_heading = insert_space(prev_heading, num)
  prev_heading = capitalize_headers(prev_heading)
  return prev_heading

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
            prev_heading = clean_headers(prev_heading)
            rows = [{prev_heading: data}]
        return rows

    return pandas.DataFrame(flatten_json(data_in))

json_query = read_file("GitHub_activity.graphql")
url = 'https://api.github.com/graphql'
headers = {"Authorization": "Bearer 575ef979a190d1dc76b4efb6a26efe5e60dfba9b"}
r = requests.post(url, json={'query': json_query}, headers=headers)
#print(r.text)

#Use to Capture a snapshot of results while token still working
#text_file = open("sampleresults.json", "w")
#text_file.write(r.text)
#text_file.close()

json_data = json.loads(r.text)
print(json_data)
if "Bad credentials" in r.text:
  print("============Replaced with")
  r = read_file("sampleresults.json")
  json_data = json.loads(r)
  print(json_data)
else:
  print("============query worked")
  
AJ_data = json_data['data']['nodes']
spreadsheet = json_to_dataframe(AJ_data)
spreadsheet.to_csv('test_Pandaspreadsheet7.csv')
print(spreadsheet)
