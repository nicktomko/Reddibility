#!/usr/bin/env python

import os
import pandas as pd
from pandas import Series, DataFrame
from flask import Flask
from flask import url_for
from flask import render_template
from flask import jsonify
from flask import request
import flaskPass
import getGlobalData
import getQAData

app = Flask(__name__)


@app.route('/')
def index():
    
    #Get global reddit dataframe
    global_df = getGlobalData.getGlobalData()  
    
    
    return render_template('index.html', title="MyTitle", global_df = global_df)




@app.route('/test',methods=['GET','POST'])
def test():
    print "Seeems to work"
    print request.form['fname']
    return render_template('test.html', 
                           my_name=request.form['fname'],
                           my_locations=[3, 4, 5, 6, 7, 8, 9, 10])



@app.route('/dropdown',methods=['GET','POST'])
def test():
    
    #Get global reddit dataframe
    global_df = getGlobalData.getGlobalData() 
    
    print "Seeems to work"
    print request.form['mySelect']
    reddit_title = str(request.form['mySelect'])
    title_no_space = reddit_title.replace(" ", "")
    reddit_id = 'reddit_id'
    
    for i in range(len(global_df)):
        df_no_space = global_df['TITLE'][i].replace(" ", "")
        if df_no_space == title_no_space:
            reddit_id = global_df['AUTHOR'][i]        
    
    #Get QA Data
    qa_df = getQAData.getQAData(reddit_id)
        
    author = 'bob'
    questions = 'questions'
    answers = 'answers'


    
    return render_template('test.html', 
                           my_locations=[3, 4, 5, 6, 7, 8, 9, 10],
                           reddit_title=reddit_title, reddit_id = reddit_id,
                           author=author, questions=questions,
                           answers=answers, qa_df = qa_df)



@app.route('/about')
def about():
          
    return render_template('about.html')


@app.route('/contact')
def contact():
          
    return render_template('contact.html')





if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    #port = int(os.environ.get('PORT', 5000))
    #app.debug = True
    app.run(host='0.0.0.0', port=80)
    #app.run()
