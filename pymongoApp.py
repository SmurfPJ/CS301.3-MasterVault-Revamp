from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Mail, Message
from forms import RegistrationForm, LoginForm
from dotenv import load_dotenv
from encryption import encrypt, decrypt
from datetime import datetime
from pymongo import MongoClient
import random, string, csv, os

# Constants
ACCOUNT_METADATA_LENGTH = 8
client = MongoClient('mongodb+srv://Conor:M0ng0DB1@mastervaultdb1.g1a7o98.mongodb.net/?retryWrites=true&w=majority&appName=MasterVaultDB1')
db = client.MasterVault
userData = db["userData"]
userPasswords = db["userPasswords"]

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



def getSessionID():
    return sessionID

def setSessionID(userID):
    global sessionID
    sessionID = userID



def generate_password(keyword, length, use_numbers, use_symbols):
    characters = string.ascii_letters  # Always use letters

    if use_numbers:
        characters += string.digits

    if use_symbols:
        characters += string.punctuation

    # Ensure the password is at least as long as the keyword
    if length < len(keyword):
        return ""

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
    findPost = userPasswords.find_one({'_id': getSessionID()})
    userList = []
    currentList = []

    if not findPost:
        print("No userData found")
        return []

    for key, value in findPost.items():
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

    # Validate options and generate password
    if not use_numbers and not use_symbols:
        error = "Please select at least one option: Use Numbers or Use Symbols."
    else:
        password = generate_password(keyword, length, use_numbers, use_symbols)
        strength = check_password_strength(password)
        if not password:
            error = "Failed to generate password. Ensure the keyword is shorter than the desired password length."

    # Render the same template with new data
    return render_template('createPassword.html', password=password, strength=strength, error=error, keyword=keyword,
                           length=length, use_numbers=use_numbers, use_symbols=use_symbols)



@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = None
        password = None

        # Check if the request is JSON (from the extension)
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
        else:
            # Handle form submission (from the web app)
            cform = LoginForm()
            if cform.validate_on_submit():
                email = cform.email.data
                password = cform.password.data
            else:
                return render_template("login.html", form=cform)

        # Ensure that email and password are not None
        if email is not None and password is not None:

            findPost = userData.find_one({"email": email, "loginPassword": password})

            print(findPost)

            if findPost:
                
                postEmail = findPost["email"]
                postPassword = findPost["loginPassword"]

                if email == postEmail and password == postPassword:

                    setSessionID(findPost["_id"])
                    print(getSessionID())

                    if findPost["masterPassword"] == None:
                            if request.is_json:
                                # JSON response indicating master password setup is needed
                                return jsonify(
                                    {"status": "setup_master_password", "message": "Master password setup required"})
                            else:
                                session['username'] = findPost["username"]
                                session['email'] = email
                                return redirect(url_for('master_password'))
                
                if email == postEmail and password == postPassword:
                    if request.is_json:
                        return jsonify({"status": "success", "username": findPost["username"], "email": email})
                    else:
                        session['username'] = findPost["username"]
                        session['email'] = email
                        return redirect(url_for('passwordList'))

            # Handle invalid email or password
            error_message = "Invalid email or password"
            if request.is_json:
                return jsonify({"status": "failure", "message": error_message}), 401
            else:
                flash(error_message)
                return render_template("login.html", form=cform)

    return render_template("login.html", form=LoginForm())



@app.route('/logout')
def logout():
    # Clear the user's session
    session.clear()
    setSessionID(None)

    return redirect(url_for('login'))



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



