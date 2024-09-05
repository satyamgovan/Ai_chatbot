import aiml
import pandas
from nltk.sem import Expression
from nltk.inference import ResolutionProver
import wikipedia
import csv
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

read_expr = Expression.fromstring
prover = ResolutionProver()

kb = []
data = pandas.read_csv('logical-kb.csv', header=None)

[kb.append(read_expr(row)) for row in data[0]]

def is_consistent(kb, expr):
    try:
        neg_expr = read_expr('-' + str(expr))
        # Check if both the expression and its negation can be proven
        result_expr, _ = prover._prove(goal=expr, assumptions=kb)
        result_neg_expr, _ = prover._prove(goal=neg_expr, assumptions=kb)
        # If both are provable, return False (indicating inconsistency)
        return not (result_expr and result_neg_expr)
    except RuntimeError:
        return False

# Create a Kernel object. No string encoding (all I/O is unicode)
kern = aiml.Kernel()
kern.setTextEncoding(None)
kern.bootstrap(learnFiles="mybot-basic.xml")

print("Welcome to this chat bot. Please feel free to ask questions from me!")

while True:
    try:
        userInput = input("> ")
    except (KeyboardInterrupt, EOFError) as e:
        print("Bye!")
        break

    responseAgent = 'aiml'

    if responseAgent == 'aiml':
        answer = kern.respond(userInput)

    if answer[0] == '#':
        params = answer[1:].split('$')
        cmd = int(params[0])
        if cmd == 0:
            print(params[1])
            break
        # Pull from Wikipedia 
        elif cmd == 1:
            try:
                wSummary = wikipedia.summary(params[1], sentences=3,auto_suggest=False)
                print(wSummary)
            except:
                print("Sorry, I do not know that. Be more specific!")
        
        # Processing the new logical component
        elif cmd == 31:  # if input pattern is "I know that * is *"
            object, subject = params[1].split(' is ')
            expr = read_expr(subject + '(' + object + ')')
            
            # Check if the new expression contradicts existing KB expressions
            if not is_consistent(kb, expr):
                print("The new expression contradicts existing knowledge!")
                # Handle the contradiction (e.g., skip adding the expression or log a warning)
            else:
                kb.append(expr)
                print('OK, I will remember that', object, 'is', subject)
        
        elif cmd == 32:  # if the input pattern is "check that * is *"
            object, subject = params[1].split(' is ')
            expr = read_expr(subject + '(' + object + ')')
            
            # Check if the negation of expr is provable from KB
            if ResolutionProver().prove(expr, kb, verbose=True):
                print('Correct.')
            else:
                neg_expr = read_expr('-' + str(expr))
                # Check if the negation of expr is not provable from KB
                if not ResolutionProver().prove(neg_expr, kb, verbose=True):
                    print('Sorry, I don\'t know.')
                else:
                    print('Incorrect.')



        elif cmd == 99:
            print("I did not get that, please try again.")
            

    # else:
    #     print(answer)