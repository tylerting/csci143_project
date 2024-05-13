import sqlalchemy
import bleach
import os
from datetime import datetime  # Import the datetime module here

from flask import (
    Flask,
    request,
    render_template,
    make_response,
    redirect,
    url_for,
    flash,
    session
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import text

app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)

engine = sqlalchemy.create_engine(
    "postgresql://postgres:pass@postgres:5432",
    connect_args={'application_name': '__init__.py'}
)

connection = engine.connect()


if __name__ == "__main__":
    # Bind to all network interfaces and specify the port to run on
    app.run(host='0.0.0.0', port=5432)


class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email


def fetch_latest_messages(page_number):
    offset = (page_number - 1) * 20
    query = text("""
        SELECT creator_id, message, time, id
        FROM messages
        ORDER BY time DESC
        LIMIT 20 OFFSET :offset;
    """)
    result = connection.execute(query, {'offset': offset})

    sender_ids = [row[0] for row in result.fetchall()]
    user_data_map = {}

    # Initialize user_query with None
    user_query = None

    if sender_ids:
        user_query = text("""
            SELECT id, username, age
            FROM users
            WHERE id IN :ids;
        """)

    if user_query is not None:
        user_result = connection.execute(
            user_query,
            {'ids': tuple(sender_ids)}
        )

        user_data_map = {
            row[0]: (row[1], row[2])
            for row in user_result.fetchall()
        }

    result = connection.execute(query, {'offset': offset})

    messages = []
    for row in result:
        sender_id, message, created_at, msg_id = row
        username, age = user_data_map.get(sender_id, (None, None))
        cleaned_message = bleach.clean(message)
        linked_message = bleach.linkify(cleaned_message)
        messages.append({
            'id': msg_id,
            'message': linked_message,
            'username': username,
            'age': age,
            'created_at': created_at,
        })

    return messages


# def login_info(username, password):
#    query = text('''
#        SELECT id, age
#        FROM users
#        WHERE username = :username AND password = :password;
#    ''')
#    result = connection.execute(
#        query,
#        {
#            'username': username,
#            'password': password,
#        }
#    )
#
#    row = result.fetchone()

def login_info(username, password):
    query = text('''
        SELECT id, age
        FROM users
        WHERE username = :username AND password = :password;
    ''')
    try:
        result = connection.execute(
            query,
            {
                'username': username,
                'password': password
            }
        )

        row = result.fetchone()
        return row
    except Exception as e:
        # Log the error and roll back the transaction if necessary
        print(f"Error occurred: {e}")
        connection.rollback()  # Roll back the transaction
        return None


@app.route('/')
def root():
    # Get logged-in status from session or cookies
    logged_in = session.get('logged_in', False)
    username = session.get('username', request.cookies.get('username'))
    password = request.cookies.get('password')
    age = None
    # Fetch user info if logged in
    if logged_in:
        login = login_info(username, password)
        if login:
            user_id, age = login
        else:
            logged_in = False
            session.clear()

    # Set the current page number
    page_number = int(request.args.get('page', 1))

    # Fetch the latest messages
    messages = fetch_latest_messages(page_number)

    # Render the template with context
    return render_template(
        'root.html',
        messages=messages,
        logged_in=logged_in,
        username=username,
        age=age,
        page_number=page_number
    )


