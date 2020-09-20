

import requests
import json


#authentication token = 1b5cf4050ba63218bf99ee2b1a36cbb7c7f31cca

"""
logCursor = 'MDEyOk9yZ2FuaXphdGlvbjcwODc1OTk2'
auth_token = '03abaa8b82490d88a7a0e4d41f3970356a396274'

def run_query(query, logCursor, headers=None, username=None, password=None):
    json = {'query': query }
    if (logCursor is not None):
        json['logCursor'] = logCursor
    if (headers is None):
        headers = { "Authorization": "token {}".format(auth_token)}
    if (username is not None):
        auth_string = username
        if (password is not None):
            auth_string = auth_string + ':' + password
    else:
        proxies = None
    r = requests.get('https://repl.it/@AJAmos/testingStuff#GitHub_activity.graphql')
    if r.status_code == 200:
        return r.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


def read_file(filename):
  return open(str(filename), 'r').read()

gitHub_query = read_file("GitHub_activity.graphql").replace('\n','').replace('\t','')
result = run_query(gitHub_query, logCursor)
print(result)
"""


#testing connection

#test = open(str("GitHub_activity.graphql"), 'r').read()
#print(test)

query = """query{
  nodes(ids: ["MDEyOk9yZ2FuaXphdGlvbjcwODc1OTk2", "MDEyOk9yZ2FuaXphdGlvbjcwODc2MjE5"]) {
    id
    __typename
    ... on Organization {
      name
      repositories(first: 100) {
        totalCount
        totalDiskUsage
        edges {
          repository: node {
            name
          }
        }
      }
      auditLog(first: 7) {
        totalCount
        edges {
          cursor
          AuditEntry: node {
            ... on AuditEntry {
              action
              createdAt
              ... on TeamAuditEntryData {
                teamName
              }
              ... on RepositoryAuditEntryData {
                repositoryName
              }
              ... on OrganizationAuditEntryData {
                organizationName
              }
              memberDetails: user {
                name
                email
              }
              actor {
                category: __typename
                ... on User {
                  login
                  email
                  name
                }
              }
            }
          }
        }
        pageInfo {
          endCursor
          hasNextPage
        }
      }
    }
  }
}
"""


print(query)

url = 'https://repl.it/@AJAmos/testingStuff#GitHub_activity.graphql'
r = requests.post(url, json={'query': query})
print(r.status_code)
print(r.text)

"""
#transform into json
json_data = json.loads(r.text)

#organise it
df_data = json_data[‘data’][‘organisations’][‘edges’]
df = pd.DataFrame(df_data)
print(df)
"""



