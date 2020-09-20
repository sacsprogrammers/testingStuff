import requests
import json
import xlsxwriter


def read_file(filename):
  return open(str(filename), 'r').read()

"""
json_query = read_file("GitHub_activity.graphql")
url = 'https://api.github.com/graphql'
headers = {"Authorization": "Bearer 1b5cf4050ba63218bf99ee2b1a36cbb7c7f31cca"}
r = requests.post(url, json={'query': json_query}, headers=headers)
#print(json_query)

json_data = json.loads(r.text)
AJ_data = json_data['data']['nodes']
print(AJ_data)
"""

# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook('Expenses02.xlsx')
worksheet = workbook.add_worksheet()

# Some data we want to write to the worksheet.
expenses = (
    ['Rent', 1000],
    ['Gas',   100],
    ['Food',  300],
    ['Gym',    50],
)

# Start from the first cell. Rows and columns are zero indexed.
row = 0
col = 0

# Iterate over the data and write it out row by row.
for item, cost in (expenses):
    worksheet.write(row, col,     item)
    worksheet.write(row, col + 1, cost)
    row += 1

# Write a total using a formula.
worksheet.write(row, 0, 'Total')
worksheet.write(row, 1, '=SUM(B1:B4)')

workbook.close()

