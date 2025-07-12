import stripe
from datetime import datetime, timezone, timedelta
import pandas as pd

# Set Stripe API key
stripe.api_key = ("rk_live_51LNznbBnnqL8bKFQck4mN1IIAI7ddjnzvNxrPulfYRwv"
                  "Qd1eoZ68vD8wfCgoPAbawp6W8jfe9Dn7ysjZGNNSs1ZN00wRpzx7em")

print("Analyzing Lost Revenue Over Last 4 Months (May-August 2025)")
print("=" * 80)

# Define month ranges
months = [
    ("May 2025", datetime(2025, 5, 1, tzinfo=timezone.utc), 
     datetime(2025, 6, 1, tzinfo=timezone.utc)),
    ("June 2025", datetime(2025, 6, 1, tzinfo=timezone.utc), 
     datetime(2025, 7, 1, tzinfo=timezone.utc)),
    ("July 2025", datetime(2025, 7, 1, tzinfo=timezone.utc), 
     datetime(2025, 8, 1, tzinfo=timezone.utc)),
    ("August 2025", datetime(2025, 8, 1, tzinfo=timezone.utc), 
     datetime(2025, 9, 1, tzinfo=timezone.utc))
]

# Store results for each month
monthly_results = []
all_delinquent_customers = []

for month_name, start_date, end_date in months:
    print(f"\n{month_name}:")
    print("-" * 40)
    
    # Fetch customers for this month
    delinquent_count = 0
    total_lost_revenue = 0
    delinquent_details = []
    
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
                if not customer.email or not customer.delinquent:
                    continue
                
                # Calculate monthly revenue for delinquent customer
                monthly_revenue = 0
                has_trial = False
                subscription_count = 0
                
                if hasattr(customer, 'subscriptions') and customer.subscriptions.data:
                    for sub in customer.subscriptions.data:
                        subscription_count += 1
                        
                        # Check if trial customer
                        if sub.trial_start or sub.trial_end:
                            has_trial = True
                        
                        # Calculate revenue
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
                
                if monthly_revenue > 0 or subscription_count > 0:
                    delinquent_count += 1
                    total_lost_revenue += monthly_revenue
                    
                    delinquent_details.append({
                        'month': month_name,
                        'customer_id': customer.id,
                        'email': customer.email,
                        'created': datetime.fromtimestamp(customer.created),
                        'monthly_revenue': monthly_revenue,
                        'is_trial': has_trial,
                        'subscription_count': subscription_count
                    })
                    
                    all_delinquent_customers.append(delinquent_details[-1])
            
            has_more = customers.has_more
            if has_more:
                starting_after = customers.data[-1].id
                
        except Exception as e:
            print(f"  Error fetching data: {str(e)}")
            has_more = False
    
    # Store monthly results
    monthly_results.append({
        'month': month_name,
        'delinquent_customers': delinquent_count,
        'lost_revenue': total_lost_revenue,
        'details': delinquent_details
    })
    
    print(f"  Delinquent customers: {delinquent_count}")
    print(f"  Lost monthly revenue: ${total_lost_revenue:,.2f}")

# Calculate totals
print("\n" + "=" * 80)
print("4-MONTH SUMMARY (May-August 2025)")
print("=" * 80)

total_delinquent = sum(r['delinquent_customers'] for r in monthly_results)
total_lost_revenue = sum(r['lost_revenue'] for r in monthly_results)

print(f"\nTotal delinquent customers: {total_delinquent}")
print(f"Total monthly revenue lost: ${total_lost_revenue:,.2f}")
print(f"Annualized revenue loss: ${total_lost_revenue * 12:,.2f}")

# Monthly breakdown table
print("\nMonthly Breakdown:")
print("-" * 60)
print(f"{'Month':<15} {'Customers':<15} {'Lost Revenue':<20}")
print("-" * 60)

for result in monthly_results:
    print(f"{result['month']:<15} {result['delinquent_customers']:<15} "
          f"${result['lost_revenue']:,.2f}")

# Customer type analysis
trial_customers = [c for c in all_delinquent_customers if c['is_trial']]
direct_customers = [c for c in all_delinquent_customers if not c['is_trial']]

print(f"\nCustomer Type Breakdown:")
print(f"  Trial customers: {len(trial_customers)} "
      f"(${sum(c['monthly_revenue'] for c in trial_customers):,.2f})")
print(f"  Direct customers: {len(direct_customers)} "
      f"(${sum(c['monthly_revenue'] for c in direct_customers):,.2f})")

# Average revenue per delinquent
if total_delinquent > 0:
    avg_revenue_lost = total_lost_revenue / total_delinquent
    print(f"\nAverage revenue per delinquent customer: ${avg_revenue_lost:.2f}")

# Save detailed data
if all_delinquent_customers:
    df = pd.DataFrame(all_delinquent_customers)
    df.to_csv('4month_delinquent_analysis.csv', index=False)
    print(f"\nDetailed data saved to 4month_delinquent_analysis.csv")

# Create visualization data
print("\n" + "=" * 80)
print("KEY INSIGHTS:")
print("=" * 80)

# Calculate cumulative impact
cumulative_lost = 0
for i, result in enumerate(monthly_results):
    if result['delinquent_customers'] > 0:
        cumulative_lost += result['lost_revenue']
        months_affected = len(monthly_results) - i
        print(f"\n{result['month']} cohort:")
        print(f"  - {result['delinquent_customers']} customers failed")
        print(f"  - ${result['lost_revenue']:,.2f}/month lost")
        print(f"  - ${result['lost_revenue'] * months_affected:,.2f} lost to date")

print(f"\nTotal revenue lost over 4 months: ${cumulative_lost:,.2f}")
print(f"If no action taken, next 4 months will lose: "
      f"${total_lost_revenue * 4:,.2f}")

# Customer retention impact
if total_delinquent > 0:
    print(f"\nCustomer Lifetime Value Impact:")
    avg_customer_value = total_lost_revenue / total_delinquent
    # Assuming 24-month average customer lifetime
    lifetime_value_lost = avg_customer_value * 24 * total_delinquent
    print(f"  Average customer value: ${avg_customer_value:.2f}/month")
    print(f"  Estimated lifetime value lost (24 months): "
          f"${lifetime_value_lost:,.2f}") 