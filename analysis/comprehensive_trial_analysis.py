import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load the data
df = pd.read_csv('may_customers_stripe.csv')

# Parse date and create derived fields
df['created_date'] = pd.to_datetime(df['Created (UTC)'])
df['has_plan'] = df['Plan'].notna() & (df['Plan'] != '')
df['days_since_creation'] = (datetime(2025, 5, 31) - df['created_date']).dt.days

print("=== COMPREHENSIVE MAY 2025 SUBSCRIPTION ANALYSIS ===\n")

# First, let's understand the data better
print("1. OVERALL CUSTOMER BREAKDOWN:")
print(f"Total customers: {len(df)}")
print(f"Customers with plans: {df['has_plan'].sum()} ({df['has_plan'].sum()/len(df)*100:.1f}%)")
print(f"Delinquent customers: {df['Delinquent'].sum()} ({df['Delinquent'].sum()/len(df)*100:.1f}%)")

# Status breakdown
print("\n2. STATUS BREAKDOWN:")
status_counts = df['Status'].value_counts(dropna=False)
for status, count in status_counts.items():
    pct = count/len(df)*100
    delinquent_count = df[df['Status'] == status]['Delinquent'].sum()
    delinquent_pct = delinquent_count/count*100 if count > 0 else 0
    print(f"  {status}: {count} ({pct:.1f}%) - {delinquent_count} delinquent ({delinquent_pct:.1f}%)")

# Let's analyze by subscription patterns
print("\n3. SUBSCRIPTION PATTERNS:")

# Group customers by their characteristics
df['customer_category'] = 'No Plan'

# Active/past_due with plan = paid subscriber
df.loc[(df['has_plan']) & (df['Status'].isin(['active', 'past_due'])), 'customer_category'] = 'Paid Subscriber'

# Trialing status = in trial
df.loc[df['Status'] == 'trialing', 'customer_category'] = 'In Trial'

# Has plan but no status or canceled = canceled
df.loc[(df['has_plan']) & ((df['Status'].isna()) | (df['Status'] == 'canceled')), 'customer_category'] = 'Canceled/Inactive'

category_summary = df.groupby('customer_category').agg({
    'id': 'count',
    'Delinquent': 'sum',
    'Total Spend': ['sum', 'mean']
}).round(2)
category_summary.columns = ['Count', 'Delinquent', 'Total Revenue', 'Avg Revenue']
print(category_summary)

# Trial analysis - focus on new customers who might be converting from trial
print("\n4. NEW CUSTOMER ANALYSIS (Signed up in May):")

# Analyze by days since creation
df['age_group'] = pd.cut(df['days_since_creation'], 
                        bins=[-1, 0, 3, 7, 14, 31],
                        labels=['Day 0', 'Days 1-3', 'Days 4-7', 'Days 8-14', 'Days 15-31'])

# Focus on paid subscribers
paid_subs = df[df['customer_category'] == 'Paid Subscriber']
print(f"\nTotal paid subscribers: {len(paid_subs)}")

# Analyze delinquency by age for paid subscribers
print("\nDelinquency by Customer Age (Paid Subscribers):")
for age in ['Day 0', 'Days 1-3', 'Days 4-7', 'Days 8-14', 'Days 15-31']:
    age_group = paid_subs[paid_subs['age_group'] == age]
    if len(age_group) > 0:
        delinquent = age_group['Delinquent'].sum()
        rate = delinquent/len(age_group)*100
        avg_spend = age_group['Total Spend'].mean()
        print(f"  {age}: {len(age_group)} customers, {delinquent} delinquent ({rate:.1f}%), "
              f"avg spend: ${avg_spend:.2f}")

# Look at spending patterns to identify likely trial conversions
print("\n5. LIKELY TRIAL CONVERSIONS (Low/No spend relative to age):")

# For paid subscribers, calculate expected vs actual spend
price_map = {
    'price_1Ozb24BnnqL8bKFQEbEdsZqn': 147,
    'price_1Ozb3ABnnqL8bKFQZ1sv1Ryx': 297,
    'price_1O7NIrBnnqL8bKFQHaxqk7B4': 97
}

paid_subs['expected_monthly'] = paid_subs['Plan'].map(price_map).fillna(147)
paid_subs['expected_total'] = (paid_subs['days_since_creation'] / 30) * paid_subs['expected_monthly']
paid_subs['spend_ratio'] = paid_subs['Total Spend'] / paid_subs['expected_total'].replace(0, 1)

