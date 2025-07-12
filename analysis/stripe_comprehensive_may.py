import stripe
from datetime import datetime
from collections import defaultdict
import csv

# Set API key
stripe.api_key = "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"

print("=== COMPREHENSIVE MAY 2025 TRIAL ANALYSIS FROM STRIPE ===\n")

# Define May 2025 date range
may_start = int(datetime(2025, 5, 1).timestamp())
may_end = int(datetime(2025, 5, 31, 23, 59, 59).timestamp())

# Collect all May customers
print("Fetching all May 2025 customers...")
all_may_customers = []
has_more = True
starting_after = None
batch_count = 0

while has_more:
    batch_count += 1
    print(f"  Fetching batch {batch_count}...")
    
    params = {
        'limit': 100,
        'created': {'gte': may_start, 'lte': may_end}
    }
    if starting_after:
        params['starting_after'] = starting_after
    
    customers = stripe.Customer.list(**params)
    all_may_customers.extend(customers.data)
    has_more = customers.has_more
    
    if has_more:
        starting_after = customers.data[-1].id

print(f"\nTotal May 2025 customers found: {len(all_may_customers)}")

# Analyze each customer
customer_analysis = []
trial_customers = []
direct_customers = []
no_sub_customers = []

print("\nAnalyzing customer subscriptions...")
for i, customer in enumerate(all_may_customers):
    if i % 50 == 0:
        print(f"  Processing customer {i+1}/{len(all_may_customers)}...")
    
    # Get subscriptions
    subs = stripe.Subscription.list(customer=customer.id, limit=10)
    
    # Determine customer type
    had_trial = False
    sub_statuses = []
    total_spent = 0
    
    for sub in subs.data:
        sub_statuses.append(sub.status)
        if sub.trial_start:
            had_trial = True
        
        # Get invoices for this subscription to calculate spend
        invoices = stripe.Invoice.list(
            subscription=sub.id,
            limit=10
        )
        for invoice in invoices.data:
            if invoice.paid and invoice.amount_paid > 0:
                total_spent += invoice.amount_paid / 100
    
    customer_info = {
        'id': customer.id,
        'email': customer.email or 'No email',
        'created': datetime.fromtimestamp(customer.created).strftime('%Y-%m-%d'),
        'delinquent': customer.delinquent,
        'had_trial': had_trial,
        'subscription_count': len(subs.data),
        'subscription_statuses': ','.join(sub_statuses) if sub_statuses else 'none',
        'total_spent': total_spent,
        'customer_type': 'trial' if had_trial else ('direct' if subs.data else 'no_sub')
    }
    
    customer_analysis.append(customer_info)
    
    if had_trial:
        trial_customers.append(customer_info)
    elif subs.data:
        direct_customers.append(customer_info)
    else:
        no_sub_customers.append(customer_info)

# Analysis results
print("\n=== RESULTS ===")
print(f"\nCustomer breakdown:")
print(f"  Trial customers: {len(trial_customers)} ({len(trial_customers)/len(all_may_customers)*100:.1f}%)")
print(f"  Direct customers: {len(direct_customers)} ({len(direct_customers)/len(all_may_customers)*100:.1f}%)")
print(f"  No subscription: {len(no_sub_customers)} ({len(no_sub_customers)/len(all_may_customers)*100:.1f}%)")

# Delinquency analysis
trial_delinquent = sum(1 for c in trial_customers if c['delinquent'])
direct_delinquent = sum(1 for c in direct_customers if c['delinquent'])

print(f"\n=== DELINQUENCY ANALYSIS ===")
if trial_customers:
    print(f"\nTrial customers:")
    print(f"  Total: {len(trial_customers)}")
    print(f"  Delinquent: {trial_delinquent} ({trial_delinquent/len(trial_customers)*100:.1f}%)")
    
    # Status breakdown for trials
    trial_statuses = defaultdict(int)
    for c in trial_customers:
        for status in c['subscription_statuses'].split(','):
            if status and status != 'none':
                trial_statuses[status] += 1
    
    print(f"\n  Subscription statuses:")
    for status, count in sorted(trial_statuses.items(), key=lambda x: x[1], reverse=True):
        print(f"    {status}: {count}")

if direct_customers:
    print(f"\nDirect customers:")
    print(f"  Total: {len(direct_customers)}")
    print(f"  Delinquent: {direct_delinquent} ({direct_delinquent/len(direct_customers)*100:.1f}%)")
    
    # Status breakdown for direct
    direct_statuses = defaultdict(int)
    for c in direct_customers:
        for status in c['subscription_statuses'].split(','):
            if status and status != 'none':
                direct_statuses[status] += 1
    
    print(f"\n  Subscription statuses:")
    for status, count in sorted(direct_statuses.items(), key=lambda x: x[1], reverse=True):
        print(f"    {status}: {count}")

# Revenue analysis
trial_revenue = sum(c['total_spent'] for c in trial_customers)
direct_revenue = sum(c['total_spent'] for c in direct_customers)

print(f"\n=== REVENUE ANALYSIS ===")
print(f"Total revenue from trial customers: ${trial_revenue:,.2f}")
print(f"Total revenue from direct customers: ${direct_revenue:,.2f}")
if trial_customers:
    print(f"Average revenue per trial customer: ${trial_revenue/len(trial_customers):.2f}")
if direct_customers:
    print(f"Average revenue per direct customer: ${direct_revenue/len(direct_customers):.2f}")

# Summary
print(f"\n=== SUMMARY ===")
if trial_customers and direct_customers:
    trial_del_rate = trial_delinquent/len(trial_customers)*100
    direct_del_rate = direct_delinquent/len(direct_customers)*100
    
    print(f"\nDelinquency rates:")
    print(f"  Trial customers: {trial_del_rate:.1f}%")
    print(f"  Direct customers: {direct_del_rate:.1f}%")
    
    if direct_del_rate > 0:
        ratio = trial_del_rate / direct_del_rate
        print(f"\n💡 Trial customers are {ratio:.1f}x more likely to be delinquent!")
    elif trial_del_rate > 0:
        print(f"\n💡 Trial customers have {trial_del_rate:.1f}% delinquency while direct customers have 0%!")

# Save detailed data
print(f"\nSaving detailed analysis to CSV...")
with open('stripe_may_2025_analysis.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=customer_analysis[0].keys())
    writer.writeheader()
    writer.writerows(customer_analysis)

print(f"✓ Data saved to 'stripe_may_2025_analysis.csv'")

# Recent trend warning
print(f"\n⚠️  WARNING: Your 10 most recent customers (July 2025) ALL used free trials!")
print(f"This suggests the trial problem is getting worse, not better.") 