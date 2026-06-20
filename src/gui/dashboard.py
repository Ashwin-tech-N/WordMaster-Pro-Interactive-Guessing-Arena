import customtkinter as ctk
import tkinter as tk
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from database import db_manager
from utils.sound_manager import SoundManager

class DashboardFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, user_id, **kwargs):
        super().__init__(parent, **kwargs)
        self.user_id = user_id
        self.sound_manager = SoundManager()
        
        self.grid_columnconfigure(0, weight=3) # Statistics & Achievements
        self.grid_columnconfigure(1, weight=2) # Leaderboards & Recent games
        
        self.refresh()
        
    def refresh(self):
        # Clear previous UI
        for child in self.winfo_children():
            child.destroy()
            
        # Get latest data
        self.analytics = db_manager.get_user_analytics(self.user_id)
        self.profile = db_manager.get_user_profile(self.user_id)
        self.achievements = db_manager.get_user_achievements(self.user_id)
        self.leaderboard = db_manager.get_leaderboard()
        
        self.build_left_column()
        self.build_right_column()
        
    def build_left_column(self):
        # Container for Left widgets
        left_container = ctk.CTkFrame(self, fg_color="transparent")
        left_container.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        left_container.grid_columnconfigure(0, weight=1)
        
        # 1. Profile Summary Card
        profile_card = ctk.CTkFrame(left_container, corner_radius=12)
        profile_card.grid(row=0, column=0, pady=10, sticky="ew")
        profile_card.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Name
        name_label = ctk.CTkLabel(
            profile_card, 
            text=f"👤 {self.profile['username'].upper()}", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        name_label.grid(row=0, column=0, padx=15, pady=20, sticky="w")
        
        # Coins
        coins_label = ctk.CTkLabel(
            profile_card,
            text=f"🪙 Coins: {self.profile['coins']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#eab308"
        )
        coins_label.grid(row=0, column=1, padx=15, pady=20)
        
        # Streak
        streak_label = ctk.CTkLabel(
            profile_card,
            text=f"🔥 Streak: {self.profile['daily_streak']} days",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f97316"
        )
        streak_label.grid(row=0, column=2, padx=15, pady=20)
        
        # Win Rate
        wr_label = ctk.CTkLabel(
            profile_card,
            text=f"📈 Win Rate: {self.analytics['win_rate']}%",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#10b981"
        )
        wr_label.grid(row=0, column=3, padx=15, pady=20, sticky="e")
        
        # 2. Stats Dashboard (Cards Grid)
        stats_frame = ctk.CTkFrame(left_container, fg_color="transparent")
        stats_frame.grid(row=1, column=0, pady=10, sticky="ew")
        stats_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Win Loss Ratio Pie/Donut Chart Canvas
        chart_card = ctk.CTkFrame(stats_frame, corner_radius=12)
        chart_card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        chart_card.grid_columnconfigure(0, weight=1)
        
        chart_title = ctk.CTkLabel(chart_card, text="Win / Loss Analysis", font=ctk.CTkFont(size=14, weight="bold"))
        chart_title.pack(pady=10)
        
        canvas = tk.Canvas(chart_card, width=150, height=150, bg=self._get_card_bg(), highlightthickness=0)
        canvas.pack(pady=5)
        self.draw_donut_chart(canvas, self.analytics["games_won"], self.analytics["games_lost"])
        
        legend_frame = ctk.CTkFrame(chart_card, fg_color="transparent")
        legend_frame.pack(pady=10)
        
        win_dot = ctk.CTkLabel(legend_frame, text="■ Won", text_color="#10b981", font=ctk.CTkFont(size=12, weight="bold"))
        win_dot.pack(side="left", padx=10)
        loss_dot = ctk.CTkLabel(legend_frame, text="■ Lost", text_color="#ef4444", font=ctk.CTkFont(size=12, weight="bold"))
        loss_dot.pack(side="left", padx=10)
        
        # Difficulty Stats
        diff_card = ctk.CTkFrame(stats_frame, corner_radius=12)
        diff_card.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        diff_card.grid_columnconfigure(0, weight=1)
        
        diff_title = ctk.CTkLabel(diff_card, text="Performance by Difficulty", font=ctk.CTkFont(size=14, weight="bold"))
        diff_title.pack(pady=10)
        
        diff_data = self.analytics["difficulty_dist"]
        for diff in ["Easy", "Medium", "Hard"]:
            data = diff_data.get(diff, {"played": 0, "wins": 0})
            played = data["played"]
            wins = data["wins"]
            rate = int((wins / played) * 100) if played > 0 else 0
            
            bar_frame = ctk.CTkFrame(diff_card, fg_color="transparent")
            bar_frame.pack(fill="x", padx=15, pady=5)
            
            label_row = ctk.CTkFrame(bar_frame, fg_color="transparent")
            label_row.pack(fill="x")
            
            ctk.CTkLabel(label_row, text=diff, font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
            ctk.CTkLabel(label_row, text=f"{wins}/{played} ({rate}%)", font=ctk.CTkFont(size=11)).pack(side="right")
            
            # Progress Bar representing rate
            pbar = ctk.CTkProgressBar(bar_frame, height=8, corner_radius=4)
            pbar.pack(fill="x", pady=2)
            pbar.set(rate / 100.0)
            if diff == "Easy": pbar.configure(progress_color="#10b981")
            elif diff == "Medium": pbar.configure(progress_color="#eab308")
            else: pbar.configure(progress_color="#ef4444")
            
        # 3. Achievement Cabinet
        ach_title_label = ctk.CTkLabel(
            left_container, 
            text="Achievements Trophy Room", 
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        ach_title_label.grid(row=2, column=0, pady=(20, 5), sticky="w")
        
        ach_grid = ctk.CTkFrame(left_container, fg_color="transparent")
        ach_grid.grid(row=3, column=0, pady=5, sticky="ew")
        ach_grid.grid_columnconfigure((0, 1), weight=1)
        
        for idx, ach in enumerate(self.achievements):
            unlocked = ach["unlocked"]
            bg = "#1e293b" if unlocked else "#0f172a"
            border_color = "#3b82f6" if unlocked else "#334155"
            
            # Subframe card for each achievement
            ach_card = ctk.CTkFrame(
                ach_grid,
                corner_radius=10,
                border_width=1 if unlocked else 0,
                border_color=border_color
            )
            
            # Adjust opacity style visually
            row_idx = idx // 2
            col_idx = idx % 2
            ach_card.grid(row=row_idx, column=col_idx, padx=5, pady=5, sticky="nsew")
            ach_card.grid_columnconfigure(1, weight=1)
            
            icon_lbl = ctk.CTkLabel(
                ach_card,
                text=ach["badge_icon"] if unlocked else "🔒",
                font=ctk.CTkFont(size=28)
            )
            icon_lbl.grid(row=0, column=0, padx=10, pady=10)
            
            lbl_container = ctk.CTkFrame(ach_card, fg_color="transparent")
            lbl_container.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ew")
            
            title = ctk.CTkLabel(
                lbl_container,
                text=ach["name"],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=("#1e293b", "#ffffff") if unlocked else ("#94a3b8", "#64748b"),
                anchor="w"
            )
            title.pack(anchor="w")
            
            desc = ctk.CTkLabel(
                lbl_container,
                text=ach["description"],
                font=ctk.CTkFont(size=11),
                text_color=("#475569", "#cbd5e1") if unlocked else ("#cbd5e1", "#475569"),
                anchor="w"
            )
            desc.pack(anchor="w")

    def build_right_column(self):
        # Container for Right widgets
        right_container = ctk.CTkFrame(self, fg_color="transparent")
        right_container.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        right_container.grid_columnconfigure(0, weight=1)
        
        # 1. Leaderboard panel
        leaderboard_title = ctk.CTkLabel(
            right_container,
            text="🏆 Global Hall of Fame",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        leaderboard_title.grid(row=0, column=0, pady=(10, 5), sticky="w")
        
        leaderboard_card = ctk.CTkFrame(right_container, corner_radius=12)
        leaderboard_card.grid(row=1, column=0, pady=5, sticky="ew")
        
        if not self.leaderboard:
            empty_lbl = ctk.CTkLabel(leaderboard_card, text="No scores recorded yet.", font=ctk.CTkFont(slant="italic"))
            empty_lbl.pack(pady=20)
        else:
            for idx, entry in enumerate(self.leaderboard):
                username = entry["username"]
                score = entry["total_score"]
                wins = entry["games_won"]
                played = entry["games_played"]
                
                is_current = (username == self.profile["username"])
                bg_col = "#3b82f6" if is_current else "transparent"
                text_col = "#ffffff" if is_current else None
                
                row_frame = ctk.CTkFrame(leaderboard_card, fg_color=bg_col, corner_radius=6)
                row_frame.pack(fill="x", padx=10, pady=3)
                
                rank = idx + 1
                medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"  {rank} "
                
                rank_lbl = ctk.CTkLabel(row_frame, text=medal, font=ctk.CTkFont(size=14, weight="bold"), text_color=text_col)
                rank_lbl.pack(side="left", padx=(10, 5), pady=5)
                
                name_lbl = ctk.CTkLabel(row_frame, text=username, font=ctk.CTkFont(size=13, weight="bold" if is_current else "normal"), text_color=text_col)
                name_lbl.pack(side="left", padx=5, pady=5)
                
                score_lbl = ctk.CTkLabel(row_frame, text=f"{score} pts (Win: {wins}/{played})", font=ctk.CTkFont(size=12, weight="bold"), text_color="#eab308" if not is_current else "#ffffff")
                score_lbl.pack(side="right", padx=10, pady=5)
                
        # 2. Recent games log
        log_title = ctk.CTkLabel(
            right_container,
            text="⏳ Battle History (Last 5)",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        log_title.grid(row=2, column=0, pady=(20, 5), sticky="w")
        
        log_card = ctk.CTkFrame(right_container, corner_radius=12)
        log_card.grid(row=3, column=0, pady=5, sticky="ew")
        
        recent = self.analytics["recent_games"]
        if not recent:
            empty_lbl = ctk.CTkLabel(log_card, text="Play a game to see your history!", font=ctk.CTkFont(slant="italic"))
            empty_lbl.pack(pady=20)
        else:
            for game in recent:
                win = game["win"]
                cat = game["category"]
                diff = game["difficulty"]
                score = game["score"]
                left = game["attempts_left"]
                
                # Strip dates to only readable time
                try:
                    dt = datetime.strptime(game["played_at"], "%Y-%m-%d %H:%M:%S")
                    date_str = dt.strftime("%b %d, %H:%M")
                except Exception:
                    date_str = game["played_at"][:16]
                
                row_frame = ctk.CTkFrame(log_card, fg_color="transparent")
                row_frame.pack(fill="x", padx=10, pady=5)
                
                # Win/Loss status dot
                status_color = "#10b981" if win else "#ef4444"
                status_txt = "WIN" if win else "LOSS"
                badge = ctk.CTkLabel(
                    row_frame,
                    text=status_txt,
                    font=ctk.CTkFont(size=10, weight="bold"),
                    text_color="#ffffff",
                    fg_color=status_color,
                    corner_radius=4,
                    width=45,
                    height=20
                )
                badge.pack(side="left", padx=5)
                
                info_lbl = ctk.CTkLabel(
                    row_frame, 
                    text=f"{cat} ({diff})",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    anchor="w"
                )
                info_lbl.pack(side="left", padx=10)
                
                right_info = ctk.CTkLabel(
                    row_frame,
                    text=f"+{score} pts  |  {date_str}",
                    font=ctk.CTkFont(size=11),
                    text_color="#64748b",
                    anchor="e"
                )
                right_info.pack(side="right", padx=5)
                
                # Bottom separator
                sep = ctk.CTkFrame(log_card, height=1, fg_color=("#e2e8f0", "#334155"))
                sep.pack(fill="x", padx=10)

    def draw_donut_chart(self, canvas, wins, losses):
        canvas.delete("all")
        
        # Calculations
        total = wins + losses
        if total == 0:
            # Draw placeholder grey donut
            canvas.create_arc(10, 10, 140, 140, start=0, extent=359.9, fill="#94a3b8", outline="")
            canvas.create_oval(35, 35, 115, 115, fill=self._get_card_bg(), outline="")
            canvas.create_text(75, 75, text="No Games", font=("Helvetica", 12, "bold"), fill="#64748b")
            return
            
        win_angle = (wins / total) * 360
        loss_angle = (losses / total) * 360
        
        # Draw arcs
        # Win arc (green)
        canvas.create_arc(10, 10, 140, 140, start=90, extent=win_angle, fill="#10b981", outline="")
        # Loss arc (red)
        canvas.create_arc(10, 10, 140, 140, start=90 + win_angle, extent=loss_angle, fill="#ef4444", outline="")
        
        # Donut inner mask
        canvas.create_oval(35, 35, 115, 115, fill=self._get_card_bg(), outline="")
        
        # Display central percentage text
        win_rate = int((wins / total) * 100)
        # Choose text color based on win rate
        text_col = "#10b981" if win_rate > 50 else "#f97316" if win_rate > 30 else "#ef4444"
        canvas.create_text(75, 68, text=f"{win_rate}%", font=("Helvetica", 18, "bold"), fill=text_col)
        canvas.create_text(75, 88, text="W/L ratio", font=("Helvetica", 9), fill="#64748b")
        
    def _get_card_bg(self):
        mode = ctk.get_appearance_mode()
        if mode == "Dark":
            return "#2b2b2b" # CustomTkinter card background in dark mode
        else:
            return "#dbdbdb" # CustomTkinter card background in light mode
