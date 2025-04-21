# Klarna Statement Parser

A simple Python tool to parse Klarna credit card statements and convert them to CSV format (so that it can be imported into Actual Budget)

## Requirements
- Python 3.7+
- pytest (for running tests)

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python klarnaParser.py --input statement.txt --output transactions.csv
```

## Testing
Run the tests using pytest:
```bash
pytest test_klarnaParser.py
```

If no input file is provided, it will process the example statement included in the code.