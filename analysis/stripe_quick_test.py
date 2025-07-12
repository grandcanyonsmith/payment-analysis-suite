import stripe
from datetime import datetime, timedelta

# Set API key
stripe.api_key = "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"

print("Testing Stripe API connection...\n")

try:
    # Get recent customers (last 10)
    customers = stripe.Customer.list(limit=10)
    print(f"✓ API Connected! Found {len(customers.data)} recent customers")
    
    # Check for trial subscriptions
    trial_count = 0
    direct_count = 0
    
    for customer in customers.data:
        subs = stripe.Subscription.list(customer=customer.id, limit=5)
        for sub in subs.data:
            if sub.trial_start:
                trial_count += 1
                print(f"\nTrial subscription found:")
                print(f"  Customer: {customer.email}")
                print(f"  Status: {sub.status}")
                print(f"  Trial end: {datetime.fromtimestamp(sub.trial_end) if sub.trial_end else 'N/A'}")
                break
            else:
                direct_count += 1
                break
    
    print(f"\nQuick summary of last 10 customers:")
    print(f"  - Subscriptions with trials: {trial_count}")
    print(f"  - Direct subscriptions: {direct_count}")
    
    # Get a sample of May 2025 data
    may_start = int(datetime(2025, 5, 1).timestamp())
    may_end = int(datetime(2025, 5, 31).timestamp())
    
    print(f"\nChecking for May 2025 customers...")
    may_customers = stripe.Customer.list(
        limit=5,
        created={'gte': may_start, 'lte': may_end}
    )
    
    print(f"Found {len(may_customers.data)} May customers (showing first 5)")
    
    for customer in may_customers.data:
        print(f"\n- {customer.email or 'No email'}")
        print(f"  Created: {datetime.fromtimestamp(customer.created)}")
        print(f"  Delinquent: {customer.delinquent}")
        
except stripe.error.AuthenticationError:
    print("❌ Authentication failed! Check your API key.")
except Exception as e:
    print(f"❌ Error: {str(e)}") 