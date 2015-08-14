#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from requests_oauthlib import OAuth1Session
import os
import requests
import sys
import time

# ----

BITBUCKET_API_ENDPOINT = 'https://bitbucket.org/api/2.0/repositories/%s/%s/pullrequests'
BITBUCKET_CONSUMER_KEY = os.environ.get('BITBUCKET_CONSUMER_KEY')
BITBUCKET_CONSUMER_SECRET = os.environ.get('BITBUCKET_CONSUMER_SECRET')
BITBUCKET_OWNERNAME = os.environ.get('BITBUCKET_OWNERNAME')
BITBUCKET_REPOSITORIES = os.environ.get('BITBUCKET_REPOSITORIES')
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL')
SLACK_USERNAME = os.environ.get('SLACK_USERNAME')
SLACK_ICON_EMOJI = os.environ.get('SLACK_ICON_EMOJI')
SLACK_TEXT = os.environ.get('SLACK_TEXT')

# ----

api = OAuth1Session(BITBUCKET_CONSUMER_KEY, BITBUCKET_CONSUMER_SECRET)

for repo in BITBUCKET_REPOSITORIES.split(','):
    print '[%s]' % repo
    api_request_url = BITBUCKET_API_ENDPOINT % (BITBUCKET_OWNERNAME, repo)
    print '  API Request URL: ' + api_request_url
    req = api.get(api_request_url)
    if req.status_code != 200:
        print ('  Error: %d (%s)' % (req.status_code, req.text))
        continue
    response = json.loads(req.text)
    for row in response['values']:
        print row
        print '  Pull Request ID: %d' % row['id']
        print '  Pull Request Title: %s' % row['title']
        print '  ----'
        text = 'Diff URL: %s' % row['links']['diff']['href']
        payload = {
            'title': row['title'],
            'text': SLACK_TEXT,
            'channel': SLACK_CHANNEL,
            'username': SLACK_USERNAME,
            'icon_emoji': SLACK_ICON_EMOJI,
            'attachments': [{
                'title': row['title'],
                'text': text,
                'color': '#1e90ff'
            }]
        }
        try:
            #res = requests.post(
            #    SLACK_WEBHOOK_URL, 
            #    json.dumps(payload), 
            #    headers={'content-type': 'application/json'}
            #)
            print res
        except Exception as e:
            print 'Error:' + e
        print '  ===='
    print '  Finished'
    time.sleep(1)

print 'Completed'
