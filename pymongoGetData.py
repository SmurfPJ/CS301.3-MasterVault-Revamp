from pymongo import MongoClient
def get_database():
 
   client = MongoClient('mongodb+srv://Conor:<password>@mastervaultdb1.g1a7o98.mongodb.net/?retryWrites=true&w=majority&appName=MasterVaultDB1')

   db = client.sample_mflix
   comments_collection = db.comments

   first = comments_collection.find_one()

   print(first)

get_database()

#    # Provide the mongodb atlas url to connect python to mongodb using pymongo
#    CONNECTION_STRING = "mongodb+srv://Conor:<password>@mastervaultdb1.g1a7o98.mongodb.net/?retryWrites=true&w=majority&appName=MasterVaultDB1"
 
#    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
#    client = MongoClient(CONNECTION_STRING)
 
#    # Create the database for our example (we will use the same database throughout the tutorial
#    return client['user_shopping_list']
  
# # This is added so that many files can reuse the function get_database()
# if __name__ == "__main__":   
  
#    # Get the database
#    dbname = get_database()