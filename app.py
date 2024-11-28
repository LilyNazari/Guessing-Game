#########################            IMPORT MODULES            ######################### 
import streamlit as st
import json
import random
import time
import nltk
from nltk.corpus import brown
from collections import Counter
nltk.download('brown')            
word_list = brown.words() 


#########################            INITIALIZING FUNCTION                 #########################      
def initialize_game_state():    
    while True:  # Loop until a word with 3, 4, 5, or 6 letters is found this is because it's difficult for people to guess longer words and it's not fun!
        random_word = random.choice(word_list).lower()  # Convert to lowercase for consistency
        word_length = len(random_word)
        if word_length in [3, 4, 5, 6]:
            st.session_state.random_word = random_word  # Store the random word in session state
            st.session_state.word_length = word_length    # Store the word length
            st.session_state.remaining_attempts = word_length + 1  # Limit the number of allowed attempts
            st.session_state.total_attempts = word_length + 1
            st.session_state.guesses = []  # Track all guesses
            st.session_state.remaining_time = 30 * word_length  # Default time for "easy" mode
            st.session_state.start_time = time.time()
            st.session_state.game_over = False
            st.session_state.score =0
            break  
# Initialize session state for game variables
if "random_word" not in st.session_state: 
    initialize_game_state()

# Retrieve the chosen values
answer = st.session_state.random_word
word_length = st.session_state.word_length
remaining_attempts = st.session_state.remaining_attempts
total_attempts = st.session_state.total_attempts
remaining_time = st.session_state.remaining_time
time_limit = st.session_state.remaining_time
score= st.session_state.score    



##################                 SAVE & LOAD HISTORY FUNCTIONS              #############################

def save_history (history, file_path= "game_history.json"):
    with open(file_path, "w") as f:
        json.dump(history, f)
    
def load_history (file_path="game_history.json"):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []  # Return an empty list if no file exists: no history


if "game_history" not in st.session_state:
        st.session_state.game_history = load_history()


###############################              BASIC LAYOUT                   #############################
tab1, tab2, tab3 = st.tabs(["Game", "Stats", "Settings"])

##############################               SETTINGS PAGE                     #############################
with tab3:
    st.header("Settings")
    mode = st.selectbox("Difficulty mode", ["easy", "medium", "hard"])    #Selection of difficulty modes   
    dark_mode = st.radio("Theme:", [("Dark Mode"), "Light Mode"])         # A toggle to switch between light and dark mode


#############################                 DIFFICULTY MODE

    # Calculating the time limit based on difficulty options
    if True:        
        if mode == "easy":
            time_limit = 30 * word_length
        elif mode == "medium":
            time_limit = 20 * word_length
        elif mode == "hard":
            time_limit = 10 * word_length
        #st.session_state.start_time = time.time()  # Reset timer
    

############################         LIGHT|DARK MODE   
    # Function to set the page theme (dark or light)
    def set_theme(dark_mode):
        if dark_mode:
            st.markdown(
                """
                <style>
                h1, h2, h3, h4, h5, h6 {color: #FFC300;}  /* Yellow header fonts*/
                .stButton>button { background-color: #FFC300; color: #2E2E2E; /*Yellow bbutton with black text */}
                .stApp {background-color: #2E2E2E;  /* Dark mode bg */}
                .stMarkdown {color: #D3D3D3;  /* Light grey text color for markdown */}
                </style>
                """, unsafe_allow_html=True)
        else:
            st.markdown(
                """
                <style>
                h1, h2, h3, h4, h5, h6 {color: #f44336;}  /* Red header fonts */
                .stButton>button { background-color: #f44336; color: #2E2E2E; /* Red button with black text */}
                .stApp {background-color: #80cbc4    ;  /* Light mode bg */}
                .stMarkdown {color: #2E2E2E;  /* Dark grey text color for markdown */}
                </style>
                """, unsafe_allow_html=True)
    # Set the theme based on the user's selection
    if dark_mode == "Dark Mode":
        set_theme(True)
    else:
        set_theme(False)




