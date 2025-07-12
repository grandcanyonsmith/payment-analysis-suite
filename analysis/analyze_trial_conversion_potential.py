import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
import stripe

# Set up Stripe API
api_key = ('rk_live_51LNznbBnnqL8bKFQck4mN1IIAI7ddjnzvNxrPulfYRwvQd1e'
           'oZ68vD8wfCgoPAbawp6W8jfe9Dn7ysjZGNNSs1ZN00wRpzx7em')
stripe.api_key = api_key

print("Fetching customer data from Stripe API...")
print("=" * 80)

# Collect all customers from March to July 2025
all_customers = []
months = ['2025-03', '2025-04', '2025-05', '2025-06', '2025-07']

for month in months:
    print(f"\nProcessing {month}...")
    
    # Set date range for the month
    if month == '2025-03':
        start_date = datetime(2025, 3, 1)
        end_date = datetime(2025, 3, 31, 23, 59, 59)
    elif month == '2025-04':
        start_date = datetime(2025, 4, 1)
        end_date = datetime(2025, 4, 30, 23, 59, 59)
    elif month == '2025-05':
        start_date = datetime(2025, 5, 1)
        end_date = datetime(2025, 5, 31, 23, 59, 59)
    elif month == '2025-06':
        start_date = datetime(2025, 6, 1)
        end_date = datetime(2025, 6, 30, 23, 59, 59)
    else:  # July
        start_date = datetime(2025, 7, 1)
        end_date = datetime(2025, 7, 31, 23, 59, 59)
    
    # Fetch customers for this month
    has_more = True
    starting_after = None
    month_customers = []
    
    while has_more:
        params = {
            'limit': 100,
            'created': {
                'gte': int(start_date.timestamp()),
                'lte': int(end_date.timestamp())
            }
        }
        if starting_after:
            params['starting_after'] = starting_after
        
        customers = stripe.Customer.list(**params)
        
        for customer in customers:
            # Get subscriptions
            subs = stripe.Subscription.list(customer=customer.id, limit=10)
            
            for sub in subs:
                # Check if this was a trial subscription
                if sub.trial_end:
                    trial_end_date = datetime.fromtimestamp(sub.trial_end)
                    
                    # Determine payment method status
                    has_payment_method = bool(
                        customer.default_source or 
                        customer.invoice_settings.get('default_payment_method')
                    )
                    
                    # Determine if converted (active/past_due) or failed
                    converted = sub.status in ['active', 'past_due']
                    delinquent = customer.delinquent
                    
                    # Calculate monthly revenue
                    monthly_revenue = 0
                    for item in sub['items']['data']:
                        price = item['price']
                        interval = price['recurring']['interval']
                        amount = price['unit_amount']
                        qty = item['quantity']
                        if interval == 'month':
                            monthly_revenue += (amount / 100) * qty
                        elif interval == 'year':
                            monthly_revenue += (amount / 100 / 12) * qty
                    
                    customer_data = {
                        'month': month,
                        'customer_id': customer.id,
                        'email': customer.email,
                        'created': datetime.fromtimestamp(customer.created),
                        'has_payment_method': has_payment_method,
                        'trial_end': trial_end_date,
                        'subscription_status': sub.status,
                        'converted': converted,
                        'delinquent': delinquent,
                        'monthly_revenue': monthly_revenue
                    }
                    
                    month_customers.append(customer_data)
                    break  # Only count first subscription per customer
        
        has_more = customers.has_more
        if has_more:
            starting_after = customers.data[-1].id
    
    print(f"  Found {len(month_customers)} trial customers")
    all_customers.extend(month_customers)

# Create DataFrame
df = pd.DataFrame(all_customers)

# Group by month and calculate conversions
results = []

for month in months:
    month_data = df[df['month'] == month]
    
    if len(month_data) == 0:
        continue
    
    # Overall stats
    total_trials = len(month_data)
    total_with_payment = len(month_data[month_data['has_payment_method']])
    total_without_payment = len(month_data[~month_data['has_payment_method']])
    
    # Actual conversions (including no payment method)
    actual_converted = len(month_data[month_data['converted']])
    if total_trials > 0:
        actual_conversion_rate = actual_converted / total_trials * 100
    else:
        actual_conversion_rate = 0
    
    # Conversions only from those with payment methods
    with_payment_converted = len(month_data[
        (month_data['has_payment_method']) & (month_data['converted'])
    ])
    if total_with_payment > 0:
        potential_conversion_rate = (
            with_payment_converted / total_with_payment * 100
        )
    else:
        potential_conversion_rate = 0
    
    # Revenue calculations
    actual_revenue = month_data[
        month_data['converted']
    ]['monthly_revenue'].sum()
    potential_revenue = month_data[
        (month_data['has_payment_method']) & (month_data['converted'])
    ]['monthly_revenue'].sum()
    lost_revenue = month_data[
        (~month_data['has_payment_method']) & (~month_data['converted'])
    ]['monthly_revenue'].sum()
    
    results.append({
        'month': month,
        'total_trials': total_trials,
        'with_payment_method': total_with_payment,
        'without_payment_method': total_without_payment,
        'actual_conversions': actual_converted,
        'actual_conversion_rate': actual_conversion_rate,
        'potential_conversions': with_payment_converted,
        'potential_conversion_rate': potential_conversion_rate,
        'conversion_rate_lift': (potential_conversion_rate - 
                               actual_conversion_rate),
        'actual_revenue': actual_revenue,
        'potential_revenue': potential_revenue,
        'lost_revenue': lost_revenue
    })

results_df = pd.DataFrame(results)

