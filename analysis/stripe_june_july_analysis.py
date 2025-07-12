import stripe
import pandas as pd
from datetime import datetime, timezone

# Set Stripe API key
stripe.api_key = ("rk_live_51LNznbBnnqL8bKFQck4mN1IIAI7ddjnzvNxrPulfYRwv"
                  "Qd1eoZ68vD8wfCgoPAbawp6W8jfe9Dn7ysjZGNNSs1ZN00wRpzx7em")


def get_month_data(start_date, end_date, month_name):
    """Get comprehensive customer data for a specific month"""
    print(f"\n{'='*60}")
    print(f"Analyzing {month_name} 2025 Customer Data")
    print('='*60)
    
    # Initialize counters
    customers_by_type = {
        'trial': [],
        'direct': []
    }
    
    delinquent_by_type = {
        'trial': 0,
        'direct': 0
    }
    
    revenue_by_type = {
        'trial': 0,
        'direct': 0
    }
    
    # Fetch all customers created in the month
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
        
        customers = stripe.Customer.list(**params)
        
        for customer in customers.data:
            # Skip if no email
            if not customer.email:
                continue
                
            # Check for trial
            has_trial = False
            is_delinquent = customer.delinquent
            monthly_revenue = 0
            
            # Check subscriptions for trial info
            if (hasattr(customer, 'subscriptions') and 
                customer.subscriptions.data):
                for sub in customer.subscriptions.data:
                    if sub.trial_start or sub.trial_end:
                        has_trial = True
                    
                    # Calculate monthly revenue
                    if sub.status in ['active', 'past_due', 'unpaid']:
                        for item in sub['items']['data']:
                            price = item['price']
                            # Convert cents to dollars
                            amount = price['unit_amount'] / 100
                            
                            # Convert to monthly if needed
                            if price['recurring']['interval'] == 'year':
                                amount = amount / 12
                            elif price['recurring']['interval'] == 'week':
                                amount = amount * 4.33
                            
                            monthly_revenue += amount
            
            # Categorize customer
            customer_type = 'trial' if has_trial else 'direct'
            customers_by_type[customer_type].append({
                'id': customer.id,
                'email': customer.email,
                'delinquent': is_delinquent,
                'monthly_revenue': monthly_revenue,
                'created': datetime.fromtimestamp(customer.created)
            })
            
            if is_delinquent:
                delinquent_by_type[customer_type] += 1
            
            revenue_by_type[customer_type] += monthly_revenue
        
        has_more = customers.has_more
        if has_more:
            starting_after = customers.data[-1].id
    
    # Calculate statistics
    total_customers = (len(customers_by_type['trial']) + 
                      len(customers_by_type['direct']))
    trial_count = len(customers_by_type['trial'])
    direct_count = len(customers_by_type['direct'])
    
    print(f"\nTotal Customers: {total_customers}")
    trial_pct = trial_count/total_customers*100 if total_customers > 0 else 0
    print(f"Trial Customers: {trial_count} ({trial_pct:.1f}%)")
    direct_pct = direct_count/total_customers*100 if total_customers > 0 else 0
    print(f"Direct Signups: {direct_count} ({direct_pct:.1f}%)")
    
    # Delinquency rates
    trial_delinquency_rate = ((delinquent_by_type['trial'] / trial_count * 100) 
                             if trial_count > 0 else 0)
    direct_delinquency_rate = ((delinquent_by_type['direct'] / direct_count * 100) 
                              if direct_count > 0 else 0)
    
    print(f"\nDelinquency Rates:")
    print(f"Trial Customers: {delinquent_by_type['trial']}/{trial_count} "
          f"({trial_delinquency_rate:.1f}%)")
    print(f"Direct Customers: {delinquent_by_type['direct']}/{direct_count} "
          f"({direct_delinquency_rate:.1f}%)")
    
    # Revenue analysis
    avg_trial_revenue = (revenue_by_type['trial'] / trial_count 
                        if trial_count > 0 else 0)
    avg_direct_revenue = (revenue_by_type['direct'] / direct_count 
                         if direct_count > 0 else 0)
    
    print(f"\nMonthly Revenue by Type:")
    print(f"Trial Customers: ${revenue_by_type['trial']:,.2f} "
          f"(avg: ${avg_trial_revenue:.2f})")
    print(f"Direct Customers: ${revenue_by_type['direct']:,.2f} "
          f"(avg: ${avg_direct_revenue:.2f})")
    
    # Lost revenue from delinquent trial customers
    active_trials = trial_count - delinquent_by_type['trial']
    avg_active_trial_revenue = ((revenue_by_type['trial'] / active_trials) 
                               if active_trials > 0 else avg_trial_revenue)
    lost_revenue = delinquent_by_type['trial'] * avg_active_trial_revenue
    
    print(f"\nRevenue Lost to Trial Delinquencies: ${lost_revenue:,.2f}/month")
    
    return {
        'month': month_name,
        'total_customers': total_customers,
        'trial_count': trial_count,
        'direct_count': direct_count,
        'trial_percentage': (trial_count/total_customers*100 
                           if total_customers > 0 else 0),
        'trial_delinquent': delinquent_by_type['trial'],
        'direct_delinquent': delinquent_by_type['direct'],
        'trial_delinquency_rate': trial_delinquency_rate,
        'direct_delinquency_rate': direct_delinquency_rate,
        'trial_revenue': revenue_by_type['trial'],
        'direct_revenue': revenue_by_type['direct'],
        'avg_trial_revenue': avg_trial_revenue,
        'avg_direct_revenue': avg_direct_revenue,
        'lost_revenue': lost_revenue,
        'customers_by_type': customers_by_type
    }

