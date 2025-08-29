
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'GottaCatchemAll'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Root route
@app.route('/')
def home():
    return redirect(url_for('login'))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM Users WHERE email = %s AND password = %s', (email, password))
        account = cursor.fetchone()

        if account:
            session['user_id'] = account['user_id']  # <-- correct key
            session['name'] = account['name']        # store name if needed
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email/password!', 'danger')
    return render_template('login.html')



# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'password' in request.form:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM Users WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            flash('Account already exists!', 'warning')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match!', 'danger')
        else:
            cursor.execute('INSERT INTO Users (name, email, password) VALUES (%s, %s, %s)', (name, email, password))
            mysql.connection.commit()
            flash('You have successfully registered!', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return '''
        <body style="background-color:black; color:white; display:flex; justify-content:center; align-items:center; height:100vh;">
            <h1>Dashboard</h1>
        </body>
        '''
    else:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))


#@app.route

if __name__ == '__main__':
    app.secret_key = "your_secret_key"
    app.run(debug=True)
