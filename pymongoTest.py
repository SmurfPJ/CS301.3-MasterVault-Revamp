from pymongo import MongoClient

client = MongoClient('mongodb+srv://Conor:M0ng0DB1@mastervaultdb1.g1a7o98.mongodb.net/?retryWrites=true&w=majority&appName=MasterVaultDB1')

db = client.Test
collection1 = db["Collection 1"]
collection2 = db["Collection 2"]
passwords = db["Password Test"]

searchC1 = collection1.find_one({"name": "Stuwart"})

def copy_id_test():

    if searchC1:
        c1ID = searchC1["_id"]

        c2Target = passwords.find_one({"_id":c1ID})

        if c2Target is None:
            passwords.insert_one({"_id":c1ID})
            print("Inserted new post.")
        else:
            print("Post already exists.")
    
    else:
        print("No dice")

# copy_id_test()



def password_test():

    if searchC1:
        ID = searchC1["_id"]

        passwordID = passwords.find_one({"_id":ID})

        if passwordID is None:
            passwords.insert_one({"_id":ID})
            print("Inserted new post.")
        else:
            print("Post already exists.")


#    results = collection1.find({"name":"Stuwart"})

#    for result in results:
#       print(result["_id"])
   
#    results = collection.find({"email":"stuwart@email"})

#    for x in results:
#       print(x)

#    print(results)

password_test()