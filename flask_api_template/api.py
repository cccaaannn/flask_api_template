from flask import Flask
from flask import request, jsonify, render_template, redirect, url_for
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
import sqlite3
import sys


#user register in form
class RegisterForm(Form):
    username = StringField("Username", validators=[validators.length(min = 3, max = 25), validators.DataRequired("username is needed")])
    password = PasswordField("Password",validators=[validators.length(min = 0, max = 6), validators.DataRequired("password is needed")])

#user login in form
class LoginForm(Form):
    username = StringField("Username")
    password = PasswordField("Password")


# user stuff
def is_username_exits(username, conn = None, database = "database.db"):
    query = "SELECT username FROM users;"

    if(not conn):
        conn = sqlite3.connect(database)

    cursor = conn.cursor()
    cursor.execute(query)
    usernames = cursor.fetchall()
    for i in usernames:
        if(i[0] == username):
            conn.close()
            return True
    conn.close()
    return False

def add_user_to_db(username, password, api_key, conn = None, database = "database.db"):
    query = "INSERT INTO users(username, password, api_key, api_usage) VALUES(?,?,?,0);"

    if(not conn):
        conn = sqlite3.connect(database)
    
    cursor = conn.cursor()   
    cursor.execute(query,(username, password, api_key))
    conn.commit()
    conn.close()

def remove_user_from_db(username, conn = None, database = "database.db"):
    # TODO
    pass

def validate_user(username, password, conn = None, database = "database.db"):
    query = "SELECT * FROM users WHERE username = ?;"

    if(not conn):
        conn = sqlite3.connect(database)
    
    cursor = conn.cursor() 
    cursor.execute(query, (username,))
    user = cursor.fetchall()
    #user is a list that has a tuple in it so user[0][0] is username
    if(len(user) > 0):
        if(user[0][0] == username):
            if(sha256_crypt.verify(password, user[0][1])):
                conn.close()
                return True
    conn.close()
    return False


# api key stuff
def get_api_key(username, conn = None, database = "database.db"):
    query = "SELECT api_key FROM users WHERE username = ?;"

    if(not conn):
        conn = sqlite3.connect(database)
    
    cursor = conn.cursor() 
    cursor.execute(query, (username,))
    key = cursor.fetchall()
    #user is a list that has a tuple in it so user[0][0] is username
    return key[0][0]

def get_all_api_keys(conn = None, database = "database.db"):
    query = "SELECT api_key FROM users;"

    if(not conn):
        conn = sqlite3.connect(database)
    
    cursor = conn.cursor() 
    cursor.execute(query,)
    keys = cursor.fetchall()
   
    return keys

def is_api_key_valid(key_to_try):
    keys = get_all_api_keys()
    for key in keys:
        if(key[0] == key_to_try):
            return True
    return False

def api_key_generator(username, rand_len=5):
    import random
    import string
    key = username + ''.join(random.choices(string.ascii_uppercase + string.digits, k=rand_len))
    return key


# api usage count
# digerlerini de boyle yap
def increase_api_usage(api_key, conn = None, database = "database.db"):
    query = "UPDATE users SET api_usage = api_usage + 1 WHERE api_key = ?;"

    if(conn):
        cursor = conn.cursor()   
        cursor.execute(query,(api_key,))
        conn.commit()
    else:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()   
        cursor.execute(query,(api_key,))
        conn.commit()
        conn.close()
    
def get_api_usage(api_key, conn = None, database = "database.db"):
    query = "SELECT api_usage FROM users WHERE api_key = ?;"

    if(conn):
        cursor = conn.cursor()   
        cursor.execute(query,(api_key,))
        usage = cursor.fetchall()
    else:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()   
        cursor.execute(query,(api_key,))
        usage = cursor.fetchall()
        conn.close()
    return usage[0][0]


# # api stuff
# def run_api(key, info = ""):
#     increase_api_usage(str(key))
#     usage = get_api_usage(str(key))

#     # ------test
#     from test_usage import get_doom_days
#     doom = get_doom_days()
#     # ------- 

#     api_out = {info:1, "doom":doom , "usage":usage, "status":0}
#     return api_out


def run_api(func): 
    def function(key, *args, **kwargs): 

        if(is_api_key_valid(key)):
            # increase usage
            increase_api_usage(str(key))
            usage = get_api_usage(str(key))
            
            returned_value = func(key, *args, **kwargs)

            # add usage and status to returned value
            returned_value.update({"usage":usage})
            returned_value.update({"status":1})
            returned_value.update({"key":1})
            
        else:
            returned_value = {"status":1, "key":0}

        return returned_value           
    return function 






@run_api
def test_api(key, info = ""):
    from test_usage import get_doom_days
    doom = get_doom_days()

    api_out = {info:1, "doom":doom}
    return api_out



# create app
app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return render_template("index.html")


@app.route("/register",methods = ["GET", "POST"])
def register():
    
    #create the form
    form = RegisterForm(request.form)

    if(request.method == "POST" and form.validate()):

        #get form data from form
        username = form.username.data
        password = sha256_crypt.encrypt(form.password.data)

        #check username from db
        if(is_username_exits(username)):
            form.username.errors.append("username exists")
            return render_template("register.html", form = form)
        else:
            api_key = api_key_generator(username)
            add_user_to_db(username,password,api_key)

        return redirect(url_for("login"))
    else:
        return render_template("register.html", form = form)


@app.route("/login",methods = ["GET", "POST"])
def login():
    #create the form
    form = LoginForm(request.form)

    if(request.method == "POST"):
        #get form data from form
        username = form.username.data
        password = form.password.data

        if(validate_user(username, password)):

            return "your key is: {0}".format(get_api_key(username))
        else:
            return redirect(url_for("login"))

    else:
        return render_template("login.html", form = form)


@app.route('/api', methods=['GET'])
def api():
    query_parameters = request.args
    key = query_parameters.get('key')
    # info = query_parameters.get('info')
    
    api_out = test_api(key)

    return api_out


app.run()