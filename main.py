from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime, date
import random
import time

app = Flask(__name__)

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'GottaCatchemAll'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Battle queue and ongoing battles (in-memory storage for simplicity)
battle_queue = {}
ongoing_battles = {}

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
    cursor = mysql.connection.cursor()

    # Check if user is in queue by looking at challenge table
    cursor.execute("""
        SELECT COUNT(*) as in_queue 
        FROM challenge 
        WHERE user_id = %s AND status = 'queued'
    """, (user_id,))
    in_queue_result = cursor.fetchone()
    in_queue = in_queue_result['in_queue'] > 0 if in_queue_result else False

    # Check for ongoing battle in database
    cursor.execute("""
        SELECT b.battle_id, b.winner, b.loser, b.date, b.status,
               b.player1_score, b.player2_score, b.current_turn, b.current_move,
               u1.name as winner_name, u2.name as loser_name,
               c1.card_id as winner_card_id, c1.name as winner_pokemon,
               c2.card_id as loser_card_id, c2.name as loser_pokemon
        FROM Battle b
        JOIN Users u1 ON b.winner = u1.user_id
        JOIN Users u2 ON b.loser = u2.user_id
        JOIN challenge ch1 ON b.battle_id = ch1.battle_id AND ch1.user_id = b.winner
        JOIN challenge ch2 ON b.battle_id = ch2.battle_id AND ch2.user_id = b.loser
        JOIN card c1 ON ch1.card_id = c1.card_id
        JOIN card c2 ON ch2.card_id = c2.card_id
        WHERE b.status = 'ongoing' AND %s IN (b.winner, b.loser)
    """, (user_id,))
    
    db_battle = cursor.fetchone()
    
    current_battle = None
    if db_battle:
        # Create battle data structure similar to our in-memory battles
        battle_id = db_battle['battle_id']
        
        # Determine if current user is winner or loser
        if db_battle['winner'] == user_id:
            user_pokemon = db_battle['winner_pokemon']
            opponent_pokemon = db_battle['loser_pokemon']
            opponent_id = db_battle['loser']
            opponent_name = db_battle['loser_name']
            user_score = db_battle['player1_score']
            opponent_score = db_battle['player2_score']
        else:
            user_pokemon = db_battle['loser_pokemon']
            opponent_pokemon = db_battle['winner_pokemon']
            opponent_id = db_battle['winner']
            opponent_name = db_battle['winner_name']
            user_score = db_battle['player2_score']
            opponent_score = db_battle['player1_score']
        
        # Get current turn username
        cursor.execute("SELECT name FROM users WHERE user_id = %s", (db_battle['current_turn'],))
        current_turn_user = cursor.fetchone()
        current_turn_name = current_turn_user['name'] if current_turn_user else "Unknown"
        
        # Create battle data structure
        current_battle = {
            'battle_id': battle_id,
            'user_pokemon': user_pokemon,
            'opponent_pokemon': opponent_pokemon,
            'username': session['name'],
            'opponent': opponent_name,
            'user_score': user_score,
            'opponent_score': opponent_score,
            'current_turn': current_turn_name,
            'current_move': db_battle['current_move'] or 'None',
            'is_users_turn': db_battle['current_turn'] == user_id  # ADDED THIS LINE
        }
        
        # Also add to ongoing_battles for the Flask app to handle moves
        if battle_id not in ongoing_battles:
            ongoing_battles[battle_id] = {
                'player1': {
                    'user_id': db_battle['winner'],
                    'username': db_battle['winner_name'],
                    'pokemon': db_battle['winner_pokemon'],
                    'score': db_battle['player1_score']
                },
                'player2': {
                    'user_id': db_battle['loser'],
                    'username': db_battle['loser_name'],
                    'pokemon': db_battle['loser_pokemon'],
                    'score': db_battle['player2_score']
                },
                'current_turn': db_battle['current_turn'],
                'current_move': db_battle['current_move'] or 'None',
                'start_time': db_battle['date']
            }

    # Fetch user's cards for selection modal
    cursor.execute("SELECT name FROM Card WHERE owner_id = %s", (user_id,))
    user_cards = cursor.fetchall()

    # Fetch battle history
    cursor.execute("""
        SELECT b.battle_id AS id,
               CASE WHEN b.winner = %s THEN u_loser.name ELSE u_winner.name END AS opponent,
               b.date,
               CASE WHEN b.winner = %s THEN 'Win' ELSE 'Loss' END AS result
        FROM Battle b
        JOIN Users u_winner ON b.winner = u_winner.user_id
        JOIN Users u_loser ON b.loser = u_loser.user_id
        WHERE %s IN (b.winner, b.loser) AND b.status = 'finished'
        ORDER BY b.date DESC
    """, (user_id, user_id, user_id))
    battles = cursor.fetchall()

    return render_template('battle.html', 
                         battles=battles, 
                         current_battle=current_battle,
                         in_queue=in_queue,
                         user_cards=user_cards)

