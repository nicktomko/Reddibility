import praw
import MySQLdb
import unicodedata


class RedditList(object):
    """This class creates a list that contains all the indivdual reddit objects"""
      
    def __init__(self, user_agent = "Insight Project 3.0 by /u/ N Tomko", 
                    url = '', NUM_REDDITS=1):
        
        r=praw.Reddit(user_agent=user_agent)  #create the user agent
        
        if url:  #if a url is supplied then get only a single reddit
            reddit_gen = r.get_submission(url = url)
            self.reddit_list = [reddit_gen]
            self.NUM_REDDITS = 1
        
        else:  #get the top_num from year
            reddit_gen = r.get_subreddit('IAmA').get_top_from_year(limit=NUM_REDDITS)
            self.reddit_list = [reddit for reddit in reddit_gen]
            self.NUM_REDDITS = NUM_REDDITS
    
    def __len__(self):
        #special method to output length of list
        return len(self.reddit_list)
        
  
    def to_tuple(self):
        """put author, title, url, self test, score, num comments into a list of 
        tuples, where each tuple is one of the fields listed and get rid of 
        weird characters"""
        
        clean_list = []
  
        for i in range(self.NUM_REDDITS):
                    clean_list.append ((str(self.reddit_list[i].author), 
                    str(unicodedata.normalize('NFKD', self.reddit_list[i].title).encode('ascii','ignore')),
                    str(unicodedata.normalize('NFKD', self.reddit_list[i].url).encode('ascii','ignore')),
                    str(unicodedata.normalize('NFKD', self.reddit_list[i].selftext).encode('ascii','ignore')),
                    self.reddit_list[i].score, self.reddit_list[i].num_comments))
    
        return clean_list

    def get_list(self):
        return self.reddit_list



class Database(object):
    """creates and populates both reddit and comment MySQL table"""
    
    def __init__(self, db_host = 'localhost', db_user = 'root', 
                   db_pass = 'oilesso', db_name = 'test'):
        
        self.db=MySQLdb.connect(db_host,db_user,db_pass, db_name)
    
    
    def create_reddit_table(self, reddit_table_name = 'reddit_table'):
        """Create global reddit table"""
        
        #prepare a cursor object using cursor() method
        cursor = self.db.cursor()
        
        #Prepare the SQL Command
        sql_command = """CREATE TABLE IF NOT EXISTS %s 
        (id INT PRIMARY KEY AUTO_INCREMENT, 
        author CHAR(100) NOT NULL,
        title TEXT NOT NULL,
        url CHAR(255) NOT NULL, 
        selftext TEXT NOT NULL, 
        score INT,
        num_comments INT)""" %(reddit_table_name)
                
        cursor.execute(sql_command)  #execute the command
        
        self.db.close()  #close the database
    
    def create_comment_table(self, comment_table_name = 'comment_table2'):
        """Create the comments table"""
        
        #prepare a cursor object using cursor() method
        cursor = self.db.cursor()
        
        #Prepare the SQL Command
        sql_command = """CREATE TABLE IF NOT EXISTS %s 
        (id INT PRIMARY KEY AUTO_INCREMENT, 
        author CHAR(100) NOT NULL,
        question TEXT NOT NULL, 
        answer TEXT NOT NULL,
        votes INT, 
        lex_div FLOAT,
        score FLOAT,
        num_comments INT)""" %(comment_table_name)
                
        cursor.execute(sql_command)  #execute the command
        
        self.db.close()  #close the database
        
    
    def pop_global(self, NUM_REDDITS, reddit_tuple, table_name):
        """populate the global data"""
        #still need to test
        
        #prepare a cursor object using cursor() method
        cursor = self.db.cursor()
        
        for i in range(NUM_REDDITS):
        
            author= reddit_tuple[i][0]
            
            title = reddit_tuple[i][1]
            
            url = reddit_tuple[i][2]
            
            selftext = reddit_tuple[i][3]
            
            selftext = selftext.replace('"', "'")  #replace double with single quotes
            #selftext = selftext.replace("'", '') 
            
            score = reddit_tuple[i][4]
            num_comments = reddit_tuple[i][5]
            
            #create the sql command to populate the global reddit table
            cursor.execute('INSERT INTO %s (author, title, \
                url, selftext, score, num_comments) \
                VALUES("%s", "%s", "%s", "%s", "%d", "%d")' % \
                (table_name, author, title, url, selftext, score, num_comments))   
      
        self.db.commit()  #commit changes
        self.db.close()   #close database




