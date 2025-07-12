import stripe
from datetime import datetime, timezone
import pandas as pd

# Set Stripe API key
stripe.api_key = ("rk_live_51LNznbBnnqL8bKFQck4mN1IIAI7ddjnzvNxrPulfYRwv"
                  "Qd1eoZ68vD8wfCgoPAbawp6W8jfe9Dn7ysjZGNNSs1ZN00wRpzx7em")

# Define June 2025 date range
june_start = datetime(2025, 6, 1, tzinfo=timezone.utc)
june_end = datetime(2025, 7, 1, tzinfo=timezone.utc)

print("Investigating Trial Periods for June 2025 Customers...")
print("=" * 80)

# Store all trial customer data
trial_customers = []

# Fetch all customers created in June
has_more = True
starting_after = None
total_customers = 0
trial_count = 0

while has_more:
    params = {
        'created': {
            'gte': int(june_start.timestamp()),
            'lt': int(june_end.timestamp())
        },
        'limit': 100,
        'expand': ['data.subscriptions']
    }
    
    if starting_after:
        params['starting_after'] = starting_after
    
    customers = stripe.Customer.list(**params)
    
    for customer in customers.data:
        if not customer.email:
            continue
            
        total_customers += 1
        
        # Check subscriptions for trial info
        if hasattr(customer, 'subscriptions') and customer.subscriptions.data:
            for sub in customer.subscriptions.data:
                if sub.trial_start or sub.trial_end:
                    trial_count += 1
                    
                    # Calculate trial period length
                    trial_start_date = datetime.fromtimestamp(sub.trial_start) if sub.trial_start else None
                    trial_end_date = datetime.fromtimestamp(sub.trial_end) if sub.trial_end else None
                    
                    if trial_start_date and trial_end_date:
                        trial_days = (trial_end_date - trial_start_date).days
                    else:
                        trial_days = None
                    
                    # Get subscription creation vs customer creation
                    customer_created = datetime.fromtimestamp(customer.created)
                    sub_created = datetime.fromtimestamp(sub.created)
                    
                    # Store detailed info
                    trial_customers.append({
                        'customer_id': customer.id,
                        'email': customer.email,
                        'customer_created': customer_created.strftime('%Y-%m-%d %H:%M'),
                        'sub_id': sub.id,
                        'sub_status': sub.status,
                        'sub_created': sub_created.strftime('%Y-%m-%d %H:%M'),
                        'trial_start': trial_start_date.strftime('%Y-%m-%d') if trial_start_date else 'None',
                        'trial_end': trial_end_date.strftime('%Y-%m-%d') if trial_end_date else 'None',
                        'trial_days': trial_days,
                        'current_period_start': datetime.fromtimestamp(sub.current_period_start).strftime('%Y-%m-%d'),
                        'current_period_end': datetime.fromtimestamp(sub.current_period_end).strftime('%Y-%m-%d'),
                        'delinquent': customer.delinquent
                    })
    
    has_more = customers.has_more
    if has_more:
        starting_after = customers.data[-1].id

# Analyze trial periods
print(f"\nTotal June customers analyzed: {total_customers}")
print(f"Customers with trials: {len(trial_customers)}")

if trial_customers:
    df = pd.DataFrame(trial_customers)
    
    # Group by trial length
    trial_length_counts = df['trial_days'].value_counts().sort_index()
    
    print("\n" + "="*50)
    print("TRIAL PERIOD ANALYSIS:")
    print("="*50)
    
    for days, count in trial_length_counts.items():
        if days is not None:
            print(f"{days} days: {count} customers ({count/len(trial_customers)*100:.1f}%)")
    
    # Show examples of different trial lengths
    print("\n" + "="*50)
    print("SAMPLE CUSTOMERS BY TRIAL LENGTH:")
    print("="*50)
    
    unique_lengths = sorted(df['trial_days'].dropna().unique())
    for length in unique_lengths[:5]:  # Show first 5 different lengths
        print(f"\n{length}-day trials:")
        samples = df[df['trial_days'] == length].head(3)
        for _, customer in samples.iterrows():
            print(f"  {customer['email']}")
            print(f"    Trial: {customer['trial_start']} to {customer['trial_end']}")
            print(f"    Status: {customer['sub_status']}, Delinquent: {customer['delinquent']}")
    
    # Check for anomalies
    print("\n" + "="*50)
    print("ANOMALY CHECK:")
    print("="*50)
    
    # Trials longer than 30 days
    long_trials = df[df['trial_days'] > 30]
    if not long_trials.empty:
        print(f"\nTrials LONGER than 30 days: {len(long_trials)} customers")
        print("Examples:")
        for _, customer in long_trials.head(5).iterrows():
            print(f"  {customer['email']} - {customer['trial_days']} days")
            print(f"    Created: {customer['customer_created']}")
            print(f"    Trial: {customer['trial_start']} to {customer['trial_end']}")
    
    # Check current period vs trial period
    print("\n" + "="*50)
    print("BILLING PERIOD ANALYSIS (for delinquent customers):")
    print("="*50)
    
    delinquent_df = df[df['delinquent'] == True]
    if not delinquent_df.empty:
        for _, customer in delinquent_df.head(5).iterrows():
            print(f"\n{customer['email']}:")
            print(f"  Trial period: {customer['trial_start']} to {customer['trial_end']} ({customer['trial_days']} days)")
            print(f"  Current billing period: {customer['current_period_start']} to {customer['current_period_end']}")
            
            # Calculate days from trial end to current period end
            if customer['trial_end'] != 'None':
                trial_end = datetime.strptime(customer['trial_end'], '%Y-%m-%d')
                current_end = datetime.strptime(customer['current_period_end'], '%Y-%m-%d')
                days_diff = (current_end - trial_end).days
                print(f"  Days from trial end to billing end: {days_diff}")
    
    # Save detailed data
    df.to_csv('june_trial_period_analysis.csv', index=False)
    print(f"\nDetailed data saved to june_trial_period_analysis.csv")
    
    # Summary statistics
    print("\n" + "="*50)
    print("SUMMARY STATISTICS:")
    print("="*50)
    print(f"Average trial length: {df['trial_days'].mean():.1f} days")
    print(f"Median trial length: {df['trial_days'].median():.1f} days")
    print(f"Min trial length: {df['trial_days'].min()} days")
    print(f"Max trial length: {df['trial_days'].max()} days") 