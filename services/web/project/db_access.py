#!/usr/bin/python3
'''
Output a summary of the contents of the twitter database.
'''

# sqlite3 is built in python3, no need to pip3 install
import sqlite3

# process command line arguments
import argparse
parser = argparse.ArgumentParser(description='Create a database for the twitter project')
parser.add_argument('--db_file', default='twitter_clone.db')
args = parser.parse_args()

# connect to the database
con = sqlite3.connect(args.db_file)
cur = con.cursor()

# print users
print('================================================================================')
print('users')
print('================================================================================')

# FIXME:
# print all of the information from the users table

sql = """
    SELECT *
    FROM users;
    """
cur_users = con.cursor()
cur_users.execute(sql)
print(cur_users.fetchall())

# print messages
print('================================================================================')
print('messages')
print('================================================================================')

# FIXME:
# print all of the information from the messages table

sql = """
    SELECT *
    FROM messages
    ORDER BY created_at DESC;
    """
cur_messages = con.cursor()
cur_messages.execute(sql)
print(cur_messages.fetchall())
