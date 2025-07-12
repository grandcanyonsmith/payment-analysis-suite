import stripe
from datetime import datetime, timezone
import pandas as pd

# Set Stripe API key
stripe.api_key = ("rk_live_51LNznbBnnqL8bKFQck4mN1IIAI7ddjnzvNxrPulfYRwv"
                  "Qd1eoZ68vD8wfCgoPAbawp6W8jfe9Dn7ysjZGNNSs1ZN00wRpzx7em")

# Define June 2025 date range
june_start = datetime(2025, 6, 1, tzinfo=timezone.utc)
june_end = datetime(2025, 7, 1, tzinfo=timezone.utc)

print("Fetching June 2025 Delinquent Accounts...")
print("=" * 80)

# Store delinquent customers
delinquent_customers = []

# Fetch all customers created in June
has_more = True
starting_after = None

while has_more:
    params = {
        'created': {
            'gte': int(june_start.timestamp()),
            'lt': int(june_end.timestamp())
        },
        'limit': 100,
        'expand': ['data.subscriptions', 'data.default_source']
    }
    
    if starting_after:
        params['starting_after'] = starting_after
    
    customers = stripe.Customer.list(**params)
    
    for customer in customers.data:
        # Skip if no email or not delinquent
        if not customer.email or not customer.delinquent:
            continue
            
        # Check for trial
        has_trial = False
        subscription_info = []
        total_monthly_revenue = 0
        
        # Get subscription details
        if hasattr(customer, 'subscriptions') and customer.subscriptions.data:
            for sub in customer.subscriptions.data:
                if sub.trial_start or sub.trial_end:
                    has_trial = True
                
                # Get subscription details
                sub_details = {
                    'id': sub.id,
                    'status': sub.status,
                    'created': datetime.fromtimestamp(sub.created).strftime('%Y-%m-%d'),
                    'current_period_end': datetime.fromtimestamp(sub.current_period_end).strftime('%Y-%m-%d')
                }
                
                # Calculate monthly revenue
                monthly_amount = 0
                for item in sub['items']['data']:
                    price = item['price']
                    amount = price['unit_amount'] / 100  # Convert cents to dollars
                    
                    # Convert to monthly if needed
                    if price['recurring']['interval'] == 'year':
                        amount = amount / 12
                    elif price['recurring']['interval'] == 'week':
                        amount = amount * 4.33
                    
                    monthly_amount += amount
                
                sub_details['monthly_amount'] = monthly_amount
                total_monthly_revenue += monthly_amount
                subscription_info.append(sub_details)
        
        # Get payment method info
        payment_method = "Unknown"
        if hasattr(customer, 'default_source') and customer.default_source:
            source = customer.default_source
            if hasattr(source, 'brand'):
                payment_method = f"{source.brand} {source.last4}"
            elif hasattr(source, 'object'):
                payment_method = source.object
        
        # Store customer details
        delinquent_customers.append({
            'customer_id': customer.id,
            'email': customer.email,
            'created_date': datetime.fromtimestamp(customer.created).strftime('%Y-%m-%d %H:%M'),
            'customer_type': 'Trial' if has_trial else 'Direct',
            'payment_method': payment_method,
            'monthly_revenue': total_monthly_revenue,
            'subscription_count': len(subscription_info),
            'subscriptions': subscription_info
        })
    
    has_more = customers.has_more
    if has_more:
        starting_after = customers.data[-1].id

# Sort by customer type and revenue
delinquent_customers.sort(key=lambda x: (x['customer_type'], -x['monthly_revenue']))

# Display results
trial_delinquent = [c for c in delinquent_customers if c['customer_type'] == 'Trial']
direct_delinquent = [c for c in delinquent_customers if c['customer_type'] == 'Direct']

print(f"\nTotal Delinquent Accounts: {len(delinquent_customers)}")
print(f"Trial Delinquent: {len(trial_delinquent)}")
print(f"Direct Delinquent: {len(direct_delinquent)}")
print("\n" + "=" * 80)

# Show trial delinquent customers
if trial_delinquent:
    print("\nTRIAL DELINQUENT CUSTOMERS:")
    print("-" * 80)
    for i, customer in enumerate(trial_delinquent, 1):
        print(f"\n{i}. {customer['email']}")
        print(f"   Customer ID: {customer['customer_id']}")
        print(f"   Created: {customer['created_date']}")
        print(f"   Monthly Revenue: ${customer['monthly_revenue']:.2f}")
        print(f"   Payment Method: {customer['payment_method']}")
        
        if customer['subscriptions']:
            print("   Subscriptions:")
            for sub in customer['subscriptions']:
                print(f"     - {sub['id']}: {sub['status']} (${sub['monthly_amount']:.2f}/mo)")
                print(f"       Created: {sub['created']}, Ends: {sub['current_period_end']}")

# Show direct delinquent customers
if direct_delinquent:
    print("\n\nDIRECT DELINQUENT CUSTOMERS:")
    print("-" * 80)
    for i, customer in enumerate(direct_delinquent, 1):
        print(f"\n{i}. {customer['email']}")
        print(f"   Customer ID: {customer['customer_id']}")
        print(f"   Created: {customer['created_date']}")
        print(f"   Monthly Revenue: ${customer['monthly_revenue']:.2f}")
        print(f"   Payment Method: {customer['payment_method']}")
        
        if customer['subscriptions']:
            print("   Subscriptions:")
            for sub in customer['subscriptions']:
                print(f"     - {sub['id']}: {sub['status']} (${sub['monthly_amount']:.2f}/mo)")
                print(f"       Created: {sub['created']}, Ends: {sub['current_period_end']}")

# Save to CSV for further analysis
df_data = []
for customer in delinquent_customers:
    base_data = {
        'customer_id': customer['customer_id'],
        'email': customer['email'],
        'created_date': customer['created_date'],
        'customer_type': customer['customer_type'],
        'payment_method': customer['payment_method'],
        'monthly_revenue': customer['monthly_revenue'],
        'subscription_count': customer['subscription_count']
    }
    
    # Add subscription details
    if customer['subscriptions']:
        for i, sub in enumerate(customer['subscriptions']):
            base_data[f'sub_{i+1}_id'] = sub['id']
            base_data[f'sub_{i+1}_status'] = sub['status']
            base_data[f'sub_{i+1}_amount'] = sub['monthly_amount']
    
    df_data.append(base_data)

df = pd.DataFrame(df_data)
df.to_csv('june_delinquent_accounts.csv', index=False)

print("\n" + "=" * 80)
print(f"Detailed data saved to june_delinquent_accounts.csv")

# Summary statistics
total_lost_revenue = sum(c['monthly_revenue'] for c in delinquent_customers)
avg_lost_revenue = total_lost_revenue / len(delinquent_customers) if delinquent_customers else 0

print(f"\nSUMMARY:")
print(f"Total Lost Monthly Revenue: ${total_lost_revenue:,.2f}")
print(f"Average Lost Revenue per Delinquent Customer: ${avg_lost_revenue:.2f}")

if trial_delinquent:
    trial_lost = sum(c['monthly_revenue'] for c in trial_delinquent)
    print(f"\nTrial Customers Lost Revenue: ${trial_lost:,.2f}")
    print(f"Average per Trial: ${trial_lost/len(trial_delinquent):.2f}")

if direct_delinquent:
    direct_lost = sum(c['monthly_revenue'] for c in direct_delinquent)
    print(f"\nDirect Customers Lost Revenue: ${direct_lost:,.2f}")
    print(f"Average per Direct: ${direct_lost/len(direct_delinquent):.2f}") 