import mysql.connector
from mysql.connector.errors import Error


# 1. Machine Learning and AI
# 2. Databases
# 3. Software engineering
# 4. Programming
# 5. Cloud Computing
def defineDomain(user_input):
    """
    Dictionary for mapping topics with tags for starting the search. These tags are updated in the database
    :param user_input: Domain id
    :return: list of tags and domain id
    """
    if user_input == 1:
        tags_list = (['datascience', 'ArtificialIntelligence', 'Machinelearning', 'BigData', 'deepLearning', 'neuralnetworks', 'Automation'])
    elif user_input == 2:
        tags_list = (['databases', 'sql', 'nosql', 'DBA', 'PostgreSQL', 'Backup','blockchain' ])
    elif user_input == 3:
        tags_list = (['softwaredevelopement','developers', 'webdevelopement','opensource','mobileappdevelopement'])
    elif user_input == 4:
        tags_list =(['programming','coding','java','python','ruby','golang'])
    elif user_input == 5:
        tags_list = (['CloudComputing', 'Azure','AWS', 'datacenters', 'iot'])
    else:
        return False
    return user_input, tags_list

def connectToDatabase(config):
    """
    Function to establish connection with database
    :param config: Database config
    :return: Connection object
    """
    try:
        cnx = mysql.connector.connect(**config)
        print("database connected")
        return cnx
    except Error:
        print("Error occured: ", str(Error()))
        return False

