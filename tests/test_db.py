import unittest
import os
import sys

# Add project path to search paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from database import db_manager

class TestDatabaseOperations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Trigger DB initialization
        db_manager.init_db()

    def test_01_user_registration_and_login(self):
        # Register test user
        username = "test_user_99"
        password = "test_password_99"
        
        # Clean up if user already exists from a previous bad run
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        conn.close()

        success, user_id = db_manager.register_user(username, password)
        self.assertTrue(success, "Failed to register test user.")
        self.assertIsInstance(user_id, int)

        # Duplicate register check
        dup_success, dup_result = db_manager.register_user(username, password)
        self.assertFalse(dup_success, "Should not allow duplicate registration.")

        # Correct login check
        login_success, login_id = db_manager.login_user(username, password)
        self.assertTrue(login_success)
        self.assertEqual(login_id, user_id)

        # Incorrect password check
        bad_login_success, bad_login_res = db_manager.login_user(username, "wrong_pass")
        self.assertFalse(bad_login_success)

    def test_02_get_random_word(self):
        # Test default word fetching
        word_data = db_manager.get_random_word(category="Technology", difficulty="Easy")
        self.assertIsNotNone(word_data)
        self.assertEqual(word_data["category"], "Technology")
        self.assertEqual(word_data["difficulty"], "Easy")
        self.assertTrue(len(word_data["word"]) > 0)

    def test_03_coins_update(self):
        username = "test_user_coins"
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        
        success, user_id = db_manager.register_user(username, "pass")
        self.assertTrue(success)

        # Get initial coins
        profile = db_manager.get_user_profile(user_id)
        self.assertEqual(profile["coins"], 100)

        # Update coins
        db_manager.update_user_coins(user_id, 50)
        profile_after = db_manager.get_user_profile(user_id)
        self.assertEqual(profile_after["coins"], 150)

        # Deduct coins
        db_manager.update_user_coins(user_id, -80)
        profile_after2 = db_manager.get_user_profile(user_id)
        self.assertEqual(profile_after2["coins"], 70)

        # Ensure no negative coins
        db_manager.update_user_coins(user_id, -200)
        profile_after3 = db_manager.get_user_profile(user_id)
        self.assertEqual(profile_after3["coins"], 0)

    def test_04_achievements_unlocking(self):
        username = "test_user_ach"
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        
        success, user_id = db_manager.register_user(username, "pass")
        self.assertTrue(success)

        # Unlock First Steps achievement
        success, msg = db_manager.unlock_achievement(user_id, "First Steps")
        self.assertTrue(success)
        
        # Check unlocked state
        achievements = db_manager.get_user_achievements(user_id)
        first_steps_unlocked = False
        for ach in achievements:
            if ach["name"] == "First Steps":
                first_steps_unlocked = bool(ach["unlocked"])
                break
        self.assertTrue(first_steps_unlocked)

if __name__ == "__main__":
    unittest.main()
