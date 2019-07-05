import mysql.connector
import config
import oauth2
import json
import Users
import Tags

def addTweet(cur,parsedJson):
    """
    Function to insert data in tweet and tweet_details table
    :param cur:  cursor
    :param parsedJson: raw content from Twitter api
    :return: None - tweet and tweet_details table are populated
    """
    try:
        dateForm = cleanDate(parsedJson["created_at"])
        try:
            # procedure to insert tweet and its info
            cur.callproc('insert_tweet',
              [str(parsedJson["id"]), '@' + parsedJson["user"]["screen_name"], parsedJson["text"].replace("'", " "),
              parsedJson["entities"]["urls"][0]["expanded_url"], dateForm[0],  dateForm[1],
              str(parsedJson["favorite_count"]),str(parsedJson["retweet_count"])])

            print("TweetAdded")

        except IndexError:
            cur.callproc('insert_tweet',
                         [str(parsedJson["id"]), '@' + parsedJson["user"]["screen_name"],
                          parsedJson["text"].replace("'", " "),
                          'NO_URL', dateForm[0], dateForm[1],
                          str(parsedJson["favorite_count"]), str(parsedJson["retweet_count"])])

            print("TweetAddedException")
    except mysql.connector.errors.IntegrityError:
        print("addtweetException")



def cleanDate(fullDate):
    """
    Function to clean date into date and time
    :param fullDate: Raw format of date
    :return: date and time tuple
    """
    splitDate = fullDate.split(" ");
    formatDate = str(splitDate[5]) + " " + str(splitDate[1]) + " " + str(splitDate[2])
    return [formatDate, splitDate[3]]


def search_tweets(cnx, user_input,list,count):
    """
    Function to search tweets with given query
    :param cnx: Connection object
    :param user_input: Domain to search tweets in
    :param list: tags associated with the domain
    :param count: Number of tweets to be returned
    :return: None-  Tweets and Users are added to the database
    """
    cur = cnx.cursor(buffered=True)
    searchUrl="https://api.twitter.com/1.1/search/tweets.json?"
    countPart="count="+str(count)+"&"
    for x in list:
        finalUrl= searchUrl+countPart+"q="+x
        getJson = connectToTwitter(finalUrl, "GET", b"", None)
        parsedJson = json.loads(getJson)

        for i in range(len(parsedJson["statuses"])):
            try:
                Users.addUsers(cur,parsedJson["statuses"][i])
                cnx.commit()
                addTweet(cur,parsedJson["statuses"][i])
                cnx.commit()
            except:
                print("user or tweet skipped")
                break

            Tags.addTweetTags(cnx,user_input,parsedJson["statuses"][i])

    Tags.removeTagDuplicates(cnx)
    cnx.commit()
    cnx.close()


def connectToTwitter(url, type, post_body, http_headers):
    """
    Function to establish connection with Twitter API. OAuth2 is used for authentication
    :param url: Url to access request
    :param type: Type of request GET/ POST
    :param post_body: data to be sent with request
    :param http_headers:  headers of the reques
    :return: content from the twitter api
    """

    http_method = type
    consumer = oauth2.Consumer(key=config.api_key, secret=config.api_secret_key)
    token = oauth2.Token(key=config.api_access_token, secret=config.api_access_token_secret)
    client = oauth2.Client(consumer, token)
    resp, content = client.request(url, method=http_method, body=post_body, headers=http_headers)

    return content