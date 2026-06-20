import customtkinter as ctk
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from database import db_manager
from gui.auth import AuthFrame
from gui.dashboard import DashboardFrame
from gui.category_selection import CategorySelectionFrame
from gui.multiplayer import MultiplayerSetupFrame
from gui.game_screen import GameScreenFrame
from utils.sound_manager import SoundManager

class WordMasterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure Main Window
        self.title("WordMaster Pro – Interactive Guessing Arena")
        self.geometry("980x640")
        self.minimum_width = 900
        self.minimum_height = 580
        self.minsize(self.minimum_width, self.minimum_height)
        
        # Setup styling theme defaults
        ctk.set_default_color_theme("blue")
        ctk.set_appearance_mode("Dark") # Default is Dark mode
        
        self.sound_manager = SoundManager()
        self.current_user_id = None
        self.active_frame = None
        self.sidebar_frame = None
        
        self.show_auth_screen()
        
    def show_auth_screen(self):
        self.clear_active_frame()
        if self.sidebar_frame:
            self.sidebar_frame.destroy()
            self.sidebar_frame = None
            
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.active_frame = AuthFrame(
            self,
            on_login_success=self.on_login_success,
            fg_color="transparent"
        )
        self.active_frame.grid(row=0, column=0, sticky="nsew")
        
    def on_login_success(self, user_id):
        self.current_user_id = user_id
        self.show_main_app()
        
    def show_main_app(self):
        self.clear_active_frame()
        
        # Configure columns: 0 for Sidebar, 1 for Content
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.build_sidebar()
        self.switch_tab("Arena") # Default tab
        
    def build_sidebar(self):
        profile = db_manager.get_user_profile(self.current_user_id)
        
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight=1)
        
        # Profile Avatar Badge
        avatar_col = profile.get("avatar_color", "#3b82f6")
        self.avatar_canvas = ctk.CTkFrame(
            self.sidebar_frame, 
            width=60, 
            height=60, 
            corner_radius=30, 
            fg_color=avatar_col
        )
        self.avatar_canvas.grid(row=0, column=0, pady=(20, 5))
        
        self.lbl_username = ctk.CTkLabel(
            self.sidebar_frame,
            text=profile["username"].upper(),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_username.grid(row=1, column=0, pady=(0, 10))
        
        # Tabs
        self.btn_arena = ctk.CTkButton(
            self.sidebar_frame,
            text="🎮 Play Arena",
            height=40,
            corner_radius=8,
            command=lambda: self.switch_tab("Arena")
        )
        self.btn_arena.grid(row=2, column=0, padx=15, pady=5, sticky="ew")
        
        self.btn_dashboard = ctk.CTkButton(
            self.sidebar_frame,
            text="📊 Analytics",
            height=40,
            corner_radius=8,
            command=lambda: self.switch_tab("Dashboard")
        )
        self.btn_dashboard.grid(row=3, column=0, padx=15, pady=5, sticky="ew")
        
        self.btn_settings = ctk.CTkButton(
            self.sidebar_frame,
            text="⚙️ Settings",
            height=40,
            corner_radius=8,
            command=lambda: self.switch_tab("Settings")
        )
        self.btn_settings.grid(row=4, column=0, padx=15, pady=5, sticky="ew")
        
        # Mute indicator
        self.btn_mute = ctk.CTkButton(
            self.sidebar_frame,
            text="🔊 Sound: On",
            fg_color="transparent",
            border_width=1,
            border_color=("#cbd5e1", "#3f3f46"),
            height=30,
            command=self.toggle_mute
        )
        self.btn_mute.grid(row=6, column=0, padx=15, pady=5, sticky="ew")
        
        # Logout
        btn_logout = ctk.CTkButton(
            self.sidebar_frame,
            text="🚪 Log Out",
            fg_color="#ef4444",
            hover_color="#dc2626",
            height=35,
            command=self.logout
        )
        btn_logout.grid(row=7, column=0, padx=15, pady=(10, 20), sticky="s")
        
    def toggle_mute(self):
        is_muted = self.sound_manager.toggle_mute()
        self.sound_manager.play("click")
        if is_muted:
            self.btn_mute.configure(text="🔇 Muted", fg_color="#ef4444", text_color="#ffffff")
        else:
            self.btn_mute.configure(text="🔊 Sound: On", fg_color="transparent", text_color=("#1e293b", "#ffffff"))

    def update_sidebar_profile(self):
        if self.sidebar_frame:
            profile = db_manager.get_user_profile(self.current_user_id)
            if profile:
                self.avatar_canvas.configure(fg_color=profile.get("avatar_color", "#3b82f6"))
                self.lbl_username.configure(text=profile["username"].upper())

    def switch_tab(self, tab_name):
        self.sound_manager.play("click")
        self.clear_active_frame()
        
        # Manage active tab button style
        self.btn_arena.configure(fg_color=("#3b82f6" if tab_name == "Arena" else "#1f2937"))
        self.btn_dashboard.configure(fg_color=("#3b82f6" if tab_name == "Dashboard" else "#1f2937"))
        self.btn_settings.configure(fg_color=("#3b82f6" if tab_name == "Settings" else "#1f2937"))
        
        if tab_name == "Arena":
            self.active_frame = CategorySelectionFrame(
                self,
                user_id=self.current_user_id,
                on_start_game=self.start_standard_game,
                on_start_multiplayer=self.start_multiplayer_setup,
                on_start_daily=self.start_daily_challenge,
                fg_color="transparent"
            )
        elif tab_name == "Dashboard":
            self.active_frame = DashboardFrame(
                self,
                user_id=self.current_user_id,
                fg_color="transparent"
            )
        elif tab_name == "Settings":
            self.active_frame = self.build_settings_frame()
            
        self.active_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.update_sidebar_profile()
        
    def build_settings_frame(self):
        settings_frame = ctk.CTkFrame(self, fg_color="transparent")
        settings_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(settings_frame, text="Application Settings", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)
        
        # 1. Dark/Light Mode switch
        theme_card = ctk.CTkFrame(settings_frame, corner_radius=12)
        theme_card.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(theme_card, text="Appearance Theme", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=20, pady=15)
        
        theme_switch = ctk.CTkSwitch(
            theme_card,
            text="Dark Mode",
            command=self.toggle_theme_mode
        )
        theme_switch.pack(side="right", padx=20, pady=15)
        if ctk.get_appearance_mode() == "Dark":
            theme_switch.select()
            
        # 2. Sound Effects Settings
        sound_card = ctk.CTkFrame(settings_frame, corner_radius=12)
        sound_card.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(sound_card, text="Sound Effects Volume", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=20, pady=15)
        
        volume_slider = ctk.CTkSlider(
            sound_card,
            from_=0.0,
            to=1.0,
            command=self.set_volume
        )
        volume_slider.pack(side="right", padx=20, pady=15)
        volume_slider.set(self.sound_manager.volume)
        
        # 3. Avatar Color selection
        avatar_card = ctk.CTkFrame(settings_frame, corner_radius=12)
        avatar_card.pack(fill="x", padx=40, pady=10)
        
        ctk.CTkLabel(avatar_card, text="Select Avatar Color", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=20, pady=15)
        
        color_palette = ctk.CTkFrame(avatar_card, fg_color="transparent")
        color_palette.pack(side="right", padx=20, pady=15)
        
        colors = ["#3b82f6", "#10b981", "#ef4444", "#8b5cf6", "#eab308", "#ec4899"]
        for color in colors:
            btn = ctk.CTkButton(
                color_palette,
                text="",
                width=24,
                height=24,
                fg_color=color,
                hover_color=color,
                corner_radius=12,
                command=lambda c=color: self.change_avatar(c)
            )
            btn.pack(side="left", padx=3)
            
        return settings_frame
        
    def toggle_theme_mode(self):
        self.sound_manager.play("click")
        if ctk.get_appearance_mode() == "Dark":
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("Dark")
            
        # If there's an active hangman canvas, redraw it to fit theme
        if self.active_frame and hasattr(self.active_frame, 'update_theme'):
            self.active_frame.update_theme()
            
    def set_volume(self, val):
        self.sound_manager.set_volume(val)
        
    def change_avatar(self, color):
        self.sound_manager.play("click")
        db_manager.update_avatar_color(self.current_user_id, color)
        self.update_sidebar_profile()
        
    def clear_active_frame(self):
        if self.active_frame:
            # Safely unbind elements if gameplay
            if hasattr(self.active_frame, 'unbind_keyboard'):
                self.active_frame.unbind_keyboard()
            self.active_frame.grid_forget()
            self.active_frame.destroy()
            self.active_frame = None
            
    def start_standard_game(self, category, difficulty):
        self.clear_active_frame()
        # Hide sidebar to give full arena scale
        if self.sidebar_frame:
            self.sidebar_frame.grid_forget()
            
        self.grid_columnconfigure(0, weight=1) # Arena takes whole screen
        self.grid_columnconfigure(1, weight=0)
        
        self.active_frame = GameScreenFrame(
            self,
            user_id=self.current_user_id,
            category=category,
            difficulty=difficulty,
            mode="Standard",
            on_back_to_menu=self.show_main_app,
            fg_color="transparent"
        )
        self.active_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
    def start_multiplayer_setup(self, difficulty):
        self.clear_active_frame()
        self.active_frame = MultiplayerSetupFrame(
            self,
            difficulty=difficulty,
            on_launch_multiplayer=lambda w, h: self.launch_multiplayer_game(w, h, difficulty),
            on_cancel=lambda: self.switch_tab("Arena"),
            fg_color="transparent"
        )
        self.active_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
    def launch_multiplayer_game(self, word, hint, difficulty):
        self.clear_active_frame()
        if self.sidebar_frame:
            self.sidebar_frame.grid_forget()
            
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        
        self.active_frame = GameScreenFrame(
            self,
            user_id=self.current_user_id,
            category="Multiplayer",
            difficulty=difficulty,
            mode="Multiplayer",
            secret_word=word,
            secret_hint=hint,
            on_back_to_menu=self.show_main_app,
            fg_color="transparent"
        )
        self.active_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
    def start_daily_challenge(self):
        # Verify if user has already played today
        challenge, already_played = db_manager.verify_and_get_daily_challenge(self.current_user_id)
        if already_played:
            self.sound_manager.play("incorrect")
            ctk.CTkLabel(
                self.active_frame,
                text="❌ You have already played today's challenge!\nReturn tomorrow to continue your streak.",
                text_color="#ef4444",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(pady=10)
            return
            
        self.clear_active_frame()
        if self.sidebar_frame:
            self.sidebar_frame.grid_forget()
            
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        
        self.active_frame = GameScreenFrame(
            self,
            user_id=self.current_user_id,
            category=challenge["category"],
            difficulty="Medium",
            mode="Daily Challenge",
            on_back_to_menu=self.show_main_app,
            fg_color="transparent"
        )
        self.active_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
    def logout(self):
        self.sound_manager.play("click")
        self.current_user_id = None
        self.show_auth_screen()
