import customtkinter as ctk
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from database import db_manager
from gui.canvas_hangman import CanvasHangman
from utils.sound_manager import SoundManager
from utils.hint_generator import HintGenerator
from utils.achievement_manager import AchievementManager

class GameScreenFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id, category, difficulty, mode, secret_word=None, secret_hint=None, on_back_to_menu=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.user_id = user_id
        self.category = category
        self.difficulty = difficulty
        self.mode = mode # Standard, Daily, Multiplayer
        self.on_back_to_menu = on_back_to_menu
        
        self.sound_manager = SoundManager()
        
        # Word states
        self.secret_word = ""
        self.db_hint = ""
        self.ai_hint_text = ""
        self.guessed_letters = set()
        
        self.score = 0
        self.attempts_left = 6
        self.coins = 100
        
        # Setup mode configuration
        self.setup_game_params(secret_word, secret_hint)
        
        # Layout configurations
        self.grid_columnconfigure(0, weight=1) # Left: Hangman canvas
        self.grid_columnconfigure(1, weight=1) # Right: Word board & Keyboard
        self.grid_rowconfigure(0, weight=1)
        
        self.build_ui()
        self.bind_keyboard()
        
    def setup_game_params(self, custom_word=None, custom_hint=None):
        profile = db_manager.get_user_profile(self.user_id)
        if profile:
            self.coins = profile["coins"]
            
        # Determine max attempts
        if self.difficulty == "Easy":
            self.attempts_left = 8
        elif self.difficulty == "Medium":
            self.attempts_left = 6
        else:
            self.attempts_left = 4
            
        # Select target word & hint
        if self.mode == "Multiplayer":
            self.secret_word = custom_word.lower()
            self.db_hint = custom_hint
            self.category = "Multiplayer"
        elif self.mode == "Daily Challenge":
            challenge, played = db_manager.verify_and_get_daily_challenge(self.user_id)
            self.secret_word = challenge["word"].lower()
            self.db_hint = challenge["hint"]
            self.category = challenge["category"]
            self.difficulty = "Medium" # Default daily challenge level
            self.attempts_left = 6
        else: # Standard mode
            word_data = db_manager.get_random_word(self.category, self.difficulty, self.user_id)
            if word_data:
                self.secret_word = word_data["word"].lower()
                self.db_hint = word_data["hint"]
                self.category = word_data["category"]
                self.difficulty = word_data["difficulty"]
            else:
                self.secret_word = "hangman"
                self.db_hint = "A simple word guessing game"
                self.category = "General Knowledge"
                
        self.guessed_letters = set()
        self.ai_hint_text = ""
        self.score = 0
        
    def build_ui(self):
        # 1. Left Side: Canvas + Controls
        left_pane = ctk.CTkFrame(self, fg_color="transparent")
        left_pane.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        left_pane.grid_columnconfigure(0, weight=1)
        left_pane.grid_rowconfigure(0, weight=1) # Canvas takes most space
        left_pane.grid_rowconfigure(1, weight=0) # Controls
        
        # Hangman drawing
        self.hangman_canvas = CanvasHangman(left_pane)
        self.hangman_canvas.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.hangman_canvas.set_state(self.difficulty, self.attempts_left)
        
        # Back and Skip Actions
        left_controls = ctk.CTkFrame(left_pane, fg_color="transparent")
        left_controls.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        left_controls.grid_columnconfigure((0, 1), weight=1)
        
        back_btn = ctk.CTkButton(
            left_controls,
            text="🚪 Return to Menu",
            fg_color="#64748b",
            hover_color="#475569",
            command=self.return_menu
        )
        back_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # 2. Right Side: Score, Word, Keyboard & Powerups
        right_pane = ctk.CTkFrame(self, fg_color="transparent")
        right_pane.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        right_pane.grid_columnconfigure(0, weight=1)
        right_pane.grid_rowconfigure(0, weight=0) # Stats
        right_pane.grid_rowconfigure(1, weight=1) # Word Display
        right_pane.grid_rowconfigure(2, weight=1) # Keyboard
        right_pane.grid_rowconfigure(3, weight=0) # Clues/Powerups
        
        # Stats Header
        stats_header = ctk.CTkFrame(right_pane, corner_radius=8)
        stats_header.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        stats_header.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.lbl_coins = ctk.CTkLabel(stats_header, text=f"🪙 {self.coins}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#eab308")
        self.lbl_coins.grid(row=0, column=0, pady=10)
        
        self.lbl_attempts = ctk.CTkLabel(stats_header, text=f"❤️ Attempts: {self.attempts_left}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ef4444")
        self.lbl_attempts.grid(row=0, column=1, pady=10)
        
        self.lbl_category = ctk.CTkLabel(stats_header, text=f"📂 {self.category}", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_category.grid(row=0, column=2, pady=10)
        
        self.lbl_diff = ctk.CTkLabel(stats_header, text=f"⚙️ {self.difficulty}", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_diff.grid(row=0, column=3, pady=10)
        
        # Word Panel
        word_panel = ctk.CTkFrame(right_pane, corner_radius=12)
        word_panel.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        word_panel.grid_columnconfigure(0, weight=1)
        word_panel.grid_rowconfigure(0, weight=1)
        
        self.lbl_word_display = ctk.CTkLabel(
            word_panel,
            text="",
            font=ctk.CTkFont(family="Courier New", size=32, weight="bold")
        )
        self.lbl_word_display.grid(row=0, column=0, pady=20)
        self.update_word_display()
        
        # Keyboard Panel (QWERTY layout)
        self.keyboard_frame = ctk.CTkFrame(right_pane, fg_color="transparent")
        self.keyboard_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.keyboard_frame.grid_columnconfigure(tuple(range(10)), weight=1)
        
        self.key_buttons = {}
        self.build_qwerty_keyboard()
        
        # Clues & Powerups panel
        clues_panel = ctk.CTkFrame(right_pane, corner_radius=12)
        clues_panel.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        clues_panel.grid_columnconfigure(0, weight=1)
        
        powerups_row = ctk.CTkFrame(clues_panel, fg_color="transparent")
        powerups_row.pack(fill="x", padx=10, pady=5)
        
        self.btn_power_reveal = ctk.CTkButton(
            powerups_row,
            text="✨ Reveal Letter (30¢)",
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=self.activate_reveal_letter
        )
        self.btn_power_reveal.pack(side="left", fill="x", expand=True, padx=2)
        
        self.btn_power_ai = ctk.CTkButton(
            powerups_row,
            text="🤖 Ask AI Clue (20¢)",
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            command=self.activate_ai_hint
        )
        self.btn_power_ai.pack(side="left", fill="x", expand=True, padx=2)
        
        self.btn_power_skip = ctk.CTkButton(
            powerups_row,
            text="⏭ Skip Word (50¢)",
            fg_color="#eab308",
            hover_color="#d97706",
            command=self.activate_skip_word
        )
        self.btn_power_skip.pack(side="left", fill="x", expand=True, padx=2)
        if self.mode == "Daily Challenge" or self.mode == "Multiplayer":
            self.btn_power_skip.configure(state="disabled")
            
        self.lbl_hint_box = ctk.CTkLabel(
            clues_panel,
            text="Need help? Try using power-ups to reveal letters or ask the AI analyzer!",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color=("#475569", "#94a3b8"),
            wraplength=350,
            justify="center",
            height=60
        )
        self.lbl_hint_box.pack(fill="x", padx=10, pady=(5, 10))

    def update_word_display(self):
        display_text = []
        for char in self.secret_word:
            if char.isalpha():
                if char in self.guessed_letters:
                    display_text.append(char.upper())
                else:
                    display_text.append("_")
            else:
                display_text.append(char)
        self.lbl_word_display.configure(text="  ".join(display_text))
        
    def build_qwerty_keyboard(self):
        for btn in self.key_buttons.values():
            btn.destroy()
        self.key_buttons = {}
        
        rows = [
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p"],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l"],
            ["z", "x", "c", "v", "b", "n", "m"]
        ]
        
        for r_idx, row in enumerate(rows):
            row_frame = ctk.CTkFrame(self.keyboard_frame, fg_color="transparent")
            row_frame.pack(pady=2)
            for c_idx, letter in enumerate(row):
                btn = ctk.CTkButton(
                    row_frame,
                    text=letter.upper(),
                    width=32,
                    height=36,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    command=lambda l=letter: self.guess_letter(l)
                )
                btn.pack(side="left", padx=2)
                self.key_buttons[letter] = btn

    def bind_keyboard(self):
        # Allow typing on physical keyboard
        top_level = self.winfo_toplevel()
        if top_level:
            self._key_bind_id = top_level.bind("<Key>", self.on_key_press)
        
    def unbind_keyboard(self):
        top_level = self.winfo_toplevel()
        if top_level and hasattr(self, '_key_bind_id') and self._key_bind_id:
            try:
                top_level.unbind("<Key>", self._key_bind_id)
            except Exception:
                pass
            self._key_bind_id = None
        
    def on_key_press(self, event):
        char = event.char.lower()
        if char.isalpha() and len(char) == 1:
            if char in self.key_buttons and self.key_buttons[char].cget("state") != "disabled":
                self.guess_letter(char)
                
    def guess_letter(self, letter):
        if letter in self.guessed_letters:
            return
            
        self.guessed_letters.add(letter)
        
        # Disable virtual button
        btn = self.key_buttons.get(letter)
        
        if letter in self.secret_word:
            self.sound_manager.play("correct")
            if btn:
                btn.configure(state="disabled", fg_color="#10b981", text_color="#ffffff") # Correct guess turns green
            self.update_word_display()
            self.check_win()
        else:
            self.sound_manager.play("incorrect")
            if btn:
                btn.configure(state="disabled", fg_color="#ef4444", text_color="#ffffff") # Incorrect guess turns red
            self.attempts_left -= 1
            self.lbl_attempts.configure(text=f"❤️ Attempts: {self.attempts_left}")
            self.hangman_canvas.set_state(self.difficulty, self.attempts_left)
            self.check_loss()
            
    def check_win(self):
        # Check if all letters are guessed
        won = True
        for char in self.secret_word:
            if char.isalpha() and char not in self.guessed_letters:
                won = False
                break
                
        if won:
            self.end_game(True)
            
    def check_loss(self):
        if self.attempts_left <= 0:
            self.end_game(False)
            
    def activate_reveal_letter(self):
        if self.coins < 30:
            self.sound_manager.play("incorrect")
            self.lbl_hint_box.configure(text="❌ Not enough coins! Need 30 coins.")
            return
            
        unrevealed_char = HintGenerator.reveal_random_letter(self.secret_word, self.guessed_letters)
        if unrevealed_char:
            self.sound_manager.play("powerup")
            self.coins -= 30
            db_manager.update_user_coins(self.user_id, -30)
            self.lbl_coins.configure(text=f"🪙 {self.coins}")
            self.guess_letter(unrevealed_char)
            self.lbl_hint_box.configure(text=f"✨ Power-up activated! Revealed letter '{unrevealed_char.upper()}'.")
        else:
            self.sound_manager.play("incorrect")
            self.lbl_hint_box.configure(text="All letters are already revealed!")
            
    def activate_ai_hint(self):
        if self.coins < 20:
            self.sound_manager.play("incorrect")
            self.lbl_hint_box.configure(text="❌ Not enough coins! Need 20 coins.")
            return
            
        if self.ai_hint_text:
            self.lbl_hint_box.configure(text=self.ai_hint_text)
            return
            
        self.sound_manager.play("powerup")
        self.coins -= 20
        db_manager.update_user_coins(self.user_id, -20)
        self.lbl_coins.configure(text=f"🪙 {self.coins}")
        
        self.ai_hint_text = HintGenerator.get_ai_hint(self.secret_word, self.db_hint)
        self.lbl_hint_box.configure(text=self.ai_hint_text)
        
    def activate_skip_word(self):
        if self.mode == "Daily Challenge" or self.mode == "Multiplayer":
            return
            
        if self.coins < 50:
            self.sound_manager.play("incorrect")
            self.lbl_hint_box.configure(text="❌ Not enough coins! Need 50 coins.")
            return
            
        self.sound_manager.play("powerup")
        self.coins -= 50
        db_manager.update_user_coins(self.user_id, -50)
        self.lbl_coins.configure(text=f"🪙 {self.coins}")
        
        # Trigger next word directly
        self.lbl_hint_box.configure(text="Skipping word...")
        self.setup_game_params()
        self.hangman_canvas.set_state(self.difficulty, self.attempts_left)
        self.lbl_attempts.configure(text=f"❤️ Attempts: {self.attempts_left}")
        self.lbl_category.configure(text=f"📂 {self.category}")
        self.lbl_diff.configure(text=f"⚙️ {self.difficulty}")
        self.update_word_display()
        self.build_qwerty_keyboard()
        
    def end_game(self, win):
        self.unbind_keyboard()
        
        # Deduce stats and reward profile
        score_earned = 0
        if win:
            self.sound_manager.play("win")
            base = 20
            mult = 1.0
            if self.difficulty == "Easy": mult = 1.0
            elif self.difficulty == "Medium": mult = 1.5
            else: mult = 2.0
            score_earned = int((base + self.attempts_left * 5) * mult)
        else:
            self.sound_manager.play("lose")
            
        # Update SQLite if not custom multiplayer
        unlocked_badges = []
        if self.mode == "Standard":
            db_manager.record_game_score(self.user_id, score_earned, self.difficulty, self.category, win, self.attempts_left)
            unlocked_badges = AchievementManager.check_and_unlock_achievements(self.user_id)
        elif self.mode == "Daily Challenge":
            # Record challenge outcome and update daily streak
            db_manager.record_daily_challenge_result(self.user_id, win)
            if win:
                # Seeding daily rewards: daily games earn flat score/coins too
                db_manager.record_game_score(self.user_id, score_earned, self.difficulty, self.category, win, self.attempts_left)
            unlocked_badges = AchievementManager.check_and_unlock_achievements(self.user_id)
            
        # Update local stats on profile
        profile = db_manager.get_user_profile(self.user_id)
        if profile:
            self.coins = profile["coins"]
            self.lbl_coins.configure(text=f"🪙 {self.coins}")
            
        # Overlay Dialog Frame
        self.overlay = ctk.CTkFrame(self, corner_radius=16, border_width=2, border_color="#3b82f6" if win else "#ef4444")
        self.overlay.place(relx=0.5, rely=0.5, anchor="center", width=420, height=350)
        self.overlay.grid_columnconfigure(0, weight=1)
        self.overlay.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)
        
        title_text = "🎉 VICTORY! 🎉" if win else "💀 ARENA DEFEAT 💀"
        title_color = "#10b981" if win else "#ef4444"
        
        ctk.CTkLabel(
            self.overlay,
            text=title_text,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=title_color
        ).grid(row=0, column=0, pady=(15, 0))
        
        # Word info
        ctk.CTkLabel(
            self.overlay,
            text=f"The secret word was: '{self.secret_word.upper()}'",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=1, column=0, pady=5)
        
        # Score earned
        details_txt = f"Score gained: +{score_earned} points" if win else "Don't give up! Try again."
        ctk.CTkLabel(
            self.overlay,
            text=details_txt,
            font=ctk.CTkFont(size=13)
        ).grid(row=2, column=0, pady=5)
        
        # Achievements Unlocked
        if unlocked_badges:
            badge_str = " | ".join(unlocked_badges)
            ach_lbl = ctk.CTkLabel(
                self.overlay,
                text=f"🏆 Achievement Unlocked: {badge_str}!",
                text_color="#eab308",
                font=ctk.CTkFont(size=12, weight="bold")
            )
            ach_lbl.grid(row=3, column=0, pady=5)
        else:
            ctk.CTkLabel(
                self.overlay,
                text=f"Daily Streak: {profile['daily_streak'] if profile else 0} days",
                font=ctk.CTkFont(size=12),
                text_color="#f97316"
            ).grid(row=3, column=0, pady=5)
            
        # Action controls
        btn_row = ctk.CTkFrame(self.overlay, fg_color="transparent")
        btn_row.grid(row=5, column=0, pady=(10, 15), sticky="ew", padx=30)
        btn_row.grid_columnconfigure((0, 1), weight=1)
        
        menu_btn = ctk.CTkButton(
            btn_row,
            text="🚪 Main Menu",
            fg_color="#64748b",
            hover_color="#475569",
            command=self.return_menu
        )
        menu_btn.grid(row=0, column=0, padx=5)
        
        next_txt = "Play Again" if self.mode == "Standard" else "Finish"
        next_action = self.restart_standard_game if self.mode == "Standard" else self.return_menu
        
        play_again_btn = ctk.CTkButton(
            btn_row,
            text=next_txt,
            fg_color="#10b981" if win else "#3b82f6",
            hover_color="#059669" if win else "#2563eb",
            command=next_action
        )
        play_again_btn.grid(row=0, column=1, padx=5)
        
    def restart_standard_game(self):
        self.sound_manager.play("click")
        if hasattr(self, 'overlay'):
            self.overlay.place_forget()
            
        self.setup_game_params()
        self.hangman_canvas.set_state(self.difficulty, self.attempts_left)
        self.lbl_attempts.configure(text=f"❤️ Attempts: {self.attempts_left}")
        self.lbl_category.configure(text=f"📂 {self.category}")
        self.lbl_diff.configure(text=f"⚙️ {self.difficulty}")
        self.lbl_hint_box.configure(text="Need help? Try using power-ups to reveal letters or ask the AI analyzer!")
        self.update_word_display()
        self.build_qwerty_keyboard()
        self.bind_keyboard()
        
    def return_menu(self):
        self.sound_manager.play("click")
        self.unbind_keyboard()
        if self.on_back_to_menu:
            self.on_back_to_menu()
