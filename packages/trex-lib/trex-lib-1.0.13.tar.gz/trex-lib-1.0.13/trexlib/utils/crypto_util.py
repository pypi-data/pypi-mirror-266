'''
Created on 3 Nov 2020

@author: jacklok
'''
from cryptography.fernet import Fernet
from trexlib.conf import CRYPTO_SECRET_KEY
import json, logging

logger = logging.getLogger('utils')

def encrypt(value, fernet_key=CRYPTO_SECRET_KEY):
    
    if value:
        f = Fernet(fernet_key)
        return f.encrypt(value.encode()).decode('utf-8')
    
def encrypt_json(json_value, fernet_key=CRYPTO_SECRET_KEY):
    
    if json_value:
        f = Fernet(fernet_key)
        return f.encrypt(json.dumps(json_value).encode()).decode('utf-8')
    
def decrypt(value, fernet_key=CRYPTO_SECRET_KEY):
    if value:
        value = str.encode(value)
            
        f = Fernet(fernet_key)
        return f.decrypt(value).decode('utf-8')
    
def decrypt_json(value, fernet_key=CRYPTO_SECRET_KEY):
    json_value_in_str = decrypt(value, fernet_key=fernet_key)
    if json_value_in_str:
        return json.loads(json_value_in_str)     
