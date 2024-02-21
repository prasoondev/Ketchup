from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'hello'
app.config['MYSQL_PASSWORD'] = '123'
app.config['MYSQL_DB'] = 'project'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.secret_key = 'secret_key_for_flash_messages'
mysql = MySQL(app)
bcrypt = Bcrypt(app)

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
                return render_template('admin.html', user_details=user_details)
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
            return redirect(url_for('website'))
        else:
            return render_template('login.html', error='Invalid username or password')
        pass

    return render_template('login.html')

@app.route('/website')
def website():
    return render_template('website.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    return render_template('login.html')

if __name__=='__main__':
    app.run(debug=True)
