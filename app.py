from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response, json
from flask_bcrypt import Bcrypt
import jwt
from functools import wraps
import datetime 
import base64
import secrets
import hashlib
import os
import psycopg2
import random
import numpy as np
from moviepy.editor import *
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from pydub import AudioSegment
from PIL import Image
from moviepy.editor import concatenate_audioclips, AudioFileClip

app = Flask(__name__)
bcrypt = Bcrypt(app)

def add_header(response):
    """
    Add headers to disable caching.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
    return r
@app.after_request
def after_request(response):
    """
    Apply headers to all responses.
    """
    return add_header(response)

secret_key = secrets.token_hex(32)
app.secret_key = secret_key

def create_table():
    conn = connect_to_database()
    with conn.cursor() as cur:
# Define the SQL statement to create the table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS UserDetails (
            UserId SERIAL PRIMARY KEY,
            UserName VARCHAR(255) NOT NULL UNIQUE,
            UserEmail VARCHAR(255) UNIQUE,
            UserPassword VARCHAR(255) NOT NULL
        );
        """
        cur.execute(create_table_query)
        conn.commit()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS UserImages (
            ImageId VARCHAR(255),
            UserId INT, 
            ImageData BYTEA,
            ImageMetadata VARCHAR(255)
        );
        """
        cur.execute(create_table_query)
        conn.commit()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS Audio (
            AudioID VARCHAR(255),
            AudioBlob BYTEA,
            AudioMetadata TEXT
        );
        """
        # create_table_query = """
        # DROP TABLE IF EXISTS UserDetails;
        # """
        # cur.execute(create_table_query)
        # conn.commit()
        # create_table_query = """
        # DROP TABLE IF EXISTS UserImages;
        # """
        # cur.execute(create_table_query)
        # conn.commit()
        # create_table_query = """
        # DROP TABLE IF EXISTS Audio;
        # """
        cur.execute(create_table_query)
        conn.commit()
        conn.close()
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
            # Handle invalid token error

            return redirect(url_for('login'))  # Redirect or handle the error accordingly

        return f(current_user, *args, **kwargs)

    return decorated_function

def connect_to_database():
    conn_params = {
        'host': 'course-project-group-55-4059.7s5.aws-ap-south-1.cockroachlabs.cloud',
        'port': 26257,
        'user': 'Ketchup',
        'password': 'F1wKiMCuYXXiIiUsCzbsOg',
        'database': 'project',
        'sslmode': 'verify-full',
        'sslrootcert': 'root.crt' # Replace with the correct path
    }

    conn_str = "host={host} port={port} user={user} password={password} dbname={database} sslmode={sslmode} sslrootcert={sslrootcert}".format(**conn_params)

    # Connect to the database
    try:
        conn = psycopg2.connect(conn_str)
        return conn
    except psycopg2.OperationalError as e:
        return None

