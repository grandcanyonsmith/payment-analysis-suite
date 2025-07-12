import stripe
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

# Set your Stripe API key
stripe.api_key = "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"

print("=== STRIPE MAY 2025 TRIAL ANALYSIS ===\n")

# Define May 2025 date range
may_start = int(datetime(2025, 5, 1).timestamp())
may_end = int(datetime(2025, 5, 31, 23, 59, 59).timestamp())

# Get customers created in May 2025
print("Fetching May 2025 customers from Stripe...")
may_customers = []
has_more = True
starting_after = None

while has_more:
    params = {
        'limit': 100,
        'created': {
            'gte': may_start,
            'lte': may_end
        }
    }
    if starting_after:
        params['starting_after'] = starting_after
    
    customers = stripe.Customer.list(**params)
    may_customers.extend(customers.data)
    has_more = customers.has_more
    if has_more:
        starting_after = customers.data[-1].id

print(f"Total customers created in May 2025: {len(may_customers)}")

# Analyze subscriptions for these customers
trial_customers = []
direct_customers = []
no_sub_customers = []

for customer in may_customers:
    # Get subscriptions for this customer
    subs = stripe.Subscription.list(customer=customer.id, limit=10)
    
    if not subs.data:
        no_sub_customers.append(customer)
        continue
    
    # Check if any subscription had a trial
    had_trial = False
    for sub in subs.data:
        if sub.trial_start:
            had_trial = True
            break
    
    customer_data = {
        'id': customer.id,
        'email': customer.email,
        'created': datetime.fromtimestamp(customer.created),
        'delinquent': customer.delinquent,
        'currency': customer.currency,
        'subscriptions': len(subs.data),
        'first_sub_status': subs.data[0].status if subs.data else None,
        'had_trial': had_trial
    }
    
    if had_trial:
        trial_customers.append(customer_data)
    else:
        direct_customers.append(customer_data)

print(f"\nCustomer breakdown:")
print(f"  Trial customers: {len(trial_customers)}")
print(f"  Direct customers: {len(direct_customers)}")
print(f"  No subscription: {len(no_sub_customers)}")

# Analyze delinquency
trial_delinquent = sum(1 for c in trial_customers if c['delinquent'])
direct_delinquent = sum(1 for c in direct_customers if c['delinquent'])

print(f"\n=== DELINQUENCY ANALYSIS ===")
print(f"\nTrial customers:")
print(f"  Total: {len(trial_customers)}")
print(f"  Delinquent: {trial_delinquent} ({trial_delinquent/len(trial_customers)*100:.1f}%)" if trial_customers else "  No trial customers")

print(f"\nDirect customers:")
print(f"  Total: {len(direct_customers)}")
print(f"  Delinquent: {direct_delinquent} ({direct_delinquent/len(direct_customers)*100:.1f}%)" if direct_customers else "  No direct customers")

# Get more details on trial subscriptions
print(f"\n=== TRIAL SUBSCRIPTION DETAILS ===")

trial_sub_statuses = defaultdict(int)
for customer in trial_customers:
    # Get their subscriptions again for detailed analysis
    subs = stripe.Subscription.list(customer=customer['id'], limit=10)
    for sub in subs.data:
        if sub.trial_start:
            trial_sub_statuses[sub.status] += 1

print("\nTrial subscription statuses:")
for status, count in trial_sub_statuses.items():
    print(f"  {status}: {count}")

# Look at recent failed charges
print(f"\n=== RECENT PAYMENT FAILURES (Last 7 days) ===")

seven_days_ago = int((datetime.now() - timedelta(days=7)).timestamp())
failed_charges = stripe.Charge.list(
    limit=50,
    created={'gte': seven_days_ago},
    status='failed'
)

print(f"\nTotal failed charges in last 7 days: {len(failed_charges.data)}")

# Group failures by reason
failure_reasons = defaultdict(int)
failure_types = defaultdict(int)

for charge in failed_charges.data:
    failure_reasons[charge.failure_code or 'unknown'] += 1
    
    # Check if this was a trial conversion attempt
    if charge.description and 'trial' in charge.description.lower():
        failure_types['trial_conversion'] += 1
    elif charge.amount == 0:
        failure_types['validation'] += 1
    else:
        failure_types['regular'] += 1

print("\nTop failure reasons:")
for reason, count in sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {reason}: {count}")

print("\nFailure types:")
for ftype, count in failure_types.items():
    print(f"  {ftype}: {count}")

# Summary
print(f"\n=== SUMMARY ===")
if trial_customers and direct_customers:
    trial_rate = trial_delinquent/len(trial_customers)*100
    direct_rate = direct_delinquent/len(direct_customers)*100
    
    print(f"\nDelinquency rates:")
    print(f"  Trial customers: {trial_rate:.1f}%")
    print(f"  Direct customers: {direct_rate:.1f}%")
    
    if direct_rate > 0:
        ratio = trial_rate / direct_rate
        print(f"\n💡 Trial customers are {ratio:.1f}x more likely to be delinquent!")
    
    print(f"\n📊 Out of {len(may_customers)} May customers:")
    print(f"   - {len(trial_customers)} ({len(trial_customers)/len(may_customers)*100:.1f}%) had free trials")
    print(f"   - {len(direct_customers)} ({len(direct_customers)/len(may_customers)*100:.1f}%) were direct signups")
    print(f"   - {len(no_sub_customers)} ({len(no_sub_customers)/len(may_customers)*100:.1f}%) have no subscriptions")

# Save data
if trial_customers or direct_customers:
    all_customers = trial_customers + direct_customers
    df = pd.DataFrame(all_customers)
    df.to_csv('stripe_may_customers_analysis.csv', index=False)
    print(f"\nDetailed data saved to 'stripe_may_customers_analysis.csv'") 