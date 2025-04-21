from enum import Enum
from dataclasses import dataclass
import os
from typing import List, Iterator
from datetime import datetime
import argparse

from klarnaParserUtilities import *


klarnaExample = """ Example Klarna statement
7. Apr.
· 34,02 €

APOTHEKE E.K.
Self-Care
34,02 €
5. Apr.
· 70,13 €

Rewe Center
Nahrungsmittel
49,78 €

Metzgerei
Nahrungsmittel
20,35 €
4. Apr.
· 54,31 €

Rewe Center
Nahrungsmittel
54,31 €
3. Apr.
· 86,58 €

Spielwarenladen
Familie
"""

THISYEAR = datetime.now().year
debugParser = True

class TokenType(Enum):
    DATE = 1
    TEXT = 2
    AMOUNT = 3

class ParserState(Enum):
    EXPECT_DATE = 1
    EXPECT_BALANCE = 2
    EXPECT_PAYEE = 3
    EXPECT_CATEGORY = 4
    EXPECT_AMOUNT = 5
    EXPECT_PAYEE_OR_DATE = 6
    INIT = 7

@dataclass
class Transaction:
    date: str
    payee: str
    amount: float

@dataclass
class Token:
    tokenType: TokenType
    content: str

@debug_tokenize
def tokenizeLine(text: str) -> Token:
    """Convert a line of text into a Token object.
    
    Args:
        text: A single line from the Klarna statement
        Note: The line should not contain any leading or trailing whitespace. or be empty.
        
    Returns:
        Token: A Token object with appropriate TokenType and content
    """
    assert text, "Text should not be empty"
    if "€" == text[-1]:
        euroValue = extractAmount(text)
        return Token(TokenType.AMOUNT, euroValue)
    elif DATEMATCHER.match(text):
        return Token(TokenType.DATE, text)
    else:
        return Token(TokenType.TEXT, text)
    
def tokenizeText(text: Iterator[str]) -> List[Token]:
    """Tokenize multiple lines of Klarna statement text.
    
    Args:
        text: Iterator of lines from Klarna statement
        
    Returns:
        List of Token objects representing the parsed content
        
    Raises:
        AssertionError: If any line is empty
    """
    return [tokenizeLine(line) for line in text]

def parseTokens(tokens : List[Token]) -> List[Transaction]:
    """Parse a list of tokens into transactions.
    
    Args:
        tokens: List of Token objects representing the Klarna statement
        
    Returns:
        List of Transaction objects containing date, payee, and amount
        
    Note:
        Expects tokens in the following order:
        1. DATE
        2. AMOUNT (balance, ignored)
        3. TEXT (payee)
        4. TEXT (category, ignored)
        5. AMOUNT (transaction amount)

        Start with INIT state and ignores everything until the first date is found.
    """
    state = ParserState.EXPECT_DATE
    transactions = []
    
    for token in tokens:
        if state == ParserState.INIT:
            if token.tokenType == TokenType.DATE:
                state = ParserState.EXPECT_BALANCE
                current_date = createDateString(token.content)
            else:
                continue

        elif (state == ParserState.EXPECT_DATE or state == ParserState.EXPECT_PAYEE_OR_DATE) and token.tokenType == TokenType.DATE:
            current_date = createDateString(token.content)
            state = ParserState.EXPECT_BALANCE
            
        elif state == ParserState.EXPECT_BALANCE and token.tokenType == TokenType.AMOUNT:
            # Ignore balance line
            state = ParserState.EXPECT_PAYEE
            
        elif (state == ParserState.EXPECT_PAYEE or state == ParserState.EXPECT_PAYEE_OR_DATE) and token.tokenType == TokenType.TEXT:
            current_payee = token.content
            current_payee = current_payee.replace(",", " ").strip()
            state = ParserState.EXPECT_CATEGORY
            
        elif state == ParserState.EXPECT_CATEGORY and token.tokenType == TokenType.TEXT:
            # Ignore category line
            state = ParserState.EXPECT_AMOUNT
            
        elif state == ParserState.EXPECT_AMOUNT and token.tokenType == TokenType.AMOUNT:
            # Parse amount and create transaction
            amount = float(token.content.replace(",", "."))
            transactions.append(Transaction(current_date, current_payee, amount))
            state = ParserState.EXPECT_PAYEE_OR_DATE

    return transactions


def parse_args():
    parser = argparse.ArgumentParser(description='Parse Klarna statement')
    parser.add_argument('--input', '-i', nargs='?', help='Input file path')
    parser.add_argument('--output', '-o', nargs='?', help='Output CSV path')
    return parser.parse_args()

def main():
    arguments = parse_args()
    pathToInputFile = arguments.input
    outputFileName = arguments.output
    if pathToInputFile and not os.path.exists(pathToInputFile) and not os.path.isfile(pathToInputFile):
        print(f"Input file {pathToInputFile} does not exist.")
        return
    
    if pathToInputFile:
        text = readText(pathToInputFile)
    else:
        klarnaExampleNoEmptyLines = os.linesep.join([s for s in klarnaExample.splitlines() if s.strip()])
        text = klarnaExampleNoEmptyLines.splitlines()
    tokens = tokenizeText(text)
    transactions = parseTokens(tokens)
    if outputFileName:
        write_csv(transactions, outputFileName)
    else:
        # For debugging purposes, print the transactions
        print(transactions)

if __name__ == "__main__":
    main()