# Insurance Document Parser

A Python tool for extracting structured data from insurance policy documents using regular expressions.

## Overview

Automates extraction of policy information and financial data from unstructured insurance documents into structured JSON format.

## Fields Extracted

**Policy Information**
- Policy Number, Policyholder Name, Policy Type
- Effective Date, Expiration Date

**Financial Data**
- Premium, Total Premium, Taxes, Fees
- Coverage Amount, Deductible, Copay
- Payment Frequency

**Coverage Details**
- List of covered perils and benefits

## Approach

Uses rule-based regex patterns to match and extract field values. Multiple patterns per field handle format variations. Missing fields return null without errors.

## Installation

Requires Python 3.7+. No external dependencies.

```bash
python parser.py
```

## Usage

```bash
python parser.py
python test_parser.py
```

## Output

Generates JSON file with extracted fields. Missing fields return null.

## Limitations

- Requires consistent field labels and formatting
- Only extracts predefined fields
- English language only
- Date format: MM/DD/YYYY or DD-MM-YYYY

## Future Improvements

- PDF and DOCX support
- Table extraction
- Multi-language support
- Batch processing

## License

MIT License
