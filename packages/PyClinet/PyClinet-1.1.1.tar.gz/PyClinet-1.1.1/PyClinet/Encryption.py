import base64
from Crypto.PublicKey import RSA
from Crypto.PublicKey.RSA import construct
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Random import get_random_bytes
from Crypto.Util import asn1
import json
import random
import string
from PyClinet import Encryption
from Crypto.Signature import PKCS1_v1_5
ivBytes = bytes([0]*16)
def toPublic(string):
    try:
        public_key_bytes = base64.b64decode(string)
        key = RSA.importKey(public_key_bytes)
        return construct((key.n, key.e)).exportKey().decode('utf-8')
    except ValueError as e:
        print(e)
        return None
def toPrivate(string):
    try:
        string = string + '='
        private_key_bytes = base64.b64decode(string)
        key = RSA.importKey(private_key_bytes)
        return construct((key.n, key.e, key.d)).exportKey().decode('utf-8')
    except ValueError as e:
        print(e)
        return None
def makeKey(string):
    i = 0
    substring = string[:8]
    substring2 = string[8:16]
    substring3 = string[16:24]
    string = string[24:32]
    str_combined = substring3 + substring + string + substring2
    
    result = ""
    for char in str_combined:
        if char.isnumeric():
            result += str((int(char) - 48 + 5) % 10)
        elif char.isalpha():
            if char.islower():
                result += chr((ord(char) - 97 + 9) % 26 + 97)
            elif char.isupper():
                result += chr((ord(char) - 65 + 29) % 26 + 65)
        else:
            result += char
    
    return result.encode()
def encrypt(CipherData,auth):
    makeKey = Encryption.makeKey(auth)
    iv = bytes([0]*16)
    cipher = AES.new(makeKey, AES.MODE_CBC, iv)
    padded_data = pad(CipherData.encode(), 16)
    encrypted_data = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted_data).decode()

def decode(var0, var1):
    var2 = Encryption.makeKey(var1)
    iv = bytes([0]*16)
    cipher = AES.new(var2, AES.MODE_CBC, iv)
    decoded_bytes = base64.b64decode(var0)
    decrypted_bytes = cipher.decrypt(decoded_bytes)
    unpadded_data = unpad(decrypted_bytes, AES.block_size)
    return unpadded_data.decode('utf-8')

def authSet(authEnc):
    result = []
    lowercase = "abcdefghijklmnopqrstuvwxyz"
    uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"

    for s in authEnc:
        if s in lowercase:
            result.append(chr((32 - (ord(s) - 97)) % 26 + 97))
        elif s in uppercase:
            result.append(chr((29 - (ord(s) - 65)) % 26 + 65))
        elif s in digits:
            result.append(chr((13 - (ord(s) - 48)) % 10 + 48))
        else:
            result.append(s)

    return ''.join(result)
def secret(e):
    t = e[:8]
    i = e[8:16]
    n = e[16:24] + t + e[24:32] + i
    
    for s in range(len(n)):
        if n[s].isnumeric():
            t_char = chr((int(n[s]) - ord('0') + 5) % 10 + ord('0'))
            n = n[:s] + t_char + n[s+1:]
        else:
            t_char = chr((ord(n[s]) - ord('a') + 9) % 26 + ord('a'))
            n = n[:s] + t_char + n[s+1:]
    
    return n
def sign_rsa(key, data_enc):
    if data_enc is None:
        return None
    else:
        key = key + '='
        private_key = Encryption.toPrivate(key)
        keypair = RSA.import_key(private_key.encode("utf-8"))
        sha_data = SHA256.new(data_enc.encode("utf-8"))
        signature = pkcs1_15.new(keypair).sign(sha_data)
        return base64.b64encode(signature).decode("utf-8")
        
def getKey():
    key = RSA.generate(1024)
    public_key = key.publickey().exportKey('PEM').decode('utf-8')
    private_key = key.exportKey('PEM').decode('utf-8')

    encoded_public_key = base64.b64encode(public_key.encode()).decode('utf-8')
    encoded_private_key = base64.b64encode(private_key.encode()).decode('utf-8')

    return [encoded_public_key, encoded_private_key]
def decrypt_rsa(ciphertext, key):
    private_key = Encryption.toPrivate(key)
    cipher = PKCS1_v1_5.new(private_key)
    decrypted_message = cipher.decrypt(base64.b64decode(ciphertext), None)
    return decrypted_message.decode('utf-8')
def encode_chars(var0):
    if var0 is None:
        return None
    else:
        var1 = []
        for char in var0:
            if char.isupper():
                var1.append(chr((29 - (ord(char) - 65)) % 26 + 65))
            elif char.islower():
                var1.append(chr((32 - (ord(char) - 97)) % 26 + 97))
            elif char.isdigit():
                var1.append(chr((13 - (ord(char) - 48)) % 10 + 48))
            else:
                var1.append(char)
        
        return ''.join(var1)

def encrypt_url(var0, var1):
    try:
        iv = get_random_bytes(16)
        cipher = AES.new(var1.encode(), AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(pad(var0.encode(), AES.block_size))
        encrypted_data_base64 = base64.b64encode(encrypted_data).decode()
        return encrypted_data_base64
    except Exception as e:
        return None
def make_json(data, json_data):
    data_e = ""
    try:
        json_data_obj = json.loads(data)
        data_e = json_data_obj.get(json_data, "")
    except json.JSONDecodeError as e:
        print(e)
    return data_e

def random_text(text, size):
    salt = ""
    while len(salt) < size:
        index = random.randint(0, len(text) - 1)
        salt += text[index]
    return salt
def to_pem_string(public_key):
    if public_key is None:
        return None
    
    try:
        key_str = public_key
        pem_str = "-----BEGIN PUBLIC KEY-----\n"
        pem_str += key_str
        pem_str += "-----END PUBLIC KEY-----"
        pem_bytes = pem_str.encode('utf-8')
        encoded_pem = base64.b64encode(pem_bytes).decode('utf-8')
        return encoded_pem
    except Exception as e:
        print(e)
        return None
def to_string(public_key):
    if public_key is None:
        return None
    
    try:
        encoded_key = base64.b64encode(public_key.export_key()).decode('utf-8')
        return encoded_key
    except Exception as e:
        print(e)
        return None
def make_random_auth():
    auth = ""
    for _ in range(32):
        auth += random.choice(string.ascii_lowercase)
    
    return auth
def replaceCharAt(e, t, i):
    return e[:t] + i + e[t + len(i):]
def MakeInt(Data, JsonData):
    DataX = ""
    try:
        json_data = json.loads(Data)
        DataX = json_data[0]
    except json.JSONDecodeError as e:
        print(e)
    return DataX

def getSaltString():
    SALTCHARS = "250118664537361040511210153736"
    salt = []
    while len(salt) < 30:
        index = random.randint(0, len(SALTCHARS)-1)
        salt.append(SALTCHARS[index])
    saltStr = ''.join(salt)
    return saltStr