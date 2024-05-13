from pymongo import MongoClient

client = MongoClient('mongodb+srv://Conor:M0ng0DB1@mastervaultdb1.g1a7o98.mongodb.net/?retryWrites=true&w=majority&appName=MasterVaultDB1')

db = client.Test
collection = db["Collection 1"]


# def find_database():
    
#    results = collection.find({"name":"Stuwart"})

#    for result in results:
#       print(result["_id"])
   
   # results = collection.find({"email":"stuwart@email"})

   # for x in results:
   #    print(x)

   # print(results)

# find_database()

def post_database():

   # post1 = {"name": "Greg", "email": "filler@email"}
   # post2 = {"name": "Stuwart", "email": "filler@email"}

   # collection.insert_many([post1, post2])

   query = {"name":"Stuwart"}
   existing_post = collection.find_one(query)

   if existing_post:
      
      new_data = {"$set":{"Username":"name"}}
      collection.update_one(query, new_data)

      print("Post updated successfully.")

   else:
      print("Post with name 'Stuwart' not found.")

post_database()