
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import date

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
from datetime import date

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM Users WHERE email = %s AND password = %s', (email, password))
        account = cursor.fetchone()

        if account:
            session['user_id'] = account['user_id']
            session['name'] = account['name']

            # --- Daily reward logic ---
            today = date.today()
            if not account.get('last_login') or account['last_login'] < today:
                daily_reward = 100.00
                new_balance = float(account['balance']) + daily_reward

                # Update balance and last_login in DB
                cursor.execute(
                    'UPDATE Users SET balance = %s, last_login = %s WHERE user_id = %s',
                    (new_balance, today, account['user_id'])
                )
                mysql.connection.commit()
                flash(f'You received {daily_reward} coins as a daily login reward!', 'success')

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
        cursor = mysql.connection.cursor()

        # Fetch user info
        cursor.execute('SELECT * FROM Users WHERE user_id = %s', (session['user_id'],))
        user = cursor.fetchone()

        # Example: count cards, trades, auctions, battles
        cursor.execute('SELECT COUNT(*) AS card_count FROM Card WHERE owner_id = %s', (session['user_id'],))
        cards = cursor.fetchone()['card_count']

        cursor.execute('SELECT COUNT(*) AS trade_count FROM participates_in WHERE user_id = %s', (session['user_id'],))
        trades = cursor.fetchone()['trade_count']

        cursor.execute('SELECT COUNT(*) AS auction_count FROM Auction WHERE user_id = %s', (session['user_id'],))
        auctions = cursor.fetchone()['auction_count']

        # Fetch latest 5 battles for the dashboard
        # Latest 5 battles for dashboard
        cursor.execute("""
            SELECT 
                b.battle_id,
                b.date,
                CASE
                    WHEN b.winner = %s THEN u_loser.name
                    ELSE u_winner.name
                END AS opponent,
                CASE
                    WHEN b.winner = %s THEN 'Win'
                    ELSE 'Loss'
                END AS result,
                b.amount AS prize
            FROM Battle b
            JOIN Users u_winner ON u_winner.user_id = b.winner
            JOIN Users u_loser ON u_loser.user_id = b.loser
            WHERE %s IN (b.winner, b.loser)
            ORDER BY b.date DESC
            LIMIT 5
        """, (session['user_id'], session['user_id'], session['user_id']))
        battles = cursor.fetchall()


        # Total battles count (separate query)
        cursor.execute("""
            SELECT COUNT(*) AS battle_count
            FROM Battle
            WHERE %s IN (winner, loser)
        """, (session['user_id'],))
        row = cursor.fetchone()
        battles_count = row['battle_count'] if row else 0

        # Fetch user info
        cursor.execute('SELECT * FROM Users')
        allusers = cursor.fetchall()

        return render_template(
            'dashboard.html',
            allusers=allusers,
            user=user,
            cards=cards,
            trades=trades,
            auctions=auctions,
            battles=battles,
            battles_count=battles_count
        )


    else:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))



@app.route('/battle-history')
def battle_history():
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    cursor = mysql.connection.cursor()  # <-- just use this

    # Fetch ongoing/current battle for the user
    cursor.execute("""
        SELECT b.battle_id,
               u_winner.name AS winner_name, u_loser.name AS loser_name,
               b.winner, b.loser, b.amount, b.date,
               '' AS user_pokemon,
               '' AS opponent_pokemon,
               '' AS current_turn,
               '' AS current_move,
               0 AS user_score,
               0 AS opponent_score
        FROM Battle b
        JOIN Users u_winner ON u_winner.user_id = b.winner
        JOIN Users u_loser ON u_loser.user_id = b.loser
        WHERE b.status='ongoing' AND %s IN (b.winner, b.loser)
        ORDER BY b.date DESC
        LIMIT 1
    """, (user_id,))
    current_battle = cursor.fetchone()

    if current_battle:
        if current_battle['winner'] == user_id:
            current_battle['username'] = current_battle['winner_name']
            current_battle['opponent'] = current_battle['loser_name']
        else:
            current_battle['username'] = current_battle['loser_name']
            current_battle['opponent'] = current_battle['winner_name']

    # Fetch battle history
    cursor.execute("""
        SELECT b.battle_id AS id,
               CASE WHEN b.winner = %s THEN u_loser.name ELSE u_winner.name END AS opponent,
               b.date,
               CASE WHEN b.winner = %s THEN 'Win' ELSE 'Loss' END AS result
        FROM Battle b
        JOIN Users u_winner ON b.winner = u_winner.user_id
        JOIN Users u_loser ON b.loser = u_loser.user_id
        WHERE %s IN (b.winner, b.loser)
        ORDER BY b.date DESC
    """, (user_id, user_id, user_id))
    battles = cursor.fetchall()

    return render_template('battle.html', battles=battles, current_battle=current_battle)


@app.route('/chatbox', methods=['GET', 'POST'])
def chatbox():
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor()
    if request.method == 'POST' and 'message' in request.form:
        message = request.form['message']
        user_id = session['user_id']
        # Insert new message into Chat table
        cursor.execute(
            'INSERT INTO Chat (user_id, message, timestamp) VALUES (%s, %s, NOW())',
            (user_id, message)
        )
        mysql.connection.commit()
        flash('Message sent!', 'success')
        return redirect(url_for('chatbox'))

    # Fetch last 50 messages
    cursor.execute("""
        SELECT c.message, c.timestamp, u.name
        FROM Chat c
        JOIN Users u ON c.user_id = u.user_id
        ORDER BY c.timestamp DESC
        LIMIT 50
    """)
    messages = cursor.fetchall()

    return render_template('chatbox.html', messages=messages)




@app.route("/start-battle", methods=["POST"])
def start_battle():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    cursor = mysql.connection.cursor(dictionary=True)

    # Check if a battle is waiting
    cursor.execute("SELECT * FROM battle WHERE status='queued' LIMIT 1")
    waiting_battle = cursor.fetchone()

    if waiting_battle:
        # Someone is waiting → update to ongoing
        battle_id = waiting_battle["battle_id"]
        cursor.execute("""
            UPDATE battle
            SET status='ongoing', start_time=%s, loser=%s
            WHERE battle_id=%s
        """, (datetime.now(), user_id, battle_id))
        mysql.connection.commit()

        # Load battle.html with current battle data
        cursor.execute("SELECT * FROM battle WHERE battle_id=%s", (battle_id,))
        battle = cursor.fetchone()
        return render_template("battle.html", battle=battle)

    else:
        # No one waiting → create queued battle
        cursor.execute("""
            INSERT INTO battle (amount, date, winner, loser, status, start_time)
            VALUES (%s, %s, NULL, %s, 'queued', %s)
        """, (0, datetime.now(), user_id, datetime.now()))
        mysql.connection.commit()
        battle_id = cursor.lastrowid

        cursor.execute("SELECT * FROM battle WHERE battle_id=%s", (battle_id,))
        battle = cursor.fetchone()
        return render_template("battle.html", battle=battle)




#@app.route

if __name__ == '__main__':
    app.secret_key = "your_secret_key"
    app.run(debug=True)
