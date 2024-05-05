import os

from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    make_response,
    redirect,
    render_template
)
from werkzeug.utils import secure_filename
import sqlalchemy
import bleach
import datetime

app = Flask(__name__)

engine = sqlalchemy.create_engine("postgresql://postgres:pass@postgres:5432", connect_args={
    'application_name': '__init__.py',
    })
connection = engine.connect()

def print_debug_info():
    # requests (PLURAL) library for downloading
    # now we need request (SINGULAR)

    # GET method
    print("request.args.get('username')=",request.args.get('username'))
    print("request.args.get('password')=",request.args.get('password'))

    # POST method
    print("request.form.get('username')=",request.form.get('username'))
    print("request.form.get('password')=",request.form.get('password'))

    # cookies
    print("request.cookies.get('username')=",request.cookies.get('username'))
    print("request.cookies.get('password')=",request.cookies.get('password'))



def are_credentials_good(username, password):

    sql = sqlalchemy.sql.text('''
        SELECT id FROM users
        WHERE username = :username
        AND password = :password
        ;
        ''')

    res = connection.execute(sql, {
        'username': username,
        'password': password
        })

    if res.fetchone() is None:
        return False
    else:
        return True

def retrieve_messages(a):

    messages = []
    sql = sqlalchemy.sql.text("""
    SELECT sender_id,message,created_at,id
    FROM messages
    ORDER BY created_at DESC LIMIT 20 OFFSET :offset * 20;
    """)

    res = connection.execute(sql, {
       'offset': a - 1
        })

    for row_messages in res.fetchall():
        # convert sender_id into a username
        sql = sqlalchemy.sql.text("""
        SELECT id,username,password,age
        FROM users
        WHERE id=:id;
        """)
        user_res = connection.execute(sql, {'id': row_messages[0]})
        row_users = user_res.fetchone()

        message = row_messages[1]
        cleaned_message = bleach.clean(message)
        linked_message = bleach.linkify(cleaned_message)

        image_url = 'https://robohash.org/' + row_users[1]

        # build the message dictionary
        messages.append({
            'id': row_messages[3],
            'message': linked_message,
            'username': row_users[1],
            'age': row_users[3],
            'created_at': row_messages[2],
            'image_url': image_url
        })

    return messages


def query_messages(query, a):

    messages = []
    sql = sqlalchemy.sql.text("""
    SELECT 
    sender_id,
    ts_headline(message, to_tsquery(:query),
    'StartSel="<span class=query><b>",
    StopSel="</b></span>"') AS highlighted_message,
    created_at,
    id
    FROM messages
    WHERE to_tsvector(message) @@ to_tsquery(:query)
    ORDER BY 
    to_tsvector(message) <=> to_tsquery(:query),
    created_at DESC 
    LIMIT 20 OFFSET :offset * 20;
    """)

    res = connection.execute(sql, {
       'offset': a - 1,
       'query': ' & '.join(query.split())
        })

    for row_messages in res.fetchall():
        # convert sender_id into a username
        sql = sqlalchemy.sql.text("""
        SELECT id,username,password,age
        FROM users
        WHERE id=:id;
        """)
        user_res = connection.execute(sql, {'id': row_messages[0]})
        row_users = user_res.fetchone()

        message = row_messages[1]
        cleaned_message = bleach.clean(message, tags=['b','span'], attributes={'span': ['class']})
        linked_message = bleach.linkify(cleaned_message)

        image_url = 'https://robohash.org/' + row_users[1]

        # build the message dictionary
        messages.append({
            'id': row_messages[3],
            'message': linked_message,
            'username': row_users[1],
            'age': row_users[3],
            'created_at': row_messages[2],
            'image_url': image_url
        })

    return messages


@app.route('/')
def root():
    
    print_debug_info()

    username=request.cookies.get('username')
    password=request.cookies.get('password')
    good_credentials=are_credentials_good(username, password)
    if good_credentials:
        logged_in=True
    else:
        logged_in=False
    print('logged-in=',logged_in)

    page_number = int(request.args.get('page', 1))
    
    messages=retrieve_messages(page_number)

    # render the jinja2 template and pass the result to firefox
    
    return render_template('root.html', messages=messages, logged_in=logged_in, username=username, page_number=page_number)

    # render_template does preprocessing of input html file
    # technically, the input to the render_template function is in a language called Jinja2
    # the output of render_template is html

