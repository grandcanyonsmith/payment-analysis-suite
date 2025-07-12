#!/usr/bin/env python3
"""
Email Validator using Mailgun API
"""

import requests
from typing import Dict, Any
import re


class MailgunEmailValidator:
    def __init__(self):
        # Mailgun API credentials from environment variables
        import os
        self.public_key = os.getenv('MAILGUN_PUBLIC_KEY', '')
        self.api_key = os.getenv('MAILGUN_API_KEY', '')
        self.base_url = "https://api.mailgun.net/v4"
        
        if not self.api_key:
            print("⚠️  Warning: MAILGUN_API_KEY not set. Only basic validation will be available.")
        
    def validate_email_basic(self, email: str) -> Dict[str, Any]:
        """
        Basic email validation using regex patterns.
        This is used as a fallback when API validation fails.
        
        Args:
            email (str): The email address to validate
            
        Returns:
            Dict[str, Any]: Basic validation result
        """
        # Basic email regex pattern
        email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        # Check if email matches basic pattern
        is_syntax_valid = bool(email_pattern.match(email))
        
        # Extract domain
        domain = email.split('@')[1] if '@' in email else ''
        
        # List of common free email providers
        free_providers = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'aol.com', 'mail.com', 'protonmail.com', 'icloud.com'
        ]
        
        # List of common disposable email domains
        disposable_domains = [
            'tempmail.com', '10minutemail.com', 'guerrillamail.com',
            'mailinator.com', 'throwaway.email'
        ]
        
        # Check for role-based emails
        role_prefixes = [
            'admin', 'info', 'support', 'sales', 'contact',
            'help', 'noreply', 'no-reply', 'postmaster'
        ]
        local_part = email.split('@')[0] if '@' in email else ''
        is_role = any(local_part.lower().startswith(prefix)
                     for prefix in role_prefixes)
        
        return {
            'is_valid': is_syntax_valid,
            'is_syntax_valid': is_syntax_valid,
            'is_domain_valid': is_syntax_valid,  # Basic check only
            'is_smtp_valid': None,  # Cannot check without API
            'is_catch_all': None,  # Cannot check without API
            'is_role_address': is_role,
            'is_free': domain.lower() in free_providers,
            'is_disposable': domain.lower() in disposable_domains,
            'risk': 'unknown',
            'validation_method': 'basic_regex'
        }
        
    def validate_email(self, email: str) -> Dict[str, Any]:
        """
        Validate an email address using Mailgun's email validation API.
        Falls back to basic validation if API fails.
        
        Args:
            email (str): The email address to validate
            
        Returns:
            Dict[str, Any]: Validation result from Mailgun API or basic
        """
        url = f"{self.base_url}/address/validate"
        
        # Parameters for the validation request
        params = {
            'address': email,
            'provider_lookup': 'true'  # Enable provider-specific checks
        }
        
        print("🔄 Attempting Mailgun API validation...")
        
        try:
            # Try with API key as password
            auth = ('api', self.api_key)
            response = requests.get(url, auth=auth, params=params)
            
            if response.status_code == 401:
                print("⚠️  API authentication failed. Trying alternative...")
                # Try with public key
                params['public_key'] = self.public_key
                response = requests.get(url, params=params)
            
            response.raise_for_status()
            result = response.json()
            result['validation_method'] = 'mailgun_api'
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️  API validation failed: {str(e)}")
            print("📝 Falling back to basic validation...")
            
            # Fall back to basic validation
            result = self.validate_email_basic(email)
            result['api_error'] = str(e)
            return result
    
    def print_validation_result(self, email: str,
                                result: Dict[str, Any]) -> None:
        """
        Pretty print the validation result.
        
        Args:
            email (str): The email address that was validated
            result (Dict[str, Any]): The validation result
        """
        separator = '=' * 60
        print(f"\n{separator}")
        print(f"Email Validation Result for: {email}")
        print(separator)
        
        validation_method = result.get('validation_method', 'unknown')
        if validation_method == 'basic_regex':
            print("⚠️  Using basic validation (API unavailable)")
        
        if 'error' in result and 'api_error' not in result:
            print(f"❌ Error: {result['error']}")
            return
        
        # Handle Mailgun API response format
        if validation_method == 'mailgun_api':
            # Get validation result from Mailgun format
            mailgun_result = result.get('result', 'unknown')
            is_valid = mailgun_result in ['deliverable', 'undeliverable']
            is_deliverable = mailgun_result == 'deliverable'
            
            # Display validation status
            if is_deliverable:
                print("✅ Valid Email Address (Deliverable)")
            elif mailgun_result == 'undeliverable':
                print("❌ Invalid Email Address (Undeliverable)")
            elif mailgun_result == 'unknown':
                print("⚠️  Email Status Unknown")
            else:
                print(f"ℹ️  Status: {mailgun_result}")
            
            # Display detailed information
            print("\nDetails:")
            print(f"  • Result: {mailgun_result}")
            print(f"  • Risk Level: {result.get('risk', 'unknown')}")
            print(f"  • Disposable: {result.get('is_disposable_address', False)}")
            print(f"  • Role Address: {result.get('is_role_address', False)}")
            
            # Display engagement info if available
            engagement = result.get('engagement', {})
            if engagement:
                print(f"  • Engagement: {engagement.get('behavior', 'unknown')}")
                print(f"  • Actively Engaging: "
                      f"{engagement.get('engaging', False)}")
                print(f"  • Is Bot: {engagement.get('is_bot', False)}")
            
            # Display reason if available
            reasons = result.get('reason', [])
            if reasons:
                print("\n📝 Reasons:")
                for reason in reasons:
                    print(f"  - {reason}")
        else:
            # Handle basic validation format
            is_valid = result.get('is_valid', False)
            risk = result.get('risk', 'unknown')
            
            # Display validation status
            if is_valid:
                print("✅ Valid Email Address")
            else:
                print("❌ Invalid Email Address")
            
            # Display detailed information
            print("\nDetails:")
            print(f"  • Risk Level: {risk}")
            print(f"  • Syntax Valid: {result.get('is_syntax_valid', False)}")
            print(f"  • Domain Exists: {result.get('is_domain_valid', False)}")
            
            # Only show SMTP valid if we have the data
            smtp_valid = result.get('is_smtp_valid')
            if smtp_valid is not None:
                print(f"  • SMTP Valid: {smtp_valid}")
            
            # Only show catch-all if we have the data
            catch_all = result.get('is_catch_all')
            if catch_all is not None:
                print(f"  • Catch-all: {catch_all}")
                
            print(f"  • Role Address: {result.get('is_role_address', False)}")
            print(f"  • Free Email: {result.get('is_free', False)}")
            print(f"  • Disposable: {result.get('is_disposable', False)}")
            
            # Display suggestion if available
            if 'did_you_mean' in result and result['did_you_mean']:
                print(f"\n💡 Did you mean: {result['did_you_mean']}")
            
            # Display reason if email is invalid
            if not is_valid and 'reason' in result:
                print(f"\n📝 Reason: {result['reason']}")
        
        # Show API error if present
        if 'api_error' in result:
            print(f"\n⚠️  API Note: {result['api_error']}")
        
        print(f"{separator}\n")


def main():
    """Main function to run the email validator."""
    # Create validator instance
    validator = MailgunEmailValidator()
    
    # Email to validate (as requested)
    email_to_validate = "canyonfsmith@gmail.com"
    
    print(f"🔍 Validating email: {email_to_validate}")
    
    # Validate the email
    result = validator.validate_email(email_to_validate)
    
    # Print the result
    validator.print_validation_result(email_to_validate, result)
    
    # Optional: Interactive mode
    while True:
        user_input = input(
            "\nEnter another email to validate (or 'quit' to exit): "
        )
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        if user_input:
            result = validator.validate_email(user_input)
            validator.print_validation_result(user_input, result)


if __name__ == "__main__":
    main() 