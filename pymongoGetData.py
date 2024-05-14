from pymongo import MongoClient

client = MongoClient('mongodb+srv://Conor:M0ng0DB1@mastervaultdb1.g1a7o98.mongodb.net/?retryWrites=true&w=majority&appName=MasterVaultDB1')

db = client.Test
collection = db["Collection 1"]


def find_database():
    
   results = collection.find({"name":"Stuwart"})

   for result in results:
      print(result["_id"])
   
   results = collection.find({"email":"stuwart@email"})

   for x in results:
      print(x)

   print(results)

# find_database()



def post_database():
    
   # post1 = {"name": "Greg", "email": "filler@email"}
   # post2 = {"name": "Stuwart", "email": "filler@email"}

   # collection.insert_many([post1, post2])

   query = {"name": "Stuwart"}
   existing_post = collection.find_one(query)
   
   if existing_post:
      new_variables = {}

      if 'Username' in existing_post:
         i = 1

         while True:
               new_username = f"Username{i}"
               new_password = f"Password{i}"

               if new_username not in existing_post and new_password not in existing_post:
                  new_variables[new_username] = "name"
                  new_variables[new_password] = "12345"
                  break
               i += 1

      else:
         new_variables["Username"] = "name"
         new_variables["Password"] = "12345"

      print(new_variables)

      new_data = {"$set": new_variables}
      collection.update_one(query, new_data)
      
      print("Post updated successfully.")
      
   else:
      print("Post with name 'Stuwart' not found.")

post_database()