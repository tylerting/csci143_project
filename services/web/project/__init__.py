from math import ceil
from flask import Flask, jsonify, send_from_directory, render_template, request, make_response, redirect
import sqlalchemy
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from sqlalchemy.exc import IntegrityError
from datetime import datetime

app = Flask(__name__)
app.config.from_object("project.config.Config")
db = SQLAlchemy(app)
engine = sqlalchemy.create_engine("postgresql://postgres:pass@postgres:5432", connect_args={
    'application_name': '__init__.py',
    })
connection = engine.connect()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(128), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True, nullable=False)

    def __init__(self, email):
        self.email = email

@app.route('/')
def retrieve_messages():
    try:
        page_number = int(request.cookies.get('page_number', 1))
    except ValueError:
        page_number = 1

    per_page = 20  # Number of messages per page
    offset = (page_number - 1) * per_page
    if page_number < 1:
        page_number = 1

    result = connection.execute(text(
        "SELECT u.id, m.message, m.created_at "
        "FROM messages AS m "
        "JOIN users AS u ON m.id = u.id "
        "ORDER BY m.created_at DESC "
        "LIMIT :per_page OFFSET :offset;"
    ), {"per_page": per_page, "offset": offset})

    rows = result.fetchall()

    messages = []
    for row in rows:
        messages.append({
            'id': row[0],
            'message': row[1],
            'created_at': row[2],
        })

    return render_template('index.html', messages=messages)

def root():
    print_debug_info()
    '''
    text = 'hello cs40'
    text = '<strong>' + text + '</strong>' # + 100
    return text
    '''
    messages = [{}]

    # check if logged in correctly
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)
    if good_credentials:
        logged_in=True
    else:
        logged_in=False
    print('logged-in=',logged_in)

    #try:
    #    page_number=int(request.args.get('page_number'))
    #    print('page_number = ', page_number)
    #except TypeError:
    #    page_number=1

    messages=retrieve_messages()

    # render_template does preprocessing of the input html file;
    # technically, the input to the render_template function is in a language called jinja2
    # the output of render_template is html
    return render_template('root.html', messages=messages, logged_in=logged_in, username=username)


def print_debug_info():
    # GET method
    print('request.args.get("username")=', request.args.get("username"))
    print('request.args.get("password")=', request.args.get("password"))

    # POST method
    print('request.form.get("username")=', request.form.get("username"))
    print('request.form.get("password")=', request.form.get("password"))

    # cookies
    print('request.cookies.get("username")=', request.cookies.get("username"))
    print('request.cookies.get("password")=', request.cookies.get("password"))


def are_credentials_good(username, password):
    # FIXME:
    # look inside the databasse and check if the password is correct for the user
    result = connection.execute(text(
        "SELECT id FROM users WHERE username=:username AND password=:password;"
        ), {"username": username, "password": password})
    for row in result:
        if row[0]:
            return True
        else:
            return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    print_debug_info()
    username = request.form.get('username')
    password = request.form.get('password')
    print('username=', username)
    print('password=', password)

    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    # the first time we've visited, no form submission
    if username is None:
        return render_template('login.html', bad_credentials=False)

    # they submitted a form; we're on the POST method
    else:
        if not good_credentials:
            return render_template('login.html', bad_credentials=True)
        else:
            template = render_template(
                'login.html', 
                bad_credentials=False,
                logged_in=True)
            #return template
            response = make_response(template)
            response.set_cookie('username', username)
            response.set_cookie('password', password)
            return response
    


@app.route('/logout')
def logout():
    print_debug_info()

    response = make_response(render_template('logout.html'))
    response.delete_cookie('username')
    response.delete_cookie('password')
    response.delete_cookie('page_number')
    return response

@app.route('/create_account', methods=['GET','POST'])
def create_user():
    print_debug_info()

    #username=request.cookies.get('username')
    #password=request.cookies.get('password')

    #good_credentials=are_credentials_good(username, password)
    #if good_credentials:
    #    logged_in=True
    #else:
    #    logged_in=False
    #print('logged-in=',logged_in)

    #if logged_in:
    #    return redirect('/')

    username=request.form.get('new_username')
    print('new_username =', username)
    password=request.form.get('new_password')
    print('new_password =', password)
    password2=request.form.get('new_password2')
    age=request.form.get('new_age')
    print('new_age =', age)

    if username is None:
        return render_template('create_user.html')
    elif not username or not password:
        return render_template('create_user.html', one_blank=True)
    elif not age.isnumeric():
        return render_template('create_user.html', invalid_age=True)
    else:
        if password!=password2:
            return render_template('create_user.html', not_matching=True)
        else:
            try:
                result = connection.execute(text(
                    "INSERT INTO users (username, password, age) VALUES (:username, :password, :age);"
                    ),  {"username": username, "password": password, "age": age})  
                template = render_template(
                    'login.html',
                    bad_credentials=False,
                    logged_in=True)
                 #return template
                response = make_response(template)
                response.set_cookie('username',username)
                response.set_cookie('password',password)
                return response
            except sqlalchemy.exc.IntegrityError:
                return render_template('create_user.html', already_exists=True)