class Comments(object):
    """This is the comments class where all the anayslis is done"""
    
    
    def __init__(self, submission):
        self.comments = praw.helpers.flatten_tree(submission.comments)
        self.author_name = str(submission.author)
        
        #Initialise list to keep comments, authors and scores
        self.comment_list = []
        self.author_list = []
        self.score_list = []
        
        self.clean_comment_list = []  #This stores cleaned comments
        
        #Lists used to store questions and answers
        self.q_comments_list = []
        self.a_comments_list = []
        self.qa_score_list = []
        self.qora_list = []
    
    
    def get_comments(self):
        return self.comments
        
        
    
    def more_filter(self):
        """get rid of more comment objects and put comments, author and score 
        into separate lists""" 
        
        for comment in self.comments:
            #Filter out more comments objects    
            if type(comment) == praw.objects.Comment:  
                self.comment_list.append(comment.body)
                self.author_list.append(comment.author)
                self.score_list.append(comment.score)
                
        return self.comment_list, self.author_list, self.score_list
 
       
    def clean_comments(self):
        """This gets rid of weird formatting that causes MySQL issues"""
        #Need to add URL remover from this
        #Also this shold be executed after I find the q's and a's to speed things up
        
        
        self.clean_comment_list = [item.encode('ascii', 'ignore') for item in self.comment_list]
            
        #Get rid of weird foratting
        self.clean_comment_list = [item.replace('"', "'") for item in self.comment_list]
        #self.clean_comment_list = [item.replace('"', ' ') for item in self.comment_list]
        self.clean_comment_list = [item.replace('...', '.') for item in self.comment_list]
        #self.clean_comment_list = [item.replace("'", '') for item in self.comment_list]
        self.clean_comment_list = [item.replace("\n", ' ') for item in self.comment_list]
        self.clean_comment_list = [item.replace("?!", ' ') for item in self.comment_list]
    
        return self.clean_comment_list 
 
    def qafinder(self):
        """Find qa pairs"""        
        
        a_score_list = []
        q_score_list = []
        
        #delete last two comments because of the funny things they do
        del self.clean_comment_list[-2:]
        del self.author_list[-2:]
        del self.score_list[-2:] 
        
        cnt = 0;  #intialise counter
        
        #Create a list with only questions and answers
        while cnt < (len(self.author_list)-1):  #loop until the second last etnry
            
            #If the current comment is not by the author but the next is then label questin
            if str(self.author_list[cnt]) <> self.author_name and str(self.author_list[cnt+1]) == self.author_name:
                self.qora_list.append('q')
                self.q_comments_list.append(self.clean_comment_list[cnt])
                q_score_list.append(self.score_list[cnt])
    
                cnt+=1  
                
            #Else if the current comment is by the author
            elif str(self.author_list[cnt]) == self.author_name:
                
                #If the author answers quesitons in two parts    
                if str(self.author_list[cnt+1]) == self.author_name and str(self.author_list[cnt+2]) != self.author_name:
                    self.qora_list.append('a')
                    a_combined = self.clean_comment_list[cnt] + ' '+ self.clean_comment_list[cnt+1]   #combine answers
                    self.a_comments_list.append(a_combined)
                    a_score_list.append(self.score_list[cnt]+self.score_list[cnt+1])  #add the score votes togehter
                    cnt+=2           
                
                
                #If three in a row
                elif str(self.author_list[cnt+1]) == self.author_name and str(self.author_list[cnt+2]) == self.author_name:
                    #raw_input('three in a row')
                    self.qora_list.append('a')
                    a_combined = self.clean_comment_list[cnt] + ' ' + self.clean_comment_list[cnt+1] + ' ' + self.clean_comment_list[cnt+2]
                    self.a_comments_list.append(a_combined)
                    a_score_list.append(self.score_list[cnt]+self.score_list[cnt+1] + self.score_list[cnt+2])
                    cnt+=3
                                
                else:  #this is the normal case where the answer is a single comment
                    self.qora_list.append('a')
                    self.a_comments_list.append(self.clean_comment_list[cnt])
                    a_score_list.append(self.score_list[cnt]+self.score_list[cnt])
                    
                    cnt+=1
             
                     
            else:  #Commet is neither a question nor an answer
                self.qora_list.append('n') #if neither question nor answer
                cnt+=1
                
        #Sum q_score and a_score to get a total score (votes) for he q/a combo
        qa_zip = zip(q_score_list, a_score_list)
        self.qa_score_list = [a+b for a,b in qa_zip]  
        
        





def main():

    
    #Table names
    reddit_table_name = 'reddit_table'
    comment_table_name = 'comment_table'
    
    #Create tables
    Database().create_reddit_table(reddit_table_name)
    Database().create_comment_table(comment_table_name)
    
    #Get reddits 
    reddits = RedditList(url = 'http://www.reddit.com/r/IAmA/comments/1hfzt0/i_am_chris_kluwe_nfl_punter_and_i_wrote_a_book/' )
    NUM_REDDITS = reddits.NUM_REDDITS
    reddit_list = reddits.get_list()
    
    #Get rid of unicode and put into list of tuples
    reddit_tuple = reddits.to_tuple()
    
    #Populate Global Reddit table
    Database().pop_global(NUM_REDDITS, reddit_tuple, reddit_table_name)
    
    #Now loop through all reddits
    for submission in reddit_list:
        
        flat_comments_obj = Comments(submission)  #this is the flat_comments object
        author_name = flat_comments_obj.author_name  #this is the reddit author
        comment_list, author_list, score_list = flat_comments_obj.more_filter()
        cleaned_comment_list = flat_comments_obj.clean_comments()
        flat_comments_obj.qafinder()  #find questions and answers
        #Next calculate the lexical diversity of all the answers
                
        
        
    
    
main()
