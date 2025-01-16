from base.assoc import Assoc
from base.constants import Team
from base.spymaster import BaseSpymaster

import requests
import json

url = "http://localhost:11434/api/chat"


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
        prompt = """
We are playing a game of Codenames. I need to find words that are associated with these words:
{pos}

But they should not be associated with the words:
{neg}

Respond with two words that are associated with the first list but not the second list. The last two words of your response will be used.
"""

        data = {
            "model": "llama3",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=data)

        return [response.json()['message']['content'], 1]
        

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
        neg = board["N"] + board["A"] + opponent_words
        # Create positive word list (words we want to target)
        pos = my_words
        
        prompt = """
We are playing a game of Codenames. I need to find a clue that is associated with these words:
{pos}

But it should not be associated with the words:
{neg}

Respond with a single word that is associated with two words in the first list but not the second list. Do not respond with a word that is on the board. Your response must be only one world long.
"""

        data = {
            "model": "llama3",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(url, headers=headers, json=data)

        if self.debug:
            print('pos:', pos)
            print('response:', response.json()['message']['content'])

        return (response.json()['message']['content'], 2), {}
