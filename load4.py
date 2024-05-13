import argparse
import sqlalchemy
from tqdm import tqdm
import random
import string
import time

parser = argparse.ArgumentParser()
parser.add_argument('--db', required=True) 
parser.add_argument('--user_rows', default=100)
args = parser.parse_args()

engine = sqlalchemy.create_engine(args.db, connect_args={
    'application_name': 'insert_data.py',
    })
connection = engine.connect()

# Read words from the dictionary file
with open('dictionary.txt', 'r') as file:
    word_list = file.read().split('\n')

for i, word in enumerate(word_list):
    sql = sqlalchemy.sql.text("""
    INSERT INTO fts_word (word) VALUES (:w);
    """)

    try:
        res = connection.execute(sql, {
            'w': word
        })
        if i % 1000 == 0:
            print('word', i)
    except sqlalchemy.exc.IntegrityError as e:
        pass

connection.close()
