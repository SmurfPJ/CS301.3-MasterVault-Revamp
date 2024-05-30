import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

password = b"secretPassword"
#salt = os.urandom(16)
# kdf = PBKDF2HMAC(
#     algorithm=hashes.SHA256(),
#     length=32,
#     salt=b')1t\xd0{\xe6\x90\xf2\x80\x8d\x81\xb6\xb3\x8c\xfc\xd0',
#     iterations=480000,
# )

# key = base64.urlsafe_b64encode(kdf.derive(password))

# def encrypt(userData):
        
#     # using the key
#     fernet = Fernet(key)
    
#     # encrypting the file
#     encrypted = fernet.encrypt(userData.encode())

#     return encrypted

# def decrypt(encrypted):
#     # using the key
#     fernet = Fernet(key)
    
#     # decrypting the file
#     if type(encrypted) == str:
#         decrypted = fernet.decrypt(encrypted[2:-1].encode('utf-8')).decode()
#     else:
#         decrypted = fernet.decrypt(encrypted).decode()
    
#     return decrypted

def pad(data):
    # PKCS7 padding
    pad_len = 16 - (len(data) % 16)
    return data + (chr(pad_len) * pad_len).encode()

def unpad(data):
    pad_len = data[-1]
    return data[:-pad_len]

def encrypt(key, plaintext):
    # Generate a random 16-byte IV
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext.encode()))
    return base64.b64encode(iv + ciphertext).decode('utf-8')

def decrypt(key, ciphertext):
    ciphertext = base64.b64decode(ciphertext)
    iv = ciphertext[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext[16:]))
    return plaintext.decode('utf-8')

# Example usage
key = b'\x1170T;o\x80I\x17G3=\xcd\xd1j\xc1\x0e\xeb\x9dP-\xe8\x08Z_x\xf8\x9bh\x7f\xa8\xc5' #get_random_bytes(32)  # AES-256 key must be 32 bytes
plaintext = "This is a test for MongoDB."

# print(f"Key: {key}")

ciphertext = "ny8h8YpQc6Xnq06ce+1KhdtpVgMA/WwsVdfXdGGNaKENdaTOFiH4XJKsZy/u4arF"#encrypt(key, plaintext)
print(f"Ciphertext: {ciphertext}")

decrypted = decrypt(key, ciphertext)
print(f"Decrypted: {decrypted}")

# def main():
#     plain_text = input("Password: ")

#     encrypted = encrypt(plain_text)
#     print("Encrypted: ", encrypted)

#     decrypted = decrypt(encrypted)
#     print("Decrypted: ", decrypted)

# main()