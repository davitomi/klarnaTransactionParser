import re
from typing import List, Callable
from functools import wraps
from enum import Enum
from datetime import datetime

# Constants
THISYEAR = datetime.now().year

# Set this to true to 
debugParser = False


EUROVALUEMATCHER = re.compile(r"(\d+,\d{2})\s*€")
DATEMATCHER = re.compile(r"(\d{1,2}\.\s*[A-Za-z]+)\.")
CSVHEADER = "Date,Payee,Amount"

class InvalidDateFormatError(Exception):
    """Raised when date format is invalid."""
    pass


def extractAmount(text: str):
    # Convert "XX,YY €" to the string XX,YY
    match = EUROVALUEMATCHER.search(text)
    if match is None:
        raise ValueError("No amount found in text (maybe cents separated by a dot instead of a comma?)")
    return match.group(1)

def createDateString(date: str):
    # Convert "7. Apr." to "2025-04-07"
    month_map = {
        "Jan.": "01", "Feb.": "02", "März": "03", "Apr.": "04",
        "Mai": "05", "Juni": "06", "Juli": "07", "Aug.": "08",
        "Sept.": "09", "Okt.": "10", "Nov.": "11", "Dez.": "12"
    }
    day, month = date.split(".", 1)
    month = month_map[month.strip()]
    if not month:
        raise InvalidDateFormatError(f"Invalid month in date: {date}")
    return f"{THISYEAR}-{month}-{day.strip()}"

def write_csv(transactions: List, output_file: str):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(CSVHEADER + "\n")
        for t in transactions:
            f.write(f"{t.date},{t.payee},{t.amount:.2f}\n")

def debug_tokenize(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(text: str):
        if not debugParser:
            return func(text)
        print(f"\nTokenizing text: '{text}'")
        token = func(text)
        print(f"Created token: {token.tokenType.name} with content '{token.content}'")
        return token
    return wrapper

def readText(pathToFile : str) :
    with open(pathToFile, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip() is not "":
                yield line.strip()
            else:
                continue