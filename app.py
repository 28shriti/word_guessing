# this code has no ui output is shown in console
# import random

# word_bank = ['rizz', 'ohio', 'sigma', 'tiktok', 'skibidi']
# word = random.choice(word_bank)
# guessedWord = ['_'] * len(word)
# attempts = 10
# while attempts > 0:
   
#     print('\nCurrent word: ' + ' '.join(guessedWord))

#     guess = input('Guess a letter: ').lower()
   
#     if guess in word:
#         for i in range(len(word)):
#             if word[i] == guess:
#                 guessedWord[i] = guess
#         print('Great guess!')
#     else:
#         attempts -= 1
#         print('Wrong guess! Attempts left: ' + str(attempts))
#     if '_' not in guessedWord:
#         print('\nCongratulations!! You guessed the word: ' + word)
#         break
#     else:
#       print('\nYou\'ve run out of attempts! The word was: ' + word)



# -----------------------------------------------------------------------------------------------------------------------------------------

# this code has ui


import random
from flask import Flask, render_template, request, session, jsonify

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for session management

# Word bank
word_bank = ['rizz', 'ohio', 'sigma', 'tiktok', 'skibidi']

def new_game():
    """ Start a new game and store values in session """
    session['word'] = random.choice(word_bank)
    session['guessed_word'] = ['_'] * len(session['word'])
    session['attempts'] = 10
    session['score'] = session.get('score', 0)  # Keep score persistent
    session['hint_used'] = False  # Track if hint is used

@app.route('/')
def index():
    new_game()  # Start game
    return render_template('index.html', 
                           word=" ".join(session['guessed_word']), 
                           attempts=session['attempts'], 
                           score=session['score'])

@app.route('/guess', methods=['POST'])
def guess():
    """ Handle the user's guess """
    guess = request.json.get('letter', '').lower()

    if not guess or len(guess) != 1:
        return jsonify(success=False, message="Enter a single letter.", 
                       word=" ".join(session['guessed_word']), 
                       attempts=session['attempts'], score=session['score'])

    word = session['word']
    guessed_word = session['guessed_word']

    if guess in word:
        for i in range(len(word)):
            if word[i] == guess:
                guessed_word[i] = guess  # Update guessed word
        
        session['guessed_word'] = guessed_word  # ✅ Store guessed letters
        message = "Great guess!"

        # If the whole word is guessed, start a new round
        if "_" not in guessed_word:
            session['score'] += 10  # Add points
            message = f"Correct! The word was '{word}'. New word generated."
            new_game()  # Start new round
    else:
        session['attempts'] -= 1
        message = f"Wrong guess! Attempts left: {session['attempts']}"

        if session['attempts'] == 0:
            return jsonify(success=False, message=f"Game over! The word was '{word}'.", 
                           word=" ".join(session['guessed_word']), attempts=session['attempts'], score=session['score'])

    return jsonify(success=True, message=message, word=" ".join(session['guessed_word']), 
                   attempts=session['attempts'], score=session['score'])

@app.route('/hint', methods=['POST'])
def hint():
    """ Provide a hint by revealing one random hidden letter """
    if session['hint_used']:
        return jsonify(success=False, message="Hint already used!", word=" ".join(session['guessed_word']), 
                       attempts=session['attempts'], score=session['score'])

    word = session['word']
    guessed_word = session['guessed_word']

    hidden_indices = [i for i, letter in enumerate(guessed_word) if letter == '_']
    
    if hidden_indices:
        hint_index = random.choice(hidden_indices)  # Pick a random hidden letter
        guessed_word[hint_index] = word[hint_index]  # Reveal it
        session['guessed_word'] = guessed_word
        session['hint_used'] = True  # Mark hint as used

    return jsonify(success=True, message="Hint used! One letter revealed.", 
                   word=" ".join(session['guessed_word']), attempts=session['attempts'], score=session['score'])

if __name__ == '__main__':
    app.run(debug=True)
