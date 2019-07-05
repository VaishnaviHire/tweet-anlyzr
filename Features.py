from textblob import TextBlob
import re
import nltk, string
from sklearn.feature_extraction.text import TfidfVectorizer

"""
Following functions are defined to analyze tweets and users. The analysis includes similarity between tweets, similarity
between users, influence of a user, sentiments regarding a user and determining how viral is the user
"""

def tagsAssoPerson(cnx,person,domain):
    """
    Function to determine tags related to a person in the given domain
    :param cnx: connection object
    :param person: user with whom the tags are associated
    :param domain: domain id of the desired topic
    :return: list of tags associated with the user
    """
    cursor = cnx.cursor()
    cursor2 = cnx.cursor()
    # procedure to determine user tags associated with domain
    cursor.callproc('associated_tags',[person, domain])
    result = []
    for result1 in cursor.stored_results():
        for row in result1.fetchall():
            getTag="select tag_details from tags where tagId='"+str(row[0])+"'"
            cursor2.execute(getTag)
            tagName = cursor2.fetchone()
            result.append(tagName[0])
        if result:
            return result
        return ["None Found"]



def similarUsers(cnx,userHandle,domain):
    """
    Function to determine similar users with respect to given user
    :param cnx: connection object
    :param userHandle: userid of the given user
    :param domain: domain id
    :return: list of users similar to given user
    """
    cursor = cnx.cursor()
    cursor2 = cnx.cursor()

    cursor.callproc('associated_tags', [userHandle, domain])
    referenceSet= set()
    for result1 in cursor.stored_results():
        for row in result1.fetchall():
            referenceSet.add(row[0])

    userQuery="SELECT userId from users where userId<>'"+userHandle+"'"

    Result=set()
    cursor.execute(userQuery)
    for row in cursor.fetchall():
        compareSet=set()
        compareQuery = "SELECT tagId from user_tags where userId='"+row[0]+"'"
        cursor2.execute(compareQuery)
        for row2 in cursor2.fetchall():
            compareSet.add(row2[0])

        # intersection between associated tags and user tags, if they match users might be similar
        resultSet= referenceSet.intersection(compareSet)
        a1=float(len(resultSet))
        a2=float(len(referenceSet))

        try:
            accr= a1/a2
            if accr > 0.1:
                Result.add(row[0])
        except ZeroDivisionError:
            a=0

    result = []
    for x in Result:
        result.append(x)

    if(len(Result)==0):
        result.append("None Found")

    return result





def clean_tweet(tweet):
    """
    Simple function to clean tweet content to include text and numbers
    :param tweet: raw tweet content
    :return: tweet text
    """
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])| (\w+:\ / \ / \S+)", " ", tweet).split())



def peopleSaying(cnx,userAcc):
    """
    Function to calculate other users` sentiments for a given user
    :param cnx: connection object
    :param userAcc: user account to be analyzed
    :return: Positive / Negative / Neutral sentiment for the user
    """
    cursor = cnx.cursor()

    # procedure to retrieve informaion regarding tweets from the user
    cursor.callproc('all_tweet_info',[])

    resS= set()
    mentions=[]

    for result1 in cursor.stored_results():
        for row in result1.fetchall():
            if userAcc in row[0].lower():
                resS.add(row[0])

    # tweets in which the user is mentioned by other users
    print ("\nPopular Mentions :\n")
    i=0
    senti=0
    for x in resS:
        if i < 3:
            mentions.append("--->" + x)

        analysis =TextBlob(clean_tweet(x))
        # Use polarity function to calculate the sentiment
        senti+= analysis.sentiment.polarity
        i+=1


    if senti  > 0:
        sentiment =  ('Net Sentiment about '+ userAcc+' is Positive')
    elif senti  == 0:
        sentiment = ('Net Sentiment '+ userAcc+' is Neutral')
    else:
        sentiment = ('Net Sentiment '+ userAcc+' is Negative')

    return mentions,sentiment


## Functions defined below help in finding similar tweets

stemmer = nltk.stem.porter.PorterStemmer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)

# Stemming is used to extract only meaningful parts of the sentence
def stem_tokens(tokens):
    return [stemmer.stem(item) for item in tokens]

