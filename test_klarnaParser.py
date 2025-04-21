import pytest
from klarnaParser import (
    TokenType, 
    Token, 
    Transaction,
    tokenizeLine,
    tokenizeText,
    parseTokens,
    extractAmount,
    createDateString
)

@pytest.fixture
def sample_klarna_text():
    return """7. Apr.
· 34,02 €
EISBAER APOTHEKE E.K.
Self-Care
34,02 €"""

def test_tokenize_line():
    # Test date token
    assert tokenizeLine("7. Apr.") == Token(TokenType.DATE, "7. Apr.")
    
    # Test amount token
    assert tokenizeLine("34,02 €") == Token(TokenType.AMOUNT, "34,02")
    
    # Test text token
    assert tokenizeLine("EISBAER APOTHEKE E.K.") == Token(TokenType.TEXT, "EISBAER APOTHEKE E.K.")

def test_extract_amount():
    assert extractAmount("34,02 €") == "34,02"
    assert extractAmount("1234,56 €") == "1234,56"

def test_create_date_string():
    assert createDateString("7. Apr.").endswith("-04-7")
    assert createDateString("15. Jan.").endswith("-01-15")
    assert createDateString("31. Dez.").endswith("-12-31")

def test_parse_tokens():
    tokens = [
        Token(TokenType.DATE, "7. Apr."),
        Token(TokenType.AMOUNT, "34,02"),
        Token(TokenType.TEXT, "EISBAER APOTHEKE E.K."),
        Token(TokenType.TEXT, "Self-Care"),
        Token(TokenType.AMOUNT, "34,02")
    ]
    
    transactions = parseTokens(tokens)
    assert len(transactions) == 1
    assert transactions[0].payee == "EISBAER APOTHEKE E.K."
    assert transactions[0].amount == 34.02

def test_tokenize_text(sample_klarna_text):
    lines = sample_klarna_text.split('\n')
    tokens = tokenizeText(lines)
    
    assert len(tokens) == 5
    assert tokens[0].tokenType == TokenType.DATE
    assert tokens[1].tokenType == TokenType.AMOUNT
    assert tokens[2].tokenType == TokenType.TEXT
    assert tokens[3].tokenType == TokenType.TEXT
    assert tokens[4].tokenType == TokenType.AMOUNT

def test_empty_input():
    with pytest.raises(AssertionError):
        tokenizeLine("")

def test_invalid_amount_format():
    with pytest.raises(ValueError):
        extractAmount("34.02")  # Wrong decimal separator

def test_full_transaction_flow(sample_klarna_text):
    lines = sample_klarna_text.split('\n')
    tokens = tokenizeText(lines)
    transactions = parseTokens(tokens)
    
    assert len(transactions) == 1
    transaction = transactions[0]
    assert isinstance(transaction, Transaction)
    assert transaction.payee == "EISBAER APOTHEKE E.K."
    assert transaction.amount == 34.02