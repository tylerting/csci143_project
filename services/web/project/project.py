import sqlite3
import argparse
import datetime
import markdown_compiler2
import bleach


'''
This is a "hello world" flask webpage.
During the last 2 weeks of class,
we will be modifying this file to demonstrate all of flask's capabilities.
This file will also serve as "starter code" for your Project 5 Twitter webpage.

NOTE:
the module flask is not built-in to python,
so you must run pip install in order to get it.
After doing do, this file should "just work".
'''

import argparse
parser = argparse.ArgumentParser(description='Create a database for the twitter project')
parser.add_argument('--db_file', default='twitter_clone.db')
args = parser.parse_args()

from flask import Flask, render_template, request, make_response, redirect
app = Flask(__name__)

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
    
    con = sqlite3.connect(args.db_file)
    sql = """
    SELECT id from users WHERE username=? and password=?;
    """
    cur = con.cursor()
    cur.execute(sql, [username, password])
    for row in cur.fetchall():
        if row[0]:
            return True
        else:
            return False

def retrieve_messages(a):
    # connect to the database
    con = sqlite3.connect(args.db_file)

    # construct messages,
    # which is a list of dictionaries,
    # where each dictionary contains the information about a message
    messages = []
    sql = """
    SELECT sender_id,message,created_at,id
    FROM messages
    ORDER BY created_at DESC LIMIT 50 OFFSET ?;
    """
    cur_messages = con.cursor()
    cur_messages.execute(sql, [str(50*(a-1))])
    for row_messages in cur_messages.fetchall():

        # convert sender_id into a username
        sql="""
        SELECT id,username,password,age
        FROM users
        WHERE id=?;
        """
        cur_users = con.cursor()
        cur_users.execute(sql, [str(row_messages[0])])
        for row_users in cur_users.fetchall():
            pass

            message=row_messages[1]
            cleaned_message=bleach.clean(message)
            html_message=markdown_compiler2.compile_lines(cleaned_message)
            linked_message=bleach.linkify(html_message)

            image_url='https://robohash.org/'+row_users[1]

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

# anything that starts with @ is called a 'decorator' in python
# in general. decorators modify the functions that follow them
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

    try:
        page_number=int(request.cookies.get('page_number'))
    except TypeError:
        page_number=1

    messages=retrieve_messages(page_number)

    # render the jinja2 template and pass the result to firefox
    return render_template('root.html', messages=messages, logged_in=logged_in, username=username, page_number=page_number)

    # render_template does preprocessing of input html file
    # technically, the input to the render_template function is in a language called Jinja2
    # the output of render_template is html

# scheme://hostname/path
# the @app.route defines the path
# the hostname and scheme are given to you in the output of the triangle button

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
    response.set_cookie('page_number',str(page_number))
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
    response.delete_cookie('page_number')
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
                con = sqlite3.connect(args.db_file)
                sql = """
                INSERT INTO users (username, password, age) VALUES (?, ?, ?);
                """
                cur = con.cursor()
                cur.execute(sql, [new_username, new_password, new_age])
                con.commit()
                response = make_response(redirect('/'))
                response.set_cookie('username',new_username)
                response.set_cookie('password',new_password)
                return response
            except sqlite3.IntegrityError:
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

    con = sqlite3.connect(args.db_file)
    sql = """
    SELECT id from users WHERE username=? and password=?;
    """
    cur = con.cursor()
    cur.execute(sql, [username, password])
    for row in cur.fetchall():
        sender_id=row[0]
    
    message=request.form.get('message')

    if message is None:
        return render_template('create_message.html', logged_in=logged_in)
    elif not message:
        return render_template('create_message.html', invalid_message=True, logged_in=logged_in)
    else:
        try:
            created_at=str(datetime.datetime.now()).split('.')[0]
            con = sqlite3.connect(args.db_file)
            sql = """
            INSERT INTO messages (sender_id,message,created_at) VALUES (?, ?, ?);
            """
            cur = con.cursor()
            cur.execute(sql, [sender_id, message, created_at])
            con.commit()
            return render_template('create_message.html', message_sent=True, logged_in=logged_in)
        except sqlite3.IntegrityError:
            return render_template('create_message.html', already_exists=True, logged_in=logged_in)

@app.route('/delete_message', methods=['GET','POST'])
def delete_message():
    message_id=request.form.get('message_id')
    con = sqlite3.connect(args.db_file)
    sql = """
    DELETE FROM messages WHERE id=?;
    """
    cur = con.cursor()
    cur.execute(sql,[str(message_id)])
    con.commit()
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
            con = sqlite3.connect(args.db_file)
            sql = """
            UPDATE messages SET message=?, created_at=? WHERE id=?;
            """
            print('message=',updated_message)
            print('message_id=',message_id)
            cur = con.cursor()
            cur.execute(sql,[updated_message,created_at,str(message_id)])
            con.commit()
            return render_template('edit_message.html', message_sent=True, logged_in=logged_in, message_id=message_id)
        except sqlite3.IntegrityError:
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

    con = sqlite3.connect(args.db_file)
    sql = """
    SELECT id from users WHERE username=? and password=?;
    """
    cur = con.cursor()
    cur.execute(sql,[username,password])
    for row in cur.fetchall():
        sender_id=row[0]
    
    sql = """
    DELETE from messages WHERE sender_id=?;
    """
    cur = con.cursor()
    cur.execute(sql,[sender_id])
    con.commit()

    sql = """
    DELETE from users WHERE username=? and password=?;
    """
    cur = con.cursor()
    cur.execute(sql,[username,password])
    con.commit()
    

    response = make_response(render_template('delete_account.html', account_deleted=True))
    response.delete_cookie('username')
    response.delete_cookie('password')
    response.delete_cookie('page_number')
    return response

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

app.run()
