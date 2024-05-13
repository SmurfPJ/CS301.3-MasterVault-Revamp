from pymongo import MongoClient

client = MongoClient('mongodb+srv://Conor:M0ng0DB1@mastervaultdb1.g1a7o98.mongodb.net/?retryWrites=true&w=majority&appName=MasterVaultDB1')

db = client.Test
collection1 = db["Collection 1"]
collection2 = db["Collection 2"]

def id_test():

    searchC1 = collection1.find_one({"name": "Stuwart"})

    if searchC1:
        c1ID = searchC1["_id"]

        c2Target = collection2.find_one({"_id":c1ID})

        if c2Target is None:
            collection2.insert_one({"_id":c1ID})
            print("Inserted new post.")
        else:
            print("Post already exists.")
    
    else:
        print("No dice")

id_test()