import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Load the data
df = pd.read_csv('may_customers_stripe.csv')

# Parse the created date
df['created_date'] = pd.to_datetime(df['Created (UTC)'])

# Delinquent column is already boolean, just rename for consistency
df['delinquent'] = df['Delinquent']

# Identify trial-related patterns
# A customer likely had a trial if:
# 1. Their status is/was "trialing"
# 2. They have a plan but $0 total spend (recently started)
# 3. They're active/past_due with low spend relative to time since creation

# Create trial identification logic
df['has_plan'] = df['Plan'].notna() & (df['Plan'] != '')
df['is_trialing'] = df['Status'] == 'trialing'
df['days_since_creation'] = (datetime(2025, 5, 31) - df['created_date']).dt.days

# Estimate if customer had a trial based on patterns
# If they have a plan and very low or no spend relative to their age, they likely had/have a trial
df['likely_trial'] = False

# Mark explicit trial customers
df.loc[df['is_trialing'], 'likely_trial'] = True

# Mark customers who have a plan but no spend (likely in trial or just converted)
df.loc[(df['has_plan']) & (df['Total Spend'] == 0), 'likely_trial'] = True

# Mark customers who have spent less than expected based on their age
# Assuming monthly subscriptions, if they've spent significantly less than months * typical price
# Calculate expected spend based on plan patterns
price_patterns = {
    'price_1Ozb24BnnqL8bKFQEbEdsZqn': 147,  # Most common price
    'price_1Ozb3ABnnqL8bKFQZ1sv1Ryx': 297,  # Second tier
    'price_1O7NIrBnnqL8bKFQHaxqk7B4': 97   # Lower tier
}

# Add expected monthly price
df['expected_monthly'] = df['Plan'].map(price_patterns).fillna(147)  # Default to most common

# Calculate if spending is suspiciously low (indicating recent conversion from trial)
df['months_active'] = df['days_since_creation'] / 30
df['expected_total'] = df['months_active'] * df['expected_monthly']
df['spend_ratio'] = df['Total Spend'] / df['expected_total'].replace(0, 1)

# If they've spent less than 50% of expected, they likely had a trial
df.loc[(df['has_plan']) & (df['spend_ratio'] < 0.5) & (df['days_since_creation'] > 7), 'likely_trial'] = True

# Categorize customers
df['customer_type'] = 'No Subscription'
df.loc[df['is_trialing'], 'customer_type'] = 'Currently Trialing'
df.loc[(df['likely_trial']) & (df['Status'].isin(['active', 'past_due'])) & (df['Total Spend'] > 0), 'customer_type'] = 'Trial Converted'
df.loc[(df['likely_trial']) & (df['Status'].isin(['active', 'past_due'])) & (df['Total Spend'] == 0), 'customer_type'] = 'Trial - Not Yet Charged'
df.loc[(df['has_plan']) & (~df['likely_trial']) & (df['Status'].isin(['active', 'past_due'])), 'customer_type'] = 'Direct Paid'
df.loc[df['Status'] == 'canceled', 'customer_type'] = 'Canceled'

print("=== MAY 2025 TRIAL TO PAID CONVERSION ANALYSIS ===\n")

# Overall summary
print("CUSTOMER BREAKDOWN:")
customer_summary = df['customer_type'].value_counts()
for ctype, count in customer_summary.items():
    pct = (count / len(df)) * 100
    print(f"{ctype}: {count} ({pct:.1f}%)")

print(f"\nTotal Customers: {len(df)}")

# Focus on trial conversions
trial_customers = df[df['likely_trial']]
print(f"\n\nTRIAL ANALYSIS:")
print(f"Total customers who had/have trials: {len(trial_customers)} ({len(trial_customers)/len(df)*100:.1f}%)")

# Conversion analysis
converted = trial_customers[trial_customers['customer_type'] == 'Trial Converted']
still_trial = trial_customers[trial_customers['customer_type'].isin(['Currently Trialing', 'Trial - Not Yet Charged'])]

print(f"\nTrial Status:")
print(f"- Converted to paid: {len(converted)} ({len(converted)/len(trial_customers)*100:.1f}% of trials)")
print(f"- Still in trial/pending: {len(still_trial)} ({len(still_trial)/len(trial_customers)*100:.1f}% of trials)")

# Delinquency analysis for converted trials
print(f"\n\nDELINQUENCY ANALYSIS:")

# Overall delinquency
delinquent_all = df[df['delinquent'] == True]
print(f"\nOverall delinquency rate: {len(delinquent_all)}/{len(df)} ({len(delinquent_all)/len(df)*100:.1f}%)")