# Customers with < 50% of expected spend likely had trials
likely_trial_conversions = paid_subs[
    (paid_subs['spend_ratio'] < 0.5) & 
    (paid_subs['days_since_creation'] > 7)
]

print(f"Likely trial conversions: {len(likely_trial_conversions)} customers")
print(f"Delinquent among likely conversions: {likely_trial_conversions['Delinquent'].sum()} "
      f"({likely_trial_conversions['Delinquent'].sum()/len(likely_trial_conversions)*100:.1f}%)" 
      if len(likely_trial_conversions) > 0 else "N/A")

# Direct subscriptions (full spend from start)
direct_subs = paid_subs[
    (paid_subs['spend_ratio'] >= 0.8) & 
    (paid_subs['days_since_creation'] > 7)
]

print(f"\nDirect subscriptions: {len(direct_subs)} customers")
print(f"Delinquent among direct: {direct_subs['Delinquent'].sum()} "
      f"({direct_subs['Delinquent'].sum()/len(direct_subs)*100:.1f}%)"
      if len(direct_subs) > 0 else "N/A")

# Card funding analysis for delinquent customers
print("\n6. PAYMENT METHOD ANALYSIS (Delinquent Customers):")
delinquent_customers = df[df['Delinquent'] == True]
funding_breakdown = delinquent_customers['Card Funding'].value_counts(dropna=False)
print("\nCard types for delinquent customers:")
for funding, count in funding_breakdown.items():
    pct = count/len(delinquent_customers)*100
    print(f"  {funding}: {count} ({pct:.1f}%)")

# Revenue impact
print("\n7. REVENUE IMPACT:")
total_delinquent = df[df['Delinquent'] == True]
delinquent_with_plans = total_delinquent[total_delinquent['has_plan']]

# Calculate monthly revenue loss
revenue_loss = 0
for idx, customer in delinquent_with_plans.iterrows():
    if customer['Plan'] in price_map:
        revenue_loss += price_map[customer['Plan']]
    else:
        revenue_loss += 147  # Default price

print(f"Total delinquent customers with plans: {len(delinquent_with_plans)}")
print(f"Monthly revenue at risk: ${revenue_loss:,.2f}")

# Key findings summary
print("\n\n=== KEY FINDINGS ===")
print("\n1. OVERALL METRICS:")
print(f"   - {len(df)} total customers in May")
print(f"   - {df['has_plan'].sum()} have subscription plans ({df['has_plan'].sum()/len(df)*100:.1f}%)")
print(f"   - {df['Delinquent'].sum()} are delinquent ({df['Delinquent'].sum()/len(df)*100:.1f}%)")

print("\n2. TRIAL VS DIRECT COMPARISON:")
if len(likely_trial_conversions) > 0 and len(direct_subs) > 0:
    trial_del_rate = likely_trial_conversions['Delinquent'].sum()/len(likely_trial_conversions)*100
    direct_del_rate = direct_subs['Delinquent'].sum()/len(direct_subs)*100
    print(f"   - Trial conversion delinquency: {trial_del_rate:.1f}%")
    print(f"   - Direct subscription delinquency: {direct_del_rate:.1f}%")
    if trial_del_rate > 0:
        print(f"   - Trial conversions are {trial_del_rate/direct_del_rate:.1f}x more likely to fail")

print("\n3. HIGH-RISK SEGMENTS:")
# Prepaid cards
prepaid_customers = df[df['Card Funding'] == 'prepaid']
if len(prepaid_customers) > 0:
    prepaid_del_rate = prepaid_customers['Delinquent'].sum()/len(prepaid_customers)*100
    print(f"   - Prepaid card delinquency: {prepaid_del_rate:.1f}%")

# New customers
new_customers = df[df['days_since_creation'] <= 3]
if len(new_customers) > 0:
    new_del_rate = new_customers['Delinquent'].sum()/len(new_customers)*100
    print(f"   - First 3 days delinquency: {new_del_rate:.1f}%")

# Save detailed analysis
analysis_df = paid_subs[['Email', 'Name', 'created_date', 'Status', 'Delinquent', 
                        'Total Spend', 'expected_total', 'spend_ratio', 'Card Funding',
                        'days_since_creation', 'age_group']].copy()
analysis_df.to_csv('detailed_subscription_analysis.csv', index=False)
print("\nDetailed analysis saved to 'detailed_subscription_analysis.csv'") 