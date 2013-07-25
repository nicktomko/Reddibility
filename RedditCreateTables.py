#QuikiReddit Populate SQL Tables
#N Tomko
#July 24, 2013

#v6
#This is the latest version as of July 24


#Packages
import praw
import pandas as pd
from pandas import Series, DataFrame
import MySQLdb
import nltk
import operator
import re 
import pprint
import unicodedata

#number of top reddits to download
NUM_REDDITS = 1
    

def getReddits(NUM_REDDITS):
    #Declare Reddit User Agent
    user_agent = ("Insight 2.0 by /u/_NTomko")
    r=praw.Reddit(user_agent=user_agent)
    
    #Uncomment next two lines if the top NUM_REDDITS
    #reddit_obj = r.get_subreddit('IAmA').get_top_from_year(limit=NUM_REDDITS)
    #reddit_list = [x for x in reddit_obj];
    
    
    #Uncomment next two lines if you want to look at a single reddit
    reddit_obj = r.get_submission(url='http://www.reddit.com/r/IAmA/comments/ntsco/i_am_salman_khan_founder_of_khan_academyama/')
    reddit_list = [reddit_obj]
    
    print len(reddit_list)
    raw_input('test')
    
    #Iterate over all subreddits
    
    return reddit_list


def createRedditTuple(NUM_REDDITS, reddit):
    
    reddit_list = []
    
    
    #Put infor from all reddits into a tuple and convert to ascii
    for i in range(NUM_REDDITS):
        reddit_list.append ((str(reddit[i].author), 
                    str(unicodedata.normalize('NFKD', reddit[i].title).encode('ascii','ignore')),
                    str(unicodedata.normalize('NFKD', reddit[i].url).encode('ascii','ignore')),
                    str(unicodedata.normalize('NFKD', reddit[i].selftext).encode('ascii','ignore')),
                    reddit[i].score, reddit[i].num_comments))
    return reddit_list
        

def createRedditSQLTable():
    
    db=MySQLdb.connect("localhost","root","oilesso","redditdata")
    
    #prepare a cursor object using cursor() method
    cursor = db.cursor()
            
    reddit_table = """CREATE TABLE TOPVARIETY (AUTHOR CHAR(100) PRIMARY KEY,
        TITLE TEXT NOT NULL,
        URL CHAR(255) NOT NULL,
        SELFTEXT TEXT NOT NULL,
        SCORE INT,
        NUM_COMMENTS INT)"""
        
    
    #Execute the create global table
    cursor.execute(reddit_table)
    
       
    qa_table = """CREATE TABLE QADATATOPVAR (ID INT PRIMARY KEY AUTO_INCREMENT,
        AUTHOR CHAR(100) NOT NULL,
        QUESTION TEXT NOT NULL,
        ANSWER TEXT NOT NULL,
        SCORE FLOAT)"""
    
    #Execute the create qa table    
    cursor.execute(qa_table)

    
    db.close()


def popRedditTable(NUM_REDDITS, reddit_tuple):
    
    #Connect to mySQL
    db=MySQLdb.connect("localhost","root","oilesso","redditdata")
    
    #prepare a cursor object using cursor() method
    cursor = db.cursor()    
                
    for i in range(NUM_REDDITS):
    
        author= reddit_tuple[i][0]
        title = reddit_tuple[i][1]
        url = reddit_tuple[i][2]
        selftext = reddit_tuple[i][3]
        selftext = selftext.replace('"', ' ')
        selftext = selftext.replace("'", '') 
        score = reddit_tuple[i][4]
        num_comments = reddit_tuple[i][5]
        
        
        #Populate table
        cursor.execute('INSERT INTO TOPVARIETY(author, title, \
  		url, selftext, score, num_comments) \
  		VALUES("%s", "%s", "%s", "%s", "%d", "%d")' % \
  		(author, title, url, selftext, score, num_comments))      

    db.commit()  #commit changes
    db.close()   #close database


