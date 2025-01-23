from base.assoc import Assoc
from base.constants import Team
from base.spymaster import BaseSpymaster

from itertools import combinations
import requests
import json
from pprint import pprint

url = "http://localhost:11434/api/chat"

codenames_intro = """We are playing a game of Codenames. Here are the rules:

**Objective:**
Guess the location of words on a grid based on one-word clues given by your 
teammate.

**Gameplay:**
1. Each team chooses a Spymaster and Field Agents.
2. The Spymasters take turns giving one-word clues that relate to multiple words on the 
grid.
3. Field Agents try to find the correct words on the grid based on their Spymaster's 
clue.
4. Words can be associated with multiple clues, but some words are "assassins" (wrong 
answers).
5. Teams score points for correctly identified words and lose points for assassins.
6. The team with the most points wins."""

spymaster_intro = """You are playing as the spymaster. You must do the following to provide your teammate with a good clue:
    1.	Identify Team Words: Review your team’s words on the key card.
    2.	Find Connections: Look for common themes, categories, or associations among multiple team words.
    3.	Avoid Opponent/Assassin Words: Ensure your hint doesn’t lead to opponent words or the assassin.
    4.	Choose One Word: Select a single, clear word that connects as many of your team’s words as possible.
    5.	Pick a Number: Indicate how many team words your hint relates to.
    6.	Think Abstractly: Be creative but ensure your team can logically make the connection.
    7.	Avoid Forbidden Words: Do not use any form or variation of the words on the board."""

guesser_intro = """You are playing as the guesser."""

class MyAssoc(Assoc):
    def __init__(self):
        super().__init__()
        # Initialize your model/embeddings/data here
    
    def getAssocs(self, pos, neg, topn):
        """
        Find words associated with positive words but not negative words.
        
        Args:
            pos: List of words to associate with
            neg: List of words to avoid
            topn: Number of associations to return
            
        Returns:
            List of (word, score) tuples
        """
        pass
        

    def preprocess(self, w):
        """
        Preprocess words before looking up associations.
        
        Args:
            w: Input word
            
        Returns:
            Processed word
        """
        pass


class MySpymaster(BaseSpymaster):
    def __init__(self, assoc, debug=False):
        super().__init__(assoc)
        self.debug = debug

    def askLlama(self, prompt, messages=[]):
        messages.append({
            "role": "user",
            "content": prompt
        })

        data = {
            "model": "llama3",
            "messages": messages,
            "stream": False,
        }
        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=data)
        messages.append(response.json()['message'])
        if self.debug:
            pprint(response.json())

        return response.json()['message']['content'], messages
    
    def evaluateClue(self, clue, board_words, intended_words):
        prompt = codenames_intro + "\n\n" + guesser_intro + f"""

Your teammate has provided you with the clue {clue}. These are the words on the table: {board_words}

Select {len(intended_words)} word(s) from the table as your guesses.
"""
        answer, conversation = self.askLlama(prompt)

        if len(intended_words) == 1:
            prompt = "What is the word you would like to guess? Say only the word."
            guess, conversation = self.askLlama(prompt, conversation)
            return True if guess in intended_words else False
        else:
            prompt = "What is the first word you would like to guess? Say only the word."
            first_guess, conversation = self.askLlama(prompt, conversation)
            if first_guess not in intended_words:
                return False
            
            for i in range(1, len(intended_words)):
                prompt = "What is the next word you would like to guess? Say only the word."
                next_guess, conversation = self.askLlama(prompt, conversation)
                if next_guess not in intended_words:
                    return False
            
            return True
    
    def makeClue(self, board, team: Team):
        """
        Generate a clue for your team.
        
        Args:
            board: Dictionary with keys:
                'R': List of red team's words
                'U': List of blue team's words
                'N': List of neutral words
                'A': List of assassin words
                'team': Team.RED or Team.BLUE
            
        Returns:
            tuple: ((clue_word, number_of_words), debug_info)
        """

        # Step 1: Extract all words from the game board into a set
        # This will be used later to ensure our clue isn't one of the board words
        board_words = set(
            [item for sublist in list(board.values()) for item in sublist]
        )

        # Step 2: Identify our team's words and the opponent's words based on team color
        # 'U' represents blue team, 'R' represents red team
        my_words = board["U" if team == Team.BLUE else "R"]
        opponent_words = board["R" if team == Team.BLUE else "U"]

        # Step 3: Create negative word list (words we want to avoid)
        # Combines opponent's words with neutral ('N') and assassin ('A') words
        # These are words our clue should NOT be similar to
        negative_words = board["N"] + board["A"] + opponent_words
        # Create positive word list (words we want to target)
        positive_words = my_words
        
        prompt = codenames_intro + "\n\n" + spymaster_intro + "\n\nHere are your team’s words:\n" + str(positive_words)
        prompt += "\n\nHow many words would you like to provide a hint for? Respond with 1, 2 or 3. Say nothing else."
        answer, conversation = self.askLlama(prompt)
        num_words = int(answer)

        prompt = "What " + str(num_words) + "word(s) would you like to select and what clue would you like to offer your "\
            "teammate for them?"
        answer, conversation = self.askLlama(prompt, conversation)
        
        intended_words = []
        if num_words == 1:
            prompt = "What is the word? Say only the word."
            word, conversation = self.askLlama(prompt, conversation)

            intended_words.append(word)

        elif num_words == 2:
            prompt = "What is the first word? Say only the word."
            first_word, conversation = self.askLlama(prompt, conversation)
            prompt = "What is the second word? Say only the word."
            second_word, conversation = self.askLlama(prompt, conversation)

            intended_words.append(first_word)
            intended_words.append(second_word)

        elif num_words == 3:
            prompt = "What is the first word? Say only the word."
            first_word, conversation = self.askLlama(prompt, conversation)
            prompt = "What is the second word? Say only the word."
            second_word, conversation = self.askLlama(prompt, conversation)
            prompt = "What is the third word? Say only the word."
            third_word, conversation = self.askLlama(prompt, conversation)

            intended_words.append(first_word)
            intended_words.append(second_word)
            intended_words.append(third_word)
        
        prompt = "What is the clue? Say only the clue."
        clue, _ = self.askLlama(prompt, conversation)

        effective = self.evaluateClue(clue, board_words, intended_words)
        print(f"Effectiveness: {effective}")

        return (clue.lower(), num_words), intended_words
