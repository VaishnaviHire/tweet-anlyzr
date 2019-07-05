import mysql.connector


def addUsers(cur, parsedJson):
    """
    Function to insert new user or update existing users
    :param cur: cursor
    :param parsedJson: raw data from API
    :return:
    """
    try:
        # procedure to insert new data into users table
        cur.callproc('insert_users',['@' + parsedJson["user"]["screen_name"], parsedJson["user"]["name"].replace("'", " "),
                                     str(parsedJson["user"]["followers_count"]),
                                     str(parsedJson["user"]["friends_count"]),str(parsedJson["user"]["statuses_count"]) ])
        print("userAdded", '@' + parsedJson["user"]["screen_name"])
    except mysql.connector.errors.IntegrityError:

        # if we are trying to add same user to database again this except block occurs.
        # here we will update the user if that particular user's followers and following and tweet count is changed

        # procedure to update existing entries in users table
        cur.execute(
            "UPDATE users SET follower_count=" + str(parsedJson["user"]["followers_count"]) + " , following_count= " + str(
                parsedJson["user"]["friends_count"]) +
            ", tweet_count=" + str(parsedJson["user"]["statuses_count"]) + "  WHERE userId='+" + '@' +
            parsedJson["user"]["screen_name"] + "'")
        # cur.callproc('update_users',[str(parsedJson["user"]["followers_count"]),str(parsedJson["user"]["friends_count"]),
        #                              str(parsedJson["user"]["statuses_count"]),'@'+parsedJson["user"]["screen_name"]])

        print("UserUpdated")


