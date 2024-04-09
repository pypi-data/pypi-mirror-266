import getpass
import os


__all__ = (
    "COLORIZE",
    "LEVELS",
    "SANATIZED_USERNAME",
    "SANATIZATION_MODE"
    "sanatize_username",
    "log",
    "error",
    "warn",
    "info",
    "debug",
)


COLORIZE = True
LEVELS = {
    "error": "\u001b[33m",
    "warn":  "\u001b[33m",
    "info":  "\u001b[36m",
    "debug": "\u001b[34m",
}

# https://www.youtube.com/watch?v=dQw4w9WgXcQ
SANITIZED_USERNAME = "dQw4w9WgXcQ"
# "sanatize" - Replace username with SANATIZED_USERNAME
# "replace" - Replace path to home with ~
# "none" - No sanatization
SANATIZATION_MODE = "replace"

# Sadly there is no easy way for me to sanatize logging from the game's process because
# the Python process is replaced with the Java one when CR is launched.
def sanitize_username(string: str | list[str]) -> str:
    if SANATIZATION_MODE == "none":
        return string

    if type(string) == list:
        return [sanatize_username(s) for s in string]

    if SANATIZATION_MODE == "sanatize":
        replace = getpass.getuser()
        replace_with = SANITIZED_USERNAME
    elif SANATIZATION_MODE == "replace":
        replace = os.path.expanduser("~")
        replace_with = "~"

    return string.replace(replace, replace_with)


def log(text: str, level: str):
    if COLORIZE:
        print(sanitize_username(f"[{LEVELS[level]}{level}\u001b[0m]: {text}"))
    else:
        print(sanitize_username(f"[{level}]: {text}"))


def error(text: str): log(text, "error")
def warn(text: str):  log(text, "warn")
def info(text: str):  log(text, "info")
def debug(text: str): log(text, "debug")
