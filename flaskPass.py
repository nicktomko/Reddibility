#flaskPass
#NTomko
#June 17, 2013

#This test passing variables to flask to be displayed in HTML

def varPass():
    reddit_author = "Bill Gates"
    reddit_title = "I am Bill Gates, ask me anything"
    reddit_questions = ["Do you like Windows?", "How old are you?"]
    reddit_answers = ["No, it sucks", "300 years old"]

    return reddit_author, reddit_title, reddit_questions, reddit_answers

