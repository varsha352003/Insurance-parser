import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False


FINANCIAL_FIELDS = [
    'premium',
    'total_premium',
    'taxes',
    'fees',
    'coverage_amount',
    'deductible',
    'effective_date',
    'expiration_date',
    'payment_frequency',
    'copay',
]

CURRENCY_SYMBOLS = r'(?:USD|INR|\$|Rs\.?)?'
NUMERIC_PATTERN = r'([\d,]+(?:\.\d{2})?)'
DATE_PATTERN = r'(\d{2}[/-]\d{2}[/-]\d{4})'


def extract_text_from_file(file_path: str) -> str:
    file_extension = Path(file_path).suffix.lower()
    
    if file_extension == '.pdf':
        if not PDF_SUPPORT:
            raise ImportError("pdfplumber not installed. Install with: pip install pdfplumber")
        
        text_content = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
        return '\n'.join(text_content)
    
    elif file_extension == '.txt':
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    else:
        raise ValueError(f"Unsupported file type: {file_extension}. Use .txt or .pdf")


class InsuranceParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.raw_text = ""
        self.normalized_text = ""
        self.parsed_data = {}

    def normalize_text(self, text: str) -> str:
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            trimmed = line.strip()
            single_spaced = ' '.join(trimmed.split())
            cleaned_lines.append(single_spaced)
        
        normalized = '\n'.join(cleaned_lines)
        normalized = re.sub(r'\n{3,}', '\n\n', normalized)
        
        return normalized

    def _extract_with_patterns(self, patterns: List[str], clean_numeric: bool = False) -> Optional[str]:
        for pattern in patterns:
            match = re.search(pattern, self.normalized_text, re.IGNORECASE)
            if match:
                extracted_value = match.group(1)
                if clean_numeric:
                    extracted_value = extracted_value.replace(',', '')
                return extracted_value.strip() if isinstance(extracted_value, str) else extracted_value
        return None

    def read_document(self) -> str:
        try:
            self.raw_text = extract_text_from_file(self.file_path)
        except FileNotFoundError:
            raise FileNotFoundError(f"Document not found: {self.file_path}")
        except PermissionError:
            raise PermissionError(f"Permission denied: {self.file_path}")
        except ImportError as e:
            raise ImportError(str(e))
        except Exception as e:
            raise Exception(f"Error reading document: {str(e)}")
        
        self.normalized_text = self.normalize_text(self.raw_text)
        return self.raw_text

    def extract_policy_number(self) -> Optional[str]:
        try:
            patterns = [
                r'Policy\s+(?:Number|No\.?|#)\s*:?\s*([A-Z0-9][A-Z0-9-/\\]+)'
            ]
            return self._extract_with_patterns(patterns)
        except Exception:
            return None

    def extract_policyholder(self) -> Optional[str]:
        try:
            patterns = [
                r'Policyholder(?:\s+Name)?:\s*([A-Za-z\s]+?)(?:\n|$)'
            ]
            return self._extract_with_patterns(patterns)
        except Exception:
            return None

    def extract_policy_type(self) -> Optional[str]:
        try:
            patterns = [
                r'Policy\s+Type:\s*([A-Za-z\s]+?)(?:\n|$)'
            ]
            return self._extract_with_patterns(patterns)
        except Exception:
            return None

    def extract_effective_date(self) -> Optional[str]:
        try:
            patterns = [
                rf'(?:Effective|Start|Commencement|From)\s+Date\s*:?\s*{DATE_PATTERN}',
                rf'Policy\s+(?:Start|Effective)\s+Date\s*:?\s*{DATE_PATTERN}',
                rf'(?:Valid|Coverage)\s+From\s*:?\s*{DATE_PATTERN}'
            ]
            date_value = self._extract_with_patterns(patterns)
            if date_value:
                return date_value.replace('-', '/')
            return None
        except Exception:
            return None

    def extract_expiration_date(self) -> Optional[str]:
        try:
            patterns = [
                rf'(?:Expiration|Expiry|End|To)\s+Date\s*:?\s*{DATE_PATTERN}',
                rf'Policy\s+(?:End|Expiry)\s+Date\s*:?\s*{DATE_PATTERN}',
                rf'(?:Valid|Coverage)\s+(?:Until|To)\s*:?\s*{DATE_PATTERN}'
            ]
            date_value = self._extract_with_patterns(patterns)
            if date_value:
                return date_value.replace('-', '/')
            return None
        except Exception:
            return None

    def extract_coverage_amount(self) -> Optional[str]:
        try:
            patterns = [
                rf'(?:Coverage|Sum)\s+(?:Amount|Insured)\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}',
                rf'Sum\s+Insured\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}',
                rf'Insured\s+(?:Amount|Value)\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}'
            ]
            return self._extract_with_patterns(patterns, clean_numeric=True)
        except Exception:
            return None

    def extract_premium(self) -> Optional[str]:
        try:
            patterns = [
                rf'(?:Base|Basic|Net)\s+Premium\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}',
                rf'Premium\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}',
                rf'(?:Monthly|Annual|Yearly)\s+Premium\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}'
            ]
            return self._extract_with_patterns(patterns, clean_numeric=True)
        except Exception:
            return None

    def extract_total_premium(self) -> Optional[str]:
        try:
            patterns = [
                rf'Total\s+Premium\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}',
                rf'(?:Gross|Final)\s+Premium\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}',
                rf'Premium\s+(?:Total|Amount)\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}'
            ]
            return self._extract_with_patterns(patterns, clean_numeric=True)
        except Exception:
            return None

    def extract_taxes(self) -> Optional[str]:
        try:
            patterns = [
                rf'(?:GST|Tax|Service\s+Tax)\s*(?:Amount)?\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}',
                rf'Tax(?:es)?\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}',
                rf'(?:Policy|Insurance)\s+Tax\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}',
                rf'GST\s*@?\s*\d+%?\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}'
            ]
            return self._extract_with_patterns(patterns, clean_numeric=True)
        except Exception:
            return None

    def extract_fees(self) -> Optional[str]:
        try:
            patterns = [
                rf'(?:Administrative|Processing|Service)\s+Fee\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}',
                rf'Fee(?:s)?\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}',
                rf'(?:Stamp|Policy)\s+Fee\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}'
            ]
            return self._extract_with_patterns(patterns, clean_numeric=True)
        except Exception:
            return None

    def extract_deductible(self) -> Optional[str]:
        try:
            patterns = [
                rf'Deductible\s*(?:Amount)?\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}',
                rf'(?:Standard|Basic)\s+Deductible\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}',
                rf'(?:Excess|Co-payment)\s*:?\s*{CURRENCY_SYMBOLS}\s*{NUMERIC_PATTERN}'
            ]
            return self._extract_with_patterns(patterns, clean_numeric=True)
        except Exception:
            return None

    def extract_payment_frequency(self) -> Optional[str]:
        try:
            patterns = [
                r'Payment\s+Frequency\s*:?\s*((?:Monthly|Quarterly|Annual|Yearly|Bi-?annual|Semi-?annual))',
                r'Billed\s+(Monthly|Quarterly|Annual|Yearly)',
                r'(?:Monthly|Quarterly|Annual|Yearly)\s+(?:Payment|Billing)'
            ]
            frequency = self._extract_with_patterns(patterns)
            return frequency.lower() if frequency else None
        except Exception:
            return None

    def extract_copay(self) -> Optional[str]:
        try:
            patterns = [
                r'Co-?pay\s*:?\s*\$?([\d,]+(?:\.\d{2})?)',
                r'Copayment\s*:?\s*\$?([\d,]+(?:\.\d{2})?)'
            ]
            return self._extract_with_patterns(patterns, clean_numeric=True)
        except Exception:
            return None

    def extract_coverage_details(self) -> List[str]:
        try:
            section_match = re.search(
                r'Coverage Details:(.*?)(?=\n\n|\Z)', 
                self.raw_text, 
                re.DOTALL | re.IGNORECASE
            )
            if section_match:
                section_content = section_match.group(1)
                items = re.findall(r'-\s*(.+)', section_content)
                return [item.strip() for item in items]
            return []
        except Exception:
            return []

    def validate_parsed_data(self) -> Dict[str, bool]:
        has_policy_number = self.parsed_data.get('policy_number') is not None
        has_policyholder = self.parsed_data.get('policyholder') is not None
        has_dates = (
            self.parsed_data.get('effective_date') is not None and 
            self.parsed_data.get('expiration_date') is not None
        )
        has_financial_data = any([
            self.parsed_data.get('premium'),
            self.parsed_data.get('coverage_amount'),
            self.parsed_data.get('total_premium')
        ])
        
        return {
            'has_policy_number': has_policy_number,
            'has_policyholder': has_policyholder,
            'has_dates': has_dates,
            'has_financial_data': has_financial_data,
            'is_complete': all([has_policy_number, has_policyholder, has_dates, has_financial_data])
        }

    def get_default_structure(self) -> Dict:
        return {
            'policy_number': None,
            'policyholder': None,
            'policy_type': None,
            'effective_date': None,
            'expiration_date': None,
            'coverage_amount': None,
            'premium': None,
            'total_premium': None,
            'taxes': None,
            'fees': None,
            'deductible': None,
            'payment_frequency': None,
            'copay': None,
            'coverage_details': None,
            'parsed_at': None
        }

    def parse(self) -> Dict:
        try:
            self.read_document()
        except Exception:
            return self.get_default_structure()
        
        self.parsed_data = {
            'policy_number': self.extract_policy_number(),
            'policyholder': self.extract_policyholder(),
            'policy_type': self.extract_policy_type(),
            'effective_date': self.extract_effective_date(),
            'expiration_date': self.extract_expiration_date(),
            'coverage_amount': self.extract_coverage_amount(),
            'premium': self.extract_premium(),
            'total_premium': self.extract_total_premium(),
            'taxes': self.extract_taxes(),
            'fees': self.extract_fees(),
            'deductible': self.extract_deductible(),
            'payment_frequency': self.extract_payment_frequency(),
            'copay': self.extract_copay(),
            'coverage_details': self.extract_coverage_details(),
            'parsed_at': datetime.now().isoformat()
        }
        
        return self.parsed_data

    def save_to_json(self, output_path: str) -> None:
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(self.parsed_data, file, indent=4, ensure_ascii=False)
        except PermissionError:
            raise PermissionError(f"Permission denied writing to: {output_path}")
        except Exception as e:
            raise Exception(f"Error writing JSON file: {str(e)}")

    def export_to_json(self, output_path: str = 'sample_output.json') -> str:
        self.save_to_json(output_path)
        return output_path


def main():
    input_file = 'sample_insurance_policy.pdf'
    output_file = 'sample_output.json'
    
    try:
        parser = InsuranceParser(input_file)
        extracted_data = parser.parse()
        parser.export_to_json(output_file)
        
        print(f"Successfully parsed: {input_file}")
        print(f"Output saved to: {output_file}")
        print("\nExtracted Data:")
        print(json.dumps(extracted_data, indent=4, ensure_ascii=False))
        
        return 0
        
    except (FileNotFoundError, PermissionError) as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
