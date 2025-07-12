import stripe
from datetime import datetime, timezone
import pandas as pd

# Set Stripe API key
stripe.api_key = ("rk_live_51LNznbBnnqL8bKFQck4mN1IIAI7ddjnzvNxrPulfYRwv"
                  "Qd1eoZ68vD8wfCgoPAbawp6W8jfe9Dn7ysjZGNNSs1ZN00wRpzx7em")

print("Analyzing Revenue Loss: March-July 2025")
print("=" * 80)

# Define month ranges
months = [
    ("March 2025", datetime(2025, 3, 1, tzinfo=timezone.utc), 
     datetime(2025, 4, 1, tzinfo=timezone.utc)),
    ("April 2025", datetime(2025, 4, 1, tzinfo=timezone.utc), 
     datetime(2025, 5, 1, tzinfo=timezone.utc)),
    ("May 2025", datetime(2025, 5, 1, tzinfo=timezone.utc), 
     datetime(2025, 6, 1, tzinfo=timezone.utc)),
    ("June 2025", datetime(2025, 6, 1, tzinfo=timezone.utc), 
     datetime(2025, 7, 1, tzinfo=timezone.utc)),
    ("July 2025", datetime(2025, 7, 1, tzinfo=timezone.utc), 
     datetime(2025, 8, 1, tzinfo=timezone.utc))
]

# Store results
monthly_results = []
all_delinquent_customers = []

for month_name, start_date, end_date in months:
    print(f"\n{month_name}:")
    print("-" * 40)
    
    # Initialize counters for this month
    delinquent_count = 0
    total_lost_revenue = 0
    trial_delinquent = 0
    direct_delinquent = 0
    new_customers = 0
    trial_customers = 0
    
    has_more = True
    starting_after = None
    
    while has_more:
        params = {
            'created': {
                'gte': int(start_date.timestamp()),
                'lt': int(end_date.timestamp())
            },
            'limit': 100,
            'expand': ['data.subscriptions']
        }
        
        if starting_after:
            params['starting_after'] = starting_after
        
        try:
            customers = stripe.Customer.list(**params)
            
            for customer in customers.data:
                if not customer.email:
                    continue
                    
                new_customers += 1
                
                # Check if trial customer
                has_trial = False
                if hasattr(customer, 'subscriptions') and customer.subscriptions.data:
                    for sub in customer.subscriptions.data:
                        if sub.trial_start or sub.trial_end:
                            has_trial = True
                            trial_customers += 1
                            break
                
                # Check if delinquent
                if customer.delinquent:
                    delinquent_count += 1
                    
                    # Calculate monthly revenue
                    monthly_revenue = 0
                    if hasattr(customer, 'subscriptions') and customer.subscriptions.data:
                        for sub in customer.subscriptions.data:
                            if sub.status in ['past_due', 'unpaid', 'canceled']:
                                for item in sub['items']['data']:
                                    price = item['price']
                                    amount = price['unit_amount'] / 100
                                    
                                    # Convert to monthly
                                    if price['recurring']['interval'] == 'year':
                                        amount = amount / 12
                                    elif price['recurring']['interval'] == 'week':
                                        amount = amount * 4.33
                                    
                                    monthly_revenue += amount
                    
                    total_lost_revenue += monthly_revenue
                    
                    if has_trial:
                        trial_delinquent += 1
                    else:
                        direct_delinquent += 1
                    
                    # Store customer details
                    all_delinquent_customers.append({
                        'month': month_name,
                        'customer_id': customer.id,
                        'email': customer.email,
                        'created': datetime.fromtimestamp(customer.created),
                        'monthly_revenue': monthly_revenue,
                        'is_trial': has_trial
                    })
            
            has_more = customers.has_more
            if has_more:
                starting_after = customers.data[-1].id
                
        except Exception as e:
            print(f"  Error: {str(e)}")
            has_more = False
    
    # Store results
    monthly_results.append({
        'month': month_name,
        'new_customers': new_customers,
        'trial_customers': trial_customers,
        'delinquent_total': delinquent_count,
        'trial_delinquent': trial_delinquent,
        'direct_delinquent': direct_delinquent,
        'lost_revenue': total_lost_revenue
    })
    
    # Print summary
    print(f"  New customers: {new_customers}")
    print(f"  Trial customers: {trial_customers}")
    print(f"  Delinquent: {delinquent_count} (Trial: {trial_delinquent}, Direct: {direct_delinquent})")
    print(f"  Lost revenue: ${total_lost_revenue:,.2f}")

