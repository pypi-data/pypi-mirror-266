#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  SPDX-License-Identifier: GPL-3.0-only
#  Copyright 2023 drad <sa@adercon.com>

import ast
import configparser
import logging
import os
import secrets
import string
import subprocess  # nosec
import sys
import threading
from optparse import OptionParser

import lmdb
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

_log_level = "INFO"  # [CRITICAL|ERROR|WARNING|INFO|DEBUG] (suggest INFO)

required_config_files = [os.path.expanduser("~/.config/spw/spw.ini")]
config = configparser.ConfigParser()
found_configs = config.read(required_config_files)
missing_configs = set(required_config_files) - set(found_configs)
if missing_configs:
    print(f"ERROR: Missing Config File: {missing_configs}, cannot continue")
    sys.exit(1)

logging.basicConfig(
    format="%(message)s",
    level=logging.getLevelName(_log_level),
    stream=sys.stdout,
)

logger_base = logging.getLogger(__name__)
write_to_console = False


def show_version():
    """
    Show application version.
    """

    import importlib.metadata

    _meta = importlib.metadata.metadata("spw")
    _name = _meta["Name"]
    _version = _meta["Version"]
    logging.critical(f"{_name} {_version}")


def expand_path(path):
    """
    Expand the path to account for user home and environment variables
    """

    return os.path.expandvars(os.path.expanduser(path))


def get_db_conn(mode="r"):
    """
    Get a db connection.
    r: gets a read only connection
    w: gets a read/write connection
    """

    if mode == "w":
        return lmdb.open(
            expand_path(config.get("DEFAULT", "PasswordDatabase")),
            map_size=config.getint("DEFAULT", "PasswordDatabaseMapSize"),
        )
    else:
        return lmdb.open(
            expand_path(config.get("DEFAULT", "PasswordDatabase")), readonly=True
        )


def decrypt(encrypted=None, suppress_warnings=False):
    """
    Decrypt an encrypted message.
    NOTE: try decrypting with SHA256 algorithm first, then fall back to SHA (SHA1).
    """

    with open(expand_path(config.get("DEFAULT", "PrivateKey")), "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(), password=None, backend=default_backend()
        )
    try:
        return private_key.decrypt(
            encrypted,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        ).decode()
    except ValueError:
        # thrown if decryption failed (and is likely due to old SHA1 encryption algorithm used)
        if not suppress_warnings:
            logging.warning("WARNING: decryption with SHA256 failed, trying SHA1...")
        try:
            # try to decrypt the value using SHA1 (note: this is an older format the pycrypto used).
            decrypted = private_key.decrypt(
                encrypted,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA1()),  # nosec
                    algorithm=hashes.SHA1(),  # nosec
                    label=None,
                ),
            )
            if not suppress_warnings:
                logging.info(
                    "* successfully decrypted using SHA1 (consider upgrading this item)"
                )
            return decrypted.decode()
        except Exception as e:
            logging.error(f"Decryption error (tried SHA256 and SHA1): {e}")
            return ""
    except Exception as e:
        logging.error(f"General decryption error: {e}")
        return ""