def commentData(flat_comments):
    '''Extract comment author, body and score for each individual comment'''
    
    #Initialise Lists
    comment_list = [] 
    author_list = [] 
    score_list = []  
    
    #Loop through each comment
    for comment in flat_comments:
        #Filter out more comments objects    
        if type(comment) == praw.objects.Comment:  
            comment_list.append(comment.body)
            author_list.append(comment.author)
            score_list.append(comment.score)
    
    #Make sure any weird characters are ignored
    comment_list = [item.encode('ascii', 'ignore') for item in comment_list]
    
    #Get rid of weird foratting
    comment_list = [item.replace('"', ' ') for item in comment_list]
    comment_list = [item.replace('...', '.') for item in comment_list]
    comment_list = [item.replace("'", '') for item in comment_list]
    comment_list = [item.replace("\n", ' ') for item in comment_list]
    comment_list = [item.replace("?!", ' ') for item in comment_list]
    
    return comment_list, author_list, score_list


def qaFinder(comment_list, author_list, author_name, score_list, comments):
    '''This labels each comment either q (question), a (answer) or n(neither)
        also counts the number of comments between each q/a pair'''
        
    reply_counter = 0  #intialise comment counter
    reply_count_list = []
    qora_list = [] #declare qora list
    a_comments_list=[]  #declare list to store answer comments only
    q_comments_list = [] #declare list to store question comments only
    q_score_list = []  #store question score
    a_score_list = []  #store answer score
    
    cnt = 0
    
    #delete last two comments
    del comment_list[-2:]
    del author_list[-2:]
    del score_list[-2:]        
    
    #Create a list with questions and answers
    while cnt < (len(author_list)-1):
      
        if str(author_list[cnt]) <> author_name and str(author_list[cnt+1]) == author_name:
            qora_list.append('q')
            q_comments_list.append(comment_list[cnt])
            a_score_list.append(score_list[cnt])

            cnt+=1
            

        elif str(author_list[cnt]) == author_name:
            
            #If two in a row        
            if str(author_list[cnt+1]) == author_name and str(author_list[cnt+2]) != author_name:
                qora_list.append('a')
                a_combined = comment_list[cnt] + ' '+ comment_list[cnt+1] 
                a_comments_list.append(a_combined)
                q_score_list.append(score_list[cnt]+score_list[cnt+1])
                cnt+=2           
            
            
            #If three in a row
            elif str(author_list[cnt+1]) == author_name and str(author_list[cnt+2]) == author_name:
                #raw_input('three in a row')
                qora_list.append('a')
                a_combined = comment_list[cnt] + ' ' + comment_list[cnt+1] + ' ' + comment_list[cnt+2]
                a_comments_list.append(a_combined)
                q_score_list.append(score_list[cnt]+score_list[cnt+1] + score_list[cnt+2])
                cnt+=3
                            
            else:
                qora_list.append('a')
                a_comments_list.append(comment_list[cnt])
                q_score_list.append(score_list[cnt]+score_list[cnt])
                
                cnt+=1
                #print a_comments_list[-1]
                #raw_input('enter') 
             
        else:
            qora_list.append('n') #if neither question nor answer
            cnt+=1
     
               
    #Now check the last comment to see if it is an answer
    if str(author_list[-1]) == author_name:
        qora_list.append('a')
        #a_score_list.append(score_list[-1])
        q_score_list.append(0)     
        a_comments_list.append(comment_list[-1])
    else:
        qora_list.append('n')   
        reply_count_list.append(0)
    
    #Delete the last entry for cases where double response form author - in the
    #future fix this so it appends the answer to the previsous answer
    if str(author_list[-1]) == author_name and str(author_list[-2]) == author_name:
        del a_comments_list[-1]
        del q_score_list[-1]
        del a_score_list[-1]
    
    if len(a_score_list) < len(a_comments_list):
        del q_comments_list[-1]
        del a_comments_list[-1]
        del q_score_list[-1]

    if len(q_comments_list) < len(a_comments_list):
        del a_comments_list[-1]
        del a_score_list[-1]
        del q_score_list[-1]
    
    
    print len(a_comments_list), len(q_comments_list), len(a_score_list), len(q_score_list)
    #raw_input('enter')    
      
    #Sum q_score and a_score to get a total score for he q/a combo
    qa_zip = zip(q_score_list, a_score_list)
    qa_score_list = [a+b for a,b in qa_zip]  
    
    reply_count_list = 0
    
    #Return qora list
    return qora_list, a_comments_list, q_comments_list, qa_score_list, reply_count_list

