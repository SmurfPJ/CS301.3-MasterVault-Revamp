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
    user_data = passwords.find_one({'_id': c1ID})
    print("Found account")

    for i in user_data:
        print(i)
    
    if not user_data:
        print("Not user_data")
        return []

    user_accounts = []
    current_list = []

    # Exclude the '_id' field and process the remaining fields
    for key, value in user_data.items():
        if key == '_id':
            continue  # Skip the '_id' field
        
        print(f"Processing field: {key} with value: {value}")
        
        current_list.append(value)  # Store only the value
        
        # If the current list reaches the specified length, add it to user_accounts and start a new list
        if len(current_list) == ACCOUNT_METADATA_LENGTH:
            user_accounts.append(current_list)
            current_list = []
    
    # Add the remaining items if the last list is not empty
    if current_list:
        user_accounts.append(current_list)

    # Sort each sublist (no need to sort since there are no keys, but keeping it for completeness)
    # for sublist in user_accounts:
    #     sublist.sort()

    print("User Accounts: ", user_accounts)
    
    # Print the first list, if it exists
    if user_accounts:
        print("First list:", user_accounts[0])
        print("Item 10: ", user_accounts[1][2])

    return user_accounts

# def old_get_passwords(user):
#     # Open csv file
#     file = open('userData.csv')
#     type(file)
#     csvreader = csv.reader(file)
#     for csvAccount in csvreader:  # Reads each account in csv
#         if user == csvAccount[0]:  # Checks if account matches user
#             userAccounts = []
#             # Splits account data into lists of size 3 (In pattern [website, email, password])
#             for accountDataIdx in range(len(csvAccount) - 1):
#                 dataChunk = csvAccount[accountDataIdx + 1]
#                 dataChunk = dataChunk
#                 if accountDataIdx % (ACCOUNT_METADATA_LENGTH) == 0:
#                     userAccounts.append([])
#                 userAccounts[-1].append(dataChunk)

#             userAccounts.sort(key=lambda x: x[0])  # Sorts data alphabetically by website
#             return userAccounts
#     return []

get_passwords('66456a65417af5ad6573f760')