@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


@app.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)


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


@app.route('/create_message', methods=['GET', 'POST'])
def create_message():
    print_debug_info()

    username = request.cookies.get('username')
    password = request.cookies.get('password')

    good_credentials = are_credentials_good(username, password)
    if good_credentials:
        logged_in = True
    else:
        logged_in = False
    print('logged-in=', logged_in)

    if not logged_in:
        return redirect('/')

    result = connection.execute(text("SELECT id from users where username= :username and password = :password"), {"username": username, "password": password})
    row = result.fetchone()
    if row:
        sender_id = row[0]
    else:
        # Handle case where user is not found
        return redirect('/')

    message = request.form.get('message')

    if message is None:
        return render_template('create_message.html', logged_in=logged_in)
    elif not message:
        return render_template('create_message.html', invalid_message=True, logged_in=logged_in)
    else:
        try:
            created_at = str(datetime.now()).split('.')[0]
            result = connection.execute(text("INSERT INTO messages (sender_id,message,created_at) VALUES (:sender_id, :message, :created_at);"),  {"sender_id": sender_id, "message": message, "created_at": created_at})
            return render_template('create_message.html', message_sent=True, logged_in=logged_in)
        except IntegrityError:
            # Handle case where message insertion fails due to integrity error
            return render_template('create_message.html', already_exists=True, logged_in=logged_in)

@app.route('/next_page', methods=['GET','POST'])  
def next_page():
    print_debug_info()

    username=request.cookies.get('username')
    password=request.cookies.get('password')
    good_credentials=are_credentials_good(username, password)
    if good_credentials:
        logged_in=True
    else:
        logged_in=False
    print('logged_in=',logged_in)

    try:
        page_number=int(request.cookies.get('page_number'))
    except TypeError:
        page_number=1
    
    print('page_number=',page_number)
    page_number+=1


    response = make_response(redirect('/'))
    response.set_cookie('page_number',str(page_number))
    return response

@app.route('/previous_page', methods=['GET','POST'])  
def previous_page():
    print_debug_info()

    username=request.cookies.get('username')
    password=request.cookies.get('password')
    good_credentials=are_credentials_good(username, password)
    if good_credentials:
        logged_in=True
    else:
        logged_in=False
    print('logged-in=',logged_in)

    try:
        page_number=int(request.cookies.get('page_number'))
    except TypeError:
        page_number=1
    
    print('page_number=',page_number)
    page_number-=1

    response = make_response(redirect('/'))
    response.set_cookie('page_number',str(page_number))
    return response

messages = []
@app.route('/search', methods=['GET', 'POST'])
def search_message():
    global messages
    message = None
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)
    if good_credentials:
        logged_in = True
    else:
        logged_in = False

    if request.method == 'POST':
        message = request.form.get('message')
        if message:
            messages.append(message)
            print('message:', message)
            print('message list:', messages)
        page = 1  # Reset page to 1 when a new search is performed
    else:
        page = request.args.get('page', 1, type=int)  # Get page number from request args

    # Fetch the message from the list of messages
    if len(messages) > 0:
        message = messages[-1]


    if message is None:
        return render_template('search.html', logged_in=logged_in)
    if not message:
        return render_template('search.html', invalid_message=True, logged_in=logged_in)

    try:
        tsquery_string = " & ".join(f"'{word.strip()}'" for word in message.split())
        query = """
            SELECT id, ts_headline('english', message, to_tsquery(:message), 'StartSel="<mark><b>", StopSel="</b></mark>"') AS highlighted_message, created_at
            FROM messages
            WHERE to_tsvector(message) @@ to_tsquery(:message)
            ORDER BY created_at;
        """
        #result = connection.execute(text("SELECT id, message, created_at FROM messages WHERE to_tsvector(message) @@ to_tsquery(:message) order by created_at;"), {"message": tsquery_string})
        result = connection.execute(text(query), {"message": tsquery_string})
        search_results = [row for row in result.fetchall()]

        # Pagination logic
        per_page = 20
        total_pages = int(ceil(len(search_results) / per_page))
        start = (page - 1) * per_page
        end = start + per_page
        paginated_results = search_results[start:end]

        return render_template('search.html', search_results=paginated_results, logged_in=logged_in, page=page, total_pages=total_pages)

    except IntegrityError:
        # Handle case where message insertion fails due to integrity error
        return render_template('search.html', already_exists=True, logged_in=logged_in)
