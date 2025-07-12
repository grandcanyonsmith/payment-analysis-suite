#!/usr/bin/env python3
"""
Analyze Stripe customer payment failures
"""

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('may_customers_stripe.csv')

# Convert date columns
df['Created (UTC)'] = pd.to_datetime(df['Created (UTC)'])
df['created_date'] = df['Created (UTC)'].dt.date

# Calculate customer age in days
current_date = datetime(2025, 5, 31)  # Based on the latest date in the data
df['customer_age_days'] = (current_date - df['Created (UTC)']).dt.days

# Define new customers (less than 7 days old)
df['is_new_customer'] = df['customer_age_days'] <= 7

# Analyze payment failures
print("=== PAYMENT FAILURE ANALYSIS ===\n")

# 1. Overall statistics
print("1. OVERALL STATISTICS:")
print(f"Total customers: {len(df)}")
print(f"New customers (≤7 days): {df['is_new_customer'].sum()}")
print(f"Established customers (>7 days): {(~df['is_new_customer']).sum()}")

# 2. Delinquent status analysis
print("\n2. DELINQUENT STATUS BY CUSTOMER AGE:")
delinquent_stats = df.groupby('is_new_customer')['Delinquent'].agg(
    ['sum', 'count', 'mean']
)
delinquent_stats['percentage'] = delinquent_stats['mean'] * 100
print(delinquent_stats)

# 3. Payment status analysis
print("\n3. PAYMENT STATUS DISTRIBUTION:")
status_counts = df['Status'].value_counts()
print(status_counts)

print("\n4. PAYMENT STATUS BY CUSTOMER AGE:")
status_by_age = pd.crosstab(
    df['is_new_customer'], df['Status'], normalize='index'
) * 100
print(status_by_age)

# 5. Card details analysis for failed payments
print("\n5. CARD ANALYSIS FOR DELINQUENT ACCOUNTS:")
delinquent_df = df[df['Delinquent']]
print(f"Total delinquent accounts: {len(delinquent_df)}")

# Analyze card types
print("\nCard brands for delinquent accounts:")
print(delinquent_df['Card Brand'].value_counts())

# Analyze card funding types
print("\nCard funding types for delinquent accounts:")
print(delinquent_df['Card Funding'].value_counts())

# Analyze AVS failures
print("\nCard AVS failures for delinquent accounts:")
print("Line1 Status:", delinquent_df['Card AVS Line1 Status'].value_counts())
print("\nZip Status:", delinquent_df['Card AVS Zip Status'].value_counts())

# 6. Risk factors analysis
print("\n6. RISK FACTORS ANALYSIS:")

# Check for prepaid cards
prepaid_delinquent_rate = (
    df[df['Card Funding'] == 'prepaid']['Delinquent'].mean() * 100
)
regular_delinquent_rate = (
    df[df['Card Funding'] != 'prepaid']['Delinquent'].mean() * 100
)
print(f"Delinquent rate for prepaid cards: {prepaid_delinquent_rate:.1f}%")
print(f"Delinquent rate for regular cards: {regular_delinquent_rate:.1f}%")

# Check international cards
df['is_international'] = ~df['Card Issue Country'].isin(['US', np.nan])
intl_delinquent_rate = (
    df[df['is_international']]['Delinquent'].mean() * 100
)
domestic_delinquent_rate = (
    df[~df['is_international']]['Delinquent'].mean() * 100
)
print(f"\nDelinquent rate for international cards: "
      f"{intl_delinquent_rate:.1f}%")
print(f"Delinquent rate for domestic cards: {domestic_delinquent_rate:.1f}%")

# 7. Time-based analysis
print("\n7. PAYMENT FAILURES BY SIGNUP DATE:")
daily_stats = df.groupby('created_date').agg({
    'Delinquent': ['sum', 'count', 'mean']
}).round(3)
daily_stats.columns = ['failures', 'total', 'failure_rate']
daily_stats['failure_percentage'] = daily_stats['failure_rate'] * 100
print(daily_stats.tail(10))