@app.route('/register', methods=['GET', 'POST'])
def register():
    cform = RegistrationForm()
    if cform.validate_on_submit():
            
        dob = cform.dob.data
        timeNow = datetime.now()
        dobTime = datetime(year=dob.year, month=dob.month, day=dob.day, hour=0, minute=0, second=0)

        post = {
                    "username": cform.username.data,
                    "email": cform.email.data,
                    "DOB": dobTime,
                    "loginPassword": cform.password.data,
                    "animalID": None,
                    "masterPassword": None,
                    "2FA": False,
                    "accountLocked": "Unlocked",
                    "lockDuration": 'empty',
                    "lockTimestamp": timeNow
                }

        userData.insert_one(post)

        # Send verification email after successfully saving account details
        send_verification_email(cform.email.data)

        flash('Account created successfully! An email will be sent to you.', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", form=cform)



@app.route('/master_password', methods=['GET', 'POST'])
def master_password():

    email = session.get('email')

    findPost = userData.find_one({"_id": getSessionID()})

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
        userData.update_one({"_id": getSessionID()}, {"$set": {"masterPassword": master_password}})

        # Flash a success message
        flash('Master password set up successfully!', 'success')
        return redirect(url_for('passwordList'))
    
    return render_template('masterPassword.html')



@app.route('/addPassword', methods=['GET', 'POST'])
def addPassword():
    if request.method == 'POST':
        # print("Session Username: ", session['username'])
        # print("Username: ", username)
        website = request.form['website']
        email = request.form['email']
        password = request.form['password']

        # website = encrypt(website)
        # email = encrypt(email)
        # password = encrypt(password)

        saveNewPassword(website, email, password)

        return redirect(url_for('passwordList'))

    return render_template('addPassword.html')


def saveNewPassword(website, email, password):
    
    searchPasswords = userPasswords.find_one({"_id": getSessionID()})

    i = 1
    post = {}

    if searchPasswords == None:
        userPasswords.insert_one({"_id": getSessionID()})


    while True:
        newName = f"Name{i}"
        newWebsite = f"Website{i}"
        newEmail = f"Email{i}"
        newUsername = f"Username{i}"
        newAccountNumber = f"AccountNumber{i}"
        newPin = f"Pin{i}"
        newDate = f"Date{i}"
        newPassword = f"Password{i}"

        if newWebsite not in searchPasswords:
            post = {
                    newName: newName,
                    newWebsite: website,
                    newEmail: email,
                    newUsername: None,
                    newAccountNumber: None,
                    newPin: None,
                    newDate: None,
                    newPassword: password
                }
            break
        i += 1

    print(post)

    newData = {"$set": post}
    userPasswords.update_one(searchPasswords, newData)


@app.route('/passwordView/<website>/<email>/<password>', methods=['GET', 'POST'])
def passwordView(website, email, password):
    if request.method == 'POST':
        username = session['username']
        newWebsite = request.form['website']
        newEmail = request.form['email']
        newPassword = request.form['password']
        saveChanges(username, website, email, password, newEmail, newPassword, newWebsite)
        return redirect(url_for('passwordList'))
    return render_template('passwordView.html', website=website, email=email, password=password)



def saveChanges(username, old_website, old_email, old_password, new_website, new_email, new_password):
    data = []
    with open('userData.csv', 'r', newline='') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if row and row[0] == username:
                for webIdx in range(int((len(row) - 1) / 3)):
                    if row[webIdx * 3 + 1] == old_website and row[webIdx * 3 + 2] == old_email and row[
                        webIdx * 3 + 3] == old_password:
                        row[webIdx * 3 + 1] = new_website
                        row[webIdx * 3 + 2] = new_email
                        row[webIdx * 3 + 3] = new_password
            data.append(row)

    with open('userData.csv', 'w', newline='') as file:
        csvwriter = csv.writer(file)
        csvwriter.writerows(data)

    # print(data)


@app.route('/resetPassword', methods=['GET', 'POST'])
def resetPassword():
    if request.method == 'POST':
        master_password = request.form['newPassword']
        username = session['username']

        resetPassword(username, master_password)

        return redirect(url_for('passwordList'))

    return render_template('resetPassword.html')


def resetPassword(username, newPassword):
    data = []
    updated = False
    with open('loginInfo.csv', 'r', newline='') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if row and row[0] == username:
                if len(row) < 6:
                    row.append(newPassword)
                else:
                    row[3] = newPassword
                updated = True
            data.append(row)

    if updated:
        with open('loginInfo.csv', 'w', newline='') as file:
            csvwriter = csv.writer(file)
            csvwriter.writerows(data)


@app.route('/passwordList', methods=['GET'])
def passwordList():
    if 'username' in session:
        findPost = userData.find_one({'_id': getSessionID()})

        if findPost.get('accountLocked') == "Locked":
            print("Account is Locked")
            return redirect(url_for('lockedPasswordList'))
        elif findPost.get('accountLocked') == "Unlocked":
            userPasswordList = getPasswords()
            print("Name: ", userPasswordList[0][2])
            print("Name: ", userPasswordList[0][4])
            print("Name: ", userPasswordList[0][7])
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


# Temporary storage for 2FA codes
temporary_2fa_storage = {}


@app.route('/enable_2fa', methods=['POST'])
def enable_2fa():
    update_2fa_status(True)
    return jsonify({'message': '2FA has been enabled'}), 200


@app.route('/disable_2fa', methods=['POST'])
def disable_2fa():
    update_2fa_status(False)
    return jsonify({'message': '2FA has been disabled'}), 200


def update_2fa_status(status):
    userData.update_one({"_id": getSessionID()}, {"$set": {"2FA": status}})
    return status


@app.route('/get_2fa_status')
def get_2fa_status():
    if 'username' in session:
        findPost = userData.find_one({'_id': getSessionID()})
        print("2FA Status:", findPost['2FA'])
        two_fa_status = findPost['2FA']
        return jsonify({'2fa_enabled': two_fa_status})
    else:
        return jsonify({'error': 'User not logged in'}), 401



@app.route('/setup_2fa', methods=['POST'])
def setup_2fa():
    user_email = request.json.get('email')
    pin = random.randint(1000, 9999)
    send_2fa_verification_email(user_email, pin)
    store_pin(user_email, pin)
    return jsonify({'message': 'A 2FA PIN has been sent to your email'}), 200


@app.route('/verify_2fa', methods=['POST'])
def verify_2fa():
    data = request.get_json()
    print("Received data:", data)  # Log received data

    if not data or 'email' not in data or 'pin' not in data:
        return jsonify({'message': 'Email and PIN are required'}), 400

    user_email = data['email']
    entered_pin = data['pin']
    print("Email:", user_email, "Entered PIN:", entered_pin)  # Log specifics

    if is_valid_pin(user_email, entered_pin):
        return jsonify({'message': '2FA verification successful!'}), 200
    else:
        return jsonify({'message': 'Invalid or expired PIN'}), 400


@app.route('/lock_account', methods=['POST'])
def lock_account():
    data = request.get_json()
    lock_duration = data.get('lockDuration')
    success = lock_account_in_db(lock_duration)  # function to lock the account

    if success:
        # Store lock state in the session
        session['lock_state'] = 'locked'
        session['unlock_time'] = datetime.now() + datetime.timedelta(minutes=int(lock_duration))
        return jsonify({'status': 'success', 'message': 'Account locked'})
    else:
        return jsonify({'status': 'error', 'message': 'Failed to lock account'})
    


@app.route('/check_lock', methods=['GET'])
def check_lock():
    findPost = userData.find_one({'_id': getSessionID()})
    lock_state = findPost['accountLocked']
    unlock_timestamp = findPost['lockTimestamp']
    current_time = datetime.now()

    # Check if there's an unlock timestamp and convert it to a datetime object
    # if unlock_timestamp:
    #     unlock_time = datetime.strptime(unlock_timestamp, '%Y-%m-%d %H:%M:%S')
    # else:
    #     unlock_time = None

    if lock_state == 'Locked' and current_time > unlock_timestamp:
        return jsonify({'locked': True, 'unlock_time': unlock_timestamp.strftime('%Y-%m-%d %H:%M:%S')})
    else:
        update_lock_state_in_db()
        return jsonify({'locked': False})



def update_lock_state_in_db():
    
    update = {
        "$set": {
            "accountLocked": "Unlocked",
            "lockTimestamp": datetime.now()
        }
    }
    userData.update_many({'_id': getSessionID()}, update)
    return True


@app.route('/unlock_account', methods=['POST'])
def unlock_account():
    data = request.get_json()
    email = session.get('email')  # assuming you store email in session upon login
    master_password = data.get('master_password')

    # check master password and update lock status in CSV
    success = verify_and_unlock_account(email, master_password)

    if success:
        # Clear lock state from the session
        session.pop('lock_state', None)
        session.pop('unlock_time', None)
        return jsonify({'status': 'success', 'message': 'Account unlocked'})
    else:
        return jsonify({'status': 'error', 'message': 'Incorrect master password'}), 401


def verify_and_unlock_account(email, master_password):
    data = []
    unlocked = False

    with open('loginInfo.csv', 'r', newline='') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if row and row[1] == email:

                if row[5] == master_password:
                    unlocked = True
                    row[6] = 'Unlocked'
                    row[7] = 'empty'  # Set lock duration to 'empty'
                    row[8] = 'empty'  # Set lock timestamp to 'empty'
            data.append(row)

    # Rewrite the CSV file with the updated data
    if unlocked:
        with open('loginInfo.csv', 'w', newline='') as file:
            csvwriter = csv.writer(file)
            csvwriter.writerows(data)

    return unlocked


def lock_account_in_db(lock_duration):
    locked = True
    lock_duration_in_minutes = int(lock_duration)  # Convert lock duration to minutes
    print("Time Now: ", datetime.now())
    print("Lock time: ", datetime.timedelta(minutes=lock_duration_in_minutes))

    datetime.

    update = {
        "$set": {
            "accountLocked": "Locked",
            "lockTimestamp": datetime.now()
        }
    }
    userData.update_many({'_id': getSessionID()}, update)

    return locked



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

    email = session['email']

    # Initialize variables
    data = []
    account_deleted = False

    with open('loginInfo.csv', 'r', newline='') as file:
        csvreader = csv.reader(file)
        for row in csvreader:
            if row[1] != email:
                data.append(row)
            else:
                account_deleted = True

        # Write the updated data back to the CSV file
    if account_deleted:
        with open('loginInfo.csv', 'w', newline='') as file:
            csvwriter = csv.writer(file)
            csvwriter.writerows(data)

        # Clear the user's session and log them out
        session.pop('email', None)
        session.pop('username', None)

        return jsonify({"success": True, "message": "Account successfully deleted."})
    else:
        return jsonify({"success": False, "message": "Account not found."})


if __name__ == '__main__':
    app.run(debug=True)