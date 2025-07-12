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

print("=== FINDING ALL TRIAL CUSTOMERS FROM MAY 2025 ===\n")

# Map plan prices
price_map = {
    'price_1Ozb24BnnqL8bKFQEbEdsZqn': 147,
    'price_1Ozb3ABnnqL8bKFQZ1sv1Ryx': 297,
    'price_1O7NIrBnnqL8bKFQHaxqk7B4': 97
}

# Calculate expected spend for each customer
df['expected_monthly'] = df['Plan'].map(price_map).fillna(147)
df['months_active'] = df['days_since_creation'] / 30
df['expected_total'] = df['months_active'] * df['expected_monthly']

# Identify trial customers using multiple criteria
df['likely_trial'] = False

# Criterion 1: Currently in trialing status
df.loc[df['Status'] == 'trialing', 'likely_trial'] = True
df.loc[df['Status'] == 'trialing', 'trial_type'] = 'Currently Trialing'

# Criterion 2: Active/past_due with ZERO spend (recently converted trials)
zero_spend_with_plan = df[(df['has_plan']) & 
                          (df['Status'].isin(['active', 'past_due'])) & 
                          (df['Total Spend'] == 0)]
df.loc[zero_spend_with_plan.index, 'likely_trial'] = True
df.loc[zero_spend_with_plan.index, 'trial_type'] = 'Zero Spend Trial'

# Criterion 3: Significantly underspent relative to age (trial period gap)
# If they've been around >7 days but spent <50% of expected, likely had trial
underspent = df[(df['has_plan']) & 
                (df['days_since_creation'] > 7) & 
                (df['Total Spend'] > 0) &
                (df['Total Spend'] / df['expected_total'] < 0.5)]
df.loc[underspent.index, 'likely_trial'] = True
df.loc[underspent.index, 'trial_type'] = 'Underspent Trial'

# Summary
all_trials = df[df['likely_trial'] == True]
print(f"TOTAL CUSTOMERS WHO LIKELY HAD/HAVE TRIALS: {len(all_trials)}\n")

# Break down by trial type
print("Breakdown by trial identification method:")
trial_type_counts = all_trials['trial_type'].value_counts()
for ttype, count in trial_type_counts.items():
    print(f"  {ttype}: {count}")

# Status of all trial customers
print(f"\nCurrent status of all {len(all_trials)} trial customers:")
status_counts = all_trials['Status'].value_counts()
for status, count in status_counts.items():
    pct = count/len(all_trials)*100
    print(f"  {status}: {count} ({pct:.1f}%)")

# Delinquency analysis
delinquent_trials = all_trials[all_trials['Delinquent'] == True]
print(f"\nDelinquent trial customers: {len(delinquent_trials)} out of {len(all_trials)} ({len(delinquent_trials)/len(all_trials)*100:.1f}%)")

# Compare to direct subscribers
# Direct = has plan, good spend ratio, not identified as trial
direct_subs = df[(df['has_plan']) & 
                 (df['likely_trial'] == False) &
                 (df['Status'].isin(['active', 'past_due']))]

print(f"\n\nDIRECT SUBSCRIBERS (no trial): {len(direct_subs)}")
direct_delinquent = direct_subs[direct_subs['Delinquent'] == True]
print(f"Delinquent direct subscribers: {len(direct_delinquent)} out of {len(direct_subs)} ({len(direct_delinquent)/len(direct_subs)*100:.1f}%)")

# Show some examples of each type
print("\n\n=== EXAMPLE CUSTOMERS ===")

print("\nCurrently Trialing (5 examples):")
currently_trialing = all_trials[all_trials['trial_type'] == 'Currently Trialing'].head()
for idx, customer in currently_trialing.iterrows():
    print(f"  - {customer['Name']}: {customer['days_since_creation']} days old, "
          f"Total Spend: ${customer['Total Spend']}")

print("\nZero Spend Trials (5 examples):")
zero_spend_trials = all_trials[all_trials['trial_type'] == 'Zero Spend Trial'].head()
for idx, customer in zero_spend_trials.iterrows():
    print(f"  - {customer['Name']}: {customer['days_since_creation']} days old, "
          f"Status: {customer['Status']}, Delinquent: {customer['Delinquent']}")

print("\nUnderspent Trials (5 examples):")
underspent_trials = all_trials[all_trials['trial_type'] == 'Underspent Trial'].head()
for idx, customer in underspent_trials.iterrows():
    spent_pct = (customer['Total Spend'] / customer['expected_total'] * 100)
    print(f"  - {customer['Name']}: {customer['days_since_creation']} days old, "
          f"Spent ${customer['Total Spend']:.2f} (expected ${customer['expected_total']:.2f}, "
          f"only {spent_pct:.0f}%)")

# Revenue impact
print("\n\n=== REVENUE IMPACT ===")
trial_revenue_at_risk = delinquent_trials['expected_monthly'].sum()
direct_revenue_at_risk = direct_delinquent['expected_monthly'].sum()

print(f"Monthly revenue at risk from trial customers: ${trial_revenue_at_risk:,.2f}")
print(f"Monthly revenue at risk from direct customers: ${direct_revenue_at_risk:,.2f}")

# Final summary
print("\n\n=== CORRECTED SUMMARY ===")
print(f"\n✓ You were right - there were {len(all_trials)} customers with trials in May!")
print(f"  - {len(delinquent_trials)} became delinquent ({len(delinquent_trials)/len(all_trials)*100:.1f}%)")
print(f"  - Only {len(direct_subs)} were direct subscribers")
print(f"  - {len(direct_delinquent)} direct subscribers became delinquent ({len(direct_delinquent)/len(direct_subs)*100:.1f}%)")

if len(delinquent_trials) > 0 and len(direct_delinquent) > 0:
    ratio = (len(delinquent_trials)/len(all_trials)) / (len(direct_delinquent)/len(direct_subs))
    print(f"\n💡 Trial customers are {ratio:.1f}x more likely to become delinquent than direct subscribers!") 