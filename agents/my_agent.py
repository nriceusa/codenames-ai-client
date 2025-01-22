from base.assoc import Assoc
from base.constants import Team
from base.spymaster import BaseSpymaster

from itertools import combinations
import requests
import json
from pprint import pprint

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
        
        # Step 4: Generate subsets
        sets = [
            list(subset) for set_size in range(1, 3) for subset in combinations(positive_words, set_size)
        ]

        pprint(sets)
        
        for subset in sets:
            prompt = f"You and a teammate are playing Codenames. You are the spymaster. Give me a clue to pass to your teammate for the word"
            
            if len(subset) == 1:
                prompt += f" {subset[0].upper()}. "
            elif len(subset) == 2:
                prompt += f"s {subset[0].upper()} and {subset[1].upper()}. "
            elif len(subset) == 3:
                prompt += f"s {subset[0].upper()}, {subset[1].upper()}, and {subset[2].upper()}. "
            
            prompt += "The clue must be a single word and cannot contain any word already on the table. A good hint will trigger your teammate to think of "
            
            if len(subset) == 1:
                prompt += f"the word {subset[0].upper()} and select it "
            elif len(subset) == 2:
                prompt += f"the words {subset[0].upper()} and {subset[1].upper()} and select them "
            elif len(subset) == 3:
                prompt += f"the words {subset[0].upper()}, {subset[1].upper()}, and {subset[2].upper()} and select them "

            prompt += "from a table with various other words on it. Be succinct."

            print("prompt:", prompt)

            answer, _ = self.askLlama(prompt)

        return (answer, 2), {}
