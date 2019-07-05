import mysql.connector


def addTweetTags(cnx, user_input, parsedJson):
    """
    Function to populate tags , user_tags and tweet_tags tables
    :param cnx: connection object
    :param user_input: domain id
    :param parsedJson: raw data from API
    :return: None - tags , user_tags and tweet_tags tables are populated
    """
    cur = cnx.cursor(buffered=True)

    try:
        for k in range(len(parsedJson["entities"]["hashtags"])):
             hashadd= parsedJson["entities"]["hashtags"][k]["text"]
             # procedure to insert in tags table
             cur.callproc('insert_tags',[hashadd.lower(),user_input])

        cnx.commit()
    except mysql.connector.errors.IntegrityError:
        print("TagAddedException")

    try:
        for k in range(len(parsedJson["entities"]["hashtags"])):



            cur.execute(
                 "select tagId from tags WHERE tag_details='" + parsedJson["entities"]["hashtags"][k]["text"].lower() + "'"
            )
            tweetid=str(parsedJson["id"])
            tagid=str(cur.fetchone()[0])

            print(tagid)
            # procedure to insert in tweet_tags table
            cur.callproc('insert_tweet_tags',[tweetid,tagid])

            userid='@' + parsedJson["user"]["screen_name"]
            print(userid,tagid)
            # procedure to insert in user_tags table
            cur.callproc('insert_user_tags',[userid,tagid])

            cnx.commit()
            print("TweetAndUserTagsAdded")
    except TypeError:
        print("Unsupported Type")



def removeTagDuplicates(cnx):
    cur = cnx.cursor(buffered=True)
    cur.execute("delete  from user_tags where tag_no NOT IN (select * from  (select min(ut.tag_no) from user_tags ut group by ut.userId,ut.tagId) as u) ")
    cnx.commit()
    cur.execute(" delete from tweet_tags where tag_no NOT IN (select * from (select min(tag_no) from tweet_tags group by tweetId,tagId) as t)")
    cnx.commit()


