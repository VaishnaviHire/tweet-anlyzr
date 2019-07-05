from flask import Flask,request,session
import config
import Connection
import Tweets
import Features
from flask import render_template

application = Flask(__name__)

# application.secret_key = config.tweet_analyzer_app_secret




@application.route('/', methods=['GET','POST'])
def home_page():
    """
    Controller for accessing different domains and creating tweet and user objects
    :return: homepage template
    """
    cnx = Connection.connectToDatabase(config.db_config)
    if request.method == 'POST':
        if 'ML' in request.form:
            Tweets.search_tweets(cnx,1,Connection.defineDomain(1)[1],5)
            session["domain"] = 1
            cnx2 = Connection.connectToDatabase(config.db_config)
            toptweets = Features.topTen(cnx2, 1)
            return render_template('tweetTest.html', your_list=toptweets[0] , userlist = toptweets[1])
        elif 'DB' in request.form:
            Tweets.search_tweets(cnx,2,Connection.defineDomain(2)[1],5)
            session["domain"] = 2
            cnx2 = Connection.connectToDatabase(config.db_config)
            toptweets = Features.topTen(cnx2, 2)
            return render_template('tweetTest.html', your_list=toptweets[0] , userlist = toptweets[1])
        elif 'SE' in request.form:
            Tweets.search_tweets(cnx,3,Connection.defineDomain(3)[1],5)
            session["domain"] = 3
            cnx2 = Connection.connectToDatabase(config.db_config)
            toptweets = Features.topTen(cnx2, 3)
            return render_template('tweetTest.html',your_list=toptweets[0] , userlist = toptweets[1])
        elif 'PR' in request.form:
            Tweets.search_tweets(cnx,4,Connection.defineDomain(4)[1],5)
            session["domain"] = 4
            cnx2 = Connection.connectToDatabase(config.db_config)
            toptweets = Features.topTen(cnx2, 4)
            return render_template('tweetTest.html', your_list=toptweets[0] , userlist = toptweets[1])
        elif 'CC' in request.form:
            Tweets.search_tweets(cnx,5,Connection.defineDomain(5)[1],5)
            session["domain"] = 5
            cnx2 = Connection.connectToDatabase(config.db_config)
            toptweets = Features.topTen(cnx2, 5)
            return render_template('tweetTest.html', your_list=toptweets[0] , userlist = toptweets[1])
    elif request.method == 'GET':
        return render_template('home.html')

@application.route('/flag', methods=['POST'])
def flag_tweet():
    """
    Controller which handles tweet delete.
    :return: same page i.e refreshes the page
    """
    cnx = Connection.connectToDatabase(config.db_config)
    if request.method == 'POST':
        Features.remove_tweet(cnx,list(request.form.keys())[0])
        cnx2 = Connection.connectToDatabase(config.db_config)
        toptweets = Features.topTen(cnx2,session.get("domain",None))
        return render_template('tweetTest.html',your_list= toptweets[0],userlist=toptweets[1])



@application.route('/searchtweet', methods=['POST'])
def search_tweet():
    """
    Controller to search similar tweets.
    :return: Page displaying all similar tweets
    """
    cnx = Connection.connectToDatabase(config.db_config)
    if request.method == 'POST':
        text = request.form['text']
        search_list= Features.postLikeMine(cnx,text)
        return render_template('searchtweet.html', search_list=search_list)

@application.route('/analyzeusers', methods=['POST'])
def analyze_user():
    """
    Controller to display all the analyze features available for user
    :return: corresponding page to features list
    """
    if request.method == 'POST':
        text = request.form['username']
        session["user"] = text
        return render_template('analyzeusers.html')

@application.route('/userfeatures', methods=['POST'])
def user_features():
    """
    Controller which handles features like similar users, sentiment analysis, associated tags
    :return: corresponding page according to user`s selection of feature
    """
    cnx = Connection.connectToDatabase(config.db_config)
    if request.method == 'POST':
        if 'SU' in request.form:
            users_list = Features.similarUsers(cnx,session.get("user",None),session.get("domain",None))
            return render_template('similarusers.html', users_list=users_list)
        elif 'AT' in request.form:
            tags_list = Features.tagsAssoPerson(cnx,session.get("user",None),session.get("domain",None))
            return render_template('associatedtags.html', tags_list=tags_list)
        elif 'PS' in request.form:
            mentions, sentiment  = Features.peopleSaying(cnx,session.get("user",None))
            influence = Features.whatsMyInfluence(cnx,session.get("user",None))
            viral = Features.viralUserTweets(cnx,session.get("user",None))
            return render_template("sentiment.html",mentions=mentions,sentiment=sentiment,influence=influence, viral=viral)


if __name__ == '__main__':
    application.run()
