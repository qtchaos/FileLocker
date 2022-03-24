import os
import time
from cryptography.fernet import Fernet
from os.path import exists
from checksumdir import dirhash
import requests

decrypt = input("What do you want to do? (decrypt/encrypt): ")

if decrypt == "decrypt":
    decrypt = True
else:
    decrypt = False

# key generation
if not exists('filekey.key'):
    key = Fernet.generate_key()
else:
    with open('filekey.key', 'rb') as filebytes:
        key = filebytes.read()

with open('filekey.key', 'wb') as filekey:
    filekey.write(key)

with open('filekey.key', 'rb') as filekey:
    key = filekey.read()
    # url = ''
    # headers = {"Content-Type": "application/json; charset=utf-8"}
    #
    # myobj = {
    #     'key': str(key)[2:-1]
    # }
    #
    #
    # x = requests.post(url, json=myobj)
    # print(f' POST request: {x.status_code}')

fernet = Fernet(key)

maintimestart = time.perf_counter()

path = input("Enter directory to encrypt/decrypt: ")
filelist = []

for root, dirs, files in os.walk(path):
    for file in files:
        # append the file name to the list
        filelist.append(os.path.join(root, file))

if decrypt:
    i = 1
    for name in filelist:
        tic = time.perf_counter()
        with open(name, 'rb') as enc_file:
            encrypted = enc_file.read()
            decrypted = fernet.decrypt(encrypted)
        with open(name, 'wb') as dec_file:
            dec_file.write(decrypted)
            toc = time.perf_counter()
            print(f"Decrypted file {i} in {toc - tic:0.4f} seconds. Total time: {toc - maintimestart:0.4f} seconds")
            i += 1
    with open("checksum.MD5", "r") as file:
        generatedHash = dirhash(path, 'md5')
        checkHash = file.read()
        print(f"Hash generated at encryption: {checkHash}, hash generated after decryption: {generatedHash}")
        if checkHash == generatedHash:
            print("HASHES MATCH!")
        else:
            print("HASHES DON'T MATCH!")
else:
    i = 1
    print("Calculating hash...")
    with open("checksum.MD5", "w") as file:
        a = dirhash(path, 'md5')
        file.write(a)
        print(f"Hash of directory: {a}")

    for name in filelist:
        tic = time.perf_counter()
        with open(name, 'rb') as file:
            original = file.read()
            encrypted = fernet.encrypt(original)
        with open(name, 'wb') as encrypted_file:
            encrypted_file.write(encrypted)
            toc = time.perf_counter()
            print(f"Encrypted file {i} in {toc - tic:0.4f} seconds. Total time: {toc - maintimestart:0.4f} seconds")
        i += 1

