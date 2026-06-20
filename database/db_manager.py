import os
import sqlite3
import hashlib
import uuid
from datetime import datetime, date

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wordmaster.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password, salt=None):
    if not salt:
        salt = uuid.uuid4().hex
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hashed, salt

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        password_salt TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. User Profiles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profiles (
        user_id INTEGER PRIMARY KEY,
        coins INTEGER DEFAULT 100,
        daily_streak INTEGER DEFAULT 0,
        last_played_daily TEXT,
        avatar_color TEXT DEFAULT "#3b82f6",
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # 3. Scores table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        difficulty TEXT NOT NULL,
        category TEXT NOT NULL,
        win INTEGER NOT NULL, -- 1 for Win, 0 for Loss
        attempts_left INTEGER NOT NULL,
        played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # 4. Achievements table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS achievements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT NOT NULL,
        badge_icon TEXT NOT NULL
    )
    """)
    
    # 5. User Achievements table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_achievements (
        user_id INTEGER NOT NULL,
        achievement_id INTEGER NOT NULL,
        unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, achievement_id),
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY(achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
    )
    """)
    
    # 6. Custom/Built-in Words table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, -- NULL for default built-in words, otherwise references a specific user
        word TEXT NOT NULL,
        category TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        hint TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    
    # 7. Daily Challenges table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_challenges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL,
        category TEXT NOT NULL,
        challenge_date TEXT UNIQUE NOT NULL, -- YYYY-MM-DD
        hint TEXT NOT NULL
    )
    """)
    
    conn.commit()
    
    # Seed default achievements if they don't exist
    cursor.execute("SELECT COUNT(*) as cnt FROM achievements")
    if cursor.fetchone()["cnt"] == 0:
        default_achievements = [
            ("First Steps", "Win your first game", "🏆"),
            ("Word Master", "Win 10 games", "🎓"),
            ("Flawless", "Win a game with 0 wrong guesses", "⭐"),
            ("Hardcore", "Win a game on Hard difficulty", "🔥"),
            ("Rich Mind", "Earn 500 total coins", "💰"),
            ("Daily Striker", "Reach a 3-day daily challenge streak", "📅"),
            ("Knowledge Seeker", "Win a game in each default category", "🧠")
        ]
        cursor.executemany("INSERT INTO achievements (name, description, badge_icon) VALUES (?, ?, ?)", default_achievements)
        conn.commit()
        
    # Seed default words if they don't exist
    cursor.execute("SELECT COUNT(*) as cnt FROM words WHERE user_id IS NULL")
    if cursor.fetchone()["cnt"] == 0:
        default_words = [
            # Technology
            (None, "code", "Technology", "Easy", "Set of instructions for a computer"),
            (None, "data", "Technology", "Easy", "Information stored by a computer"),
            (None, "file", "Technology", "Easy", "A resource for storing information on a computer"),
            (None, "web", "Technology", "Easy", "The World Wide..."),
            (None, "python", "Technology", "Medium", "A popular high-level programming language named after a snake"),
            (None, "server", "Technology", "Medium", "A computer that provides data to other computers"),
            (None, "network", "Technology", "Medium", "A group of interconnected computers"),
            (None, "hacking", "Technology", "Medium", "Gaining unauthorized access to data"),
            (None, "algorithm", "Technology", "Hard", "A step-by-step procedure for solving a problem"),
            (None, "database", "Technology", "Hard", "An organized collection of structured information"),
            (None, "interface", "Technology", "Hard", "A point where two systems meet and interact"),
            (None, "artificial", "Technology", "Hard", "Made by human skill; not natural (e.g. __ intelligence)"),
            
            # Sports
            (None, "golf", "Sports", "Easy", "Game played on a course with clubs and a tiny ball"),
            (None, "swim", "Sports", "Easy", "Propelling yourself through water"),
            (None, "run", "Sports", "Easy", "Moving rapidly on foot"),
            (None, "ball", "Sports", "Easy", "Spherical object used in many games"),
            (None, "soccer", "Sports", "Medium", "Called football outside North America"),
            (None, "tennis", "Sports", "Medium", "Racket sport played on a court with a net"),
            (None, "hockey", "Sports", "Medium", "Played on ice or grass with curved sticks"),
            (None, "boxing", "Sports", "Medium", "Combat sport involving punching gloves"),
            (None, "gymnastics", "Sports", "Hard", "Sport involving exercises displaying physical agility and coordination"),
            (None, "badminton", "Sports", "Hard", "Racket sport played with a shuttlecock"),
            (None, "marathon", "Sports", "Hard", "Long-distance running race, officially 26.2 miles"),
            (None, "athletics", "Sports", "Hard", "Collection of sporting events like running, jumping, throwing"),
            
            # Movies
            (None, "star", "Movies", "Easy", "Famous actor or a celestial body"),
            (None, "film", "Movies", "Easy", "Another word for movie"),
            (None, "hero", "Movies", "Easy", "Main good character in an action movie"),
            (None, "plot", "Movies", "Easy", "The storyline of a movie"),
            (None, "titanic", "Movies", "Medium", "1997 disaster romance movie set on a famous sinking ship"),
            (None, "matrix", "Movies", "Medium", "Sci-fi action movie where reality is a simulation"),
            (None, "avatar", "Movies", "Medium", "Highest grossing sci-fi movie featuring blue-skinned aliens on Pandora"),
            (None, "thriller", "Movies", "Medium", "Genre of movie that keeps you on the edge of your seat"),
            (None, "godfather", "Movies", "Hard", "Classic mafia crime drama directed by Francis Ford Coppola"),
            (None, "inception", "Movies", "Hard", "Christopher Nolan film about entering dreams within dreams"),
            (None, "gladiator", "Movies", "Hard", "Historical drama starring Russell Crowe as a Roman general turned slave"),
            (None, "interstellar", "Movies", "Hard", "Space epic about searching for a new home for humanity"),
            
            # Science
            (None, "atom", "Science", "Easy", "Basic unit of a chemical element"),
            (None, "acid", "Science", "Easy", "Chemical substance with pH less than 7"),
            (None, "cell", "Science", "Easy", "The smallest structural and functional unit of an organism"),
            (None, "moon", "Science", "Easy", "Earth's natural satellite"),
            (None, "gravity", "Science", "Medium", "Force that pulls objects toward each other"),
            (None, "physics", "Science", "Medium", "Branch of science concerned with nature and properties of matter"),
            (None, "biology", "Science", "Medium", "The scientific study of life and living organisms"),
            (None, "element", "Science", "Medium", "Substance consisting of atoms which all have the same number of protons"),
            (None, "photosynthesis", "Science", "Hard", "Process by which green plants use sunlight to synthesize food"),
            (None, "molecule", "Science", "Hard", "Group of atoms bonded together"),
            (None, "chemistry", "Science", "Hard", "Branch of science that deals with properties and reactions of substances"),
            (None, "telescope", "Science", "Hard", "Optical instrument used for viewing distant objects in space"),
            
            # General Knowledge
            (None, "earth", "General Knowledge", "Easy", "The planet we live on"),
            (None, "ocean", "General Knowledge", "Easy", "Large body of salt water covering most of Earth"),
            (None, "maps", "General Knowledge", "Easy", "Visual representations of areas"),
            (None, "flag", "General Knowledge", "Easy", "Piece of cloth with a design representing a country"),
            (None, "desert", "General Knowledge", "Medium", "Barren area of landscape where little precipitation occurs"),
            (None, "capital", "General Knowledge", "Medium", "City serving as the seat of government"),
            (None, "history", "General Knowledge", "Medium", "The study of past events"),
            (None, "country", "General Knowledge", "Medium", "A nation with its own government, occupying a particular territory"),
            (None, "continent", "General Knowledge", "Hard", "One of the earth's large continuous masses of land"),
            (None, "parliament", "General Knowledge", "Hard", "A legislative body of government"),
            (None, "monument", "General Knowledge", "Hard", "Statue, building, or other structure erected to commemorate a person or event"),
            (None, "geography", "General Knowledge", "Hard", "The study of physical features of the earth and its atmosphere")
        ]
        cursor.executemany("INSERT INTO words (user_id, word, category, difficulty, hint) VALUES (?, ?, ?, ?, ?)", default_words)
        conn.commit()
        
    conn.close()

# User Auth Functions
def register_user(username, password):
    username = username.strip()
    if not username or not password:
        return False, "Username and password cannot be empty."
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if username exists
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            return False, "Username already exists."
        
        password_hash, password_salt = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, password_salt) VALUES (?, ?, ?)",
            (username, password_hash, password_salt)
        )
        user_id = cursor.lastrowid
        
        # Create user profile
        cursor.execute(
            "INSERT INTO user_profiles (user_id, coins, daily_streak, last_played_daily) VALUES (?, 100, 0, NULL)",
            (user_id,)
        )
        conn.commit()
        return True, user_id
    except sqlite3.Error as e:
        return False, str(e)
    finally:
        conn.close()

def login_user(username, password):
    username = username.strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, password_hash, password_salt FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if not row:
            return False, "Invalid username or password."
        
        user_id = row["id"]
        stored_hash = row["password_hash"]
        salt = row["password_salt"]
        
        computed_hash, _ = hash_password(password, salt)
        if computed_hash == stored_hash:
            return True, user_id
        else:
            return False, "Invalid username or password."
    except sqlite3.Error as e:
        return False, str(e)
    finally:
        conn.close()

# Profile & Coins Functions
def get_user_profile(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT u.username, p.coins, p.daily_streak, p.last_played_daily, p.avatar_color
            FROM users u
            JOIN user_profiles p ON u.id = p.user_id
            WHERE u.id = ?
        """, (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        conn.close()

def update_user_coins(user_id, coin_delta):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT coins FROM user_profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return False
        
        current_coins = row["coins"]
        new_coins = max(0, current_coins + coin_delta)
        cursor.execute("UPDATE user_profiles SET coins = ? WHERE user_id = ?", (new_coins, user_id))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

def update_avatar_color(user_id, color):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE user_profiles SET avatar_color = ? WHERE user_id = ?", (color, user_id))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

# Daily Streak Functions
def verify_and_get_daily_challenge(user_id):
    """
    Returns the daily challenge word for today. If not initialized in DB, initializes it.
    Also returns whether the user has already played today's challenge.
    """
    today_str = date.today().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check daily challenge word in db for today
        cursor.execute("SELECT word, category, hint FROM daily_challenges WHERE challenge_date = ?", (today_str,))
        challenge = cursor.fetchone()
        
        if not challenge:
            # Pick a random word from default list to be the daily challenge
            cursor.execute("SELECT word, category, hint FROM words WHERE user_id IS NULL ORDER BY RANDOM() LIMIT 1")
            word_row = cursor.fetchone()
            if word_row:
                cursor.execute(
                    "INSERT INTO daily_challenges (word, category, challenge_date, hint) VALUES (?, ?, ?, ?)",
                    (word_row["word"], word_row["category"], today_str, word_row["hint"])
                )
                conn.commit()
                challenge = {"word": word_row["word"], "category": word_row["category"], "hint": word_row["hint"]}
            else:
                # Fallback in case table is empty
                challenge = {"word": "challenge", "category": "General Knowledge", "hint": "A task or situation that tests someone's abilities"}
        else:
            challenge = dict(challenge)
            
        # Check if user already played today
        cursor.execute("SELECT last_played_daily, daily_streak FROM user_profiles WHERE user_id = ?", (user_id,))
        profile = cursor.fetchone()
        
        already_played = False
        if profile and profile["last_played_daily"] == today_str:
            already_played = True
            
        return challenge, already_played
    finally:
        conn.close()

def record_daily_challenge_result(user_id, win):
    today_str = date.today().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Get current profile
        cursor.execute("SELECT daily_streak, last_played_daily FROM user_profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return False
            
        streak = row["daily_streak"]
        last_played = row["last_played_daily"]
        
        if last_played == today_str:
            # Already played today, do not alter streak
            return True
            
        # Check if they played yesterday to continue streak
        if win:
            yesterday_str = (date.today() - sqlite3.dbapi2.timedelta(days=1)).isoformat() if hasattr(sqlite3.dbapi2, 'timedelta') else None
            # Standard python date operations
            from datetime import timedelta
            yesterday_str = (date.today() - timedelta(days=1)).isoformat()
            
            if last_played == yesterday_str or last_played is None or streak == 0:
                new_streak = streak + 1
            else:
                new_streak = 1 # Streak restarted
        else:
            new_streak = 0 # Streak lost
            
        cursor.execute(
            "UPDATE user_profiles SET daily_streak = ?, last_played_daily = ? WHERE user_id = ?",
            (new_streak, today_str, user_id)
        )
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

# Gameplay Words & Scoring
def get_random_word(category=None, difficulty=None, user_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT word, category, difficulty, hint FROM words WHERE (user_id IS NULL OR user_id = ?)"
        params = [user_id]
        
        if category and category != "All":
            query += " AND category = ?"
            params.append(category)
        if difficulty and difficulty != "All":
            query += " AND difficulty = ?"
            params.append(difficulty)
            
        query += " ORDER BY RANDOM() LIMIT 1"
        cursor.execute(query, params)
        row = cursor.fetchone()
        if row:
            return dict(row)
        
        # Fallback if no matching custom word
        cursor.execute("SELECT word, category, difficulty, hint FROM words WHERE user_id IS NULL ORDER BY RANDOM() LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def record_game_score(user_id, score, difficulty, category, win, attempts_left):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Insert score
        cursor.execute(
            "INSERT INTO scores (user_id, score, difficulty, category, win, attempts_left) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, score, difficulty, category, int(win), attempts_left)
        )
        
        # Reward coins on win
        if win:
            multiplier = 1.0
            if difficulty == "Easy":
                multiplier = 1.0
            elif difficulty == "Medium":
                multiplier = 1.5
            elif difficulty == "Hard":
                multiplier = 2.0
                
            base_reward = 20
            # Additional reward for remaining attempts
            attempts_bonus = attempts_left * 5
            total_coins_earned = int((base_reward + attempts_bonus) * multiplier)
            
            cursor.execute("SELECT coins FROM user_profiles WHERE user_id = ?", (user_id,))
            prof = cursor.fetchone()
            current_coins = prof["coins"] if prof else 0
            cursor.execute("UPDATE user_profiles SET coins = ? WHERE user_id = ?", (current_coins + total_coins_earned, user_id))
            
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

# Analytics & Dashboard
def get_user_analytics(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    analytics = {}
    try:
        # 1. Total games played
        cursor.execute("SELECT COUNT(*) as played, SUM(win) as wins, SUM(score) as total_score FROM scores WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        analytics["games_played"] = row["played"] or 0
        analytics["games_won"] = row["wins"] or 0
        analytics["games_lost"] = (row["played"] or 0) - (row["wins"] or 0)
        analytics["total_score"] = row["total_score"] or 0
        
        if analytics["games_played"] > 0:
            analytics["win_rate"] = int((analytics["games_won"] / analytics["games_played"]) * 100)
        else:
            analytics["win_rate"] = 0
            
        # 2. Category Distribution
        cursor.execute("SELECT category, COUNT(*) as cnt FROM scores WHERE user_id = ? GROUP BY category", (user_id,))
        analytics["category_dist"] = {r["category"]: r["cnt"] for r in cursor.fetchall()}
        
        # 3. Difficulty Distribution
        cursor.execute("SELECT difficulty, COUNT(*) as cnt, SUM(win) as wins FROM scores WHERE user_id = ? GROUP BY difficulty", (user_id,))
        analytics["difficulty_dist"] = {r["difficulty"]: {"played": r["cnt"], "wins": r["wins"]} for r in cursor.fetchall()}
        
        # 4. Recent matches (last 5)
        cursor.execute(
            "SELECT score, difficulty, category, win, attempts_left, played_at FROM scores WHERE user_id = ? ORDER BY played_at DESC LIMIT 5",
            (user_id,)
        )
        analytics["recent_games"] = [dict(r) for r in cursor.fetchall()]
        
        # 5. Coins, streaks from profile
        cursor.execute("SELECT coins, daily_streak FROM user_profiles WHERE user_id = ?", (user_id,))
        prof = cursor.fetchone()
        analytics["coins"] = prof["coins"] if prof else 0
        analytics["daily_streak"] = prof["daily_streak"] if prof else 0
        
        return analytics
    finally:
        conn.close()

def get_leaderboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Top 10 users by total score
        cursor.execute("""
            SELECT u.username, SUM(s.score) as total_score, COUNT(s.id) as games_played, SUM(s.win) as games_won, p.avatar_color
            FROM users u
            JOIN scores s ON u.id = s.user_id
            JOIN user_profiles p ON u.id = p.user_id
            GROUP BY u.id
            ORDER BY total_score DESC
            LIMIT 10
        """)
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()

# Custom word packs import/management
def import_custom_words(user_id, word_list):
    """
    word_list: List of dicts, each containing:
    {"word": "example", "category": "Custom Category", "difficulty": "Easy/Medium/Hard", "hint": "A hint description"}
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    imported_count = 0
    try:
        for item in word_list:
            word = item.get("word", "").strip().lower()
            category = item.get("category", "Custom").strip()
            difficulty = item.get("difficulty", "Medium").strip()
            hint = item.get("hint", "").strip()
            
            if not word or not hint:
                continue
                
            cursor.execute(
                "INSERT INTO words (user_id, word, category, difficulty, hint) VALUES (?, ?, ?, ?, ?)",
                (user_id, word, category, difficulty, hint)
            )
            imported_count += 1
        conn.commit()
        return True, imported_count
    except sqlite3.Error as e:
        return False, str(e)
    finally:
        conn.close()

def get_custom_categories(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT category FROM words WHERE user_id = ?", (user_id,))
        return [r["category"] for r in cursor.fetchall()]
    finally:
        conn.close()

def delete_custom_category(user_id, category):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM words WHERE user_id = ? AND category = ?", (user_id, category))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

# Achievements System
def get_user_achievements(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT a.id, a.name, a.description, a.badge_icon,
                   (ua.user_id IS NOT NULL) as unlocked, ua.unlocked_at
            FROM achievements a
            LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = ?
            ORDER BY a.id ASC
        """, (user_id,))
        return [dict(r) for r in cursor.fetchall()]
    finally:
        conn.close()

def unlock_achievement(user_id, achievement_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Find achievement ID
        cursor.execute("SELECT id FROM achievements WHERE name = ?", (achievement_name,))
        row = cursor.fetchone()
        if not row:
            return False, "Achievement not found"
        achievement_id = row["id"]
        
        # Check if already unlocked
        cursor.execute("SELECT 1 FROM user_achievements WHERE user_id = ? AND achievement_id = ?", (user_id, achievement_id))
        if cursor.fetchone():
            return False, "Already unlocked"
            
        cursor.execute("INSERT INTO user_achievements (user_id, achievement_id) VALUES (?, ?)", (user_id, achievement_id))
        conn.commit()
        return True, "Achievement unlocked!"
    except sqlite3.Error as e:
        return False, str(e)
    finally:
        conn.close()
