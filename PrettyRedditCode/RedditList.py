import praw
import unicodedata

class RedditList(object):
 
      
    def __init__(self, user_agent = "Insight Project 3.0 by /u/ N Tomko", 
                    url = '', num_reddits=0):
        
        self.num_reddits = num_reddits                    
        r=praw.Reddit(user_agent=user_agent)  #create the user agent
        
        if url:  #if a url is supplied
            print 'yes'
            reddit_gen = r.get_submission(url = url)
            self.reddit_list = [reddit_gen]
        
        else:  #get the top_num
            print 'top num'
            reddit_gen = r.get_subreddit('IAmA').get_top_from_year(limit=num_reddits)
        
            self.reddit_list = [reddit for reddit in reddit_gen]
    
    def __len__(self):
        #special method to output length of list
        return len(self.reddit_list)
        
  
    def to_tuple(self):
        """put author, title, url, self test, score, num comments into a list of 
        tuples, where each tuple is one of the fields listed and get rid of 
        weird characters"""
        
        clean_list = []
  
        for i in range(self.num_reddits):
                    clean_list.append ((str(self.reddit_list[i].author), 
                    str(unicodedata.normalize('NFKD', self.reddit_list[i].title).encode('ascii','ignore')),
                    str(unicodedata.normalize('NFKD', self.reddit_list[i].url).encode('ascii','ignore')),
                    str(unicodedata.normalize('NFKD', self.reddit_list[i].selftext).encode('ascii','ignore')),
                    self.reddit_list[i].score, self.reddit_list[i].num_comments))
    
        return clean_list

            



#Test
def main():
    reddits = RedditList(num_reddits = 5)
    print len(reddits)
    cleaned_reddits = reddits.to_tuple()
    print cleaned_reddits[0][0]


main()
        
        
        
        
            

            
