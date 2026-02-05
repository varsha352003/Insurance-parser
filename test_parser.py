import json
from parser import InsuranceParser


def test_sample_document():
    print("Testing Insurance Parser")
    print("=" * 50)
    
    parser = InsuranceParser('sample_insurance_policy.txt')
    parsed_data = parser.parse()
    
    print("\nExtraction Results:")
    print("-" * 50)
    
    for key, value in parsed_data.items():
        if key != 'coverage_details' and key != 'parsed_at':
            status = "✓" if value else "✗"
            print(f"{status} {key}: {value}")
    
    print(f"\nCoverage Details: {len(parsed_data.get('coverage_details', []))} items found")
    
    validation = parser.validate_parsed_data()
    print("\nValidation Results:")
    print("-" * 50)
    for check, result in validation.items():
        status = "✓" if result else "✗"
        print(f"{status} {check}: {result}")
    
    print("\n" + "=" * 50)
    if validation['is_complete']:
        print("✓ All critical fields extracted successfully")
    else:
        print("⚠ Some fields are missing - document may be incomplete")
    
    return parsed_data


def test_missing_fields():
    print("\n\nTesting with incomplete document")
    print("=" * 50)
    
    test_text = """
    Policy Number: TEST-123
    Policyholder: John Doe
    """
    
    with open('test_incomplete.txt', 'w') as f:
        f.write(test_text)
    
    parser = InsuranceParser('test_incomplete.txt')
    parsed_data = parser.parse()
    
    validation = parser.validate_parsed_data()
    print(f"\nValidation: {validation}")
    print("\nParser handles missing fields gracefully without crashes")
    
    import os
    os.remove('test_incomplete.txt')


if __name__ == '__main__':
    test_sample_document()
    test_missing_fields()
