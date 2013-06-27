import pandas.io.sql as psql
import MySQLdb
#THis gets the global reddit table from sql

         
def getGlobalData():
    #Connect to database       
    mysql_cn=MySQLdb.connect("localhost","root","awsmysql","redditdata")

    #Get global reddit data in a dataframe                                               
    global_df = psql.frame_query('select * from topvariety;', con=mysql_cn)
                      
    mysql_cn.close()


    return(global_df)

