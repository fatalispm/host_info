"""
Module for deleting urls older than some time
"""

import os

import connector
import db_api
from local import settings

if __name__ == '__main__':
    hours = os.getenv('HOURS', 24)
    connection = connector.get_connection(settings)

    db_api.delete_old_urls(connection, hours)
