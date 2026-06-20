import tkinter as tk
import customtkinter as ctk

class CanvasHangman(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.canvas = tk.Canvas(
            self,
            bg=self._get_bg_color(),
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Color palettes
        self.colors = {
            "gallows_glow": "#1e293b",
            "gallows": "#64748b",
            "rope": "#d97706",
            "rope_glow": "#fef3c7",
            "neon_cyan": "#06b6d4",
            "neon_cyan_glow": "#22d3ee",
            "neon_orange": "#ea580c",
            "neon_orange_glow": "#ffedd5",
            "neon_red": "#ef4444",
            "neon_red_glow": "#fee2e2",
            "white": "#ffffff"
        }
        
        self.difficulty = "Medium"
        self.attempts_left = 6
        self.max_attempts = 6
        
        self.bind("<Configure>", self.on_resize)
        
    def _get_bg_color(self):
        # Dynamically determine the theme color
        mode = ctk.get_appearance_mode()
        if mode == "Dark":
            return "#1e293b" # Slate 800
        else:
            return "#f8fafc" # Slate 50
            
    def update_theme(self):
        self.canvas.configure(bg=self._get_bg_color())
        self.draw()
        
    def set_state(self, difficulty, attempts_left):
        self.difficulty = difficulty
        self.attempts_left = attempts_left
        
        if difficulty == "Easy":
            self.max_attempts = 8
        elif difficulty == "Medium":
            self.max_attempts = 6
        else:
            self.max_attempts = 4
            
        self.draw()
        
    def on_resize(self, event):
        self.draw()
        
    def draw_glow_line(self, x1, y1, x2, y2, color, glow_color, width=4):
        # Draw soft glow behind
        self.canvas.create_line(x1, y1, x2, y2, fill=glow_color, width=width+4, capstyle="round")
        # Draw sharp bright line in front
        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, capstyle="round")

    def draw_glow_oval(self, x1, y1, x2, y2, color, glow_color, width=4):
        # Draw soft glow behind
        self.canvas.create_oval(x1, y1, x2, y2, outline=glow_color, width=width+4)
        # Draw sharp bright oval in front
        self.canvas.create_oval(x1, y1, x2, y2, outline=color, width=width)

    def draw(self):
        self.canvas.delete("all")
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Fallback dimensions if canvas not fully rendered yet
        if w < 50 or h < 50:
            w = 300
            h = 300
            
        # Scale drawing coordinates to fit container
        scale_x = w / 300.0
        scale_y = h / 300.0
        
        # Choose neon color based on health/attempts left
        percent_left = self.attempts_left / self.max_attempts
        if percent_left > 0.6:
            char_color = self.colors["neon_cyan"]
            char_glow = self.colors["neon_cyan_glow"]
        elif percent_left > 0.3:
            char_color = self.colors["neon_orange"]
            char_glow = self.colors["neon_orange_glow"]
        else:
            char_color = self.colors["neon_red"]
            char_glow = self.colors["neon_red_glow"]
            
        mistakes = self.max_attempts - self.attempts_left
        
        # Standard structural layout positions
        base_y = 260 * scale_y
        gallows_x = 70 * scale_x
        top_y = 40 * scale_y
        beam_x = 180 * scale_x
        rope_y = 80 * scale_y
        
        # 1. Base Stand (always visible as context)
        self.draw_glow_line(30 * scale_x, base_y, 150 * scale_x, base_y, self.colors["gallows"], self.colors["gallows_glow"], width=6)
        
        # 2. Vertical Pole (always visible)
        self.draw_glow_line(gallows_x, base_y, gallows_x, top_y, self.colors["gallows"], self.colors["gallows_glow"], width=6)
        
        # 3. Horizontal Beam (always visible)
        self.draw_glow_line(gallows_x, top_y, beam_x, top_y, self.colors["gallows"], self.colors["gallows_glow"], width=6)
        
        # 4. Diagonal Brace (always visible)
        self.draw_glow_line(gallows_x, top_y + 40*scale_y, gallows_x + 40*scale_x, top_y, self.colors["gallows"], self.colors["gallows_glow"], width=4)
        
        # 5. Rope (always visible, dangling)
        self.draw_glow_line(beam_x, top_y, beam_x, rope_y, self.colors["rope"], self.colors["rope_glow"], width=3)
        
        # Depending on mistakes, draw parts of the body
        if self.difficulty == "Easy":
            # 8 Attempts
            if mistakes >= 1: # Head
                self.draw_glow_oval(beam_x - 18*scale_x, rope_y, beam_x + 18*scale_x, rope_y + 36*scale_y, char_color, char_glow, width=3)
            if mistakes >= 2: # Neck & Spine/Body
                self.draw_glow_line(beam_x, rope_y + 36*scale_y, beam_x, rope_y + 110*scale_y, char_color, char_glow, width=4)
            if mistakes >= 3: # Left Arm
                self.draw_glow_line(beam_x, rope_y + 50*scale_y, beam_x - 35*scale_x, rope_y + 80*scale_y, char_color, char_glow, width=3)
            if mistakes >= 4: # Right Arm
                self.draw_glow_line(beam_x, rope_y + 50*scale_y, beam_x + 35*scale_x, rope_y + 80*scale_y, char_color, char_glow, width=3)
            if mistakes >= 5: # Left Leg
                self.draw_glow_line(beam_x, rope_y + 110*scale_y, beam_x - 30*scale_x, rope_y + 170*scale_y, char_color, char_glow, width=3)
            if mistakes >= 6: # Right Leg
                self.draw_glow_line(beam_x, rope_y + 110*scale_y, beam_x + 30*scale_x, rope_y + 170*scale_y, char_color, char_glow, width=3)
            if mistakes >= 7: # Face Details (X eyes for dead/dying)
                # Left eye
                self.draw_glow_line(beam_x - 7*scale_x, rope_y + 13*scale_y, beam_x - 3*scale_x, rope_y + 17*scale_y, char_color, char_glow, width=2)
                self.draw_glow_line(beam_x - 3*scale_x, rope_y + 13*scale_y, beam_x - 7*scale_x, rope_y + 17*scale_y, char_color, char_glow, width=2)
                # Right eye
                self.draw_glow_line(beam_x + 3*scale_x, rope_y + 13*scale_y, beam_x + 7*scale_x, rope_y + 17*scale_y, char_color, char_glow, width=2)
                self.draw_glow_line(beam_x + 7*scale_x, rope_y + 13*scale_y, beam_x + 3*scale_x, rope_y + 17*scale_y, char_color, char_glow, width=2)
            if mistakes >= 8: # Frown/Sad mouth
                self.canvas.create_arc(beam_x - 8*scale_x, rope_y + 20*scale_y, beam_x + 8*scale_x, rope_y + 32*scale_y, start=0, extent=180, style="arc", outline=char_color, width=2)
                
        elif self.difficulty == "Medium":
            # 6 Attempts
            if mistakes >= 1: # Head
                self.draw_glow_oval(beam_x - 18*scale_x, rope_y, beam_x + 18*scale_x, rope_y + 36*scale_y, char_color, char_glow, width=3)
            if mistakes >= 2: # Body
                self.draw_glow_line(beam_x, rope_y + 36*scale_y, beam_x, rope_y + 110*scale_y, char_color, char_glow, width=4)
            if mistakes >= 3: # Left Arm
                self.draw_glow_line(beam_x, rope_y + 50*scale_y, beam_x - 35*scale_x, rope_y + 80*scale_y, char_color, char_glow, width=3)
            if mistakes >= 4: # Right Arm
                self.draw_glow_line(beam_x, rope_y + 50*scale_y, beam_x + 35*scale_x, rope_y + 80*scale_y, char_color, char_glow, width=3)
            if mistakes >= 5: # Left Leg
                self.draw_glow_line(beam_x, rope_y + 110*scale_y, beam_x - 30*scale_x, rope_y + 170*scale_y, char_color, char_glow, width=3)
            if mistakes >= 6: # Right Leg & Dead Face
                self.draw_glow_line(beam_x, rope_y + 110*scale_y, beam_x + 30*scale_x, rope_y + 170*scale_y, char_color, char_glow, width=3)
                # Dead Eyes (X X)
                self.draw_glow_line(beam_x - 7*scale_x, rope_y + 13*scale_y, beam_x - 3*scale_x, rope_y + 17*scale_y, char_color, char_glow, width=2)
                self.draw_glow_line(beam_x - 3*scale_x, rope_y + 13*scale_y, beam_x - 7*scale_x, rope_y + 17*scale_y, char_color, char_glow, width=2)
                self.draw_glow_line(beam_x + 3*scale_x, rope_y + 13*scale_y, beam_x + 7*scale_x, rope_y + 17*scale_y, char_color, char_glow, width=2)
                self.draw_glow_line(beam_x + 7*scale_x, rope_y + 13*scale_y, beam_x + 3*scale_x, rope_y + 17*scale_y, char_color, char_glow, width=2)
                # Mouth
                self.canvas.create_arc(beam_x - 8*scale_x, rope_y + 20*scale_y, beam_x + 8*scale_x, rope_y + 32*scale_y, start=0, extent=180, style="arc", outline=char_color, width=2)
                
        else:
            # Hard: 4 Attempts
            if mistakes >= 1: # Head & Neck
                self.draw_glow_oval(beam_x - 18*scale_x, rope_y, beam_x + 18*scale_x, rope_y + 36*scale_y, char_color, char_glow, width=3)
            if mistakes >= 2: # Body & Left Arm
                self.draw_glow_line(beam_x, rope_y + 36*scale_y, beam_x, rope_y + 110*scale_y, char_color, char_glow, width=4)
                self.draw_glow_line(beam_x, rope_y + 50*scale_y, beam_x - 35*scale_x, rope_y + 80*scale_y, char_color, char_glow, width=3)
            if mistakes >= 3: # Right Arm & Left Leg
                self.draw_glow_line(beam_x, rope_y + 50*scale_y, beam_x + 35*scale_x, rope_y + 80*scale_y, char_color, char_glow, width=3)
                self.draw_glow_line(beam_x, rope_y + 110*scale_y, beam_x - 30*scale_x, rope_y + 170*scale_y, char_color, char_glow, width=3)
            if mistakes >= 4: # Right Leg & Dead Face
                self.draw_glow_line(beam_x, rope_y + 110*scale_y, beam_x + 30*scale_x, rope_y + 170*scale_y, char_color, char_glow, width=3)
                # Dead Eyes (X X)
                self.draw_glow_line(beam_x - 7*scale_x, rope_y + 13*scale_y, beam_x - 3*scale_x, rope_y + 17*scale_y, char_color, char_glow, width=2)
                self.draw_glow_line(beam_x - 3*scale_x, rope_y + 13*scale_y, beam_x - 7*scale_x, rope_y + 17*scale_y, char_color, char_glow, width=2)
                self.draw_glow_line(beam_x + 3*scale_x, rope_y + 13*scale_y, beam_x + 7*scale_x, rope_y + 17*scale_y, char_color, char_glow, width=2)
                self.draw_glow_line(beam_x + 7*scale_x, rope_y + 13*scale_y, beam_x + 3*scale_x, rope_y + 17*scale_y, char_color, char_glow, width=2)
                # Mouth
                self.canvas.create_arc(beam_x - 8*scale_x, rope_y + 20*scale_y, beam_x + 8*scale_x, rope_y + 32*scale_y, start=0, extent=180, style="arc", outline=char_color, width=2)
