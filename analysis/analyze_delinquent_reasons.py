import stripe
from datetime import datetime, timezone
import pandas as pd
from collections import defaultdict

# Set Stripe API key
stripe.api_key = ("rk_live_51LNznbBnnqL8bKFQck4mN1IIAI7ddjnzvNxrPulfYRwv"
                  "Qd1eoZ68vD8wfCgoPAbawp6W8jfe9Dn7ysjZGNNSs1ZN00wRpzx7em")

print("Analyzing Delinquent Customer Reasons (March-July 2025)")
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

# Store all delinquent customer details
all_delinquent_details = []
failure_reasons = defaultdict(int)
payment_method_types = defaultdict(int)

# Process each month
for month_name, start_date, end_date in months:
    print(f"\nProcessing {month_name}...")
    
    has_more = True
    starting_after = None
    month_count = 0
    
    while has_more:
        params = {
            'created': {
                'gte': int(start_date.timestamp()),
                'lt': int(end_date.timestamp())
            },
            'limit': 100,
            'expand': ['data.subscriptions', 'data.default_source', 
                      'data.invoice_settings.default_payment_method']
        }
        
        if starting_after:
            params['starting_after'] = starting_after
        
        try:
            customers = stripe.Customer.list(**params)
            
            for customer in customers.data:
                if not customer.email or not customer.delinquent:
                    continue
                
                month_count += 1
                
                # Get customer details
                customer_details = {
                    'month': month_name,
                    'customer_id': customer.id,
                    'email': customer.email,
                    'created': datetime.fromtimestamp(customer.created),
                    'payment_method': 'None',
                    'card_brand': 'None',
                    'card_last4': 'None',
                    'failure_reason': 'Unknown',
                    'subscription_status': 'None',
                    'trial_end': None,
                    'monthly_revenue': 0,
                    'is_trial': False,
                    'last_payment_attempt': None,
                    'invoice_status': 'None'
                }
                
                # Check payment method
                if hasattr(customer, 'default_source') and customer.default_source:
                    source = customer.default_source
                    if hasattr(source, 'object'):
                        customer_details['payment_method'] = source.object
                        if hasattr(source, 'brand'):
                            customer_details['card_brand'] = source.brand
                        if hasattr(source, 'last4'):
                            customer_details['card_last4'] = source.last4
                
                # Get subscription details
                if hasattr(customer, 'subscriptions') and customer.subscriptions.data:
                    for sub in customer.subscriptions.data:
                        customer_details['subscription_status'] = sub.status
                        
                        # Check if trial
                        if sub.trial_end:
                            customer_details['is_trial'] = True
                            customer_details['trial_end'] = datetime.fromtimestamp(sub.trial_end)
                        
                        # Calculate revenue
                        if sub.status in ['past_due', 'unpaid', 'canceled']:
                            for item in sub['items']['data']:
                                price = item['price']
                                amount = price['unit_amount'] / 100
                                
                                if price['recurring']['interval'] == 'year':
                                    amount = amount / 12
                                elif price['recurring']['interval'] == 'week':
                                    amount = amount * 4.33
                                
                                customer_details['monthly_revenue'] += amount
                
                # Get latest invoice to find failure reason
                try:
                    invoices = stripe.Invoice.list(
                        customer=customer.id,
                        limit=5,
                        expand=['data.charge']
                    )
                    
                    for invoice in invoices.data:
                        if invoice.status in ['uncollectible', 'void']:
                            customer_details['invoice_status'] = invoice.status
                            
                            # Get charge failure reason
                            if hasattr(invoice, 'charge') and invoice.charge:
                                charge = invoice.charge
                                if hasattr(charge, 'failure_code'):
                                    customer_details['failure_reason'] = charge.failure_code or 'generic_decline'
                                if hasattr(charge, 'failure_message'):
                                    customer_details['failure_message'] = charge.failure_message
                                
                                # Get payment method from charge
                                if hasattr(charge, 'payment_method_details'):
                                    pm_details = charge.payment_method_details
                                    if hasattr(pm_details, 'card'):
                                        card = pm_details.card
                                        customer_details['card_brand'] = card.brand
                                        customer_details['card_last4'] = card.last4
                                        if hasattr(card, 'funding'):
                                            customer_details['card_funding'] = card.funding
                            
                            customer_details['last_payment_attempt'] = datetime.fromtimestamp(invoice.created)
                            break
                    
                    # If no failed invoice found, check for missing payment method
                    if customer_details['failure_reason'] == 'Unknown' and customer_details['payment_method'] == 'None':
                        customer_details['failure_reason'] = 'no_payment_method'
                        
                except Exception as e:
                    print(f"    Error fetching invoices for {customer.email}: {str(e)}")
                
                # Track failure reasons
                failure_reasons[customer_details['failure_reason']] += 1
                payment_method_types[customer_details['payment_method']] += 1
                
                # Store details
                all_delinquent_details.append(customer_details)
            
            has_more = customers.has_more
            if has_more:
                starting_after = customers.data[-1].id
                
        except Exception as e:
            print(f"  Error: {str(e)}")
            has_more = False
    
    print(f"  Found {month_count} delinquent customers")

