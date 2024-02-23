from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import jwt
from functools import wraps
import datetime 
import mysql.connector
from mysql.connector import Error
import base64
import secrets
import hashlib

# Initialize Flask app
app = Flask(__name__)

# Configure MySQL database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'hello'
app.config['MYSQL_PASSWORD'] = '123'
app.config['MYSQL_DB'] = 'project'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Initialize MySQL and Bcrypt instances
mysql = MySQL(app)
bcrypt = Bcrypt(app)

# Generate a secret key for JWT
secret_key = secrets.token_hex(32)
app.secret_key = secret_key

# Define a decorator to require authentication
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('token')

        if not token:
            return redirect(url_for('login'))
        try:
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
            current_user = data['username']
        except jwt.ExpiredSignatureError:
            return redirect(url_for('login'))
        except jwt.InvalidTokenError:
            return redirect(url_for('login'))

        return f(current_user, *args, **kwargs)

    return decorated_function


@app.route("/")
def form():
    token = request.cookies.get('token')
    if token:
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            username = data['username']
            # If token is valid, redirect to website
            return redirect('/website')
        except jwt.ExpiredSignatureError:
            # Token has expired, render the registration page
            pass
        except jwt.InvalidTokenError:
            # Invalid token, render the registration page
            pass
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
        email = request.form['register-useremail']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM UserDetails WHERE UserName = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user:
            return render_template('register.html', error='User Email already exists')

        # Hash the password before storing it
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
                msg = 'Incorrect username / password !'
                return render_template('adminlogin.html', msg=msg)
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
            # Generate JWT token
            token = jwt.encode({'username': username}, secret_key, algorithm='HS256')

            # Set JWT token in cookies
            response = make_response(redirect(url_for('website')))
            response.set_cookie('token', token, httponly=True)  # Set HttpOnly flag for security
            return response

        msg = 'Incorrect username / password !'
        return render_template('login.html', msg = msg)
    
    # If the user is already logged in, redirect to the website
    if 'username' in session:
        return redirect(url_for('website'))

    return render_template('login.html')

@app.route('/website')
@token_required
def website(current_user):
    # Retrieve user_id based on username
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT UserId FROM UserDetails WHERE Username = %s", (current_user,))
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

@app.route('/videomaker')
@token_required
def videomaker(current_user):
    # Retrieve user_id based on username
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT UserId FROM UserDetails WHERE Username = %s", (current_user,))
    user = cursor.fetchone()

    if not user:
        return render_template('videomaker.html', message="User not found.")

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
        return render_template('videomaker.html', message="No images found for the user.")

    return render_template('videomaker.html', images=encoded_images)


@app.route('/upload', methods=['GET', 'POST'])
@token_required
def upload_page(current_user):
    if request.method == 'POST':
        # Check if the request contains files
        if 'files' not in request.files:
            return redirect(request.url)

        # Get the list of files uploaded
        files = request.files.getlist('files')

        # Retrieve user_id based on username
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT UserId FROM UserDetails WHERE UserName = %s", (current_user,))
        user = cursor.fetchone()

        if not user:
            return 'User not found.'

        user_id = user['UserId']

        for file in files:
            if file.filename == '':
                continue  # Skip empty file inputs

            # Calculate hash value of the image data incorporating user ID
            image_data = file.read()
            combined_data = f"{user_id}:{image_data}".encode('utf-8')
            image_hash = hashlib.sha256(combined_data).hexdigest()

            try:
                # Check if the image hash already exists in ImageMetadata column of UserImages table
                cursor.execute("SELECT * FROM UserImages WHERE ImageMetadata = %s", (image_hash,))
                existing_image = cursor.fetchone()

                if existing_image:
                    flash('You have already uploaded one or more images.', 'error')
                    continue

                # Insert image data and metadata into UserImages table
                cursor.execute("INSERT INTO UserImages (UserId, ImageMetadata, ImageData) VALUES (%s, %s, %s)", (user_id, image_hash, image_data))
                mysql.connection.commit()

            except Error as e:
                print(f"The error '{e}' occurred")
                flash('An error occurred while uploading one or more images.', 'error')

        return redirect('/upload')

    return render_template('upload.html')

@app.route('/delete_images', methods=['GET', 'POST'])
@token_required
def delete_images(current_user):
    if request.method == 'POST':
        # Get the list of image IDs to be deleted
        images_to_delete = request.form.getlist('delete')

        if images_to_delete:
            try:
                # Delete the selected images from the database
                cursor = mysql.connection.cursor()
                for image_id in images_to_delete:
                    cursor.execute("DELETE FROM UserImages WHERE ImageId = %s AND UserId = (SELECT UserId FROM UserDetails WHERE UserName = %s)", (image_id, current_user))
                    mysql.connection.commit()

                flash('Selected images deleted successfully.', 'success')
            except Error as e:
                print(f"The error '{e}' occurred")
                flash('An error occurred while deleting selected images.', 'error')

            return redirect('/delete_images')

    # Fetch images associated with the current user from the database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM UserImages WHERE UserId = (SELECT UserId FROM UserDetails WHERE UserName = %s)", (current_user,))
    images = cursor.fetchall()
    cursor.close()
    for image in images:
        image_data = base64.b64encode(image['ImageData']).decode('utf-8')
        image['ImageData'] = image_data

    return render_template('delete_images.html', images=images)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    # Clear the token cookie
    response = make_response(render_template('login.html'))
    response.set_cookie('token', '', expires=0, httponly=True)
    return response

if __name__=='__main__':
    app.run(debug=True)
