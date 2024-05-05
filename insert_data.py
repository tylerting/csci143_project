import argparse
import sqlalchemy
from sqlalchemy import create_engine
from tqdm import tqdm
import faker
import random
import string
from sqlalchemy.exc import IntegrityError

# Define command-line arguments
#parser = argparse.ArgumentParser()
#parser.add_argument('--db', required=True)
#parser.add_argument('--print_every', type=int, default=1000)
#args = parser.parse_args()

# Create database connection
#engine = create_engine(args.db, connect_args={'application_name': 'insert_data.py'})
# Define the database URI
#db_uri = "postgresql://postgres:pass@localhost:9373"
db_uri = "postgresql://postgres:pass@localhost:9373"
engine = create_engine(db_uri, connect_args={'application_name': 'insert_data.py'})
connection = engine.connect()

# Create Faker instance
fake = faker.Faker()

# Define characters for alphanumeric string generation
alphanumeric_chars = string.ascii_letters + string.digits

# Function to generate random alphanumeric strings
def generate_random_alphanumeric(length):
    return ''.join(random.choice(alphanumeric_chars) for _ in range(length))

# Function to generate random users
def generate_users(num_users):
    for i in tqdm(range(num_users), desc="Generating Users"):
        user_id = i + 1
        username = generate_random_alphanumeric(10)  # Adjust length as needed
        password = generate_random_alphanumeric(12)  # Adjust length as needed
        age = random.randint(18, 80)
        connection.execute("INSERT INTO users (username, password, age) VALUES (%s, %s, %s)", (username, password, age))
        print("user",i)

def generate_tweet_urls(num_tweet_urls, max_tweet_id, max_url_id):
    for i in tqdm(range(num_tweet_urls), desc="Generating Tweet URLs"):
        tweet_id = random.randint(1, max_tweet_id)
        url_id = random.randint(1, max_url_id)
        try:
            connection.execute("INSERT INTO tweet_urls (id_tweets, id_urls) VALUES (%s, %s)", (tweet_id, url_id))
            print("tweet_url", i)
        except IntegrityError as e:
            # Handle the case where the record already exists
            print(f"Skipping duplicate tweet_url: {tweet_id}, {url_id}")

messages_list = [
    "hello world", "hola mundo", "salve munde",
    "Big Data is hard", "The final is hard", "Mike, please be merciful",
    "I love my dog", "Henry is smort", "I am excited for summer"
]
# Function to generate random messages
def generate_messages(num_messages):
    for i in tqdm(range(num_messages), desc="Generating Messages"):
        sender_id = random.randint(1, 100)  # Assuming users have IDs up to 1 million
        message = messages_list[i % len(messages_list)]
        connection.execute("INSERT INTO messages (sender_id, message) VALUES (%s, %s)", (sender_id, message))
        print("message",i)

# Call functions to generate data
generate_tweet_urls(1000000, 1000, 100)

# Close the connection
connection.close()