def encrypt(unencrypted=None):
    """
    Encrypt an unencrypted message.
    Return: encrypted message.
    NOTE: encrypt using RSA - SHA256 algorithm.
    """

    with open(expand_path(config.get("DEFAULT", "PublicKey")), "rb") as key_file:
        public_key = serialization.load_ssh_public_key(
            key_file.read(), backend=default_backend()
        )
    return public_key.encrypt(
        unencrypted.encode(),  # encode the string to utf-8.
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def format_pwd(pwd):
    """
    Format password for display.
    """

    return f"Password:\n\t{pwd}"


def write_to_clipboard(message):
    """
    Write message to clipboard.
    """

    logging.debug("* writing message to clipboard...")
    send_to_clipboard(text=message)
    logging.info("Value copied to Clipboard")
    if config.getint("DEFAULT", "ClipboardTimeToLive") > 0:
        t = threading.Timer(10.0, clear_clipboard)
        t.start()
        logging.info(
            f"\t(clipboard will be cleared in {config.getint('DEFAULT', 'ClipboardTimeToLive')} seconds)"
        )
    else:
        logging.error(
            f"Invalid CLIPBOARD_TTL [{config.getint('DEFAULT', 'ClipboardTimeToLive')}], please check configuration for proper setup"
        )


def clear_clipboard():
    """
    Clear clipboard.
    """

    send_to_clipboard("")
    logging.info("Clipboard cleared.")


def add_key(key=None, value=None, use_safe=None, requested_password_length=None):
    """
    Add a key/value to the store
    NOTE: if value is not specified the password-generator will be used to generate one.
    """

    logging.debug(f"* adding key [{key}] to store...")
    if value:
        val = value
    else:
        val = password_generate(
            use_safe=use_safe, requested_password_length=requested_password_length
        )
    with get_db_conn(mode="w").begin(write=True) as txn:
        k = key.encode()
        v = encrypt(unencrypted=val)
        txn.put(k, v)
    logging.info(f"* key [{key}] added to store")


def del_key(key):
    """
    Delete an item by key.
    """

    logging.debug(f"* deleting item by key [{key}]...")
    with get_db_conn(mode="w").begin(write=True) as txn:
        txn.delete(key.encode())
    logging.info("* key deleted from store")


def get_key(key):
    """
    Get a value by key.
    """

    enc_key = key.encode()
    logging.debug(f"* getting key: {key}")

    with get_db_conn(mode="r").begin() as txn:
        r = txn.get(enc_key)
        if r:
            val = decrypt(encrypted=r)
            if write_to_console:
                print(val)
            else:
                write_to_clipboard(val)
        else:
            logging.info("Key Not Found - the key supplied was not found.")


def get_allkv():
    """
    Get all key/values from the store.
    """

    logging.debug("* getting all key/values from store...")
    with get_db_conn(mode="r").begin() as txn:
        cursor = txn.cursor()
        for key, value in cursor:
            val = decrypt(encrypted=value, suppress_warnings=True)
            logging.info(f"{key.decode()}:{val}")


def get_allkeys():
    """
    Get all keys.
    """

    logging.debug("* getting all keys from store...")
    with get_db_conn(mode="r").begin() as txn:
        cursor = txn.cursor()
        for key, value in cursor:
            logging.info(f"{key.decode()}")


def password_generate(use_safe=False, requested_password_length=None):
    """
    Generate a pretty good random password.
    """

    logging.debug(
        f"* generating password with use_safe=[{use_safe}], password_length=[{requested_password_length}]"
    )
    # https://docs.python.org/3.1/library/string.html
    # printable, digits, ascii_letters, punctuation, whitespace         # take care of whitespace as it contains: tab, linefeed, return, formfeed and vertical tab.
    char_classes_default = (string.ascii_letters, string.digits, string.punctuation)
    char_classes_safe = (string.ascii_letters, string.digits)
    char_classes = char_classes_default
    if use_safe:
        logging.debug("** NOTICE: safe password requested!")
        char_classes = char_classes_safe

    password_length = config.getint("DEFAULT", "PasswordGeneratorLength")
    if requested_password_length:
        password_length = int(requested_password_length)
    if password_length < 13:
        logging.error(
            "Password Generator Error: the password length must be at least 13 characters."
        )
        return
    else:
        logging.debug(f"* generating password of length: {password_length}")
        char = lambda: secrets.choice(secrets.choice(char_classes))  # NOQA
        pw = lambda: "".join([char() for _ in range(password_length)])  # NOQA
        val = pw()
        return val


def password_generator(use_safe=False, requested_password_length=None):
    """
    Wrapper to password_generate.
    """

    val = password_generate(
        use_safe=use_safe, requested_password_length=requested_password_length
    )
    if val:
        if write_to_console:
            logging.info(format_pwd(val))
        else:
            write_to_clipboard(val)
    else:
        logging.error("An error occurred, password not created")


def send_to_clipboard(text=""):
    """
    Send text to the clipboard.
    """

    _clipboard_command = config.get("DEFAULT", "ClipboardCommand")
    cmd = f"echo '{text.strip()}' | {ast.literal_eval(_clipboard_command)}"
    logging.debug(f"- sending to clipboard with command: {cmd}")
    return subprocess.check_call(cmd, shell=True)  # nosec


def app():
    global write_to_console

    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option(
        "-g", "--get-key", dest="keyget", help="get an item by key from the store"
    )
    parser.add_option(
        "-a", "--add-key", dest="keyadd", help="add an item (key/value) to the store"
    )
    parser.add_option(
        "--value",
        dest="value",
        help="the value to add (only valid for '--add-key' mode) to the store",
    )
    parser.add_option("--delete-key", dest="keydel", help="delete an item by key")
    parser.add_option(
        "--dump",
        action="store_true",
        dest="allkeys",
        help="dump all keys from the store",
    )
    parser.add_option(
        "--dump-all",
        action="store_true",
        dest="allkv",
        help="dump all key/values from the store",
    )
    parser.add_option(
        "-p",
        "--password-generator",
        action="store_true",
        dest="pwgen",
        help="generate a password",
    )
    parser.add_option(
        "-s",
        "--safe",
        action="store_true",
        dest="pwgensafe",
        help="used with -p to make the password a 'safe' password (letters and numbers only)",
    )
    parser.add_option(
        "-l",
        "--length",
        dest="length",
        help="[optional] length of password to generate (config.PASSWORD_GENERATOR_LENGTH will be used if not specified)",
    )
    parser.add_option(
        "-u",
        "--to-console",
        action="store_true",
        dest="to_console",
        help="write results to console rather than to clipboard",
    )
    parser.add_option(
        "--version",
        action="store_true",
        dest="showVersion",
        help="show script version and exit",
    )

    (options, args) = parser.parse_args()

    if options.to_console:
        write_to_console = True

    if options.showVersion:
        show_version()
        sys.exit()
    if options.keydel:
        key = options.keydel
        del_key(key)
        sys.exit()
    if options.allkv:
        get_allkv()
        sys.exit()
    if options.allkeys:
        get_allkeys()
        sys.exit()
    if options.keyadd:
        add_key(
            key=options.keyadd,
            value=options.value,
            use_safe=options.pwgensafe,
            requested_password_length=options.length,
        )
        sys.exit()
    if options.keyget:
        key = options.keyget
        get_key(key)
        sys.exit()
    if options.pwgen:
        password_generator(
            use_safe=options.pwgensafe, requested_password_length=options.length
        )
        sys.exit()
