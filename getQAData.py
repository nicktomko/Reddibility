import pandas.io.sql as psql
import MySQLdb
import pprint

         
def getQAData(author_name):
    #Connect to database       
    mysql_cn=MySQLdb.connect("localhost","reddibility","awsmysql","redditdata")
    
    query_text =  "select QUESTION, ANSWER from QADATATOPVAR where AUTHOR = '%s' ORDER BY SCORE" %(author_name)
            
    #Get global reddit data in a dataframe                                               
#    qa_df = psql.frame_query("select QUESTION, ANSWER from QADATA where AUTHOR = '%s'", con=mysql_cn)  %(author_name)h
    qa_df = psql.frame_query(query_text, con=mysql_cn)


                                                          
    mysql_cn.close()


    return(qa_df)

#qa_df = getQAData('BobMetcalfe')

#print qa_df['QUESTION'][0]