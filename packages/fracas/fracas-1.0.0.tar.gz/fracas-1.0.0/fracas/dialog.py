import getpass
import os.path

from . import crypto


def input_journal_path():
    while True:
        path = input("Please enter the file path to your new journal:\n")
        dirpath = os.path.dirname(path)
        if os.path.exists(dirpath):
            return path
        else:
            expanded_path = os.path.expanduser(path)
            dirpath = os.path.dirname(expanded_path)
            if os.path.exists(dirpath):
                return expanded_path
            print(f"Directory {dirpath} does not exist.")


def input_password():
    return getpass.getpass(prompt="Password: ")


def input_password_twice():
    while True:
        pw1 = getpass.getpass(prompt="Password: ")
        pw2 = getpass.getpass(prompt="Password again: ")
        if pw1 == pw2:
            crypto.genkey(pw1)
            break
        else:
            print("Passwords didn't match.")


def welcome():
    print("Welcome to the fracas journal")
    path = input_journal_path()
    fencrypt = input("Encrypt the file? [Y/n]\n")
    if fencrypt.lower() == "n":
        encrypt = False
    else:
        encrypt = True
        input_password_twice()
    return dict(path=path, editor="vim", encrypt=encrypt)
