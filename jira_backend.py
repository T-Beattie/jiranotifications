import requests
from requests.auth import HTTPBasicAuth
import json
import os
import datetime


BASE_URL = os.getenv('JIRA_URL')

AUTH_EMAIL = os.getenv('JIRA_EMAIL')
AUTH_KEY = os.getenv('JIRA_KEY')

AUTH = HTTPBasicAuth(AUTH_EMAIL, AUTH_KEY)

def get_request(request_url, request_headers, request_params=''):
    response = requests.request(
        "GET",
        request_url,
        headers=request_headers,
        params=request_params,
        auth=AUTH
    )
    if response.status_code != 400:
        return json.loads(response.text)
    else:
        print 'failed - Could not access jira with credentials'

def get_new_issues():
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    query = {
        'jql': 'statusCategory in (2, 4) AND assignee in (EMPTY) AND issuetype in ("Workflow feature request", "Workflow Issue", "Project configuration issue", "Cross site syncing", "Shotgun issue", "Publish Job Issue", "Render Job issue") and createdDate > -1m',
        "maxResults": 100,
    }

    my_url = BASE_URL + '/search'
    return  get_request(my_url, headers, query)['issues']

def get_issues_between_times(last_ran_time):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    query = {
        'jql': 'statusCategory in (2, 4) AND assignee in (EMPTY) AND issuetype in ("Workflow feature request", "Workflow Issue", "Project configuration issue", "Cross site syncing", "Shotgun issue", "Publish Job Issue", "Render Job issue") and createdDate < -1m AND createdDate > ',
        "maxResults": 100,
    }

    my_url = BASE_URL + '/search'
    return  get_request(my_url, headers, query)['issues']