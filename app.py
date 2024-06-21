from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Mail, Message
from forms import RegistrationForm, LoginForm, AnimalSelectionForm, FamilyRegistrationForm
from dotenv import load_dotenv
from encryption import encrypt, decrypt
from datetime import datetime, timedelta
from pymongo import MongoClient
import random, string, csv, os

# Constants
ACCOUNT_METADATA_LENGTH = 11
client = MongoClient('mongodb+srv://Conor:M0ng0DB1@mastervaultdb1.g1a7o98.mongodb.net/')
db = client.MasterVault
userData = db["userData"]
userPasswords = db["userPasswords"]
temporary_2fa_storage = {} # Temporary storage for 2FA codes

# Encrypt data
# def encryptData():

#     file = open('userData.csv')
#     type(file)
#     csvreader = csv.reader(file)
#     for csvAccount in csvreader:
#         for accountDataIdx in range(len(csvAccount) - 1):
#                 dataChunk = csvAccount[accountDataIdx + 1]

# Database paths
writeToLogin = open('loginInfo', 'w')

app = Flask(__name__)
mail = Mail(app)
load_dotenv()

app.config['SECRET_KEY'] = '47a9cee106fa8c2c913dd385c2be207d'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'nickidummyacc@gmail.com'
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
mail = Mail(app)



def setSessionID(userID):
    global sessionID
    sessionID = userID



