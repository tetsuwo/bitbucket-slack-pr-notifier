#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import json
from requests_oauthlib import OAuth1Session
import os
import random
import requests
import sqlite3
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
SQLITE_DB_FILE = os.environ.get('SQLITE_DB_FILE')

# ----

con = sqlite3.connect(SQLITE_DB_FILE)
cur = con.cursor()
api = OAuth1Session(BITBUCKET_CONSUMER_KEY, BITBUCKET_CONSUMER_SECRET)

# ----

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
CURRENT_TIME = datetime.datetime.now()
COMPARE_TIME = CURRENT_TIME - datetime.timedelta(minutes=120)

for repo in BITBUCKET_REPOSITORIES.split(','):
    print '[%s]' % repo
    api_request_url = BITBUCKET_API_ENDPOINT % (BITBUCKET_OWNERNAME, repo)
    req = api.get(api_request_url)
    if req.status_code != 200:
        print u'  Error: %d (%s)' % (req.status_code, req.text)
        continue
    response = json.loads(req.text)
    for row in response['values']:
        print u'  Pull Request ID: %d' % row['id']
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

        sql = 'SELECT id, checked_at FROM pull_requests WHERE id = ? AND repository_name = ? LIMIT 1'
        cur.execute(sql, (row['id'], row['source']['repository']['full_name']))
        res = cur.fetchone()
        has_record = res != None
        if has_record == True:
            target_time = datetime.datetime.strptime(res[1], DATETIME_FORMAT)
            if False == (target_time <= COMPARE_TIME):
                print '  - Skipped:', row['id'], row['source']['repository']['full_name']
                print '  - CheckedAt:', target_time, COMPARE_TIME
                continue

        try:
            res = requests.post(
                SLACK_WEBHOOK_URL, 
                json.dumps(payload), 
                headers={'content-type': 'application/json'}
            )
            print '  - Response:', res
            if has_record == True:
                cur.execute(
                    u"UPDATE pull_requests SET checked_at = ? WHERE id = ? AND repository_name = ?",
                    (
                        datetime.datetime.strftime(CURRENT_TIME, '%Y-%m-%d %H:%M:%S'),
                        int(row['id']),
                        row['source']['repository']['full_name']
                    )
                )
                con.commit()
            else:
                cur.execute(
                    u"INSERT INTO pull_requests VALUES (?, ?, ?, ?)",
                    (
                        int(row['id']),
                        row['source']['repository']['full_name'],
                        datetime.datetime.strftime(CURRENT_TIME, '%Y-%m-%d %H:%M:%S'),
                        datetime.datetime.strftime(CURRENT_TIME, '%Y-%m-%d %H:%M:%S')
                    )
                )
                con.commit()
        except Exception as e:
            print '  - Error:', e
    print '  Finished'
    time.sleep(0)
    print ''

con.close()

print 'Completed'