# Overall summary
print("\n" + "=" * 80)
print("5-MONTH SUMMARY (March-July 2025)")
print("=" * 80)

# Calculate totals
total_new = sum(r['new_customers'] for r in monthly_results)
total_trials = sum(r['trial_customers'] for r in monthly_results)
total_delinquent = sum(r['delinquent_total'] for r in monthly_results)
total_trial_delinquent = sum(r['trial_delinquent'] for r in monthly_results)
total_direct_delinquent = sum(r['direct_delinquent'] for r in monthly_results)
total_lost_revenue = sum(r['lost_revenue'] for r in monthly_results)

print(f"\nTotal new customers: {total_new}")
print(f"Total trial customers: {total_trials}")
print(f"Total delinquent: {total_delinquent}")
print(f"  - Trial delinquent: {total_trial_delinquent}")
print(f"  - Direct delinquent: {total_direct_delinquent}")
print(f"\nTotal monthly revenue lost: ${total_lost_revenue:,.2f}")
print(f"Annualized revenue loss: ${total_lost_revenue * 12:,.2f}")

# Monthly breakdown table
print("\n" + "-" * 100)
print(f"{'Month':<12} {'New':<8} {'Trials':<8} {'Delinquent':<12} {'Trial Del':<10} {'Direct Del':<12} {'Lost Revenue':<15}")
print("-" * 100)

for r in monthly_results:
    print(f"{r['month']:<12} {r['new_customers']:<8} {r['trial_customers']:<8} "
          f"{r['delinquent_total']:<12} {r['trial_delinquent']:<10} "
          f"{r['direct_delinquent']:<12} ${r['lost_revenue']:,.2f}")

# Calculate failure rates
print("\n" + "=" * 80)
print("FAILURE RATE ANALYSIS")
print("=" * 80)

for i, r in enumerate(monthly_results):
    if r['new_customers'] > 0:
        overall_failure_rate = (r['delinquent_total'] / r['new_customers']) * 100
        
        # For trial failure rate, we need to look at previous month's trials
        if i > 0 and monthly_results[i-1]['trial_customers'] > 0:
            trial_failure_rate = (r['trial_delinquent'] / monthly_results[i-1]['trial_customers']) * 100
            print(f"\n{r['month']}:")
            print(f"  Overall failure rate: {overall_failure_rate:.1f}% of same-month signups")
            print(f"  Trial failure rate: {trial_failure_rate:.1f}% of previous month's trials")
        else:
            print(f"\n{r['month']}:")
            print(f"  Overall failure rate: {overall_failure_rate:.1f}% of same-month signups")

# Save detailed data
if all_delinquent_customers:
    df = pd.DataFrame(all_delinquent_customers)
    df.to_csv('march_july_delinquent_analysis.csv', index=False)
    print(f"\nDetailed data saved to march_july_delinquent_analysis.csv")

# Key insights
print("\n" + "=" * 80)
print("KEY INSIGHTS")
print("=" * 80)

# Calculate cumulative losses
cumulative_loss = 0
for i, r in enumerate(monthly_results):
    months_active = len(monthly_results) - i
    cumulative_loss += r['lost_revenue'] * months_active

print(f"\nCumulative revenue lost (March-July): ${cumulative_loss:,.2f}")
print(f"Average delinquent customers per month: {total_delinquent/5:.1f}")
print(f"Average revenue lost per delinquent: ${total_lost_revenue/total_delinquent:.2f}" if total_delinquent > 0 else "N/A")

# Trial vs Direct comparison
if total_trial_delinquent > 0:
    trial_revenue = sum(c['monthly_revenue'] for c in all_delinquent_customers if c['is_trial'])
    print(f"\nTrial customers:")
    print(f"  - {total_trial_delinquent} delinquent ({total_trial_delinquent/total_delinquent*100:.1f}%)")
    print(f"  - ${trial_revenue:,.2f} lost revenue")
    print(f"  - ${trial_revenue/total_trial_delinquent:.2f} average per customer")

if total_direct_delinquent > 0:
    direct_revenue = sum(c['monthly_revenue'] for c in all_delinquent_customers if not c['is_trial'])
    print(f"\nDirect customers:")
    print(f"  - {total_direct_delinquent} delinquent ({total_direct_delinquent/total_delinquent*100:.1f}%)")
    print(f"  - ${direct_revenue:,.2f} lost revenue")
    print(f"  - ${direct_revenue/total_direct_delinquent:.2f} average per customer" if total_direct_delinquent > 0 else "  - $0 average (no revenue)")

print("\n" + "=" * 80) 