@app.route('/reset')
def reset():
    print_debug_info()

    username=request.cookies.get('username')
    password=request.cookies.get('password')
    good_credentials=are_credentials_good(username, password)
    if good_credentials:
        logged_in=True
    else:
        logged_in=False
    print('logged-in=',logged_in)

    page_number=1

    response = make_response(redirect('/'))
    return response

@app.route('/login', methods=['GET','POST'])
def login():
    print_debug_info()

    username=request.cookies.get('username')
    password=request.cookies.get('password')

    good_credentials=are_credentials_good(username, password)
    if good_credentials:
        logged_in=True
    else:
        logged_in=False
    print('logged-in=',logged_in)

    if logged_in:
        return redirect('/')

    username=request.form.get('username')
    password=request.form.get('password')

    good_credentials=are_credentials_good(username, password)
    print('good_credentials=',good_credentials)

    # first time we visited, no form submission
    if username is None:
        return render_template('login.html', bad_credentials=False)

    # they submitted a form--we're on the POST method
    else:
        if not good_credentials:
            return render_template('login.html', bad_credentials=True)
        else:
            #create a cookie that contains the username/password info
            # set cookie
            response = make_response(redirect('/'))
            response.set_cookie('username',username)
            response.set_cookie('password',password)
            return response

@app.route('/logout')
def logout():
    print_debug_info()

    response = make_response(render_template('logout.html'))
    response.delete_cookie('username')
    response.delete_cookie('password')
    return response



@app.route('/create_user', methods=['GET','POST'])
def create_user():
    print_debug_info()

    username=request.cookies.get('username')
    password=request.cookies.get('password')

    good_credentials=are_credentials_good(username, password)
    if good_credentials:
        logged_in=True
    else:
        logged_in=False
    print('logged-in=',logged_in)

    if logged_in:
        return redirect('/')

    new_username=request.form.get('new_username')
    new_password=request.form.get('new_password')
    new_password2=request.form.get('new_password2')
    new_age=request.form.get('new_age')

    if new_username is None:
        return render_template('create_user.html')
    elif not new_username or not new_password:
        return render_template('create_user.html', one_blank=True)
    elif not new_age.isnumeric():
        return render_template('create_user.html', invalid_age=True)
    else:
        if new_password!=new_password2:
            return render_template('create_user.html', not_matching=True)
        else:
            try:

                sql=sqlalchemy.sql.text('''
                    INSERT INTO users (username, password, age)
                    VALUES (:username, :password, :age)
                    ''')

                res = connection.execute(sql, {
                    'username': new_username,
                    'password': new_password,
                    'age': new_age
                    })

                response = make_response(redirect('/'))
                response.set_cookie('username',new_username)
                response.set_cookie('password',new_password)
                return response
            except sqlalchemy.exc.IntegrityError:
                return render_template('create_user.html', already_exists=True)



@app.route('/create_message', methods=['GET', 'POST'])
def create_message():
    print_debug_info()

    username=request.cookies.get('username')
    password=request.cookies.get('password')

    good_credentials=are_credentials_good(username, password)
    if good_credentials:
        logged_in=True
    else:
        logged_in=False
    print('logged-in=',logged_in)

    if not logged_in:
        return redirect('/')

    sql=sqlalchemy.sql.text('''
        SELECT id FROM users
        WHERE username = :username AND password = :password
        ''')

    res = connection.execute(sql, {
        'username': username,
        'password': password
        })


    for row in res.fetchall():
        sender_id=row[0]

    message=request.form.get('message')

    if message is None:
        return render_template('create_message.html', logged_in=logged_in)
    elif not message:
        return render_template('create_message.html', invalid_message=True, logged_in=logged_in)
    else:
        created_at=str(datetime.datetime.now()).split('.')[0]
        sql = sqlalchemy.sql.text("""
        INSERT INTO messages (sender_id,message,created_at) VALUES (:sender_id, :message, :created_at);
        """)
        res = connection.execute(sql, {
            'sender_id': sender_id,
            'message': message,
            'created_at': created_at
            })
        return render_template('create_message.html', message_sent=True, logged_in=logged_in)