@app.route("/start-battle", methods=["POST"])
def start_battle():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    username = session["name"]
    pokemon = request.form.get("pokemon")
    
    if not pokemon:
        flash("Please select a Pokémon to battle with!", "danger")
        return redirect(url_for("battle_history"))
    
    cursor = mysql.connection.cursor()
    
    # Check if user is already in a battle or queue
    cursor.execute("""
        SELECT b.status 
        FROM battle b
        JOIN challenge c ON b.battle_id = c.battle_id
        WHERE c.user_id = %s AND b.status IN ('ongoing', 'queued')
    """, (user_id,))
    existing_battle = cursor.fetchone()
    
    if existing_battle:
        flash("You are already in a battle or queue!", "warning")
        return redirect(url_for("battle_history"))
    
    # Get the card ID for the selected Pokémon
    cursor.execute("SELECT card_id FROM card WHERE owner_id = %s AND name = %s", (user_id, pokemon))
    card = cursor.fetchone()
    
    if not card:
        flash("Invalid Pokémon selection!", "danger")
        return redirect(url_for("battle_history"))
    
    card_id = card['card_id']
    
    # Check if there's someone waiting in the queue
    cursor.execute("""
        SELECT c.user_id, u.name, c.card_id, card.name as pokemon_name
        FROM challenge c
        JOIN users u ON c.user_id = u.user_id
        JOIN card ON c.card_id = card.card_id
        WHERE c.status = 'queued' AND c.user_id != %s
        LIMIT 1
    """, (user_id,))
    waiting_challenge = cursor.fetchone()
    
    if waiting_challenge:
        # Match with the waiting player
        opponent_id = waiting_challenge['user_id']
        opponent_name = waiting_challenge['name']
        opponent_pokemon = waiting_challenge['pokemon_name']
        opponent_card_id = waiting_challenge['card_id']
        
        # Create a new battle
        cursor.execute("""
            INSERT INTO battle (winner, loser, status, current_turn, current_move)
            VALUES (%s, %s, 'ongoing', %s, 'None')
        """, (user_id, opponent_id, user_id))
        battle_id = cursor.lastrowid
        
        # Update both challenges to match_found
        cursor.execute("""
            UPDATE challenge 
            SET battle_id = %s, status = 'match_found' 
            WHERE user_id IN (%s, %s) AND status = 'queued'
        """, (battle_id, user_id, opponent_id))
        
        mysql.connection.commit()
        
        flash(f"Battle started! You are battling against {opponent_name}", "success")
    else:
        # Add to queue
        cursor.execute("""
            INSERT INTO challenge (user_id, card_id, status)
            VALUES (%s, %s, 'queued')
        """, (user_id, card_id))
        mysql.connection.commit()
        
        flash("You've been added to the battle queue. Waiting for an opponent...", "info")
    
    return redirect(url_for("battle_history"))

