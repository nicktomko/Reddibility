#Create class to interact with reddit api

import praw

class Reddit:
   
    def __init__(self, user_agent = "Insight Project 3.0 by /u/ N Tomko"):
        # Create the user agent object
        self.r=praw.Reddit(user_agent=user_agent)
        
    
    def getSingle(self, url):
        #This will get single reddits and return the reddit obj generator
        
        return self.r.get_submission(url = url)
    
    def getMultipleTop(self, num_reddits):
        #This will get multipl top reddits and return the reddit obj generator
        
        return self.r.get_subreddit('IAmA').get_top_from_year(limit=num_reddits)
    
    #def listReddit(self, reddit_generator):
    #    #Converts a reddit genertor into a list
    #    
    #    if type(reddit_generator) == praw.objects.Submission:
    #        reddit_list = [reddit_generator]
    #    else:
    #        reddit_list = [reddit for reddit in reddit_generator]                                   
    #    
    #    return reddit_list
    

    @staticmethod    
    def listReddit(reddit_generator):
        reddit_list = [reddit_generator]
        
        return reddit_list


def main():
    
    r = Reddit()
    reddit_obj = r.getSingle('http://www.reddit.com/r/IAmA/comments/1ezafj/im_roger_federer_a_professional_tennis_player/')
    reddit_l = Reddit.listReddit(reddit_obj)    

    
    #reddit_list = r.listReddit(reddit_obj)

         
main()
         
