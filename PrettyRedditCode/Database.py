import MySQLdb

class Database(object):
    """creates and populates both reddit and comment MySQL table"""
    
    def __init__(self, db_host = 'localhost', db_user = 'root', 
                   db_pass = '', db_name = 'test'):
        
        self.db=MySQLdb.connect(db_host,db_user,db_pass, db_name)
    
    
    def create_reddit_table(self, reddit_table_name = 'reddit_table'):
        """Create global reddit table"""
        
        #prepare a cursor object using cursor() method
        cursor = self.db.cursor()
        
        #Prepare the SQL Command
        sql_command = """CREATE TABLE IF NOT EXISTS %s 
        (id INT PRIMARY KEY AUTO_INCREMENT, 
        author CHAR(100) NOT NULL,
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
        sql_command = """INSERT INTO %s (author, title, url, selftext, score,
        num_comments) VALUES(%s, %s, %s, %s, %d, %d)""" %(table_name, author, title, url, selftext, score, num_comments)
        
        cursor.execute(sql_command)  #execute the sql command
        self.db.commit()  #commit changes
        self.db.close()   #close database
        
        
        
def main():
    
    #Set table names
    reddit_table_name = 'test_reddit_table1'
    comment_table_name = 'test_comment_table2'
        
    #Create tables
    Database().create_reddit_table(reddit_table_name)
    Database().create_comment_table(comment_table_name)
    
    
    
main()
        
