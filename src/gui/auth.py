import customtkinter as ctk
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from database import db_manager
from utils.sound_manager import SoundManager

class AuthFrame(ctk.CTkFrame):
    def __init__(self, parent, on_login_success, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_login_success = on_login_success
        self.sound_manager = SoundManager()
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.is_login_mode = True
        self.build_ui()
        
    def build_ui(self):
        # Clear frame
        for child in self.winfo_children():
            child.destroy()
            
        # Main container with card styling
        self.card = ctk.CTkFrame(self, width=400, height=500, corner_radius=16)
        self.card.grid(row=0, column=0, padx=20, pady=20, sticky="ns")
        self.card.grid_propagate(False)
        self.card.grid_columnconfigure(0, weight=1)
        self.card.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        
        # 1. App Title Logo
        self.title_label = ctk.CTkLabel(
            self.card,
            text="WordMaster Pro",
            font=ctk.CTkFont(family="Helvetica", size=32, weight="bold"),
            text_color=("#1e3a8a", "#38bdf8") # Light blue / Neon cyan
        )
        self.title_label.grid(row=0, column=0, pady=(30, 0), sticky="ew")
        
        self.subtitle_label = ctk.CTkLabel(
            self.card,
            text="Interactive Guessing Arena",
            font=ctk.CTkFont(family="Helvetica", size=14),
            text_color=("#475569", "#94a3b8")
        )
        self.subtitle_label.grid(row=1, column=0, pady=(0, 20), sticky="ew")
        
        # Form Header
        self.header_label = ctk.CTkLabel(
            self.card,
            text="SIGN IN",
            font=ctk.CTkFont(family="Helvetica", size=18, weight="bold")
        )
        self.header_label.grid(row=2, column=0, pady=(10, 5))
        
        # 2. Username Input
        self.username_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="Username",
            width=280,
            height=45,
            corner_radius=8
        )
        self.username_entry.grid(row=3, column=0, pady=10)
        
        # 3. Password Input
        self.password_entry = ctk.CTkEntry(
            self.card,
            placeholder_text="Password",
            show="*",
            width=280,
            height=45,
            corner_radius=8
        )
        self.password_entry.grid(row=4, column=0, pady=10)
        
        # 4. Error Label
        self.error_label = ctk.CTkLabel(
            self.card,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#ef4444"
        )
        self.error_label.grid(row=5, column=0, pady=5)
        
        # 5. Submit Button
        self.submit_btn = ctk.CTkButton(
            self.card,
            text="Login",
            width=280,
            height=45,
            corner_radius=8,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.handle_submit
        )
        self.submit_btn.grid(row=6, column=0, pady=10)
        
        # 6. Mode Switch Link
        self.switch_mode_btn = ctk.CTkButton(
            self.card,
            text="Don't have an account? Sign Up",
            fg_color="transparent",
            hover_color=None,
            text_color=("#2563eb", "#60a5fa"),
            font=ctk.CTkFont(size=12, underline=True),
            command=self.toggle_mode
        )
        self.switch_mode_btn.grid(row=7, column=0, pady=(0, 20))
        
    def toggle_mode(self):
        self.sound_manager.play("click")
        self.is_login_mode = not self.is_login_mode
        self.error_label.configure(text="")
        
        if self.is_login_mode:
            self.header_label.configure(text="SIGN IN")
            self.submit_btn.configure(text="Login")
            self.switch_mode_btn.configure(text="Don't have an account? Sign Up")
        else:
            self.header_label.configure(text="CREATE ACCOUNT")
            self.submit_btn.configure(text="Sign Up")
            self.switch_mode_btn.configure(text="Already have an account? Login")
            
    def handle_submit(self):
        self.sound_manager.play("click")
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.error_label.configure(text="Please fill in all fields.")
            self.sound_manager.play("incorrect")
            return
            
        if self.is_login_mode:
            success, result = db_manager.login_user(username, password)
            if success:
                self.error_label.configure(text="")
                self.sound_manager.play("correct")
                self.on_login_success(result)
            else:
                self.error_label.configure(text=result)
                self.sound_manager.play("incorrect")
        else:
            success, result = db_manager.register_user(username, password)
            if success:
                self.error_label.configure(text="Registration success! Please login.", text_color="#22c55e")
                self.sound_manager.play("correct")
                # Automatically toggle mode to login
                self.is_login_mode = True
                self.header_label.configure(text="SIGN IN")
                self.submit_btn.configure(text="Login")
                self.switch_mode_btn.configure(text="Don't have an account? Sign Up")
                self.password_entry.delete(0, 'end')
            else:
                self.error_label.configure(text=result, text_color="#ef4444")
                self.sound_manager.play("incorrect")