@app.route('/delete_message', methods=['GET','POST'])
def delete_message():
    message_id=request.form.get('message_id')
    sql = sqlalchemy.sql.text("""
    DELETE FROM messages WHERE id= :id;
    """)
    res = connection.execute(sql, {
        'id': message_id
        })
    return redirect('/')



@app.route('/edit_message', methods=['POST','GET'])
def edit_message():
    print_debug_info()

    username=request.cookies.get('username')
    password=request.cookies.get('password')

    good_credentials=are_credentials_good(username, password)
    if good_credentials:
        logged_in=True
    else:
        logged_in=False
    print('logged-in=',logged_in)

    if not logged_in:
        return redirect('/')

    message_id=request.form.get('message_id')
    print('message_id=',message_id)
    original_message=request.form.get('original_message')[3:-4]
    print('original_message=',original_message)
    updated_message=request.form.get('updated_message')

    if not message_id:
        return redirect('/')

    if updated_message is None:
        return render_template('edit_message.html', logged_in=logged_in, message_id=message_id, original_message=original_message)
    elif not updated_message:
        return render_template('edit_message.html', invalid_message=True, logged_in=logged_in, message_id=message_id, original_message=original_message)
    else:
        try:
            created_at=str(datetime.datetime.now()).split('.')[0]
            sql = sqlalchemy.sql.text("""
            UPDATE messages SET message= :updated_message, created_at= :created_at WHERE id= :message_id;
            """)
            print('message=',updated_message)
            print('message_id=',message_id)
            res = connection.execute(sql, {
                'updated_message': updated_message,
                'created_at': created_at,
                'message_id': str(message_id)
                })
            return render_template('edit_message.html', message_sent=True, logged_in=logged_in, message_id=message_id)
        except sqlalchemy.exc.IntegrityError: 
            return render_template('edit_message.html', already_exists=True, logged_in=logged_in, message_id=message_id, original_message=original_message)


@app.route('/delete_account', methods=['GET','POST'])
def delete_account0():
    print_debug_info()

    username=request.cookies.get('username')
    password=request.cookies.get('password')

    good_credentials=are_credentials_good(username, password)
    if good_credentials:
        logged_in=True
    else:
        logged_in=False
    print('logged-in=',logged_in)

    if not logged_in:
        return redirect('/')

    return render_template('delete_account.html', logged_in=logged_in, account_deleted=False)

@app.route('/account_deleted', methods=['GET','POST'])
def account_deleted():
    print_debug_info()

    username=request.cookies.get('username')
    password=request.cookies.get('password')

    good_credentials=are_credentials_good(username, password)
    if good_credentials:
        logged_in=True
    else:
        logged_in=False
    print('logged-in=',logged_in)

    if not logged_in:
        return redirect('/')

    sql = sqlalchemy.sql.text("""
    SELECT id from users WHERE username= :username and password= :password;
    """)
    res = connection.execute(sql, {
        'username': username,
        'password': password
        })
    for row in res.fetchall():
        sender_id=row[0]

    sql = sqlalchemy.sql.text("""
    DELETE from messages WHERE sender_id= :id;
    """)
    res = connection.execute(sql, {
        'id': sender_id
        })

    sql = sqlalchemy.sql.text("""
    DELETE from users WHERE username= :u and password= :p;
    """)
    res = connection.execute(sql, {
        'u': username,
        'p': password
        })


    response = make_response(render_template('delete_account.html', account_deleted=True))
    response.delete_cookie('username')
    response.delete_cookie('password')
    return response

@app.route('/search', methods=['GET','POST'])
def search():

    print_debug_info()

    username=request.cookies.get('username')
    password=request.cookies.get('password')
    good_credentials=are_credentials_good(username, password)
    if good_credentials:
        logged_in=True
    else:
        logged_in=False
    print('logged-in=',logged_in)

    page_number = int(request.args.get('page', 1))
    
    if request.form.get('query'):
        query=request.form.get('query')
    elif request.cookies.get('query'):
        query=request.cookies.get('query')
    else:
        query = None

    if query:
        messages=query_messages(query, page_number)
    else:
        messages=retrieve_messages(page_number)

    response = make_response(render_template('search.html', messages=messages, logged_in=logged_in, username=username, page_number=page_number))

    if query:
        response.set_cookie('query',query)

    return response

    # render_template does preprocessing of input html file
    # technically, the input to the render_template function is in a language called Jinja2
    # the output of render_template is html