# Define date ranges
june_start = datetime(2025, 6, 1, tzinfo=timezone.utc)
june_end = datetime(2025, 7, 1, tzinfo=timezone.utc)

july_start = datetime(2025, 7, 1, tzinfo=timezone.utc)
july_end = datetime(2025, 8, 1, tzinfo=timezone.utc)

# Analyze each month
june_data = get_month_data(june_start, june_end, "June")
july_data = get_month_data(july_start, july_end, "July")

# Combined summary
print("\n" + "="*60)
print("COMBINED SUMMARY: May-July 2025 Trends")
print("="*60)

# May data from our previous analysis
may_data = {
    'total_customers': 190,
    'trial_count': 188,
    'direct_count': 2,
    'trial_percentage': 98.9,
    'trial_delinquent': 43,
    'direct_delinquent': 0,
    'trial_delinquency_rate': 22.9,
    'direct_delinquency_rate': 0,
    'avg_trial_revenue': 316,
    'avg_direct_revenue': 757,
    'lost_revenue': 9688
}

# Trend analysis
print("\nCustomer Acquisition Trends:")
print(f"May: {may_data['total_customers']} customers "
      f"({may_data['trial_percentage']:.1f}% trials)")
print(f"June: {june_data['total_customers']} customers "
      f"({june_data['trial_percentage']:.1f}% trials)")
print(f"July: {july_data['total_customers']} customers "
      f"({july_data['trial_percentage']:.1f}% trials)")

print("\nTrial Delinquency Rate Trends:")
print(f"May: {may_data['trial_delinquency_rate']:.1f}%")
print(f"June: {june_data['trial_delinquency_rate']:.1f}%")
print(f"July: {july_data['trial_delinquency_rate']:.1f}%")

print("\nAverage Revenue per Customer:")
print(f"May: Trial ${may_data['avg_trial_revenue']:.2f} vs "
      f"Direct ${may_data['avg_direct_revenue']:.2f}")
print(f"June: Trial ${june_data['avg_trial_revenue']:.2f} vs "
      f"Direct ${june_data['avg_direct_revenue']:.2f}")
print(f"July: Trial ${july_data['avg_trial_revenue']:.2f} vs "
      f"Direct ${july_data['avg_direct_revenue']:.2f}")

# Total impact
total_lost = (may_data['lost_revenue'] + june_data['lost_revenue'] + 
              july_data['lost_revenue'])
print(f"\nTotal Monthly Revenue Lost (May-July): ${total_lost:,.2f}")
print(f"Projected Annual Loss: ${total_lost * 4:,.2f}")

# Save detailed data
all_data = []
for month_data in [june_data, july_data]:
    for ctype, customers in month_data['customers_by_type'].items():
        for customer in customers:
            all_data.append({
                'month': month_data['month'],
                'customer_id': customer['id'],
                'email': customer['email'],
                'type': ctype,
                'delinquent': customer['delinquent'],
                'monthly_revenue': customer['monthly_revenue'],
                'created': customer['created']
            })

df = pd.DataFrame(all_data)
df.to_csv('june_july_customers.csv', index=False)
print("\nDetailed customer data saved to june_july_customers.csv")

# Create summary report
summary_data = []
for month, data in [('May', may_data), ('June', june_data), ('July', july_data)]:
    summary_data.append({
        'Month': month,
        'Total Customers': data['total_customers'],
        'Trial Customers': data['trial_count'],
        'Direct Signups': data['direct_count'],
        'Trial %': f"{data['trial_percentage']:.1f}%",
        'Trial Delinquency Rate': f"{data['trial_delinquency_rate']:.1f}%",
        'Direct Delinquency Rate': f"{data['direct_delinquency_rate']:.1f}%",
        'Avg Trial Revenue': f"${data['avg_trial_revenue']:.2f}",
        'Avg Direct Revenue': f"${data['avg_direct_revenue']:.2f}",
        'Lost Revenue': f"${data['lost_revenue']:,.2f}"
    })

summary_df = pd.DataFrame(summary_data)
summary_df.to_csv('may_july_summary.csv', index=False)
print("Summary data saved to may_july_summary.csv") 