# Notes

## Brainstorm
- Attempt to have a model "reason," going "step by step."
- Measure the mean-squared distance of each word-vector to the others, choose two words that are the closest to each other, and present a clue word that is the closest to the middle.
- Present clues to a model until it's able to successfully guess the right word. Then present that clue to the user.
    - Prompt the model first for a word, then prompt it again to output exclusively the word (to isolate it from other text)
- Algorithmically compare edges between positive words to determine whether they pass too closely to negative words.

## Llama Download URL
https://llama3-2-lightweight.llamameta.net/*?Policy=eyJTdGF0ZW1lbnQiOlt7InVuaXF1ZV9oYXNoIjoiZm5wOXEzcDV1c2owd3hkYWE2cmwyOTgzIiwiUmVzb3VyY2UiOiJodHRwczpcL1wvbGxhbWEzLTItbGlnaHR3ZWlnaHQubGxhbWFtZXRhLm5ldFwvKiIsIkNvbmRpdGlvbiI6eyJEYXRlTGVzc1RoYW4iOnsiQVdTOkVwb2NoVGltZSI6MTczNzE0MTgyN319fV19&Signature=W%7E1tWuOweTwf1N7i4fNCM41ymBXghtuMu3t3WQS4Ytf6tm34-dFzPjbehBYdxAfqr3EGlroS7qOHCwDsCa7LhJT6x%7E3uxS6Jh84gQCwIncMYKa4sJrhuPVqf7AiqLGqflGGC%7EoiaMtXM5-94N92mklhkVzOpQUQ8G-nL%7E6D83FON-T0T-XzfiOq-HyXpa7dGsswsXk7Aw7skDgGHxvwMa1je7bQ5stAmBLN0KFqqm83fp%7EcKzFJBwITed9VtaKUDbb2PbQgyjO7kP%7EgnX0ecgvjK2q4mwBcaJ0rfyA-%7E0FHfCVd%7EAU1GZTFtliGGHIWCPriYBrrNi7JmS4LywrARog__&Key-Pair-Id=K15QRJLYKIFSLZ&Download-Request-ID=978637077460680


## Test my game
python3 client.py WDYY red

python3 client.py WDYY blue

Website: https://mind.cs.byu.edu/codenames/game?code=WDYY&role=spymaster&team=red

## Codenames Instructions
Here are the basic rules of Codenames:

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
6. The team with the most points wins.


## Ollama prompts
```
curl http://localhost:11434/api/chat -d '{
  "model": "llama3",
  "stream": false,
  "messages": [
    {
      "role": "user",
      "content": "why is the sky blue?"
    },
    {
      "role": "assistant",
      "content": "due to rayleigh scattering."
    },
    {
      "role": "user",
      "content": "how is that different than mie scattering?"
    }
  ],
  "max_tokens": 5
}'
```