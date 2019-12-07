import argparse
import simplecypher



ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def encrypt(message, key):
    message = message.replace(':', '')
    message = message.replace(';', '')
    message = message.replace(',', '')
    message = message.replace('.', '')
    message = message.replace('?', '')
    message = message.replace('!', '')

    message = message.upper()

    encrypted_message = ''

    for i in range(len(message)):
        message_letter_index = ALPHABET.index(message[i])
        key_letter_index = ALPHABET.index(key[(i % len(key))].upper())
        index = (message_letter_index + key_letter_index) % len(ALPHABET)
        encrypted_message += ALPHABET[index]

    return encrypted_message

def decrypt(message, key):
    message = message.replace(':', '')
    message = message.replace(';', '')
    message = message.replace(',', '')
    message = message.replace('.', '')
    message = message.replace('?', '')
    message = message.replace('!', '')

    message = message.upper()

    decrypted_message = ''

    for i in range(len(message)):
        message_letter_index = ALPHABET.index(message[i])
        key_letter_index = ALPHABET.index(key[(i % len(key))].upper())
        index = (message_letter_index - key_letter_index) % len(ALPHABET)
        decrypted_message += ALPHABET[index]

    return decrypted_message
print(encrypt("Aaron 2019","chat"))
print(decrypt(encrypt("Aaron 2019","chat"),"chat"))