def wordCntLexDiv(comments):
    """Find word count, distinct word count and lexical diversity of each comment"""
    
    #raw_test = "My name is Nicholas and I live in London.  I I I I name name live."
    
    #Initialise Lists
    word_count_list = [];
    dist_word_count_list = [];
    lex_div_list = [];
    
    for comment in comments:
        
        #Remove punctuation
        punctuation = re.compile(r'[-.?!,":;()|0-9]')
        comment = punctuation.sub(" ", comment)
        
        #Tokenize raw text into words
        raw_tokens = nltk.word_tokenize(comment)
        #print raw_tokens
    
        #Convert tokens to NLTK text type
        nltk_text = nltk.Text(raw_tokens)
    
        #Non-disctinct Word Count
        #This counts puncuation as words
        word_count = len(nltk_text)
        word_count_list.append(word_count)
    
        #Find number of disctinct words
        sorted_text = sorted(set(nltk_text))
        dist_word_count = len(set(nltk_text))
        dist_word_count_list.append(dist_word_count)
        
    
        #Calculate Lexical Diversity, Lexical Richness
        if len(set(nltk_text)) !=0:
            lex_div = (len(nltk_text)*len(nltk_text)) / float(len(set(nltk_text)))
            #lex_div = len(set(nltk_text)) / float(len(nltk_text))
            #lex_div = len(nltk_text)*float(len(set(nltk_text)))


        else: 
            lex_div = 0
            
            
        #lex_div = len(nltk_text)*float(len(set(nltk_text)))
        #lex_div = len(set(nltk_text)) / float(len(nltk_text))
        lex_div_list.append(lex_div)
  
    return word_count_list, dist_word_count_list, lex_div_list
    
def questionFilter(comments):
    #This filters out questions but also keeps the previous sentence if it is a two 
    #sentence question  
    
    #Regular expression to find quesitons
    #Note [^.?!] means find anything that ins't .?!                        
    
    #comments = ['Hello?',  'What is you'r name?',  'How old are you? I love hockey?', 'Not a question']
    #question = re.findall(r'[^.?!]*\?', comments[0])

    questions = []

    for i in range(len(comments)):
        #find sentences
        pat = re.compile(r'([A-Z][^\.!?]*[\.!?])', re.M)
        sentences = pat.findall(comments[i])
        question = re.findall(r'[^.?!]*\?', comments[i])
        
        #If there are only questions 
        if len(question) == len(sentences) and len(question) !=0:
            qs_joined = " ".join(question)
            questions.append(qs_joined)
    
        #If there are no questions
        elif len(question)== 0:
            questions.append('no q')
    
        #If there are 2 sentences and the last is a question keep previous
    
        elif len(sentences) ==2 and len(question) ==1 and question[0][-1] =='?' and sentences[-1][-1] == '?':
            qs_joined = " ".join(sentences)
            questions.append(qs_joined)
        
        #Other cases
        else:
            qs_joined = " ".join(question)
            questions.append(qs_joined)  

    
    return questions
      
    
def scoreCalc(feat1_list, feat2_list):
    #calculate an overall score for each question and answer pair based on:
    #chosen features
    
    #pprint.pprint(feat1_list)
    #raw_input('1')
    #pprint.pprint(feat2_list)
    #raw_input('1')
    #pprint.pprint(feat3_list)
    #raw_input('1')
    
    wt_vector = [0.5, 0.5, 0]
    #wt_vector = [0.8, 0.2, 0]
 
    #Weight each feature
    feat1_list = [num*wt_vector[0] for num in feat1_list]
    feat2_list = [num*wt_vector[1] for num in feat2_list]
    #feat3_list = [num*wt_vector[2] for num in feat3_list]
    
    
    zip_lists = zip(feat1_list, feat2_list)
    total_score = [a+b for a,b in zip_lists]
    
    #pprint.pprint(lex_div)
    #pprint.pprint(total_score)
    #raw_input('eneter')
    
    return total_score

def normFeat(feat_list):
    #Input a list of some feature scores, output a normalised list between 0 and 1
    B = max(feat_list)
    A = min(feat_list)

    norm_list = [(i-A)/float((B-A)) for i in feat_list]
    
    return norm_list
    
