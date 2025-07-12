#!/usr/bin/env python3
"""
Validate emails from CSV file and add validation marks
"""

import csv
from email_validator import MailgunEmailValidator
import time


def validate_csv_emails(input_file='emails.csv',
                        output_file='emails_validated.csv'):
    """
    Read emails from CSV, validate them, and add validation marks.
    
    Args:
        input_file (str): Input CSV filename
        output_file (str): Output CSV filename with validation marks
    """
    # Create validator instance
    validator = MailgunEmailValidator()
    
    # Read the input CSV
    with open(input_file, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        headers = next(reader)  # Get the header row
        
        # Prepare output data
        output_headers = headers + ['Validation']
        output_rows = []
        
        print(f"🔍 Validating emails from {input_file}...")
        print(f"{'='*60}\n")
        
        for row_num, row in enumerate(reader, start=2):
            if row:  # Skip empty rows
                email = row[0].strip()
                print(f"[{row_num-1}/49] Validating: {email}")
                
                try:
                    # Validate the email
                    result = validator.validate_email(email)
                    
                    # Determine validation mark based on result
                    if result.get('validation_method') == 'mailgun_api':
                        # Using Mailgun API response
                        mailgun_result = result.get('result', 'unknown')
                        if mailgun_result == 'deliverable':
                            mark = '✅'
                        elif mailgun_result in ['undeliverable',
                                                'do_not_send']:
                            mark = '❌'
                        else:
                            mark = '⚠️'
                    else:
                        # Using basic validation
                        if result.get('is_valid', False):
                            mark = '✅'
                        else:
                            mark = '❌'
                    
                    # Add row with validation mark
                    output_rows.append(row + [mark])
                    
                    # Show brief result
                    print(f"   → {mark} {result.get('result', 'validated')}")
                    
                except Exception as e:
                    print(f"   → ⚠️ Error: {str(e)}")
                    output_rows.append(row + ['⚠️'])
                
                # Add small delay to avoid rate limiting
                time.sleep(0.1)
    
    # Write the output CSV with validation marks
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(output_headers)
        writer.writerows(output_rows)
    
    print(f"\n{'='*60}")
    print(f"✅ Validation complete! Results saved to: {output_file}")
    
    # Show summary
    valid_count = sum(1 for row in output_rows if '✅' in row[-1])
    invalid_count = sum(1 for row in output_rows if '❌' in row[-1])
    warning_count = sum(1 for row in output_rows if '⚠️' in row[-1])
    
    print("\nSummary:")
    print(f"  • ✅ Valid emails: {valid_count}")
    print(f"  • ❌ Invalid emails: {invalid_count}")
    print(f"  • ⚠️ Warnings/Unknown: {warning_count}")
    print(f"  • Total processed: {len(output_rows)}")


if __name__ == "__main__":
    validate_csv_emails() 