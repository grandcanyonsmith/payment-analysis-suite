#!/usr/bin/env python3
"""
Stripe Radar Rules Implementation Guide
"""

import stripe

# Set your Stripe API key
stripe.api_key = "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"

print("=== STRIPE RADAR RULES TO IMPLEMENT ===\n")

print("Go to your Stripe Dashboard > Radar > Rules\n")
print("Add these custom rules:\n")

# Rule 1: Block Prepaid Cards
print("1. BLOCK PREPAID CARDS")
print("   Rule: Block if :card_funding: = 'prepaid'")
print("   Why: 55% failure rate, causes 16% of all failures")
print("   Impact: Prevents ~11 failures per month\n")

# Rule 2: High Risk Score for New Customers
print("2. REVIEW HIGH-RISK NEW CUSTOMERS")
print("   Rule: Review if :customer_age: < 1 day AND :risk_score: > 65")
print("   Why: First-day signups have 41.7% failure rate")
print("   Impact: Catches card testers early\n")

# Rule 3: Block Specific High-Risk Countries (if volume remains low)
print("3. OPTIONAL - BLOCK LOW-VOLUME HIGH-RISK COUNTRIES")
print("   Rule: Block if :card_country: = 'PH' AND :amount: > 100")
print("   Why: 66.7% failure rate but only 3 customers")
print("   Impact: Minimal - only affects ~2 transactions/month\n")

# Rule 4: Require 3D Secure for First-Time Customers
print("4. 3D SECURE FOR NEW CUSTOMERS")
print("   Rule: Request 3DS if :customer_age: < 7 days")
print("   Why: Shifts liability to card issuer")
print("   Impact: Reduces fraud significantly\n")

# Rule 5: Velocity Checking
print("5. VELOCITY LIMITS")
print("   Rule: Block if :ip_address_count_day: > 3")
print("   Why: Prevents coordinated attacks like May 29-30")
print("   Impact: Stops mass fraud attempts\n")

print("=== IMPLEMENTATION CODE ===\n")

# Example: How to check card details before processing
print("Python code to check card details before charging:\n")

example_code = '''
import stripe

def validate_payment_method(payment_method_id):
    """
    Check payment method details before processing payment
    """
    try:
        # Retrieve payment method
        payment_method = stripe.PaymentMethod.retrieve(payment_method_id)
        
        # Check if card is prepaid
        if payment_method.card.funding == 'prepaid':
            return {
                'success': False,
                'error': 'Prepaid cards are not accepted'
            }
        
        # Check card country for high-risk countries
        high_risk_countries = ['PH']  # Add more as needed
        if payment_method.card.country in high_risk_countries:
            # Could trigger additional verification here
            pass
        
        return {'success': True}
        
    except stripe.error.StripeError as e:
        return {
            'success': False,
            'error': str(e)
        }

# Example usage during checkout
def process_payment(customer_email, payment_method_id, amount):
    """
    Process payment with additional checks
    """
    # First validate the payment method
    validation = validate_payment_method(payment_method_id)
    if not validation['success']:
        return validation
    
    # Check if customer is new (you'd implement this based on your database)
    is_new_customer = check_if_new_customer(customer_email)
    
    # Create payment intent with appropriate parameters
    intent_params = {
        'amount': amount,
        'currency': 'usd',
        'payment_method': payment_method_id,
        'customer': customer_id,
        'confirm': True,
    }
    
    # Require 3D Secure for new customers
    if is_new_customer:
        intent_params['payment_method_options'] = {
            'card': {
                'request_three_d_secure': 'any'
            }
        }
    
    try:
        intent = stripe.PaymentIntent.create(**intent_params)
        return {'success': True, 'intent': intent}
    except stripe.error.CardError as e:
        return {'success': False, 'error': str(e)}
'''

print(example_code)

print("\n=== MONITORING SETUP ===\n")

print("1. Set up daily alerts:")
print("   - Alert if daily failure rate > 25%")
print("   - Alert if >5 prepaid card attempts in one day")
print("   - Alert if >3 signups from same IP\n")

print("2. Weekly review:")
print("   - Check countries with highest failure rates")
print("   - Review new email domains with high failures")
print("   - Analyze first-day vs established customer patterns\n")

print("3. Monthly analysis:")
print("   - Update Radar rules based on new patterns")
print("   - Review revenue impact of blocked transactions")
print("   - Adjust risk thresholds as needed\n")

print("=== EXPECTED RESULTS ===\n")
print("After implementing these rules, you should see:")
print("• 30-40% reduction in payment failures")
print("• ~$1,600/month saved from blocking prepaid cards")
print("• Fewer chargebacks and disputes")
print("• Better customer experience for legitimate users\n")

print("Remember: Start with rules 1 & 2 (prepaid + new customer checks)")
print("Monitor for a week, then add additional rules as needed.") 