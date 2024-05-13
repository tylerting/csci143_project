import sqlalchemy
import string
import argparse
import random
from tqdm import tqdm
from sqlalchemy.exc import IntegrityError

# setting up the parser

parser = argparse.ArgumentParser()
parser.add_argument('--db', required=True)
parser.add_argument('--user_rows', default=100)
args = parser.parse_args()

# setting up the connection

engine = sqlalchemy.create_engine(args.db, connect_args={'application_name': 'load_tweets.py'})
connection = engine.connect()


with open('dictionary.txt', 'r') as file:
    word_list = file.read().split('\n')


def generate_words(num_words):
    random_words = random.sample(word_list, num_words)
    return random_words

# Generating Random Users
def generate_users(num_users):
    for i in tqdm(range(num_users), desc="Currently Generating and Populating Users"):
        # As id is BIGSERIAL No Need To Generate
        username=''.join(generate_words(2))
        password=''.join(generate_words(3))
        age=random.randint(8,100)
        cell=''.join([str(random.randint(0,9)) for _ in range(10)])
        sql=sqlalchemy.sql.text("""INSERT INTO users (username, password, age, cell) VALUES (:u, :p, :a, :c);""")
        try:
            res = connection.execute(sql, {
                'u': username,
                'p': password,
                'a': age,
                'c': cell
                })
        except IntegrityError as e:
            print("Could Not Insert User Number: ",i, " Due To Duplication ","Error Message: ", e)

# Generating Random Urls
def generate_urls(num_urls):
    for i in tqdm(range(num_urls), desc="Currently Generating and Populating Urls"):
        # As id_urls is BIGSERIAL No Need To Generate
        url=''.join(generate_words(4))
        sql=sqlalchemy.sql.text("""INSERT INTO urls (url) VALUES (:url);""")
        try:
            res = connection.execute(sql, {
                'url': url,
                })
        except IntegrityError as e:
            print("Could Not Insert Url Number" ,i," Due To Duplication ","Error Message: ", e)

# Generating Random Messages
def generate_messages(num_messages):
    # Check which Users can send messages
    sql = sqlalchemy.sql.text("""SELECT id FROM users;""")
    res = connection.execute(sql)
    creator_ids = [tup[0] for tup in res.fetchall()]    
    for i in tqdm(range(num_messages), desc="Currently Generating and Populating Messages"):
        # As id is BIGSERIAL No Need To Generate
        creator_id = random.choice(creator_ids)
        message=''.join(generate_words(5))
        sql=sqlalchemy.sql.text("""INSERT INTO messages (creator_id, message) VALUES (:ci, :m);""")
        try:
            res = connection.execute(sql, {
                'ci': creator_id,
                'm': message
                })
        except IntegrityError as e:
            print("Could Not Insert Message: ",i," Due To Duplication ","Error Message: ", e)

# Generating Data
generate_users(5400*int(args.user_rows))
generate_urls(10000*int(args.user_rows))
generate_messages(10000 * int(args.user_rows))

connection.close()
