from flask import Flask,render_template,request,redirect,url_for,jsonify,make_response
import json
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity,decode_token
from flask_bcrypt import Bcrypt
import os
import requests
app = Flask(__name__)
app.secret_key = 'secret_key_for_flash_messages'
app.config['JWT_SECRET_KEY'] = '1234567'
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
def read_data():
    if os.path.exists('users.txt'):
        try:
            with open('users.txt', 'r') as f:
                return json.load(f)
        except:
            return []
    else:
        return []

def wrdata(data):
    with open('users.txt', 'w') as f:
        json.dump(data, f)
@app.route("/")
def form():
    return render_template("register.html")
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "POST":
        data=request.form
        username=data['register-username']
        password=data['register-password']
        password=bcrypt.generate_password_hash(data['register-password']).decode('utf-8')
        users=read_data()
        for i in users:
            if i['username']==username:
                return render_template('register.html', error='Username already exists')
        user={
            'username':username,
            'password':password
        }
        temp = read_data()
        temp.append(user)
        wrdata(temp)
        return redirect(url_for('login'))    
    return render_template('register.html')
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        data=request.form
        username=data['login-username']
        password=data['login-password']
        if username=='admin':
            data=read_data()
            for i in data:
                if i['username']=='admin':
                    if bcrypt.check_password_hash(i['password'], password):
                        return render_template('admin.html', data=data)
    return render_template('adminlogin.html')
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        data = request.form
        username = data['login-username']
        password = data['login-password']
        users = read_data()
        for user in users:
            if user['username'] == username and bcrypt.check_password_hash(user['password'], password):
                access_token1 = create_access_token(identity=username)
                return redirect(url_for('website', access_token=access_token1))
        return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    return render_template('login.html')
@app.route('/website')
def website():
    access_token = request.args.get('access_token')
    if access_token:
        return render_template('website.html')
    return redirect(url_for('login'))
if __name__=='__main__':
    app.run(debug=True)