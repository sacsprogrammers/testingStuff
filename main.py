import requests
import json
from copy import deepcopy
import pandas
from string import Template

#======================================================================================================
#                                               Functions
#======================================================================================================

#------------------------------------------------------------------------------------------------------
# FUNCTION NAME: read_file
# DESCRIPTION: Simple function that opens the GraphQL file as READ ONLY
# PARAMETERS:
#      query  - JSON query object
#------------------------------------------------------------------------------------------------------

def read_file(filename):
  return open(str(filename), 'r').read()

#------------------------------------------------------------------------------------------------------
# FUNCTION NAME: cross_join
# DESCRIPTION: joins the rows in the spreadsheet together
# PARAMETERS:
#
#------------------------------------------------------------------------------------------------------

def cross_join(left, right):
    new_rows = []
    for left_row in left:
        for right_row in right:
            temp_row = deepcopy(left_row)
            for key, value in right_row.items():
                temp_row[key] = value
            new_rows.append(deepcopy(temp_row))
    return new_rows

#------------------------------------------------------------------------------------------------------
# FUNCTION NAME: flatten_list
# DESCRIPTION: used in relation with json_to_dataframe to "flatten" the data to separate the information from the "edges" and "nodes"
# PARAMETERS:
#
#------------------------------------------------------------------------------------------------------

def flatten_list(data):
    for elem in data:
        if isinstance(elem, list):
            yield from flatten_list(elem)
        else:
            yield elem

#------------------------------------------------------------------------------------------------------
# FUNCTION NAME: json_to_dataframe
# DESCRIPTION: separates the data and headers from the rest of the GraphQL Data using a process called "flattening" and puts it into a spreadsheet. Uses functions flatten_list and cross_join
# PARAMETERS:
#      query  - JSON query object
#      dataframe - Pandas function that creates spreadsheet
#------------------------------------------------------------------------------------------------------

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

#------------------------------------------------------------------------------------------------------
# FUNCTION NAME: insert_space
# DESCRIPTION: simple function that allows you to insert a space between words (specifically used for the headers)
# PARAMETERS:
#
#------------------------------------------------------------------------------------------------------

def insert_space(word, index):
  return word[:index] + ' ' + word[index:]

#------------------------------------------------------------------------------------------------------
# FUNCTION NAME: capitalize_headers
# DESCRIPTION: similar to insert_space but instead capitalizes the first word in the header
# PARAMETERS:
#
#------------------------------------------------------------------------------------------------------

def capitalize_headers(headers):
  return headers[:1].capitalize() + headers[1:]

#------------------------------------------------------------------------------------------------------
# FUNCTION NAME: clean_headers
# DESCRIPTION: cleans the headers, with help from the functions insert_space and capitalize_headers, by removing unnecessary characters and making them easy to read
# PARAMETERS:
#
#------------------------------------------------------------------------------------------------------

def clean_headers(prev_heading):
  filter_heading = prev_heading.rindex('.')
  prev_heading = prev_heading[filter_heading + 1:]
  for i in prev_heading:
    if i.isupper() == True:
      num = prev_heading.index(i)
      prev_heading = insert_space(prev_heading, num)
  prev_heading = capitalize_headers(prev_heading)
  return prev_heading

#------------------------------------------------------------------------------------------------------
# FUNCTION NAME: confirm_query
# DESCRIPTION: confirms whether the query worked or not. Useful to determine if the authorization token expired
# PARAMETERS:
#       query   - JSON query object
#------------------------------------------------------------------------------------------------------

def confirm_Query(json_data, r):
  if "Bad credentials" in r.text:
    r = read_file("sampleresults.json")
    json_data = json.loads(r)
    print("============Replaced with")
    return json_data
  else:
    print("============query worked")
    return json_data

#------------------------------------------------------------------------------------------------------
# FUNCTION NAME: retrieve_Query_information
# DESCRIPTION: captures the required information from the previous GraphQL Query
# PARAMETERS:
#      query  - JSON query object
#------------------------------------------------------------------------------------------------------

def retrieve_Query_information (spreadsheet, counter=0):
  if counter == 0:
    counter = 1
    # captures from the last row, which is one less than the total number of rows since it starts counting at 0. Change integer to the last row if you change the numbered queried at one time
    has_next_page = spreadsheet.iloc[8]['Has Next Page']
    cursor = spreadsheet.iloc[8]['Cursor']
    total_count = spreadsheet.iloc[8]['Total Count']
    return has_next_page, cursor, total_count, counter
  else:
    cursor = spreadsheet.iloc[8]['Cursor']
    return cursor

#------------------------------------------------------------------------------------------------------
# FUNCTION NAME: first_Time_through
# DESCRIPTION: runs the query the first time. Main difference between this and MAIN CONTROL is that this includes the first audit log that it starts on whilst MAIN CONTROL excludes it
# PARAMETERS:
#      query  - JSON query object
#------------------------------------------------------------------------------------------------------

def first_Time_through(cursor, final, has_next_page):
  json_query = read_file("GitHub_activity.graphql")
  queryTemplate = Template(json_query)
  url = 'https://api.github.com/graphql'
  headers = {"Authorization": "Bearer 482dd10370d60fe39152e27e7adc104a2f111b27"}
  queryTemplate = queryTemplate.substitute(MYCURSOR=cursor)
  r = requests.post(url, json={'query': queryTemplate}, headers=headers)

  json_data = json.loads(r.text)
  json_data = confirm_Query(json_data, r)
  AJ_data = json_data['data']['nodes']
  spreadsheet = json_to_dataframe(AJ_data)
  has_next_page, cursor, total_count, counter = retrieve_Query_information(spreadsheet)
  final = final.append(spreadsheet, ignore_index=True)
  return spreadsheet, final, has_next_page, cursor, total_count, counter

#======================================================================================================
#                                             MAIN CONTROL
#======================================================================================================
cursor = 	"null"
has_next_page = True
final = pandas.DataFrame()

# runs the query one time through so that the first audit log is included
spreadsheet, final, has_next_page, cursor, total_count, counter = first_Time_through(cursor, final, has_next_page)

# keeps running until all logs are retrieved, starting after the one that it stops at 
while has_next_page == True:
  json_query = read_file("GitHub_activity.graphql")
  url = 'https://api.github.com/graphql'

  # you'll need to consistently change the Bearer Token as they expire
  headers = {"Authorization": "Bearer 482dd10370d60fe39152e27e7adc104a2f111b27"}

  # replaces the "variable" in the GraphQL Query with end cursor
  json_query = json_query.replace("$MYCURSOR", f'\"{cursor}\"')
  r = requests.post(url, json={'query': json_query}, headers=headers)

  json_data = json.loads(r.text)
  json_data = confirm_Query(json_data, r)
  AJ_data = json_data['data']['nodes']

  # puts the data into a spreadsheet
  spreadsheet = json_to_dataframe(AJ_data)
  final = final.append(spreadsheet, ignore_index=True)
  print(final)

  # determines if it has received all of the audit logs
  if len(final.index) >= total_count:
    has_next_page = False
  elif len(final.index) <= total_count:
    cursor = retrieve_Query_information(spreadsheet, counter)

# converts the spreadsheet into a csv file
final.to_csv('test_Pandaspreadsheet15.csv')
