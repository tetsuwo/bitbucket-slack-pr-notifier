#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sqlite3
import sys

# ----

SQLITE_DB_FILE = os.environ.get('SQLITE_DB_FILE')

# ----

con = sqlite3.connect(SQLITE_DB_FILE)
cur = con.cursor()

cur.execute("DROP TABLE IF EXISTS pull_requests")

cur.execute("""
    CREATE TABLE pull_requests (
        id INTEGER, 
        repository_name VARCHAR(100), 
        created_at TIMESTAMP,
        checked_at TIMESTAMP,
        PRIMARY KEY(id, repository_name)
    )
""")

con.commit()
con.close()

print 'Completed'