# Analyze results
print("\n" + "=" * 80)
print("FAILURE REASON ANALYSIS")
print("=" * 80)

# Sort failure reasons by frequency
sorted_reasons = sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True)
print("\nTop Failure Reasons:")
for reason, count in sorted_reasons[:10]:
    percentage = (count / len(all_delinquent_details)) * 100 if all_delinquent_details else 0
    print(f"  {reason}: {count} ({percentage:.1f}%)")

# Payment method analysis
print("\nPayment Method Types:")
sorted_methods = sorted(payment_method_types.items(), key=lambda x: x[1], reverse=True)
for method, count in sorted_methods:
    percentage = (count / len(all_delinquent_details)) * 100 if all_delinquent_details else 0
    print(f"  {method}: {count} ({percentage:.1f}%)")

# Card brand analysis
card_brands = defaultdict(int)
card_funding = defaultdict(int)
for detail in all_delinquent_details:
    if detail['card_brand'] != 'None':
        card_brands[detail['card_brand']] += 1
    if 'card_funding' in detail:
        card_funding[detail['card_funding']] += 1

print("\nCard Brands (for customers with cards):")
for brand, count in sorted(card_brands.items(), key=lambda x: x[1], reverse=True):
    print(f"  {brand}: {count}")

print("\nCard Funding Types:")
for funding, count in sorted(card_funding.items(), key=lambda x: x[1], reverse=True):
    print(f"  {funding}: {count}")

# Trial vs Direct analysis
trial_failures = [d for d in all_delinquent_details if d['is_trial']]
direct_failures = [d for d in all_delinquent_details if not d['is_trial']]

print(f"\nCustomer Type Analysis:")
print(f"  Trial customers: {len(trial_failures)} ({len(trial_failures)/len(all_delinquent_details)*100:.1f}%)")
print(f"  Direct customers: {len(direct_failures)} ({len(direct_failures)/len(all_delinquent_details)*100:.1f}%)")

# Revenue analysis by failure reason
revenue_by_reason = defaultdict(float)
for detail in all_delinquent_details:
    revenue_by_reason[detail['failure_reason']] += detail['monthly_revenue']

print("\nRevenue Lost by Failure Reason:")
sorted_revenue = sorted(revenue_by_reason.items(), key=lambda x: x[1], reverse=True)
for reason, revenue in sorted_revenue[:10]:
    if revenue > 0:
        print(f"  {reason}: ${revenue:,.2f}")

# Save detailed data
if all_delinquent_details:
    df = pd.DataFrame(all_delinquent_details)
    df.to_csv('delinquent_reasons_detailed.csv', index=False)
    print(f"\nDetailed data saved to delinquent_reasons_detailed.csv")
    
    # Create summary by failure reason
    summary_data = []
    for reason in failure_reasons.keys():
        reason_customers = [d for d in all_delinquent_details if d['failure_reason'] == reason]
        if reason_customers:
            summary_data.append({
                'failure_reason': reason,
                'count': len(reason_customers),
                'percentage': (len(reason_customers) / len(all_delinquent_details)) * 100,
                'total_revenue_lost': sum(d['monthly_revenue'] for d in reason_customers),
                'avg_revenue_per_customer': sum(d['monthly_revenue'] for d in reason_customers) / len(reason_customers),
                'trial_count': len([d for d in reason_customers if d['is_trial']]),
                'direct_count': len([d for d in reason_customers if not d['is_trial']])
            })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.sort_values('count', ascending=False)
    summary_df.to_csv('failure_reason_summary.csv', index=False)
    print("Summary by failure reason saved to failure_reason_summary.csv")

print("\n" + "=" * 80)
print(f"Total delinquent customers analyzed: {len(all_delinquent_details)}") 