# Delinquency by customer type
print("\nDelinquency by Customer Type:")
for ctype in ['Direct Paid', 'Trial Converted', 'Trial - Not Yet Charged', 'Currently Trialing']:
    type_customers = df[df['customer_type'] == ctype]
    if len(type_customers) > 0:
        delinquent = type_customers[type_customers['delinquent'] == True]
        rate = len(delinquent) / len(type_customers) * 100
        print(f"- {ctype}: {len(delinquent)}/{len(type_customers)} ({rate:.1f}%)")

# Time-based analysis for trial conversions
print("\n\nTIME-BASED ANALYSIS (Trial Conversions):")
if len(converted) > 0:
    # Group by days since creation
    converted['days_group'] = pd.cut(converted['days_since_creation'], 
                                    bins=[0, 7, 14, 21, 31], 
                                    labels=['0-7 days', '8-14 days', '15-21 days', '22-31 days'])
    
    print("\nDelinquency by Time Since Trial Start:")
    for group in ['0-7 days', '8-14 days', '15-21 days', '22-31 days']:
        group_data = converted[converted['days_group'] == group]
        if len(group_data) > 0:
            delinquent = group_data[group_data['delinquent'] == True]
            rate = len(delinquent) / len(group_data) * 100 if len(group_data) > 0 else 0
            print(f"- {group}: {len(delinquent)}/{len(group_data)} ({rate:.1f}%)")

# Payment failure reasons for trial conversions
print("\n\nPAYMENT DETAILS (Trial Conversions with Issues):")
trial_delinquent = converted[converted['delinquent'] == True]
if len(trial_delinquent) > 0:
    # Check card details
    print(f"\nTotal delinquent trial conversions: {len(trial_delinquent)}")
    
    # Card funding types
    funding_counts = trial_delinquent['Card Funding'].value_counts()
    print("\nCard Types for Failed Trial Conversions:")
    for funding, count in funding_counts.items():
        if pd.notna(funding):
            print(f"- {funding}: {count}")
    
    # Check for patterns in failed payments
    prepaid_fails = trial_delinquent[trial_delinquent['Card Funding'] == 'prepaid']
    print(f"\nPrepaid cards in failed conversions: {len(prepaid_fails)} ({len(prepaid_fails)/len(trial_delinquent)*100:.1f}%)")

# Revenue impact
print("\n\nREVENUE IMPACT:")
successful_conversions = converted[converted['delinquent'] == False]
failed_conversions = converted[converted['delinquent'] == True]

successful_revenue = successful_conversions['expected_monthly'].sum()
failed_revenue = failed_conversions['expected_monthly'].sum()

print(f"Successful trial conversions: {len(successful_conversions)} (${successful_revenue:,.2f}/month)")
print(f"Failed trial conversions: {len(failed_conversions)} (${failed_revenue:,.2f}/month lost)")
if len(successful_conversions) + len(failed_conversions) > 0:
    success_rate = len(successful_conversions)/(len(successful_conversions)+len(failed_conversions))*100
    print(f"Trial conversion success rate: {success_rate:.1f}%")
else:
    print("Trial conversion success rate: N/A (no conversions yet)")

# Key insights
print("\n\n=== KEY INSIGHTS ===")
print("\n1. TRIAL CONVERSION METRICS:")
if len(trial_customers) > 0:
    conversion_rate = len(converted) / len(trial_customers) * 100
    print(f"   - {conversion_rate:.1f}% of trials convert to paid")
    
    if len(converted) > 0:
        fail_rate = len(trial_delinquent) / len(converted) * 100
        print(f"   - {fail_rate:.1f}% of converted trials become delinquent")

print("\n2. COMPARISON TO DIRECT SUBSCRIPTIONS:")
direct_paid = df[df['customer_type'] == 'Direct Paid']
if len(direct_paid) > 0:
    direct_delinquent = direct_paid[direct_paid['delinquent'] == True]
    direct_fail_rate = len(direct_delinquent) / len(direct_paid) * 100
    print(f"   - Direct paid delinquency: {direct_fail_rate:.1f}%")
    
    if len(converted) > 0:
        trial_fail_rate = len(trial_delinquent) / len(converted) * 100
        print(f"   - Trial conversion delinquency: {trial_fail_rate:.1f}%")
        
        if trial_fail_rate > direct_fail_rate:
            print(f"   - Trial conversions fail {trial_fail_rate/direct_fail_rate:.1f}x more often than direct subscriptions")

# Save detailed data for further analysis
trial_analysis = df[df['likely_trial']].copy()
trial_analysis['delinquent_status'] = trial_analysis['delinquent'].map({True: 'Delinquent', False: 'Good Standing'})
trial_analysis[['Email', 'Name', 'created_date', 'customer_type', 'Status', 'delinquent_status', 
                'Total Spend', 'Card Funding', 'days_since_creation']].to_csv('trial_conversion_details.csv', index=False)

print("\n\nDetailed trial customer data saved to 'trial_conversion_details.csv'") 