# Print detailed results
print("\n" + "=" * 100)
print("TRIAL CONVERSION ANALYSIS: ACTUAL vs POTENTIAL "
      "(If All Had Payment Methods)")
print("=" * 100)

for _, row in results_df.iterrows():
    print(f"\n{row['month']}:")
    print(f"  Total Trials: {row['total_trials']}")
    pct_with = row['with_payment_method']/row['total_trials']*100
    pct_without = row['without_payment_method']/row['total_trials']*100
    print(f"  With Payment Method: {row['with_payment_method']} "
          f"({pct_with:.1f}%)")
    print(f"  Without Payment Method: {row['without_payment_method']} "
          f"({pct_without:.1f}%)")
    print(f"  \n  Actual Conversion Rate: {row['actual_conversion_rate']:.1f}%")
    print(f"  Potential Conversion Rate (payment method only): "
          f"{row['potential_conversion_rate']:.1f}%")
    print(f"  Improvement: +{row['conversion_rate_lift']:.1f} percentage points")
    print("  \n  Monthly Revenue Impact:")
    print(f"    Current: ${row['actual_revenue']:,.2f}")
    print(f"    Potential: ${row['potential_revenue']:,.2f}")
    print(f"    Lost to No Payment: ${row['lost_revenue']:,.2f}")

# Create visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

months_list = results_df['month'].tolist()

# 1. Conversion Rate Comparison
x = np.arange(len(months_list))
width = 0.35

bars1 = ax1.bar(x - width/2, results_df['actual_conversion_rate'], width, 
                 label='Actual (All Trials)', color='#ff6b6b', alpha=0.8)
bars2 = ax1.bar(x + width/2, results_df['potential_conversion_rate'], width,
                 label='Potential (Payment Method Only)', 
                 color='#4ecdc4', alpha=0.8)

ax1.set_xlabel('Month')
ax1.set_ylabel('Conversion Rate (%)')
ax1.set_title('Trial Conversion Rates: Actual vs Potential', 
              fontsize=14, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels(months_list)
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
for bar in bars2:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{height:.1f}%', ha='center', va='bottom', fontsize=9)

# 2. Payment Method Status by Month
ax2.bar(months_list, results_df['without_payment_method'], 
        label='No Payment Method', color='#ff6b6b', alpha=0.8)
ax2.bar(months_list, results_df['with_payment_method'], 
        bottom=results_df['without_payment_method'],
        label='Has Payment Method', color='#4ecdc4', alpha=0.8)

ax2.set_xlabel('Month')
ax2.set_ylabel('Number of Trial Customers')
ax2.set_title('Trial Customers by Payment Method Status', 
              fontsize=14, fontweight='bold')
ax2.legend()
ax2.grid(axis='y', alpha=0.3)

# 3. Revenue Impact
revenue_data = results_df[['actual_revenue', 'potential_revenue', 
                          'lost_revenue']]
revenue_data.index = months_list

ax3.plot(months_list, results_df['actual_revenue'], marker='o', 
         linewidth=3, markersize=10, label='Actual Revenue', color='#ff6b6b')
ax3.plot(months_list, results_df['potential_revenue'], marker='s', 
         linewidth=3, markersize=10, label='Potential Revenue', 
         color='#4ecdc4')
ax3.fill_between(range(len(months_list)), results_df['actual_revenue'], 
                 results_df['potential_revenue'], alpha=0.3, color='#ffd93d')

ax3.set_xlabel('Month')
ax3.set_ylabel('Monthly Revenue ($)')
ax3.set_title('Revenue Impact of No Payment Method Trials', 
              fontsize=14, fontweight='bold')
ax3.legend()
ax3.grid(True, alpha=0.3)

# 4. Conversion Rate Lift
ax4.bar(months_list, results_df['conversion_rate_lift'], 
        color='#52de97', alpha=0.8)
ax4.set_xlabel('Month')
ax4.set_ylabel('Percentage Point Increase')
ax4.set_title('Potential Conversion Rate Improvement', 
              fontsize=14, fontweight='bold')
ax4.grid(axis='y', alpha=0.3)

# Add value labels
for i, v in enumerate(results_df['conversion_rate_lift']):
    ax4.text(i, v + 0.5, f'+{v:.1f}pp', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('trial_conversion_potential.png', dpi=300, bbox_inches='tight')
print("\n✅ Visualization saved as 'trial_conversion_potential.png'")

# Summary statistics
print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)

total_trials = results_df['total_trials'].sum()
total_without_payment = results_df['without_payment_method'].sum()
avg_actual_conversion = results_df['actual_conversion_rate'].mean()
avg_potential_conversion = results_df['potential_conversion_rate'].mean()
total_lost_revenue = results_df['lost_revenue'].sum()

pct_without_payment = total_without_payment/total_trials*100
print(f"\nTotal trial customers analyzed: {total_trials}")
print(f"Total without payment method: {total_without_payment} "
      f"({pct_without_payment:.1f}%)")
print(f"\nAverage conversion rates:")
print(f"  Actual (all trials): {avg_actual_conversion:.1f}%")
print(f"  Potential (payment method only): {avg_potential_conversion:.1f}%")
avg_improvement = avg_potential_conversion - avg_actual_conversion
print(f"  Average improvement: +{avg_improvement:.1f} percentage points")
print("\nTotal monthly revenue lost to no payment method: "
      f"${total_lost_revenue:,.2f}")
print(f"Annual revenue impact: ${total_lost_revenue * 12:,.2f}")

# Save detailed data
results_df.to_csv('trial_conversion_potential_analysis.csv', index=False)
print("\n✅ Detailed data saved to 'trial_conversion_potential_analysis.csv'") 