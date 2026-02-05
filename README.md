# Insurance Document Parser

A Python-based tool for extracting structured financial and policy information from insurance policy documents using rule-based pattern matching.

## Goal

This parser automates the extraction of critical financial and policy data from insurance documents, converting unstructured text into structured JSON format. It enables downstream systems to process insurance information without manual data entry, reducing errors and improving efficiency.

## Financial Fields Extracted

The parser extracts the following key fields from insurance policy documents:

### Policy Information
- Policy Number
- Policyholder Name
- Policy Type
- Effective Date (Policy Start Date)
- Expiration Date (Policy End Date)

### Financial Data
- Base Premium
- Total Premium (Gross Premium)
- Taxes (GST/Service Tax)
- Administrative and Processing Fees
- Deductible Amount
- Copay Amount
- Coverage Amount (Sum Insured)
- Payment Frequency

### Coverage Details
- List of covered perils and benefits
- Coverage terms and conditions

## Parsing Approach

The parser uses a rule-based approach with regular expressions to extract data:

1. **Text Normalization**: Input text is normalized by removing extra whitespace and standardizing line breaks for consistent pattern matching.

2. **Pattern Matching**: Each field has multiple regex patterns to handle format variations (e.g., "Premium:", "Base Premium:", "Monthly Premium:").

3. **Currency Handling**: Patterns recognize multiple currency symbols (USD, INR, $, Rs.) and automatically strip commas from numeric values.

4. **Graceful Degradation**: Missing fields return null values rather than causing errors, ensuring partial extraction succeeds even with incomplete documents.

5. **Structured Output**: All extracted data is returned in a consistent dictionary structure and exported to JSON.

## Why Rule-Based Method

The rule-based regex approach was chosen for several reasons:

**Deterministic and Transparent**: The extraction logic is explicit and auditable. Each regex pattern clearly defines what it matches.

**No Training Data Required**: Unlike machine learning approaches, this method works immediately without labeled training data.

**Lightweight and Fast**: Uses only Python standard library with no external dependencies. Parsing is near-instantaneous.

**Predictable Behavior**: Given the same input, the parser always produces identical output, making it reliable for production systems.

**Easy to Maintain**: Adding new fields or patterns requires only adding new regex patterns, not retraining models.

**Domain-Specific Optimization**: Patterns can be precisely tuned for insurance document conventions and terminology.

## Limitations

**Format Dependency**: The parser relies on consistent field labels and formatting. Documents with significantly different structures may require pattern updates.

**No Semantic Understanding**: The parser matches text patterns without understanding context. It cannot infer missing information or resolve ambiguities.

**Fixed Field Set**: Only extracts predefined fields. Novel fields in documents are ignored.

**Limited Error Recovery**: Malformed or ambiguous values may not be extracted correctly. The parser returns null for failed matches.

**Single Language**: Currently optimized for English-language documents. Other languages would require new patterns.

**No Table Extraction**: Cannot extract data from complex tables or multi-column layouts.

**Date Format Constraints**: Expects dates in MM/DD/YYYY or DD-MM-YYYY formats. Other formats may not be recognized.

## Future Improvements

**Enhanced Pattern Libraries**: Expand regex patterns to cover more document format variations and insurance types.

**Multi-Format Support**: Add support for PDF, DOCX, and image-based documents using OCR preprocessing.

**Table Extraction**: Implement structured table parsing for premium breakdowns and coverage schedules.

**Validation Layer**: Add field validation to check for reasonable value ranges and internal consistency.

**Fuzzy Matching**: Incorporate approximate string matching for fields with typos or OCR errors.

**Configuration-Driven Patterns**: Allow users to define custom extraction patterns via configuration files.

**Batch Processing**: Add support for processing multiple documents in parallel.

**Confidence Scores**: Provide extraction confidence metrics for each field to flag uncertain results.

**Machine Learning Hybrid**: Combine rule-based extraction with ML models for handling edge cases and unstructured sections.

**Multi-Language Support**: Add internationalization for documents in languages beyond English.

## Project Structure

```
Insurance-parser/
├── parser.py                    # Main parsing script
├── sample_insurance_policy.txt  # Sample input document
├── sample_output.json          # Sample parsed output
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore patterns
└── README.md                   # Documentation
```

## Installation

No external dependencies required. Python 3.7+ is sufficient.

```bash
git clone <repository-url>
cd Insurance-parser
```

## Usage

### Basic Usage

Run the parser on the sample document:

```bash
python parser.py
```

### Using as a Module

```python
from parser import InsuranceParser

parser = InsuranceParser('path/to/policy.txt')
parsed_data = parser.parse()
parser.export_to_json('output.json')

print(parsed_data['policy_number'])
print(parsed_data['premium'])
```

### Individual Field Extraction

```python
from parser import InsuranceParser

parser = InsuranceParser('policy_document.txt')
parser.read_document()

policy_number = parser.extract_policy_number()
coverage_amount = parser.extract_coverage_amount()
dates = {
    'start': parser.extract_effective_date(),
    'end': parser.extract_expiration_date()
}
```

## Output Format

```json
{
  "policy_number": "HOM-2024-789456",
  "policyholder": "Sarah Johnson",
  "policy_type": "Homeowners Insurance",
  "effective_date": "01/15/2024",
  "expiration_date": "01/15/2025",
  "coverage_amount": "450000",
  "premium": "1850.00",
  "total_premium": null,
  "taxes": null,
  "fees": null,
  "deductible": "1000",
  "payment_frequency": null,
  "copay": null,
  "coverage_details": [
    "Dwelling coverage up to policy limit",
    "Personal property protection",
    "Liability coverage"
  ],
  "parsed_at": "2026-02-05T10:30:00.000000"
}
```

## Requirements

- Python 3.7+
- Standard library only (re, json, datetime, typing)

## License

MIT License
