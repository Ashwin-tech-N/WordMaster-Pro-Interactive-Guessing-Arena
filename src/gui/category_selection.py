import customtkinter as ctk
from tkinter import filedialog, messagebox
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from database import db_manager
from utils.sound_manager import SoundManager

class CategorySelectionFrame(ctk.CTkFrame):
    def __init__(self, parent, user_id, on_start_game, on_start_multiplayer, on_start_daily, **kwargs):
        super().__init__(parent, **kwargs)
        self.user_id = user_id
        self.on_start_game = on_start_game
        self.on_start_multiplayer = on_start_multiplayer
        self.on_start_daily = on_start_daily
        self.sound_manager = SoundManager()
        
        self.selected_category = "All"
        self.selected_difficulty = "Medium"
        self.selected_mode = "Standard" # Standard, Daily, Multiplayer
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        
        self.build_ui()
        
    def refresh_custom_categories(self):
        custom_cats = db_manager.get_custom_categories(self.user_id)
        
        # Reset the option menu or list
        if hasattr(self, 'custom_cats_list') and hasattr(self, 'category_option'):
            current_options = ["All", "Technology", "Sports", "Movies", "Science", "General Knowledge"]
            current_options.extend(custom_cats)
            self.category_option.configure(values=current_options)
            
            # Rebuild custom category list frame
            for child in self.custom_cats_list.winfo_children():
                child.destroy()
                
            if not custom_cats:
                ctk.CTkLabel(self.custom_cats_list, text="No custom packs imported.", font=ctk.CTkFont(slant="italic")).pack(pady=10)
            else:
                for cat in custom_cats:
                    row = ctk.CTkFrame(self.custom_cats_list, fg_color="transparent")
                    row.pack(fill="x", pady=2, padx=5)
                    ctk.CTkLabel(row, text=f"📂 {cat}", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
                    
                    del_btn = ctk.CTkButton(
                        row, 
                        text="Delete", 
                        width=60, 
                        height=20, 
                        fg_color="#ef4444", 
                        hover_color="#dc2626",
                        command=lambda c=cat: self.delete_custom_pack(c)
                    )
                    del_btn.pack(side="right")

    def build_ui(self):
        # 1. Main Title
        header_lbl = ctk.CTkLabel(
            self,
            text="Set Up Your Arena",
            font=ctk.CTkFont(family="Helvetica", size=24, weight="bold")
        )
        header_lbl.pack(pady=(20, 10))
        
        # Split layout: Settings on Left, Custom Packs on Right
        split_frame = ctk.CTkFrame(self, fg_color="transparent")
        split_frame.pack(fill="both", expand=True, padx=20, pady=10)
        split_frame.grid_columnconfigure(0, weight=3) # Configuration
        split_frame.grid_columnconfigure(1, weight=2) # Word packs
        
        # Config Panel (Left)
        config_panel = ctk.CTkFrame(split_frame, corner_radius=12)
        config_panel.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="nsew")
        config_panel.grid_columnconfigure(0, weight=1)
        
        # A. Mode Selection
        ctk.CTkLabel(config_panel, text="Choose Game Mode", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        
        self.mode_segmented = ctk.CTkSegmentedButton(
            config_panel,
            values=["Standard", "Daily Challenge", "Multiplayer"],
            command=self.on_mode_change
        )
        self.mode_segmented.pack(fill="x", padx=20, pady=5)
        self.mode_segmented.set("Standard")
        
        # B. Category Choice
        self.cat_label = ctk.CTkLabel(config_panel, text="Select Category", font=ctk.CTkFont(size=14, weight="bold"))
        self.cat_label.pack(pady=(15, 5))
        
        default_cats = ["All", "Technology", "Sports", "Movies", "Science", "General Knowledge"]
        self.category_option = ctk.CTkOptionMenu(
            config_panel,
            values=default_cats,
            command=self.set_category
        )
        self.category_option.pack(fill="x", padx=20, pady=5)
        self.category_option.set("All")
        
        # C. Difficulty Choice
        self.diff_label = ctk.CTkLabel(config_panel, text="Select Difficulty", font=ctk.CTkFont(size=14, weight="bold"))
        self.diff_label.pack(pady=(15, 5))
        
        self.diff_segmented = ctk.CTkSegmentedButton(
            config_panel,
            values=["Easy", "Medium", "Hard"],
            command=self.set_difficulty
        )
        self.diff_segmented.pack(fill="x", padx=20, pady=5)
        self.diff_segmented.set("Medium")
        
        # D. Play CTA
        self.play_btn = ctk.CTkButton(
            config_panel,
            text="⚡ ENTER ARENA ⚡",
            font=ctk.CTkFont(size=18, weight="bold"),
            height=50,
            corner_radius=8,
            command=self.start_game
        )
        self.play_btn.pack(fill="x", padx=20, pady=30)
        
        # Custom Packs Panel (Right)
        packs_panel = ctk.CTkFrame(split_frame, corner_radius=12)
        packs_panel.grid(row=0, column=1, padx=(10, 0), pady=10, sticky="nsew")
        packs_panel.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(packs_panel, text="Custom Word Packs", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        
        import_btn = ctk.CTkButton(
            packs_panel,
            text="📥 Import Word Pack (TXT/JSON)",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.import_word_pack
        )
        import_btn.pack(fill="x", padx=15, pady=5)
        
        desc_lbl = ctk.CTkLabel(
            packs_panel,
            text="TXT Format: one word per line (word,category,difficulty,hint)\nJSON Format: a list of objects with those properties.",
            font=ctk.CTkFont(size=10),
            text_color="#64748b",
            justify="left",
            wraplength=200
        )
        desc_lbl.pack(pady=5, padx=15)
        
        # Divider line
        ctk.CTkFrame(packs_panel, height=1, fg_color=("#cbd5e1", "#334155")).pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(packs_panel, text="Your Custom Packs", font=ctk.CTkFont(size=12, weight="bold")).pack(pady=2)
        
        self.custom_cats_list = ctk.CTkScrollableFrame(packs_panel, height=180)
        self.custom_cats_list.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        self.refresh_custom_categories()
        
    def on_mode_change(self, mode):
        self.sound_manager.play("click")
        self.selected_mode = mode
        
        # Manage widget availability depending on game mode
        if mode == "Daily Challenge":
            self.category_option.configure(state="disabled")
            self.diff_segmented.configure(state="disabled")
            self.cat_label.configure(text_color="#64748b")
            self.diff_label.configure(text_color="#64748b")
        elif mode == "Multiplayer":
            self.category_option.configure(state="disabled")
            self.diff_segmented.configure(state="normal")
            self.cat_label.configure(text_color="#64748b")
            self.diff_label.configure(text_color=("#1e293b", "#ffffff"))
        else: # Standard
            self.category_option.configure(state="normal")
            self.diff_segmented.configure(state="normal")
            self.cat_label.configure(text_color=("#1e293b", "#ffffff"))
            self.diff_label.configure(text_color=("#1e293b", "#ffffff"))
            
    def set_category(self, cat):
        self.sound_manager.play("click")
        self.selected_category = cat
        
    def set_difficulty(self, diff):
        self.sound_manager.play("click")
        self.selected_difficulty = diff
        
    def start_game(self):
        self.sound_manager.play("click")
        if self.selected_mode == "Standard":
            self.on_start_game(self.selected_category, self.selected_difficulty)
        elif self.selected_mode == "Multiplayer":
            self.on_start_multiplayer(self.selected_difficulty)
        else: # Daily Challenge
            self.on_start_daily()
            
    def import_word_pack(self):
        self.sound_manager.play("click")
        file_path = filedialog.askopenfilename(
            title="Import Word Pack",
            filetypes=[("Text & JSON Files", "*.txt *.json"), ("Text Files", "*.txt"), ("JSON Files", "*.json")]
        )
        if not file_path:
            return
            
        words_to_import = []
        try:
            filename = os.path.basename(file_path)
            if filename.endswith(".json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            words_to_import.append({
                                "word": item.get("word", ""),
                                "category": item.get("category", "Custom"),
                                "difficulty": item.get("difficulty", "Medium"),
                                "hint": item.get("hint", "")
                            })
                    else:
                        raise ValueError("JSON file must contain a list of objects.")
            else: # Text format
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        parts = line.split(",")
                        if len(parts) >= 2:
                            word = parts[0].strip()
                            category = parts[1].strip() if len(parts) >= 2 else "Custom"
                            difficulty = parts[2].strip() if len(parts) >= 3 else "Medium"
                            hint = parts[3].strip() if len(parts) >= 4 else f"A word related to {category}"
                            
                            words_to_import.append({
                                "word": word,
                                "category": category,
                                "difficulty": difficulty,
                                "hint": hint
                            })
            
            if not words_to_import:
                messagebox.showerror("Import Error", "No valid words found in file.")
                self.sound_manager.play("incorrect")
                return
                
            success, count = db_manager.import_custom_words(self.user_id, words_to_import)
            if success:
                messagebox.showinfo("Success", f"Successfully imported {count} words!")
                self.sound_manager.play("correct")
                self.refresh_custom_categories()
            else:
                messagebox.showerror("Database Error", f"Failed to save to database: {count}")
                self.sound_manager.play("incorrect")
                
        except Exception as e:
            messagebox.showerror("Parsing Error", f"Could not parse file: {e}")
            self.sound_manager.play("incorrect")

    def delete_custom_pack(self, category):
        self.sound_manager.play("click")
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the custom pack: '{category}'?")
        if confirm:
            success = db_manager.delete_custom_category(self.user_id, category)
            if success:
                self.sound_manager.play("correct")
                self.refresh_custom_categories()
            else:
                self.sound_manager.play("incorrect")
                messagebox.showerror("Error", "Could not delete custom category.")
