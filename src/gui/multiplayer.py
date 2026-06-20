import customtkinter as ctk
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from utils.sound_manager import SoundManager

class MultiplayerSetupFrame(ctk.CTkFrame):
    def __init__(self, parent, difficulty, on_launch_multiplayer, on_cancel, **kwargs):
        super().__init__(parent, **kwargs)
        self.difficulty = difficulty
        self.on_launch_multiplayer = on_launch_multiplayer
        self.on_cancel = on_cancel
        self.sound_manager = SoundManager()
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.build_ui()
        
    def build_ui(self):
        # Card style container
        card = ctk.CTkFrame(self, width=450, height=480, corner_radius=16)
        card.grid(row=0, column=0, padx=20, pady=20, sticky="ns")
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        
        # 1. Title
        title_lbl = ctk.CTkLabel(
            card,
            text="Local Multiplayer Setup",
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold")
        )
        title_lbl.grid(row=0, column=0, pady=(20, 0))
        
        desc_lbl = ctk.CTkLabel(
            card,
            text="Player 1: Enter a secret word and hint.\nPlayer 2: Will attempt to guess it!",
            font=ctk.CTkFont(size=13),
            text_color=("#475569", "#94a3b8")
        )
        desc_lbl.grid(row=1, column=0, pady=(0, 10))
        
        # 2. Secret Word Input
        ctk.CTkLabel(card, text="Secret Word (Alphabetic only)", font=ctk.CTkFont(size=12, weight="bold")).grid(row=2, column=0, sticky="w", padx=45, pady=(5, 0))
        
        self.word_entry = ctk.CTkEntry(
            card,
            placeholder_text="Enter secret word",
            show="*",
            width=360,
            height=40,
            corner_radius=8
        )
        self.word_entry.grid(row=3, column=0, pady=5)
        
        # Toggle visibility button
        self.show_word = False
        self.toggle_btn = ctk.CTkButton(
            card,
            text="👁 Show Word",
            width=80,
            height=20,
            fg_color="transparent",
            hover_color=None,
            text_color=("#2563eb", "#60a5fa"),
            font=ctk.CTkFont(size=11, underline=True),
            command=self.toggle_word_visibility
        )
        self.toggle_btn.grid(row=3, column=0, sticky="e", padx=50)
        
        # 3. Hint Input
        ctk.CTkLabel(card, text="Riddle / Hint for Player 2", font=ctk.CTkFont(size=12, weight="bold")).grid(row=4, column=0, sticky="w", padx=45, pady=(5, 0))
        
        self.hint_entry = ctk.CTkEntry(
            card,
            placeholder_text="Enter a helpful clue",
            width=360,
            height=40,
            corner_radius=8
        )
        self.hint_entry.grid(row=5, column=0, pady=5)
        
        # 4. Error Label
        self.error_label = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#ef4444"
        )
        self.error_label.grid(row=6, column=0, pady=5)
        
        # 5. Bottom Actions
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.grid(row=7, column=0, pady=(10, 20), sticky="ew", padx=45)
        actions_frame.grid_columnconfigure((0, 1), weight=1)
        
        cancel_btn = ctk.CTkButton(
            actions_frame,
            text="Cancel",
            fg_color="#64748b",
            hover_color="#475569",
            height=40,
            command=self.cancel
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 5))
        
        start_btn = ctk.CTkButton(
            actions_frame,
            text="Start Game",
            fg_color="#10b981",
            hover_color="#059669",
            height=40,
            command=self.handle_start
        )
        start_btn.grid(row=0, column=1, padx=(5, 0))
        
    def toggle_word_visibility(self):
        self.sound_manager.play("click")
        self.show_word = not self.show_word
        if self.show_word:
            self.word_entry.configure(show="")
            self.toggle_btn.configure(text="🙈 Hide Word")
        else:
            self.word_entry.configure(show="*")
            self.toggle_btn.configure(text="👁 Show Word")
            
    def cancel(self):
        self.sound_manager.play("click")
        self.on_cancel()
        
    def handle_start(self):
        self.sound_manager.play("click")
        word = self.word_entry.get().strip().lower()
        hint = self.hint_entry.get().strip()
        
        if not word:
            self.error_label.configure(text="Secret word cannot be empty.")
            self.sound_manager.play("incorrect")
            return
            
        if not word.isalpha():
            self.error_label.configure(text="Word must contain letters only (no numbers or spaces).")
            self.sound_manager.play("incorrect")
            return
            
        if not hint:
            hint = "No custom hint provided by Player 1."
            
        self.error_label.configure(text="")
        self.sound_manager.play("correct")
        
        # Start game using multiplayer settings
        self.on_launch_multiplayer(word, hint)
