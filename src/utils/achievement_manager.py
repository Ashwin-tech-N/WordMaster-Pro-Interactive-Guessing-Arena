import os
import sys
# Make sure database path is resolved
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from database import db_manager

class AchievementManager:
    @staticmethod
    def check_and_unlock_achievements(user_id):
        """
        Evaluates the user's history and unlocks achievements if they meet requirements.
        Returns a list of newly unlocked achievement names.
        """
        newly_unlocked = []
        
        # 1. Fetch user analytics
        analytics = db_manager.get_user_analytics(user_id)
        profile = db_manager.get_user_profile(user_id)
        if not analytics or not profile:
            return newly_unlocked
            
        wins = analytics.get("games_won", 0)
        coins = profile.get("coins", 0)
        daily_streak = profile.get("daily_streak", 0)
        
        # Check 'First Steps' - Win your first game
        if wins >= 1:
            success, msg = db_manager.unlock_achievement(user_id, "First Steps")
            if success:
                newly_unlocked.append("First Steps")
                
        # Check 'Word Master' - Win 10 games
        if wins >= 10:
            success, msg = db_manager.unlock_achievement(user_id, "Word Master")
            if success:
                newly_unlocked.append("Word Master")
                
        # Check 'Rich Mind' - Earn 500 total coins
        if coins >= 500:
            success, msg = db_manager.unlock_achievement(user_id, "Rich Mind")
            if success:
                newly_unlocked.append("Rich Mind")
                
        # Check 'Daily Striker' - Reach a 3-day daily challenge streak
        if daily_streak >= 3:
            success, msg = db_manager.unlock_achievement(user_id, "Daily Striker")
            if success:
                newly_unlocked.append("Daily Striker")
                
        # Connect to DB to do more complex queries
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        try:
            # Check 'Flawless' - Win a game with 0 wrong guesses
            # Easy max: 8 attempts_left, Medium max: 6, Hard max: 4
            cursor.execute("""
                SELECT COUNT(*) as flawless_cnt FROM scores 
                WHERE user_id = ? AND win = 1 AND (
                    (difficulty = 'Easy' AND attempts_left = 8) OR
                    (difficulty = 'Medium' AND attempts_left = 6) OR
                    (difficulty = 'Hard' AND attempts_left = 4)
                )
            """, (user_id,))
            flawless_row = cursor.fetchone()
            if flawless_row and flawless_row["flawless_cnt"] > 0:
                success, msg = db_manager.unlock_achievement(user_id, "Flawless")
                if success:
                    newly_unlocked.append("Flawless")
                    
            # Check 'Hardcore' - Win a game on Hard difficulty
            cursor.execute("SELECT COUNT(*) as hardcore_cnt FROM scores WHERE user_id = ? AND win = 1 AND difficulty = 'Hard'", (user_id,))
            hardcore_row = cursor.fetchone()
            if hardcore_row and hardcore_row["hardcore_cnt"] > 0:
                success, msg = db_manager.unlock_achievement(user_id, "Hardcore")
                if success:
                    newly_unlocked.append("Hardcore")
                    
            # Check 'Knowledge Seeker' - Win a game in each default category
            default_categories = ["Technology", "Sports", "Movies", "Science", "General Knowledge"]
            cursor.execute("SELECT DISTINCT category FROM scores WHERE user_id = ? AND win = 1", (user_id,))
            won_categories = {row["category"] for row in cursor.fetchall()}
            
            if all(cat in won_categories for cat in default_categories):
                success, msg = db_manager.unlock_achievement(user_id, "Knowledge Seeker")
                if success:
                    newly_unlocked.append("Knowledge Seeker")
                    
        except Exception as e:
            print(f"Error checking achievements: {e}")
        finally:
            conn.close()
            
        return newly_unlocked
