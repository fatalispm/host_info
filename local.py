"""
Store user settings here
"""

import os

import configparser

CONFROOT = os.environ.get('CONFROOT', '')

db_conf_path = os.path.join(CONFROOT, 'db.cfg')

parser = configparser.ConfigParser(
    dict(user='i1', password='password', host='localhost',
         database='host'))

parser.read(db_conf_path)

host = parser.get('db', 'host')
username = parser.get('db', 'username')
password = parser.get('db', 'password')
db = parser.get('db', 'database')

settings = dict(host=host, user=username, database=db, password=password)