def topList(a_list, q_list, total_score_list):
    
    #make a df with qs and as and make lex_div the index
    #lex_series = Series(data=a_list, index=lex_div)
    
    #pprint.pprint(total_score_list)
    #print len(total_score_list)
    #print len(q_list), len(a_list)
    #raw_input('test lengths')
    
    
    score_df = DataFrame(data = q_list, index=total_score_list)
    
    score_df[1] = a_list
    #sort by lex div in descending
    score_df = score_df.sort_index(ascending = False)
    
    q_list_sorted = [i for i in score_df[0]]
    a_list_sorted = [i for i in score_df[1]]

    return q_list_sorted, a_list_sorted 
    

def createQASQLTable(author, questions, answers, scores):
   
    #Connect to mySQL
    db=MySQLdb.connect("localhost","root","oilesso","redditdata")
    
    print author
    print questions[0]
    print answers[0]
    print len(answers), len(questions)
    
    #prepare a cursor object using cursor() method
    cursor = db.cursor()    
                
    for i in range(len(questions)):
        #Populate table
        cursor.execute('INSERT INTO QADATATOPVAR(author, question, \
  		answer, score) \
  		VALUES("%s", "%s", "%s", "%d")' % \
  		(author, str(questions[i]), str(answers[i]), scores[i]))     

    db.commit()  #commit changes
    db.close()   #close database



def mean(numberList):
    if len(numberList) == 0:
        return float('nan')
 
    floatNums = [float(x) for x in numberList]
    return sum(floatNums) / len(numberList)




def main():

    #Use praw to get Reddits and put objects into list
    reddit_list = getReddits(NUM_REDDITS)
    
    #Put info (author, title, url, ...) for all reddits into a tuple
    reddit_list_tuple = createRedditTuple(NUM_REDDITS, reddit_list)
    #pprint.pprint(reddit_list_tuple)
    
    #Create the Global SQL Reddit Table
    #createRedditSQLTable()
    
    #Populate the Global Reddit Table
    #popRedditTable(NUM_REDDITS, reddit_list_tuple)
    
    #Loop for all reddits to extract comments
    i = 1
    for submission in reddit_list:
        
        author_name = str(submission.author)
        
        #Flatten comments
        flat_comments = praw.helpers.flatten_tree(submission.comments) 
        
        #Extract comments.body, .author, .score into lists
        comment_list, author_list, score_list = commentData(flat_comments)
        #print comment_list
        
        #Label each comment q (quesiton), a (answer) or n (neither)
        qora_list, a_list, q_list, qa_score_list, num_replies_list = qaFinder(comment_list, author_list, author_name, score_list, flat_comments)
               
        #Calculate word count, distince word count and lexical diversity of answers
        word_cnt_list, distword_cnt_list, lex_div_list = wordCntLexDiv(a_list)
        
        #Normalise features that go into calculating score
        norm_lex = normFeat(lex_div_list)
        norm_score = normFeat(qa_score_list)
        #norm_replies = normFeat(num_replies_list)
        
        #Calculate Overall Comment Score based on score, lex diversity
        #maybe use *args for variable length
        total_score_list = scoreCalc(norm_lex, norm_score)
        
        #Find only questions in each comment
        q_only_list = questionFilter(q_list)
                     
                
        #Sort by lex div and other features to find best questions
        q_sorted_list, a_sorted_list = topList(a_list, q_only_list, total_score_list)
        
        q_db  = []
        a_db = []
        score_db = []
        
        for j in range(len(a_list)):
            if q_sorted_list[j] != 'no q':
                q_db.append(q_sorted_list[j])
                a_db.append(a_sorted_list[j])
                score_db.append(total_score_list[j])
                #print q_sorted_list[j]
                print q_db[-1]
                #print a_sorted_list[j]
                print a_db[-1]
                raw_input('enter')
        
     
        #Populate the SQL table with q and a data
        createQASQLTable(author_name, q_db, a_db, score_db)
        
        print "done reddit number " + str(i) + "of" + str(NUM_REDDITS)
        raw_input('done')
        i+=1
 
   
       
main()