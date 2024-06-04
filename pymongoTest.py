from pymongo import MongoClient
import csv

client = MongoClient('mongodb+srv://Conor:M0ng0DB1@mastervaultdb1.g1a7o98.mongodb.net/?retryWrites=true&w=majority&appName=MasterVaultDB1')

db = client.MasterVault
collection1 = db["userData"]
collection2 = db["Collection 2"]
passwords = db["userPasswords"]

searchC1 = collection1.find_one({"username": "Conor"})
c1ID = searchC1["_id"]

ACCOUNT_METADATA_LENGTH = 7

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

# password_test()


def get_passwords(user_id):
    # Connect to MongoDB

    # Find user by _id
    userData = passwords.find_one({'_id': c1ID})
    print("Found account")

    for i in userData:
        print(i)
    
    if not userData:
        print("Not userData")
        return []

    userAccounts = []
    currentList = []

    # Exclude the '_id' field and process the remaining fields
    for key, value in userData.items():
        if key == '_id':
            continue  # Skip the '_id' field
        
        print(f"Processing field: {key} with value: {value}")
        
        currentList.append(value)  # Store only the value
        
        # If the current list reaches the specified length, add it to userAccounts and start a new list
        if len(currentList) == ACCOUNT_METADATA_LENGTH:
            userAccounts.append(currentList)
            currentList = []
    
    # Add the remaining items if the last list is not empty
    if currentList:
        userAccounts.append(currentList)

    # Sort each sublist (no need to sort since there are no keys, but keeping it for completeness)
    # for sublist in userAccounts:
    #     sublist.sort()

    print("User Accounts: ", userAccounts)
    
    # Print the first list, if it exists
    if userAccounts:
        print("First list:", userAccounts[0])
        print("Item 10: ", userAccounts[1][2])

    return userAccounts

# get_passwords('66456a65417af5ad6573f760')



def mongodbIf():

    print(searchC1.get('accountLocked'))

    if searchC1.get('accountLocked') == False:
        print("Statement is detecting False")

mongodbIf()