def print_debug_info():
    # GET method
    print('request.args.get("username") =', request.args.get("username"))
    print('request.args.get("password") =', request.args.get("password"))

    # POST method
    print('request.form.get("username") =', request.form.get("username"))
    print('request.form.get("password") =', request.form.get("password"))

    # cookies
    print('request.cookies.get("username") =', request.cookies.get("username"))
    print('request.cookies.get("password") =', request.cookies.get("password"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Print debug information
    print_debug_info()

    # If the request is a POST, handle form data
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        password = request.form.get('password')

        # Authenticate the user
        user_info = authenticate_user(username, password)

        # If the user is authenticated, handle successful login
        if user_info:
            return handle_successful_login(user_info, username)

        # Handle failed login
        return handle_failed_login()

    # Render the login form for GET requests
    return render_template('login.html')


def authenticate_user(username, password):
    return login_info(username, password)


def handle_successful_login(user_info, username):
    user_id, age = user_info
    session['user_id'] = user_id
    session['username'] = username
    session['logged_in'] = True

    # Set cookies for username and password
    response = make_response(redirect(url_for('root')))
    response.set_cookie('username', username)
    response.set_cookie('password', request.form.get('password'))

    return response


def handle_failed_login():
    flash('Incorrect username or password. Please try again.')
    return render_template('login.html', bad_credentials=True)


@app.route('/logout')
def logout():
    # Create a response to render the logout.html template
    response = make_response(render_template('logout.html'))

    # Delete the cookies and clear session data
    response.set_cookie('username', '', expires=0)
    response.set_cookie('password', '', expires=0)
    session.clear()  # Clear the session data

    # Return the response to the client
    return response


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    # Print debug information
    print_debug_info()

    # Get logged-in status from session or cookies
    logged_in = session.get('logged_in', False)
    # username = session.get('username', request.cookies.get('username'))
    # password = request.cookies.get('password')

    # Redirect logged-in users to home page
    if logged_in:
        return redirect('/')

    # Handle form submission
    if request.method == 'POST':
        new_username = request.form.get('new_username')
        new_password = request.form.get('new_password')
        new_password2 = request.form.get('new_password2')
        new_age = request.form.get('new_age')

        # Check for empty fields
        if not new_username or not new_password:
            return render_template('create_user.html', one_blank=True)

        # Check for matching passwords
        if new_password != new_password2:
            return render_template('create_user.html', not_matching=True)

        # Check for valid age input
        if not new_age.isnumeric():
            return render_template('create_user.html', invalid_age=True)

        # Try creating a new user
        try:
            sql = text('''
                INSERT INTO users (username, password, age)
                VALUES (:username, :password, :age)
            ''')
            connection.execute(sql, {
                'username': new_username,
                'password': new_password,
                'age': int(new_age)  # Convert age to integer
            })

            # Create response and set cookies
            response = make_response(redirect('/'))
            response.set_cookie('username', new_username)
            response.set_cookie('password', new_password)
            return response
        except sqlalchemy.exc.IntegrityError:
            # Handle case where user already exists
            return render_template('create_user.html', already_exists=True)

    # Render the create_user.html template for GET requests
    return render_template('create_user.html')


@app.route('/create_message', methods=['GET', 'POST'])
def create_message():
    # Print debug information
    print_debug_info()

    # Retrieve logged-in status and user credentials from cookies/session
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    logged_in = session.get('logged_in', False)

    # Check if the user is logged in
    if not logged_in:
        return redirect('/')

    # Retrieve user ID based on username and password
    user_query = text(
        "SELECT id FROM users "
        "WHERE username = :username AND password = :password"
    )

    result = connection.execute(
        user_query,
        {
            "username": username,
            "password": password,
        }
    )

    row = result.fetchone()

    # Handle case where user is not found
    if not row:
        return redirect('/')
    creator_id = row[0]

    # Handle form submission
    if request.method == 'POST':
        message = request.form.get('message')

        # Validate form data
        if not message:
            return render_template(
                'create_message.html',
                invalid_message=True,
                logged_in=logged_in
            )

        # Insert the new message
        try:
            time = str(datetime.now()).split('.')[0]
            insert_query = text("""
                INSERT INTO messages (creator_id, message, time)
                VALUES (:creator_id, :message, :time);
            """)
            connection.execute(insert_query, {
                "creator_id": creator_id,
                "message": message,
                "time": time
            })

            # Successfully created message
            return render_template(
                'create_message.html',
                message_sent=True,
                logged_in=logged_in
            )

        except sqlalchemy.exc.IntegrityError:
            # Handle error (e.g., if there was an issue with insertion)
            return render_template(
                'create_message.html',
                already_exists=True,
                logged_in=logged_in
            )

    # Render the create_message.html template for GET requests
    return render_template('create_message.html', logged_in=logged_in)


def query_messages(query, a):

    messages = []
    sql = sqlalchemy.sql.text("""
    SELECT
    creator_id,
    ts_headline(message, to_tsquery(:query),
    'StartSel="<span class=query><b>",
    StopSel="</b></span>"') AS highlighted_message,
    time,
    messages.id,
    username,
    age
    FROM messages
    JOIN users ON (messages.creator_id = users.id)
    WHERE to_tsvector('english', message) @@ to_tsquery(:query)
    ORDER BY
    ts_rank(to_tsvector('english', message), to_tsquery(:query)) DESC,
    time DESC
    LIMIT 20 OFFSET :offset;
    """)

    res = connection.execute(sql, {
        'offset': 20 * (a - 1),
        'query': ' & '.join(query.split())
   })

    print('inside query_messages')

    for row_messages in res.fetchall():

        message = row_messages[1]
        cleaned_message = bleach.clean(
            message,
            tags=['b', 'span'],
            attributes={'span': ['class']}
        )
        linked_message = bleach.linkify(cleaned_message)

        image_url = 'https://robohash.org/' + row_messages[4]

        # build the message dictionary
        messages.append({
            'id': row_messages[3],
            'message': linked_message,
            'username': row_messages[4],
            'age': row_messages[5],
            'created_at': row_messages[2],
            'image_url': image_url
        })

    return messages


def give_suggestion(query):

    suggestion_list = []

    for word in query.split():

        sql = sqlalchemy.sql.text("""
        SELECT word, sml
        FROM fts_word,
        SIMILARITY(word, :query) AS sml
        ORDER BY sml DESC LIMIT 1;
        """)

        res = connection.execute(sql, {
            'query': word
        })

        try:
            suggestion_list.append(res.fetchone()[0])
        except TypeError:
            pass

    suggestion = ' '.join(suggestion_list)
    print('suggestion=', suggestion)
    return suggestion


@app.route('/search', methods=['GET', 'POST'])
def search_message():
    # Get username and password from cookies/session
    username = request.cookies.get('username')
    logged_in = session.get('logged_in', False)

    # Check if the user is logged in
    if not logged_in:
        return redirect('/')

    page_number = int(request.args.get('page', 1))

    if request.form.get('query'):
        query = request.form.get('query')
    else:
        query = request.args.get('query', '')

    print('before query_messages')

    if query:
        messages = query_messages(query, page_number)
        suggestion = give_suggestion(query)
    else:
        messages = fetch_latest_messages(page_number)
        suggestion = ''

    response = make_response(render_template(
        'search.html',
        messages=messages,
        logged_in=logged_in,
        username=username,
        page_number=page_number,
        query=query,
        suggestion=suggestion
    ))

    if query:
        response.set_cookie('query', query)

    return response


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
    return """
    <!doctype html>
    <title>upload new File</title>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file><input type=submit value=Upload>
    </form>
    """