@app.route("/cancel-queue", methods=["POST"])
def cancel_queue():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    
    if user_id in battle_queue:
        del battle_queue[user_id]
        flash("You've been removed from the battle queue.", "info")
    else:
        flash("You are not in the battle queue.", "warning")
    
    return redirect(url_for("battle_history"))

@app.route("/make-move", methods=["POST"])
def make_move():
    if "user_id" not in session:
        return jsonify({"success": False, "message": "Not logged in"})
    
    user_id = session["user_id"]
    username = session["name"]
    data = request.get_json()
    battle_id = data.get("battle_id")
    move = data.get("move")
    
    if not battle_id or not move:
        return jsonify({"success": False, "message": "Invalid request"})
    
    battle_id = int(battle_id)
    
    # Check if battle exists in database
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT b.*, u1.name as winner_name, u2.name as loser_name
        FROM battle b
        JOIN users u1 ON b.winner = u1.user_id
        JOIN users u2 ON b.loser = u2.user_id
        WHERE b.battle_id = %s AND b.status = 'ongoing'
    """, (battle_id,))
    db_battle = cursor.fetchone()
    
    if not db_battle:
        return jsonify({"success": False, "message": "Battle not found"})
    
    # Check if user is in this battle
    if user_id not in [db_battle['winner'], db_battle['loser']]:
        return jsonify({"success": False, "message": "You are not in this battle"})
    
    # Check if it's the user's turn
    if db_battle['current_turn'] != user_id:
        return jsonify({"success": False, "message": "It's not your turn"})
    
    # Determine opponent ID
    opponent_id = db_battle['loser'] if db_battle['winner'] == user_id else db_battle['winner']
    
    # Process move and calculate damage
    damage = 0
    if move == "attack":
        damage = random.randint(10, 20)
    elif move == "special":
        damage = random.randint(15, 30)
    # Defend move doesn't do damage
    
    # Update scores in database
    if db_battle['winner'] == user_id:
        new_score = db_battle['player1_score'] + damage
        cursor.execute("""
            UPDATE battle SET player1_score = %s, current_move = %s 
            WHERE battle_id = %s
        """, (new_score, move, battle_id))
    else:
        new_score = db_battle['player2_score'] + damage
        cursor.execute("""
            UPDATE battle SET player2_score = %s, current_move = %s 
            WHERE battle_id = %s
        """, (new_score, move, battle_id))
    
    # Switch turns to opponent
    cursor.execute("""
        UPDATE battle SET current_turn = %s WHERE battle_id = %s
    """, (opponent_id, battle_id))
    
    mysql.connection.commit()
    
    # Check for win condition
    cursor.execute("SELECT player1_score, player2_score FROM battle WHERE battle_id = %s", (battle_id,))
    scores = cursor.fetchone()
    
    if scores['player1_score'] >= 100 or scores['player2_score'] >= 100:
        # Determine winner and loser
        if scores['player1_score'] >= 100:
            winner_id = db_battle['winner']
            loser_id = db_battle['loser']
        else:
            winner_id = db_battle['loser']
            loser_id = db_battle['winner']
        
        # Update battle status to finished
        cursor.execute("""
            UPDATE battle SET status = 'finished', winner = %s, loser = %s 
            WHERE battle_id = %s
        """, (winner_id, loser_id, battle_id))
        
        # Update challenge status
        cursor.execute("""
            UPDATE challenge SET status = 'completed' WHERE battle_id = %s
        """, (battle_id,))
        
        mysql.connection.commit()
        
        # Remove from ongoing battles if it exists there
        if battle_id in ongoing_battles:
            del ongoing_battles[battle_id]
        
        # Determine if current user won or lost
        if winner_id == user_id:
            flash("You won the battle!", "success")
        else:
            flash("You lost the battle.", "warning")
            
        return jsonify({"success": True, "battle_over": True})
    
    return jsonify({"success": True, "battle_over": False, "damage": damage})

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

if __name__ == '__main__':
    app.secret_key = "your_secret_key"
    app.run(debug=True)