# remove punctuation, lowercase, stem
def normalize(text):
    return stem_tokens(nltk.word_tokenize(text.lower().translate(remove_punctuation_map)))

# Converts raw documents into features
vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')


def cosine_sim(text1, text2):
    """
    Function to find cosine similarity between given two texts
    :param text1: text or string
    :param text2: text or string
    :return: similarity score between two texts
    """
    tfidf = vectorizer.fit_transform([text1, text2])
    return ((tfidf * tfidf.T).A)[0,1]


def postLikeMine(cnx, referenceTweet):
    """
    Function to find tweet similar to the text entered by the user
    :param cnx: connection object
    :param referenceTweet: Text or string entered by the user
    :return: list of similar tweets in the database
    """
    cursor = cnx.cursor()

    # procedure to find tweet content to analyze
    cursor.callproc('similar_tweets',[])
    resS = set()
    result = []
    for result1 in cursor.stored_results():
        for row in result1.fetchall():
            simRating = cosine_sim(clean_tweet(referenceTweet), clean_tweet(row[0]))
            if simRating > 0.25:
                resS.add(row)

    if len(resS)==0:
        result.append("No Similar Tweets found")

    for row in resS:
        result.append(row[2])
    return result



def whatsMyInfluence(cnx, usrnm):
    """
    Function to calculate how user influeneces other users
    :param cnx: connection object
    :param usrnm: user to be analyzed for influence
    :return: String determining if user is a Low, moderate or High influence
    """
    cursor2 = cnx.cursor()
    # Stored function to calculate ratio between user followers and number of users the given user handle is following
    getTag = "select calculate_influence(%(tagid)s)"
    cursor2.execute(getTag, {'tagid': usrnm})
    ratio = cursor2.fetchone()[0]
    print("This is rato", ratio)

    # procedure to calculate average retweets, favorites for given user
    cursor2.callproc('user_analysis', [usrnm])

    for re in cursor2.stored_results():
        rtfavd = re.fetchone()
        break

    infPerTweet = ratio*(float((rtfavd[1]+rtfavd[2])/2))

    if infPerTweet < 8:
        print(infPerTweet)
        influence = ("Low Influence")
    if 8<infPerTweet < 15:
        print(infPerTweet)
        influence = ("Moderate Influence")
    else:
        print(infPerTweet)
        influence = ("Highly Influencial ")

    return influence



def viralUserTweets(cnx,usrnm):
    """
    Function to determine if the user is viral or not
    :param cnx: connection object
    :param usrnm: user to be analyzed
    :return: the viral value of the user
    """
    cursor2 = cnx.cursor()

    cursor2.callproc('user_analysis', [usrnm])
    for re in cursor2.stored_results():
        rtfavd = re.fetchone()
        break

    avgdetails= float((rtfavd[1]+rtfavd[2])/2)

    if avgdetails<15:
        viral = ("User is not Viral")
    if 15<avgdetails<100:
        viral = ("User is Moderately Viral")
    if avgdetails>100:
        viral = ("User is Highly Viral ")
    return viral




def topTen(cnx, domain):
    """
    Given a domain, the function determines top tweets
    :param cnx: connection object
    :param domain: id of the domain to be considred
    :return: List of tweets and list of users who retweeted those tweets
    """
    cursor = cnx.cursor()
    # procedure to calculate top tweets taking intop account stored users, retweets and follower and following counts
    cursor.callproc('top_tweets_of_domain',[domain])

    result =[]
    userlist = []
    for result1 in cursor.stored_results():
        for row in result1.fetchall():
            result.append(row[1])
            userlist.append(row[0])

    return (list(dict.fromkeys(result)))[:6], userlist[:6]

def remove_tweet(cnx, tweet_id):
    """
    Function to delete flagged tweets
    :param cnx: connection object
    :param tweet_id: tweet to be removed
    :return: None
    """
    cursor = cnx.cursor()
    output1 = "DELETE FROM tweet WHERE tweetId = " + str(tweet_id)

    # A trigger is initiated to add deleted tweet to backup table
    cursor.execute(output1)
    cnx.commit()