##############################               MAIN PAGE                    #############################
with tab1:
    ###################           Some basic instructions    
    st.header("Wordle Game 🎮")
    with st.expander("How to play?"):
        st.image("https://images.unsplash.com/photo-1652451764453-eff80b50f736?q=80&w=1932&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D")
        st.write('''
        - Guess the word within the allowed attempts and time.
        - Use the on-screen keyboard and input boxes to make your guess.
        - You can request hints, but each hint costs one guess!             
    ''') 
    #################         Input section for each guess and extra info
    guess = st.text_input(f"The answer has {word_length} letters and you have {remaining_attempts} attempts to guess the correct word in {time_limit} seconds. Good luck!", max_chars=word_length).lower()
         


    #####################           SCORE CALCULATION FUNCTION
    def calculate_score():        
        if mode == "easy":
            st.session_state.score +=  st.session_state.remaining_time *  st.session_state.remaining_attempts
        elif mode == "medium":
            st.session_state.score  +=  2 * st.session_state.remaining_time *  st.session_state.remaining_attempts
        elif mode == "hard":
            st.session_state.score  +=  3 * st.session_state.remaining_time *  st.session_state.remaining_attempts
        return st.session_state.score
    

    ########################    GUESS  EVALUATION  
    if st.button("Submit"):
        if remaining_attempts > 0:       #Checking to see if there's enough attempts left
            if guess:   
                st.session_state.remaining_attempts -= 1       #adjusting the remaining attempts
                st.session_state.guesses.append(guess)   
                if guess == answer:            #Calculating the score and saving the results for the correct answer
                    calculate_score()
                    st.success(f"Congratulations! You guessed the correct word! Your score: {st.session_state.score}")
                    st.session_state.game_over = True
                    st.session_state.game_history.append({ "score": st.session_state.score, "won": st.session_state.score > 0, "attempt" : st.session_state.total_attempts - st.session_state.remaining_attempts})   
                    save_history(st.session_state.game_history)
                elif (not all(item.isalpha() for item in guess)) or len(guess) != word_length:  #Entry validation
                    st.warning("Please enter a valid guess.")
                else:        #Revealing the common letters for incorrect guesses 
                    common_letters = []
                    answer_list = [answer[i] for i in range(len(answer))]
                    guess_list =  [guess[i] for i in range(len(guess))]
                    for i in guess_list:
                        if i in answer_list:
                            common_letters.append(i)
                    if common_letters:       
                        common_letters_count = len(common_letters)
                        answer_count = len(answer_list)
                        guess_quality = common_letters_count / answer_count * 100
                        st.write(f"Common letters are: {', '.join(sorted(set(common_letters)))} and your guess quality was: {guess_quality}")
                    else:
                        st.write("No common letters found.")
        
        else:    #Calculating the score and saving the results for the lost games
            st.error(f" No attempts left! Game over. The correct word was: {answer}")
            st.session_state.game_over = True
            st.session_state.game_history.append({ "score": st.session_state.score, "won": st.session_state.score > 0, "attempt" : st.session_state.total_attempts - st.session_state.remaining_attempts})
            save_history(st.session_state.game_history)

        
        
    #################            Create a New Game
    def start_new_game(): # Store current session data for later and clear and reinitialize game state
        st.session_state.previous_session = {
            "random_word": st.session_state.random_word,
            "word_length": st.session_state.word_length,
            "remaining_attempts": st.session_state.remaining_attempts,
            "remaining_time": st.session_state.remaining_time,
            "guesses": st.session_state.guesses,
            "score": st.session_state.score,
            "game_over": st.session_state.game_over
        }
        st.session_state.clear()  # Reset the session state to starting a new game
        initialize_game_state()
        st.rerun()  # Reloads the app and starts fresh
    if st.button("New Game"):
        start_new_game()

   
          

    #######################                TIMER
    
    timer_placeholder = st.empty()       # A placeholder for the timer display
    while st.session_state.remaining_time> 0 :
        if st.session_state.game_over is False:
            # Calculate the remaining time dynamically
            elapsed_time = time.time() - st.session_state.start_time
            st.session_state.remaining_time = max(0, time_limit - int(elapsed_time))
        # Update the timer display
        timer_placeholder.write(f"**Remaining Time**: {st.session_state.remaining_time} seconds")
        # Pause for 1 second to simulate the countdown
        time.sleep(1)
    # Game-over by time and calculating the score and saving the results for the lost games
    if st.session_state.remaining_time == 0:          
        score == 0
        st.session_state.game_over = True
        st.error(f"Time's up! Game over. The correct word was: {answer}")
        st.session_state.game_history.append({ "score": st.session_state.score, "won": st.session_state.score > 0, "attempt" : st.session_state.total_attempts - st.session_state.remaining_attempts})
        save_history(st.session_state.game_history)
        


##############################               STATS PAGE                     #############################
with tab2:
    st.header("Stats")

    


    # Making sure that there's at least one game played before displaying stats
    if st.session_state.game_history:
        # 1. Winning Rate
        won_games = sum(1 for game in st.session_state.game_history if game["won"])
        lost_games = len(st.session_state.game_history) - won_games
        total_games = len(st.session_state.game_history)
        winning_rate = (won_games / max(total_games, 1)) * 100  
        st.write(f"Winning Rate: **{winning_rate:.2f}%**")

        # 2. Best Score
        best_score = max(game["score"] for game in st.session_state.game_history)
        st.write(f"Best Score: **{best_score}**")

        # 3. Average Score
        total_score = sum(game["score"] for game in st.session_state.game_history)
        avg_score = total_score / len(st.session_state.game_history)
        st.write(f"Average Score: **{avg_score:.2f}**")
        st.subheader("Scores")
        # 4. Bar Chart of Scores
        scores = [game["score"] for game in st.session_state.game_history]
        st.bar_chart(scores)
        st.subheader("Atempts")
        # 5.  attempts
        attempts = [game.get("attempt",0) for game in st.session_state.game_history] 
        st.line_chart(attempts)

    else:
        st.write("No games played yet. Play a game to see your stats!")
    
    










  











