import os
import sys

# Ensure project folders are in the Python search path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database import db_manager
from utils.sound_manager import SoundManager
from gui.app import WordMasterApp

def main():
    print("Initializing WordMaster Pro...")
    
    # 1. Initialize SQLite Database schemas and built-in seeds
    db_manager.init_db()
    
    # 2. Check and generate WAV sound assets
    print("Checking audio assets...")
    SoundManager() # Instantiating generates default WAV sounds if missing
    
    # 3. Boot GUI application
    print("Launching interface...")
    app = WordMasterApp()
    app.mainloop()

if __name__ == "__main__":
    main()
