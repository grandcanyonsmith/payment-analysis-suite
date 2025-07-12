import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Load the data
df = pd.read_csv('may_customers_stripe.csv')

# Parse date and add calculated fields
df['created_date'] = pd.to_datetime(df['Created (UTC)'])
df['days_since_creation'] = (datetime(2025, 5, 31) - df['created_date']).dt.days
df['has_plan'] = df['Plan'].notna() & (df['Plan'] != '')

print("=== UNDERSTANDING DAY 0 FAILURES ===\n")

# First, let's look at customers created on May 31 (Day 0)
day0_customers = df[df['days_since_creation'] == 0]
print(f"Total customers created on May 31 (Day 0): {len(day0_customers)}")

# Break down by status
print("\nDay 0 customers by status:")
status_breakdown = day0_customers['Status'].value_counts(dropna=False)
for status, count in status_breakdown.items():
    delinquent = day0_customers[day0_customers['Status'] == status]['Delinquent'].sum()
    print(f"  {status}: {count} customers, {delinquent} delinquent")

# Look specifically at delinquent Day 0 customers
day0_delinquent = day0_customers[day0_customers['Delinquent'] == True]
print(f"\nDay 0 delinquent customers: {len(day0_delinquent)}")

if len(day0_delinquent) > 0:
    print("\nDetails of Day 0 delinquent customers:")
    for idx, customer in day0_delinquent.iterrows():
        print(f"\n  Customer: {customer['Name']} ({customer['Email']})")
        print(f"  Status: {customer['Status']}")
        print(f"  Plan: {customer['Plan']}")
        print(f"  Total Spend: ${customer['Total Spend']}")
        print(f"  Card Funding: {customer['Card Funding']}")
        print(f"  Payment Count: {customer['Payment Count']}")

# Now let's understand the customer journey better
print("\n\n=== CUSTOMER JOURNEY ANALYSIS ===")

# Look at customers with 'trialing' status
trialing = df[df['Status'] == 'trialing']
print(f"\nCustomers currently in trial: {len(trialing)}")
print("Age of trialing customers:")
for idx, customer in trialing.iterrows():
    days_old = customer['days_since_creation']
    print(f"  - {customer['Name']}: {days_old} days old, Total Spend: ${customer['Total Spend']}")

# Look at past_due customers to understand when they failed
past_due = df[df['Status'] == 'past_due']
print(f"\n\nPast due customers: {len(past_due)}")

# Analyze past_due by age and spending
print("\nPast due customers by age group:")
age_groups = [(0, 0, 'Day 0'), (1, 3, 'Days 1-3'), (4, 7, 'Days 4-7'), 
              (8, 14, 'Days 8-14'), (15, 31, 'Days 15-31')]

for min_days, max_days, label in age_groups:
    group = past_due[(past_due['days_since_creation'] >= min_days) & 
                     (past_due['days_since_creation'] <= max_days)]
    if len(group) > 0:
        avg_spend = group['Total Spend'].mean()
        zero_spend = len(group[group['Total Spend'] == 0])
        print(f"\n  {label}: {len(group)} customers")
        print(f"    - Average spend: ${avg_spend:.2f}")
        print(f"    - Zero spend: {zero_spend} customers")
        print(f"    - Card types: {group['Card Funding'].value_counts().to_dict()}")

# Let's identify different customer types more clearly
print("\n\n=== CUSTOMER TYPE IDENTIFICATION ===")

# Type 1: Direct subscribers who failed immediately
direct_immediate_fail = df[(df['has_plan']) & 
                           (df['Status'] == 'past_due') & 
                           (df['Total Spend'] == 0) & 
                           (df['days_since_creation'] <= 3)]

print(f"\n1. Direct subscribers who failed immediately: {len(direct_immediate_fail)}")
if len(direct_immediate_fail) > 0:
    print("   Examples:")
    for idx, customer in direct_immediate_fail.head(3).iterrows():
        print(f"   - {customer['Name']}: Day {customer['days_since_creation']}, "
              f"Card: {customer['Card Funding']}")

# Type 2: Trial conversions (have plan, low spend relative to age)
potential_trial_conversions = df[(df['has_plan']) & 
                                 (df['Status'].isin(['active', 'past_due'])) &
                                 (df['days_since_creation'] > 14) &
                                 (df['Total Spend'] < 100)]

print(f"\n2. Likely trial conversions (>14 days old, <$100 spend): {len(potential_trial_conversions)}")
trial_conv_delinquent = potential_trial_conversions[potential_trial_conversions['Delinquent'] == True]
print(f"   - Delinquent: {len(trial_conv_delinquent)} ({len(trial_conv_delinquent)/len(potential_trial_conversions)*100:.1f}%)")

# Type 3: Currently trialing
print(f"\n3. Currently trialing: {len(trialing)}")

# Type 4: Direct subscribers (immediate payment)
direct_success = df[(df['has_plan']) & 
                    (df['Status'] == 'active') & 
                    (df['Total Spend'] > 50) &
                    (df['days_since_creation'] <= 7)]

print(f"\n4. Direct subscribers who paid immediately: {len(direct_success)}")

# Summary insights
print("\n\n=== KEY INSIGHTS ===")
print("\n1. Day 0 failures are NOT trial customers - they're direct signups where the card failed immediately")
print("2. Trial customers show up as 'trialing' status initially, not 'past_due'")
print("3. Trial conversions typically fail AFTER the trial period (14-30 days)")
print("\n4. Customer types breakdown:")
print(f"   - Direct signup, immediate failure: {len(direct_immediate_fail)}")
print(f"   - Trial conversion failures: ~{len(trial_conv_delinquent)}")
print(f"   - Currently in trial: {len(trialing)}")
print(f"   - Successful direct signups: {len(direct_success)}") 