# 8. Card expiration analysis
print("\n8. CARD EXPIRATION ANALYSIS:")
df['card_exp_date'] = pd.to_datetime(
    df['Card Exp Year'].astype(str) + '-' + 
    df['Card Exp Month'].astype(str) + '-01', 
    errors='coerce'
)
df['months_until_expiry'] = (
    (df['card_exp_date'] - current_date).dt.days / 30
).round(0)
expired_or_soon = df[df['months_until_expiry'] <= 1]
print(f"Cards expired or expiring within 1 month: {len(expired_or_soon)}")
expiry_delinquent_rate = expired_or_soon['Delinquent'].mean() * 100
print(f"Delinquent rate for expired/expiring cards: {expiry_delinquent_rate:.1f}%")

# 9. Email domain analysis
print("\n9. EMAIL DOMAIN ANALYSIS FOR DELINQUENT ACCOUNTS:")
df['email_domain'] = df['Email'].str.split('@').str[1]
delinquent_domains = (
    df[df['Delinquent']]['email_domain'].value_counts().head(10)
)
print(delinquent_domains)

# 10. Summary and recommendations
print("\n=== SUMMARY AND KEY FINDINGS ===")
new_customer_delinquent_rate = (
    df[df['is_new_customer']]['Delinquent'].mean() * 100
)
old_customer_delinquent_rate = (
    df[~df['is_new_customer']]['Delinquent'].mean() * 100
)
print(f"New customer delinquent rate: {new_customer_delinquent_rate:.1f}%")
print(f"Established customer delinquent rate: {old_customer_delinquent_rate:.1f}%")
ratio = new_customer_delinquent_rate / old_customer_delinquent_rate
print(f"Ratio: {ratio:.1f}x higher for new customers")

# Create visualizations
plt.figure(figsize=(15, 10))

# Plot 1: Delinquent rate by customer age
plt.subplot(2, 3, 1)
age_groups = pd.cut(
    df['customer_age_days'], 
    bins=[0, 1, 3, 7, 14, 30, 365], 
    labels=['0-1d', '2-3d', '4-7d', '8-14d', '15-30d', '30+d']
)
delinquent_by_age = df.groupby(age_groups)['Delinquent'].mean() * 100
delinquent_by_age.plot(kind='bar')
plt.title('Delinquent Rate by Customer Age')
plt.ylabel('Delinquent Rate (%)')
plt.xticks(rotation=45)

# Plot 2: Payment status distribution
plt.subplot(2, 3, 2)
status_counts.plot(kind='bar')
plt.title('Payment Status Distribution')
plt.ylabel('Count')
plt.xticks(rotation=45)

# Plot 3: Card funding types for delinquent accounts
plt.subplot(2, 3, 3)
delinquent_df['Card Funding'].value_counts().plot(kind='bar')
plt.title('Card Funding Types (Delinquent Accounts)')
plt.ylabel('Count')
plt.xticks(rotation=45)

# Plot 4: Daily signup and failure trends
plt.subplot(2, 3, 4)
daily_signups = df.groupby('created_date').size()
daily_failures = df.groupby('created_date')['Delinquent'].sum()
plt.plot(daily_signups.index, daily_signups.values, label='Signups', alpha=0.7)
plt.plot(daily_failures.index, daily_failures.values, label='Failures', alpha=0.7)
plt.title('Daily Signups vs Failures')
plt.xlabel('Date')
plt.ylabel('Count')
plt.legend()
plt.xticks(rotation=45)

# Plot 5: Card brands for delinquent accounts
plt.subplot(2, 3, 5)
delinquent_df['Card Brand'].value_counts().plot(kind='pie', autopct='%1.1f%%')
plt.title('Card Brands (Delinquent Accounts)')

# Plot 6: AVS failure analysis
plt.subplot(2, 3, 6)
avs_failures = delinquent_df['Card AVS Zip Status'].value_counts()
avs_failures.plot(kind='bar')
plt.title('AVS Zip Status (Delinquent Accounts)')
plt.ylabel('Count')
plt.xticks(rotation=45)

plt.tight_layout()
plt.savefig('payment_failure_analysis.png', dpi=300)
print("\n\nVisualizations saved to 'payment_failure_analysis.png'")

# Export detailed analysis
analysis_df = df[[
    'Email', 'Name', 'Created (UTC)', 'customer_age_days', 'is_new_customer', 
    'Delinquent', 'Status', 'Card Brand', 'Card Funding', 'Card Issue Country',
    'Card AVS Zip Status', 'Card Exp Month', 'Card Exp Year', 'months_until_expiry'
]]
analysis_df.to_csv('payment_failure_detailed_analysis.csv', index=False)
print("Detailed analysis exported to 'payment_failure_detailed_analysis.csv'") 