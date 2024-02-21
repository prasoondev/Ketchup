from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import jwt
from functools import wraps
import datetime 
import mysql.connector
from mysql.connector import Error
import base64

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'hello'
app.config['MYSQL_PASSWORD'] = '123'
app.config['MYSQL_DB'] = 'project'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.secret_key = 'secret_key_for_flash_messages'
app.config['SECRET_KEY'] = '$%#GJdjsklwJLqwn321QDdjaA'
mysql = MySQL(app)
bcrypt = Bcrypt(app)

# Define a decorator to require authentication
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def form():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM UserDetails WHERE UserName = %s", ('admin',))
    admin_user = cur.fetchone()
    if not admin_user:
        hashed_password = bcrypt.generate_password_hash('123456').decode('utf-8')
        cur.execute("INSERT INTO UserDetails (UserName, UserPassword) VALUES (%s, %s)", ('admin', hashed_password))
    mysql.connection.commit()
    cur.close()
    return render_template("register.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['register-username']
        password = request.form['register-password']
        email=request.form['register-useremail']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM UserDetails WHERE UserEmail = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user:
            return render_template('register.html', error='User Email already exists')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO UserDetails (UserName, UserEmail, UserPassword) VALUES (%s, %s, %s)", (username, email, hashed_password))
        mysql.connection.commit()
        cur.close()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html') 

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        data = request.form
        username = data['login-username']
        password = data['login-password']
        if username == 'admin':
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM UserDetails WHERE UserName = %s", (username,))
            admin_user = cur.fetchone()
            cur.close()
            if admin_user and bcrypt.check_password_hash(admin_user['UserPassword'], password):
                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM UserDetails")
                user_details = cur.fetchall()
                cur.close()

                # Set cookie for the username
                response = make_response(render_template('admin.html', user_details=user_details))
                response.set_cookie('username', username)

                return response
            else:
                return render_template('adminlogin.html', error='Invalid username or password')
    return render_template('adminlogin.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['login-username']
        password = request.form['login-password']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM UserDetails WHERE UserName = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.check_password_hash(user['UserPassword'], password):
            session['username'] = username

            # Set cookie for the username
            response = make_response(redirect(url_for('website')))
            response.set_cookie('username', username)

            return response

        return "Invalid Username or Password. Please Try Again."
    
    # Check if the user has a valid session token
    if 'username' in session and 'token' in session:
        # Validate the token
        try:
            jwt.decode(session['token'], app.config['SECRET_KEY'], algorithms=['HS256'])
            # Token is valid, redirect to the dashboard
            return redirect(url_for('website'))
        except jwt.ExpiredSignatureError:
            # Token has expired, require the user to log in again
            session.pop('username', None)
            session.pop('token', None)
    return render_template('login.html')

@app.route('/website')
@login_required
def website():
    username = session.get('username')
    if not username:
        return redirect('/login')  # Redirect to login if username is not in session

    # Retrieve user_id based on username
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT UserId FROM UserDetails WHERE Username = %s", (username,))
    user = cursor.fetchone()
    if not user:
        return render_template('website.html', message="User not found.")

    user_id = user['UserId']

    # Retrieve images uploaded by the user
    cursor.execute("SELECT * FROM UserImages WHERE UserId = %s", (user_id,))
    images = cursor.fetchall()

    encoded_images = []
    for image in images:
        encoded_image = base64.b64encode(image['ImageData']).decode('utf-8')
        encoded_images.append(encoded_image)

    if not encoded_images:
        # If no images are found, render the website with a message
        return render_template('website.html', message="No images found for the user.")

    return render_template('website.html', images=encoded_images)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_page():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)

        username = session.get('username')
        if not username:
            return redirect('/login')  # Redirect to login if username is not in session

        # Retrieve user_id based on username
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT UserId FROM UserDetails WHERE Username = %s", (username,))
        user = cursor.fetchone()
        if not user:
            return 'User not found.'

        user_id = user['UserId']

        try:
            cursor.execute("INSERT INTO UserImages (UserId, ImageData) VALUES (%s, %s)", (user_id, file.read(),))
            mysql.connection.commit()
            return redirect('/website')
        except Error as e:
            print(f"The error '{e}' occurred")
            return 'An error occurred while uploading the image'


    return render_template('upload.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)

    # Clear the username cookie
    response = make_response(render_template('login.html'))
    response.set_cookie('username', '', expires=0)

    return response

if __name__=='__main__':
    app.run(debug=True)


