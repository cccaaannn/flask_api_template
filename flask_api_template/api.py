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
    query = "INSERT INTO users(username, password, api_key) VALUES(?,?,?);"

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

def api_key_generator():
    # TODO
    return 100000


# api stuff
def run_api(info):
    # TODO
    return {info:1,"hi":2}



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
            api_key = api_key_generator()
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
    key = int(query_parameters.get('key'))
    
    if(is_api_key_valid(key)):
        info = query_parameters.get('info')
        print(info, file=sys.stdout)

        api_out = run_api(info)
        return api_out
    else:
        return {"status":0}



app.run()