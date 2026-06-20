import random

class HintGenerator:
    @staticmethod
    def get_ai_hint(word, db_hint):
        """
        Constructs a structured, engaging hint description (AI-like) using the word structure and the DB hint.
        """
        word_clean = word.strip().lower()
        length = len(word_clean)
        first_letter = word_clean[0].upper()
        last_letter = word_clean[-1].upper()
        
        vowels = "aeiou"
        vowel_count = sum(1 for char in word_clean if char in vowels)
        consonant_count = length - vowel_count
        
        ai_templates = [
            f"🧠 [AI CLUE] I am a {length}-letter word. I begin with '{first_letter}' and end with '{last_letter}'. Vowels count: {vowel_count}. Riddle: {db_hint}",
            f"🤖 [AI ANALYZER] Structural breakdown: Length = {length}, Consonants = {consonant_count}. Starting letter: '{first_letter}'. Definition: {db_hint}",
            f"🔮 [AI PREDICTED] HINT: {db_hint}. (Technical signature: {length} chars, starts with '{first_letter}', contains {vowel_count} vowels)"
        ]
        
        return random.choice(ai_templates)

    @staticmethod
    def reveal_random_letter(word, revealed_letters):
        """
        Returns a random letter from the word that has not been revealed yet.
        word: str
        revealed_letters: set/list of chars currently guessed correctly
        """
        word_clean = word.lower()
        unrevealed = [char for char in word_clean if char.isalpha() and char not in revealed_letters]
        
        if unrevealed:
            return random.choice(unrevealed)
        return None
