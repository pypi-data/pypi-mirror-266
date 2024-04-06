### About

spw is an application that stores and retrieves passwords in a secure manner. spw is designed to be quick, light on resources/dependencies, and command line/script driven.

Passwords are stored in an encrypted format using PKCS1_OAEP encryption. This means you use a public and private key to encrypt and decrypt items stored within the store. This is a secure method of password storage and there is virtually no chance someone (including yourself) can view decrypted passwords without the private key.

spw is intended to provide a secure mechanism to store (and more importantly retrieve) passwords. spw's command-line interface allows easy integration into openbox's keyboard shortcut functionality (or similar tools). spw provides an easy mechanism for copying a password to the clipboard (e.g. C+A+j will copy the gmail junk account's password to your clipboard).


### Latest Changes

- upgraded packages: lmdb, cryptography
- changed --version to use importlib.metadata


### Requiremnts

- python3


### Install

We recommend using [pipx](https://github.com/pypa/pipx). To install:

- with pipx: `pipx install spw`
- with pip: `pip install --user spw`


### Configure

cryptik uses a config file to store your setup. This file contains information where your secure database is stored and the private key to use as well as other configuration items. You can grab the sample config file from  [spw/example/spw.ini.template](https://gitlab.com/drad/spw/-/blob/master/examples/spw.ini.template) and place it at `~/.config/spw/spw.ini`.

Refer to the example `spw.ini.template` file for details on each config item. The default (e.g. `spw.ini.template`) should suffice for most usage; however, you can change where your keys are located, logging level, and more in the file.


### Usage

After spw has been installed and setup you can use it as follows:
- add a key: `spw --add-key="abc" --value="123"`
- get a key: `spw --get-key="abc"`
  + note that the password retrieved is not show but rather placed on your clipboard so you can easily paste it somewhere ;-)

You can find more on the usage by calling help: `spw --help`


### Notes

- to avoid special character issues in keys/values, surround them with single (') or double (") quotes. If your password has single quotes in it, surround it with double quotes. If your password has double quotes in it, surround it with single quotes.
- you can use spw to store any string for quick retrieval, a commonly used URL, a base64 encoded picture, a snippet of code, etc.


### More Info

- [Wiki](https://g.dradux.com/dradux/spw/wikis/home)
- [Issues/Enhancements](https://g.dradux.com/dradux/spw/issues)
- [bandit](https://github.com/PyCQA/bandit)
- [flake8](https://gitlab.com/pycqa/flake8)