@app.route("/")
def form():
    # create_table()
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
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute("SELECT * FROM UserDetails WHERE UserName = %s", ('admin',))
    admin_user = cur.fetchone()
    if not admin_user:
        hashed_password = bcrypt.generate_password_hash('123456').decode('utf-8')
        cur.execute("INSERT INTO UserDetails (UserName, UserPassword) VALUES (%s, %s)", ('admin', hashed_password))
    conn.commit()
    cur.close()
    conn.close()
    return render_template("landing_page.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['register-username']
        password = request.form['register-password']
        email = request.form['register-useremail']
        
        conn = connect_to_database()
        cur = conn.cursor()
        cur.execute("SELECT * FROM UserDetails WHERE UserEmail = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:
            return render_template('register.html', msg='Invalid! Email already exists')
        # Hash the password before storing it
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        conn = connect_to_database()
        cur = conn.cursor()
        cur.execute("INSERT INTO UserDetails (UserName, UserEmail, UserPassword) VALUES (%s, %s, %s)", (username, email, hashed_password))
        conn.commit()
        cur.close()
        conn.close()
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
            conn = connect_to_database()
            cur = conn.cursor()
            cur.execute("SELECT * FROM UserDetails WHERE UserName = %s", (username,))
            admin_user = cur.fetchone()
            cur.close()
            if admin_user and bcrypt.check_password_hash(admin_user[3], password):
                conn = connect_to_database()
                cur = conn.cursor()
                cur.execute("SELECT * FROM UserDetails")
                user_details = cur.fetchall()
                # Set cookie for the username
                response = make_response(render_template('admin.html', user_details=user_details))
                response.set_cookie('username', username)

                return response
            else:
                msg2 = 'Incorrect username / password !'
                return render_template('adminlogin.html', msg=msg2)
        else:
            msg2 = 'Incorrect username / password !'
            return render_template('adminlogin.html', msg=msg2)
    return render_template('adminlogin.html')
    cur.close()
    conn.close()

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['login-username']
        password = request.form['login-password']
        
        conn = connect_to_database()
        cur = conn.cursor()
        cur.execute("SELECT * FROM UserDetails WHERE UserName = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and bcrypt.check_password_hash(user[3], password):
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
    conn = connect_to_database()
    cur = conn.cursor()
    cur.execute("SELECT UserId FROM UserDetails WHERE Username = %s", (current_user,))
    user = cur.fetchone()

    if not user:
        return render_template('website.html', message="User not found.")

    user_id = user[0]

    # Retrieve images uploaded by the user
    cur.execute("SELECT * FROM UserImages WHERE UserId = %s", (user_id,))
    images = cur.fetchall()

    encoded_images = []
    for image in images:
        encoded_image = base64.b64encode(image[2]).decode('utf-8')
        encoded_images.append(encoded_image)

    if not encoded_images:
        # If no images are found, render the website with a message
        return render_template('website.html', message="No images found for the user.")
    cur.close()
    conn.close()
    return render_template('website.html', images=encoded_images)

@app.route('/videomaker')
@token_required
def videomaker(current_user):
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Audio")
    audio_files = cursor.fetchall()
    cursor.close()
    conn.close()

    # Encode audio data to base64
    encoded_audio_files = []
    for audio in audio_files:
        audio_id, audio_blob, audio_metadata = audio
        print(audio_id)
        encoded_audio = base64.b64encode(audio_blob).decode('utf-8')
        encoded_audio_files.append((audio_id, encoded_audio, audio_metadata))
    
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT UserId FROM UserDetails WHERE Username = %s", (current_user,))
    user = cursor.fetchone()

    if not user:
        return render_template('videomaker.html', message="User not found.")

    user_id = user[0]

    # Retrieve images uploaded by the user
    cursor.execute("SELECT * FROM UserImages WHERE UserId = %s", (user_id,))
    images = cursor.fetchall()

    encoded_images = []
    for image in images:
        encoded_image = base64.b64encode(image[2]).decode('utf-8')
        encoded_images.append(encoded_image)
    
    if not encoded_images:
        # If no images are found, render the website with a message
        return render_template('videomaker.html', message="No images found for the user.")
    cursor.close()
    conn.close()
    return render_template('videomaker.html', images=encoded_images, audio_files=encoded_audio_files)


@app.route('/upload', methods=['GET','POST'])
@token_required
def upload_page(current_user):
    if request.method == 'POST':
        
        # Check if the request contains files
        if 'fileInput' not in request.files:
            return redirect(request.url)

        # Get the list of files uploaded
        files = request.files.getlist('fileInput')

        # Retrieve user_id based on username
        conn = connect_to_database()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT UserId FROM UserDetails WHERE UserName = %s", (current_user,))
                user = cursor.fetchone()

                if not user:
                    return 'User not found.'

                user_id = user[0]
                flag = 0
                for file in files:
                    if file.filename == '':
                        continue  # Skip empty file inputs

                    # Calculate hash value of the image data incorporating user ID
                    image_data = file.read()
                    image_filename = str(file.filename)
                    print(image_filename)
                    combined_data = f"{user_id}:{image_data}".encode('utf-8')
                    image_hash = hashlib.sha256(combined_data).hexdigest()

                    # Check if the image hash already exists in ImageMetadata column of UserImages table
                    cursor.execute("SELECT * FROM UserImages WHERE ImageMetadata = %s", (image_hash,))
                    existing_image = cursor.fetchone()

                    if existing_image:
                        flash('You have already uploaded one or more images.', 'error')
                        flag = 1
                        continue

                    # Insert image data and metadata into UserImages table
                    cursor.execute("INSERT INTO UserImages (ImageId, UserId, ImageMetadata, ImageData) VALUES (%s, %s, %s, %s)",
                                   (image_filename, user_id, image_hash, image_data))
                conn.commit()  # Commit the transaction if all queries executed successfully
                if flag:
                    msg = 'Some Images were already in Database'
                else:
                    msg = 'Uploaded Successfully'
                return render_template('upload.html', msg=msg)
        except Exception as e:
            conn.rollback()  # Rollback the transaction in case of an error
            msg = 'Error occurred! Please Try Again.'
            print(f"The error '{e}' occurred")
            flash('An error occurred while uploading one or more images.', 'error')
            return render_template('upload.html', msg=msg)
        finally:
            conn.close()  # Ensure the database connection is closed after use
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
                conn = connect_to_database()
                cursor = conn.cursor()
                for image_id in images_to_delete:
                    cursor.execute("DELETE FROM UserImages WHERE ImageId = %s AND UserId = (SELECT UserId FROM UserDetails WHERE UserName = %s)", (image_id, current_user))
                    conn.commit()
                cursor.close()
                conn.close()
                flash('Selected images deleted successfully.', 'success')
            except Error as e:
                print(f"The error '{e}' occurred")
                flash('An error occurred while deleting selected images.', 'error')

            return redirect('/delete_images')

    # Fetch images associated with the current user from the database
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM UserImages WHERE UserId = (SELECT UserId FROM UserDetails WHERE UserName = %s)", (current_user,))
    images = cursor.fetchall()
    cursor.close()
    conn.close()
    modified_images = []
    for image in images:
        image_data = base64.b64encode(image[2]).decode('utf-8')
        modified_images.append({
            'ImageId': image[0],
            'ImageData': image_data,
            'ImageMetadata': image[3]  # Assuming ImageMetadata is the fourth column
        })

    return render_template('delete_images.html', images=modified_images)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    # Clear the token cookie
    response = make_response(render_template('landing_page.html'))
    response.set_cookie('token', '', expires=0, httponly=True)
    return response

def resize_image(input_path, output_path, resolution):
    try:
        image = Image.open(input_path)
        if image.mode == "RGBA":
            image = image.convert("RGB")
        resized_image = image.resize(resolution)
        resized_image.save(output_path)
    except Exception as e:
        a=1

def concatenate_audio_moviepy(audio_clip_paths, output_path):
    clips = [AudioFileClip(c) for c in audio_clip_paths]
    final_clip = concatenate_audioclips(clips)
    final_clip.write_audiofile(output_path)

def video(img_name_list,duration,directory,audiofile,transition,audio_duration,diraudio):
    clips = []
    i=0
    if transition=="fadein":
        for img_name in img_name_list:
            img_clip = ImageClip(os.path.join(directory, img_name)).set_duration(duration[i])
            i=i+1
            img_clip = fadein(img_clip, duration=0.5).fadeout(0.5)
            clips.append(img_clip)
    if transition=="fadeout":
        for img_name in img_name_list:
            img_clip = ImageClip(os.path.join(directory, img_name)).set_duration(duration[i])
            i=i+1
            img_clip = fadeout(img_clip, duration=0.5).fadeout(0.5)
            clips.append(img_clip)
    if transition=="crossfade":
        for img_name in img_name_list:
            img_clip = ImageClip(os.path.join(directory, img_name)).set_duration(duration[i])
            i=i+1
            img_clip = img_clip.crossfadein(0.5)
            clips.append(img_clip)
    video_clip = concatenate_videoclips(clips, method='compose')
    i=0
    print(len(audio_duration))
    final_aud=[0]*len(audio_duration)
    for audiof in audiofile:
        print(os.path.join(diraudio, audiof))
        audio_file=AudioFileClip(os.path.join(diraudio, audiof))
        j=0
        c=[]
        if audio_file.duration>=audio_duration[i]:
            c.append(os.path.join(diraudio, audiof))
            concatenate_audio_moviepy(c,f"audio{i}.mp3")
            final_aud[i]=f"audio{i}.mp3"
            audio_file = AudioFileClip(f"audio{i}.mp3")
        while audio_file.duration<audio_duration[i]:
            print(f"looping audio{i}.mp3...")
            if j==0:
                c=[os.path.join(diraudio, audiof),os.path.join(diraudio, audiof)]
            else:
                c=[f"audio{i}.mp3",os.path.join(diraudio, audiof)]
            j=1
            concatenate_audio_moviepy(c,f"audio{i}.mp3")
            final_aud[i]=f"audio{i}.mp3"
            audio_file = AudioFileClip(f"audio{i}.mp3")
        i=i+1   
    i=0
    print(final_aud)
    for iu in audiofile:
        os.remove(os.path.join(diraudio,iu))
    audiofile=final_aud
    d=[]
    for audiof in audiofile:
        print(audiof)
        audio_file=AudioFileClip(audiof)
        final=audio_file.subclip(0,audio_duration[i])
        final.write_audiofile(f"faud{i}.mp3")
        d.append(f"faud{i}.mp3")
        i=i+1
    audiofile=d
    concatenate_audio_moviepy(audiofile,"out.mp3")
    audio_file=AudioFileClip("out.mp3")
    video_clip = video_clip.set_audio(audio_file.subclip(0, video_clip.duration))
    video_clip.write_videofile("static/video.mp4", fps=24, codec="libx264", timeout=1000)
    os.remove("out.mp3")
    for i in audiofile:
        os.remove(i)

def extract_number(filename):
    a=(filename.strip("image"))
    b=a.split(".")
    return int(b[0])

@app.route('/create-video', methods=['GET','POST'])
@token_required
def create_video(current_user):
    transition = session.get('transition', '')
    resolution = session.get('resolution', '')
    print(resolution)
    durations = session.get('durations', [])  # Retrieve durations list from session
    audio_durations = session.get('audiodurations', [])
    audio_names = session.get('audionames', [])
    folder = "received_images"
    directory = f'{folder}'
    img_name_list = os.listdir(directory)
    img_name_list = sorted(img_name_list, key=extract_number)
    if resolution == '2160':
        desired_resolution = (3840, 2160)  # 2160p (4K)
    elif resolution == '1440':
        desired_resolution = (2560, 1440)  # 1440p
    elif resolution == '720':
        desired_resolution = (1280, 720)   # 720p
    elif resolution == '480':
        desired_resolution = (854, 480)    # 480p
    elif resolution == '360':
        desired_resolution = (640, 360)    # 360p
    elif resolution == '240':
        desired_resolution = (426, 240)    # 240p
    elif resolution == '144':
        desired_resolution = (256, 144)    # 144p
    else:
        # Default to 720p if resolution is not recognized
        desired_resolution = (1280, 720)
    for i in img_name_list:
        resize_image(os.path.join(directory, i),os.path.join(directory, i),desired_resolution)
    print(img_name_list)
    print(durations)
    print(directory)
    print(audio_names)
    print(transition)
    print(audio_durations)
    received_audio="received_audios"
    audio_names=os.listdir(f"{received_audio}")
    print(audio_names)
    video(img_name_list, durations, directory, audio_names, transition, audio_durations, received_audio)
    return redirect(url_for('videomaker'))

@app.route('/receive-images', methods=['POST'])
def receive_images():
    data = request.json

    if data:
        images = data.get('images', [])
        audios = data.get('audios', [])
        session['transition'] = data.get('transition', '')
        session['audio'] = data.get('audio', '')
        session['resolution'] = data.get('resolution', '')

        # Create directories if they do not exist
        if not os.path.exists('received_images'):
            os.makedirs('received_images')
        if not os.path.exists('received_audios'):
            os.makedirs('received_audios')

        # Remove existing files in 'received_images' directory
        for filename in os.listdir('received_images'):
            file_path = os.path.join('received_images', filename)
            os.remove(file_path)
        print("All files in 'received_images' directory removed successfully.")

        # Remove existing files in 'received_audios' directory
        for filename in os.listdir('received_audios'):
            file_path = os.path.join('received_audios', filename)
            os.remove(file_path)
        print("All files in 'received_audios' directory removed successfully.")

        # Retrieve audio filenames from MySQL database

        # Retrieve image durations from Flask request
        durations = []
        for index, image in enumerate(images, start=1):
            src = image.get('src', '')
            duration = image.get('duration', 0)
            durations.append(duration)
            image_data = base64.b64decode(src.split(',')[1])
            image_path = f'received_images/image{index}.jpg'
            with open(image_path, 'wb') as file:
                file.write(image_data)

        audio_durations = []
        audio_names = []
        for index, audio in enumerate(audios, start=1):
            duration = audio.get('duration', 0)
            audio_durations.append(duration)
            name = audio.get('name', '')
            name = name + ".mp3"
            audio_names.append(name)
        try:
            for audio_filename in audio_names:
                audio_path = f'received_audios/{audio_filename}'
                with open(audio_path, 'wb') as file:
                    conn = connect_to_database()
                    cursor = conn.cursor()
                    print("hello")
                    cursor.execute("SELECT AudioBlob FROM Audio WHERE AudioID = %s", (audio_filename,))
                    audio_data = cursor.fetchone()[0]
                    file.write(audio_data)
                    cursor.close()
                    conn.close()

            print("Audio files retrieved from the database and saved successfully.")
        except Exception as e:
            print(f"Error retrieving audio files from the database: {e}")
            return 'Error retrieving audio files from the database.', 500
        # Store durations list in session
        session['durations'] = durations
        session['audiodurations'] = audio_durations
        session['audionames'] = audio_names

        print(durations)
        print(audio_durations)
        print(audio_names)
        return 'Images Saved', 200
    else:
        return 'No data received.', 400

@app.route('/upload_audio', methods=['GET','POST'])
@token_required
def upload_audio(current_user):
    if request.method == 'POST':
        if 'audioFile' not in request.files:
            return redirect(request.url)
        audio_files = request.files.getlist('audioFile')
        conn = connect_to_database()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT UserId FROM UserDetails WHERE UserName = %s", (current_user,))
                user = cursor.fetchone()

                if user[1]!="admin":
                    return redirect(url_for(website))

                user_id = user[0]
                for audio_file in audio_files:
                    if audio_file.filename == '':
                        continue
                    audio_data = audio_file.read()
                    audio_filename = audio_file.filename
                    cursor.execute("INSERT INTO Audio (AudioID, AudioBlob, AudioMetadata) VALUES (%s, %s, %s)",
                                   (audio_filename, audio_data, datetime.datetime.now()))
                conn.commit()
                msg = 'Audio uploaded successfully.'
                return render_template('upload_audio.html', msg=msg)
        except Exception as e:
            conn.rollback()
            msg = 'Error occurred! Please try again.'
            print(f"The error '{e}' occurred")
            flash('An error occurred while uploading audio files.', 'error')
            return render_template('upload_audio.html', msg=msg)
        finally:
            conn.close()
    return render_template('upload_audio.html')

@app.route('/audio_list', methods=['GET', 'POST'])
@token_required
def audio_list(current_user):
    # Retrieve audio files associated with the current user from the database
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Audio")
    audio_files = cursor.fetchall()
    cursor.close()
    conn.close()
    encoded_audio_files = []
    for audio in audio_files:
        audio_id, audio_blob, audio_metadata = audio
        encoded_audio = base64.b64encode(audio_blob).decode('utf-8')
        encoded_audio_files.append((audio_id, encoded_audio, audio_metadata))

    return render_template('audio_list.html', audio_files=encoded_audio_files)

if __name__=='__main__':
    app.run(debug=True)
