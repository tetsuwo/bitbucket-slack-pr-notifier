#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from requests_oauthlib import OAuth1Session
import os
import random
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
SLACK_TEXTS = os.environ.get('SLACK_TEXTS')

# ----

api = OAuth1Session(BITBUCKET_CONSUMER_KEY, BITBUCKET_CONSUMER_SECRET)

for repo in BITBUCKET_REPOSITORIES.split(','):
    print '[%s]' % repo
    api_request_url = BITBUCKET_API_ENDPOINT % (BITBUCKET_OWNERNAME, repo)
    print '  API Request URL: ' + api_request_url
    req = api.get(api_request_url)
    if req.status_code != 200:
        print u'  Error: %d (%s)' % (req.status_code, req.text)
        continue
    response = json.loads(req.text)
    for row in response['values']:
        print u'  Pull Request ID: %d' % row['id']
        print '  ----'
        title = '#%d: %s' % (row['id'], row['title'])
        text = random.choice(SLACK_TEXTS.split(','))
        payload = {
            'title': title,
            'text': text,
            'channel': SLACK_CHANNEL,
            'username': SLACK_USERNAME,
            'icon_emoji': SLACK_ICON_EMOJI,
            'mrkdwn': True,
            'attachments': [{
                'color': '#1f3134',
                'title': title,
                'title_link': row['links']['html']['href'],
                'text': row['description'],
                'author_name': row['author']['username'],
                'author_icon': row['author']['links']['avatar']['href'],
                'mrkdwn_in': ['text', 'pretext', 'fields'],
                'fields': [
                    {
                        'title': 'Pull Request#',
                        'value': row['id'],
                        'short': True
                    },
                    {
                        'title': 'Author',
                        'value': '%s (%s)' % (row['author']['username'], row['author']['display_name']),
                        'short': True
                    },
                    {
                        'title': 'Repository Name',
                        'value': row['source']['repository']['full_name'],
                        'short': True
                    },
                    {
                        'title': 'Branch Situation',
                        'value': '`%s` from `%s`' % (row['destination']['branch']['name'], row['source']['branch']['name']),
                        'short': True
                    }
                ]
            }]
        }
        try:
            res = requests.post(
                SLACK_WEBHOOK_URL, 
                json.dumps(payload), 
                headers={'content-type': 'application/json'}
            )
            print res
        except Exception as e:
            print u'Error:' + e
        print '  ===='
    print '  Finished'
    time.sleep(1)

print 'Completed'