def generate_password(keyword, length, use_numbers, use_symbols, replace_vowels, replace_most_frequent_vowel, remove_vowels, randomize):
    characters = string.ascii_letters  # Always use letters

    if use_numbers:
        characters += string.digits

    if use_symbols:
        characters += string.punctuation

    # Ensure the password is at least as long as the keyword
    if length < len(keyword):
        return ""

    # Apply transformations
    if replace_vowels:
        keyword = keyword.replace('a', '@').replace('e', '3').replace('i', '1').replace('o', '0').replace('u', 'u')

    if replace_most_frequent_vowel:
        most_frequent_vowel = max(set(keyword), key=keyword.count)
        if most_frequent_vowel in 'aeiou':
            keyword = keyword.replace(most_frequent_vowel, 'x')

    if remove_vowels:
        keyword = ''.join([char for char in keyword if char not in 'aeiou'])

    if randomize:
        keyword = ''.join(random.sample(keyword, len(keyword)))

    # Add random characters to the keyword until desired length is reached
    while len(keyword) < length:
        keyword += random.choice(characters)

    # Pattern is basically every third character from the keyword (subjected to change)
    password = ""
    for i in range(length):
        if i % 3 == 0 and i // 3 < len(keyword):
            password += keyword[i // 3]
        else:
            password += random.choice(characters)

    return password



def getPasswords():
    searchPasswords = userPasswords.find_one({'_id': sessionID})
    userList = []
    currentList = []

    searchPasswords = userPasswords.find_one({"_id": sessionID})

    if searchPasswords == None:
        userPasswords.insert_one({"_id": sessionID})

    if not searchPasswords:
        print("No userData found")
        return []

    for key, value in searchPasswords.items():
        if key == '_id':
            continue  # Skip the '_id' key

        print(f"Processing field: {key} with value: {value}")
        currentList.append(value)  # Store value to the list

        # If the account reaches the max length, add the list to userList
        if len(currentList) == ACCOUNT_METADATA_LENGTH:
            userList.append(currentList)
            currentList = []

    # Add the remaining items if the last list is not empty
    if currentList:
        userList.append(currentList)


    print("User Accounts: ", userList)
    return userList



def check_password_strength(password):
    strength = {'status': 'Weak', 'score': 0, 'color': 'red'}

    # Check if password is None or empty and return weak strength immediately
    if not password:
        return strength

    if len(password) >= 8:
        strength['score'] += 1

    if any(char.isdigit() for char in password):
        strength['score'] += 1

    if any(char.isupper() for char in password):
        strength['score'] += 1

    if any(char in string.punctuation for char in password):
        strength['score'] += 1

    # Update status and color based on score
    if strength['score'] == 4:
        strength['status'] = 'Very Strong'
        strength['color'] = 'green'
    elif strength['score'] == 3:
        strength['status'] = 'Strong'
        strength['color'] = 'lightgreen'
    elif strength['score'] == 2:
        strength['status'] = 'Moderate'
        strength['color'] = 'orange'
    elif strength['score'] == 1:
        strength['status'] = 'Weak'
        strength['color'] = 'red'

    return strength



@app.route('/create_password', methods=['GET'])
def create_password():
    # Default values for initial page load
    return render_template('createPassword.html')  # , password="", keyword="", length=8, use_numbers=False, use_symbols=False



@app.route('/create_password', methods=['POST'])
def handle_create_password():
    # Initialize variables
    password = ""
    strength = None
    error = None
    keyword = request.form.get('keyword')
    length = int(request.form.get('length', 8))  # Provide a default value in case it's not set
    use_numbers = 'numbers' in request.form
    use_symbols = 'symbols' in request.form
    replace_vowels = 'replace_vowels' in request.form
    replace_most_frequent_vowel = 'replace_most_frequent_vowel' in request.form
    remove_vowels = 'remove_vowels' in request.form
    randomize = 'randomize' in request.form

    # Validate options and generate password
    if not use_numbers and not use_symbols:
        error = "Please select at least one option: Use Numbers or Use Symbols."
    else:
        password = generate_password(keyword, length, use_numbers, use_symbols, replace_vowels, replace_most_frequent_vowel, remove_vowels, randomize)
        strength = check_password_strength(password)
        if not password:
            error = "Failed to generate password. Ensure the keyword is shorter than the desired password length."

    # Render the same template with new data
    return render_template('createPassword.html', password=password, strength=strength, error=error, keyword=keyword,
                           length=length, use_numbers=use_numbers, use_symbols=use_symbols, replace_vowels=replace_vowels,
                           replace_most_frequent_vowel=replace_most_frequent_vowel, remove_vowels=remove_vowels, randomize=randomize)



@app.route('/', methods=['GET', 'POST'])
def login():
    cform = LoginForm()
    if request.method == 'POST':
        email = cform.email.data

        # Ensure that email and password are not None
        if email is not None:

            findPost = userData.find_one({"email": email})

            print(findPost)

            if findPost:
                
                postEmail = findPost["email"]

                if email == postEmail:

                    # setSessionID(findPost["_id"])
                    setSessionID(findPost['_id']) 
                    # print(session['id'])
                                    
                    session['username'] = findPost["username"]
                    session['email'] = email
                    # session['_id'] = findPost['_id']
                    return redirect(url_for('animalIDVerification'))

            flash("Invalid email")
            return render_template("login.html", form=cform)

    return render_template("login.html", form=LoginForm())



@app.route('/logout')
def logout():
    # Clear the user's session
    session.clear()
    setSessionID(None)

    return redirect(url_for('login'))

@app.route('/about', methods=['GET'])
def aboutUs():

    return render_template('aboutUs.html')



@app.route('/animalID_verification', methods=['GET', 'POST'])
def animalIDVerification():
    findPost = userData.find_one({"_id": sessionID})
    available_animals = ['giraffe', 'dog', 'chicken', 'monkey', 'peacock', 'tiger']

    selected_animal = findPost['animalID']
    if selected_animal not in available_animals:
        selected_animal = random.choice(available_animals)

    if request.method == 'POST':
        password = request.form.get('password')
        security_check = request.form.get('securityCheck')

        if security_check and password == findPost['loginPassword']:
            if findPost['masterPassword'] == None:
                return redirect(url_for('master_password'))
            else:
                return redirect(url_for('passwordList'))

        flash('Incorrect password or security check not confirmed', 'danger')

    return render_template('animal_IDLogin.html', selected_animal=selected_animal)



@app.route('/choose_animal', methods=['GET', 'POST'])
def animal_id():
    form = AnimalSelectionForm()

    if form.validate_on_submit():
        selected_animal = form.animal.data
        # user_email = findPost['email']  # Assuming you have the user's email stored in session

        userData.update_one({"_id": sessionID}, {"$set": {"animalID": selected_animal}})

        return redirect(url_for('login'))

    return render_template('animal_ID.html', form=form)



def send_2fa_verification_email(email, pin):
    msg = Message("Your MasterVault 2FA PIN",
                  sender='nickidummyacc@gmail.com',
                  recipients=[email])
    msg.body = f'Your 2FA verification PIN is: {pin}'
    mail.send(msg)



def send_verification_email(email):
    msg = Message("Welcome to MasterVault",
                  sender='nickidummyacc@gmail.com',
                  recipients=[email])
    msg.body = 'Hello, your account has been registered successfully! Thank you for using MasterVault. (This is a test program for a college project)'
    mail.send(msg)

def send_family_account_request(email, current_user):
    msg = Message("Family Account Request",
                  sender='nickidummyacc@gmail.com',
                  recipients=[email])
    # URL for the family member to register
    registration_link = url_for('register_family', _external=True)
    msg.body = (f'Hello,\n\n{current_user} has requested to add you to their MasterVault family account.\n'
                f'Please click the link below to register:\n\n{registration_link}\n\n'
                f'Thank you for using MasterVault. (This is a test program for a college project)')
    mail.send(msg)


@app.route('/register', methods=['GET', 'POST'])
def register():
    cform = RegistrationForm()
    print("Starting")
    if cform.validate_on_submit():

        print("Started")
            
        dob = cform.dob.data
        timeNow = datetime.now()
        dobTime = datetime(year=dob.year, month=dob.month, day=dob.day, hour=0, minute=0, second=0)
        idCounter = 1

        if cform.account_type.data == "family":
            for i in userData.find():
                if 'familyID' in i and isinstance(i['familyID'], int):
                    idCounter += 1
                    print(idCounter)
        else:
            idCounter = 0
        

        post = {
                    "username": cform.username.data,
                    "email": cform.email.data,
                    "DOB": dobTime,
                    "loginPassword": cform.password.data,
                    "animalID": None,
                    "accountType": cform.account_type.data,
                    "familyID": idCounter,
                    "masterPassword": None,
                    "2FA": False,
                    "accountLocked": "Unlocked",
                    "lockDuration": 'empty',
                    "lockTimestamp": timeNow
                }
        
        print(post)

        userData.insert_one(post)

        findPost = userData.find_one(post)
        setSessionID(findPost['_id'])

        # Send verification email after successfully saving account details
        send_verification_email(cform.email.data)

        flash('Account created successfully! An email will be sent to you.', 'success')
        return redirect(url_for('animal_id'))
    print('ending')
    return render_template("register.html", form=cform)

@app.route('/register_family', methods=['GET', 'POST'])
def register_family():
    form = FamilyRegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        dob = form.dob.data
        password = form.password.data

        timeNow = datetime.now()
        dobTime = datetime(year=dob.year, month=dob.month, day=dob.day, hour=0, minute=0, second=0)


        familyID = session.get('familyID', 0)

        post = {
            "username": username,
            "email": None,  # No email for family members in this form
            "DOB": dobTime,
            "loginPassword": password,
            "animalID": None,
            "accountType": 'family',
            "familyID": familyID,
            "masterPassword": None,
            "2FA": False,
            "accountLocked": "Unlocked",
            "lockDuration": 'empty',
            "lockTimestamp": timeNow
        }

        userData.insert_one(post)
        findPost = userData.find_one(post)
        setSessionID(findPost['_id'])

        flash('Family member added successfully!', 'success')

        # Redirect to set up animal ID
        return redirect(url_for('animal_id'))

    return render_template('registrationAddFamily.html', form=form)





@app.route('/master_password', methods=['GET', 'POST'])
def master_password():

    findPost = userData.find_one({"_id": sessionID})
    email = findPost['email']

    # Check if the user is logged in and if the account is locked
    if email:
        print("Before lockPost is assigned a variable")
        print
        lockedPost = findPost["accountLocked"]
        print(lockedPost)
        if lockedPost == "Locked":
            flash(
            'Your account is currently locked. You cannot set or reset the master password while the account is locked.',
            'error')
            return redirect(url_for('settings'))
    
    if request.method == 'POST':
        master_password = request.form['master_password']

        # Save the encrypted master password to the user's account
        userData.update_one({"_id": sessionID}, {"$set": {"masterPassword": master_password}})

        # Flash a success message
        flash('Master password set up successfully!', 'success')
        return redirect(url_for('passwordList'))
    
    return render_template('masterPassword.html')



@app.route('/addPassword', methods=['GET', 'POST'])
def addPassword():
    if request.method == 'POST':
        if request.form.get('action') == 'generate_password':
            # Password generator form was submitted
            keyword = request.form.get('keyword')
            length = int(request.form.get('length', 8))  # Provide a default value in case it's not set
            use_numbers = 'numbers' in request.form
            use_symbols = 'symbols' in request.form
            replace_vowels = 'replace_vowels' in request.form
            replace_most_frequent_vowel = 'replace_most_frequent_vowel' in request.form
            remove_vowels = 'remove_vowels' in request.form
            randomize = 'randomize' in request.form

            # Validate options and generate password
            if not use_numbers and not use_symbols:
                error = "Please select at least one option: Use Numbers or Use Symbols."
            else:
                password = generate_password(keyword, length, use_numbers, use_symbols, replace_vowels, replace_most_frequent_vowel, remove_vowels, randomize)
                strength = check_password_strength(password)
                if not password:
                    error = "Failed to generate password. Ensure the keyword is shorter than the desired password length."

            # Render the same template with new data
            return render_template('addPassword.html', password=password, strength=strength, error=error, keyword=keyword,
                                   length=length, use_numbers=use_numbers, use_symbols=use_symbols, replace_vowels=replace_vowels,
                                   replace_most_frequent_vowel=replace_most_frequent_vowel, remove_vowels=remove_vowels, randomize=randomize)
        else:
            # Add password form was submitted
            website = request.form.get('website')
            username = request.form.get('username')
            password = request.form.get('password')

            additional_fields = {
                'account_number': request.form.get('account_number'),
                'pin': request.form.get('pin'),
                'date': request.form.get('date'),
                'other': request.form.get('other')
            }

            saveNewPassword(website, username, password, additional_fields)
            return redirect(url_for('passwordList'))
    return render_template('addPassword.html')






def saveNewPassword(website, username, password, additional_fields):
    searchPasswords = userPasswords.find_one({"_id": sessionID})
    i = 1
    post = {}

    if searchPasswords is None:
        userPasswords.insert_one({"_id": sessionID})
        searchPasswords = {"_id": sessionID}

    while True:
        newName = f"name{i}"
        newCreatedDate = f"createdDate{i}"
        newWebsite = f"website{i}"
        newUsername = f"username{i}"
        newAccountNumber = f"accountNumber{i}"
        newPin = f"pin{i}"
        newDate = f"date{i}"
        newPassword = f"password{i}"
        newOther = f"other{i}"
        newPasswordLocked = f"passwordLocked{i}"

        if newWebsite not in searchPasswords:
            post = {
                newName: newName,
                newCreatedDate: datetime.now(),
                newWebsite: website,
                newUsername: username,
                newAccountNumber: additional_fields.get('account_number'),
                newPin: additional_fields.get('pin'),
                newDate: additional_fields.get('date'),
                newPassword: password,
                newOther: additional_fields.get('other'),
                newPasswordLocked: False
            }
            break
        i += 1

    print(post)

    newData = {"$set": post}
    userPasswords.update_one(searchPasswords, newData)




@app.route('/passwordView/<website>/<email>/<password>', methods=['GET', 'POST'])
def passwordView(website, email, password):
    if request.method == 'POST':
        newWebsite = request.form['website']
        newEmail = request.form['email']
        newPassword = request.form['password']
        updatePassword(website, email, password, newEmail, newPassword, newWebsite)
        return redirect(url_for('passwordList'))
    return render_template('passwordView.html', website=website, email=email, password=password)



def updatePassword(oldWebsite, oldEmail, oldPassword, newWebsite, newEmail, newPassword):

    searchPasswords = userPasswords.find_one({'_id': sessionID})

    # Find the document with the specified sessionID and the old password details
    if not searchPasswords:
        print("No passwords found for the user.")
        return

    # Iterate through the user's passwords to find the one that matches the old values
    i = 1
    updated = False
    while True:
        websiteKey = f"Website{i}"
        emailKey = f"Email{i}"
        passwordKey = f"Password{i}"

        if websiteKey not in searchPasswords:
            break  # Exit the loop if the website key does not exist

        if (searchPasswords[websiteKey] == oldWebsite and 
            searchPasswords[emailKey] == oldEmail and 
            searchPasswords[passwordKey] == oldPassword):
            
            # Update the values
            userPasswords.update_one(
                {"_id": sessionID},
                {"$set": {
                    websiteKey: newWebsite,
                    emailKey: newEmail,
                    passwordKey: newPassword
                }}
            )
            updated = True
            break

        i += 1

    if not updated:
        print("The specified password was not found and could not be updated.")



@app.route('/resetPassword', methods=['GET', 'POST'])
def resetPassword():
    if request.method == 'POST':    
        newPassword = request.form['newPassword']
        
        userData.update_one({"_id": sessionID}, {"$set": {"loginPassword": newPassword}})
        
        return redirect(url_for('passwordList'))

    return render_template('resetPassword.html')



@app.route('/passwordList', methods=['GET'])
def passwordList():

    findPost = userData.find_one({'_id': sessionID})

    if 'username' in session:

        if findPost.get('accountLocked') == "Locked":
            print("Account is Locked")
            return redirect(url_for('lockedPasswordList'))
        elif findPost.get('accountLocked') == "Unlocked":
            userPasswordList = getPasswords()

            if not userPasswordList:
                return render_template('passwordList.html', passwords=[])
            
            return render_template('passwordList.html', passwords=userPasswordList)
    else:
        flash('Please log in to access your passwords.', 'warning')
        return redirect(url_for('login'))



@app.route('/lockedPasswordList', methods=['GET'])
def lockedPasswordList():
    return render_template('lockedPasswordList.html')



@app.route('/delete-password', methods=['POST'])
def delete_password():
    username = session.get('username')
    if not username:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    website = data.get('website')
    email = data.get('email')
    password = data.get('password')

    if not all([website, email, password]):
        return jsonify({'error': 'Missing data'}), 400

    success = remove_passwordList_entry(username, website, email, password)

    if success:
        return jsonify({'message': 'Password entry deleted successfully'}), 200
    else:
        return jsonify({'error': 'Entry not found'}), 404



def remove_passwordList_entry(username, website, email, password):
    updated_data = []
    entry_found = False

    with open('userData.csv', 'r', newline='') as file:
        csvreader = csv.reader(file)
        for row in csvreader:

            if row and row[0] == username and row[1] == website and row[2] == email and row[3] == password:
                entry_found = True
                continue
            updated_data.append(row)

    if entry_found:
        with open('userData.csv', 'w', newline='') as file:
            csvwriter = csv.writer(file)
            csvwriter.writerows(updated_data)

    return entry_found



@app.route('/settings', methods=['GET'])
def settings():
    return render_template('settings.html')

@app.route('/settingsFamily', methods=['GET'])
def settings_family():
    return render_template('settingsFamily.html')


@app.route('/add_family_account', methods=['POST'])
def add_family_account():
    data = request.get_json()
    family_email = data.get('email')

    # Ensure the email is provided
    if not family_email:
        return jsonify({"success": False, "message": "No email provided"}), 400

    # Assume the current user's email is stored in session
    current_user_email = session.get('email')
    current_user = userData.find_one({"email": current_user_email})

    if current_user:
        current_username = current_user["username"]

        # Send the email to the family member
        send_family_account_request(family_email, current_username)

        return jsonify({"success": True, "message": "Request sent successfully"})
    else:
        return jsonify({"success": False, "message": "Current user not found"}), 404



@app.route('/enable_2fa', methods=['POST'])
def enable_2fa():
    sessionID = session.get('_id')
    if not sessionID:
        return jsonify({'message': 'User not logged in'}), 401

    update_2fa_status(sessionID, True)
    return jsonify({'message': '2FA has been enabled'}), 200



@app.route('/disable_2fa', methods=['POST'])
def disable_2fa():
    sessionID = session.get('_id')
    if not sessionID:
        return jsonify({'message': 'User not logged in'}), 401

    update_2fa_status(sessionID, False)
    return jsonify({'message': '2FA has been disabled'}), 200



def update_2fa_status(sessionID, status):
    userData.update_one({"_id": sessionID}, {"$set": {"2FA": status}})
    return status



@app.route('/get_2fa_status')
def get_2fa_status():
    sessionID = session.get('_id')
    if not sessionID:
        return jsonify({'error': 'User not logged in'}), 401

    findPost = userData.find_one({'_id': sessionID})

    if findPost:
        print("2FA Status:", findPost['2FA'])
        two_fa_status = findPost['2FA']
        return jsonify({'2fa_enabled': two_fa_status})
    else:
        return jsonify({'error': 'User not found'}), 404




@app.route('/setup_2fa', methods=['POST'])
def setup_2fa():
    sessionID = session.get('_id')
    if not sessionID:
        return jsonify({'message': 'User not logged in'}), 401

    user_email = request.json.get('email')
    pin = random.randint(1000, 9999)
    send_2fa_verification_email(user_email, pin)
    store_pin(user_email, pin)
    return jsonify({'message': 'A 2FA PIN has been sent to your email'}), 200



@app.route('/verify_2fa', methods=['POST'])
def verify_2fa():
    sessionID = session.get('_id')
    if not sessionID:
        return jsonify({'message': 'User not logged in'}), 401

    data = request.get_json()
    print("Received data:", data)

    if not data or 'email' not in data or 'pin' not in data:
        return jsonify({'message': 'Email and PIN are required'}), 400

    user_email = data['email']
    entered_pin = data['pin']
    print("Email:", user_email, "Entered PIN:", entered_pin)

    if is_valid_pin(user_email, entered_pin):
        return jsonify({'message': '2FA verification successful!'}), 200
    else:
        return jsonify({'message': 'Invalid or expired PIN'}), 400





@app.route('/lock_account', methods=['POST'])
def lock_account():
    data = request.get_json()
    lock_duration = data.get('lockDuration')
    sessionID = session.get('_id')

    if not sessionID:
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

    success = lock_account_in_db(sessionID, lock_duration)

    if success:
        session['lock_state'] = 'locked'
        session['unlock_time'] = datetime.now() + timedelta(minutes=int(lock_duration))
        return jsonify({'status': 'success', 'message': 'Account locked'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to lock account'})
    


@app.route('/check_lock', methods=['GET'])
def check_lock():
    findPost = userData.find_one({'_id': sessionID})
    lock_state, unlock_timestamp = get_lock_state_from_db(findPost['email'])
    current_time = datetime.now()

    # Check if there's an unlock timestamp and convert it to a datetime object
    # if unlock_timestamp:
    #     unlock_time = datetime.strptime(unlock_timestamp, '%Y-%m-%d %H:%M:%S')
    # else:
    #     unlock_time = None

    if lock_state == 'Locked' and unlock_timestamp and current_time < unlock_timestamp:
        return jsonify({'locked': True, 'unlock_time': unlock_timestamp})
    else:
        update_lock_state_in_db(findPost['email'], 'Unlocked')
        return jsonify({'locked': False})



def get_lock_state_from_db(sessionID):
    findPost = userData.find_one({'_id': sessionID})
    if findPost:
        return findPost['accountLocked'], findPost.get('lockTimestamp')
    return 'Unlocked', None



def update_lock_state_in_db(sessionID, lock_state):
    update = {
        "$set": {
            "accountLocked": lock_state,
            "lockTimestamp": datetime.now()
        }
    }
    userData.update_one({'_id': sessionID}, update)



@app.route('/unlock_account', methods=['POST'])
def unlock_account():
    data = request.get_json()
    sessionID = session.get('_id')
    master_password = data.get('master_password')

    if not sessionID:
        return jsonify({'status': 'error', 'message': 'User not logged in'}), 401

    success = verify_and_unlock_account(sessionID, master_password)

    if success:
        session.pop('lock_state', None)
        session.pop('unlock_time', None)
        return jsonify({'status': 'success', 'message': 'Account unlocked'})
    else:
        return jsonify({'status': 'error', 'message': 'Incorrect master password'}), 401



def verify_and_unlock_account(sessionID, master_password):
    findPost = userData.find_one({'_id': sessionID})
    if findPost and findPost['masterPassword'] == master_password:
        userData.update_one({'_id': sessionID}, {"$set": {"accountLocked": "Unlocked"}})
        return True
    return False



def lock_account_in_db(sessionID, lock_duration):
    lock_duration_in_minutes = int(lock_duration)
    update = {
        "$set": {
            "accountLocked": "Locked",
            "lockTimestamp": datetime.now() + timedelta(minutes=lock_duration_in_minutes)
        }
    }
    result = userData.update_one({'_id': sessionID}, update)
    return result.modified_count > 0



def store_pin(email, pin):
    temporary_2fa_storage[email] = {
        'pin': pin, 'timestamp': datetime.now()
    }



def is_valid_pin(email, entered_pin):
    pin_data = temporary_2fa_storage.get(email)
    print("Stored PIN data for", email, ":", pin_data)  # Log stored PIN data

    if pin_data and str(pin_data['pin']) == str(entered_pin):
        time_diff = datetime.now() - pin_data['timestamp']
        if time_diff.total_seconds() <= 600:  # 10 minutes validity
            return True
    return False


@app.route('/delete_account', methods=['POST'])
def delete_account():
    # Check if the user is authenticated
    if 'email' not in session:
        return jsonify({"success": False, "message": "User not logged in."}), 401

    # Retrieve the session email
    session_email = session['email']

    # Find the user in the database
    findPost = userData.find_one({'email': session_email})


    if findPost:
        if session_email == findPost['email']:
            # Delete the user from the database
            userData.delete_one({'email': session_email})

            # Clear the user's session and log them out
            session.clear()

            return jsonify({"success": True, "message": "Account successfully deleted."})
        else:
            return jsonify({"success": False, "message": "Email mismatch."})
    else:
        return jsonify({"success": False, "message": "Account not found."})





if __name__ == '__main__':
    app.run(debug=True)