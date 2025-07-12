import stripe
import pandas as pd
from datetime import datetime, timedelta
import json

# Set your Stripe API key
stripe.api_key = "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"

print("=== STRIPE TRIAL ANALYSIS - PULLING LIVE DATA ===\n")

# Get subscriptions with trials
print("Fetching subscription data from Stripe...")

all_subscriptions = []
has_more = True
starting_after = None

# Fetch all subscriptions (including canceled ones)
while has_more:
    if starting_after:
        subscriptions = stripe.Subscription.list(
            limit=100,
            starting_after=starting_after,
            status='all'  # Get all statuses
        )
    else:
        subscriptions = stripe.Subscription.list(
            limit=100,
            status='all'
        )
    
    all_subscriptions.extend(subscriptions.data)
    has_more = subscriptions.has_more
    if has_more:
        starting_after = subscriptions.data[-1].id

print(f"Total subscriptions fetched: {len(all_subscriptions)}")

# Analyze trial subscriptions
trial_subs = []
direct_subs = []

for sub in all_subscriptions:
    sub_data = {
        'id': sub.id,
        'customer_id': sub.customer,
        'status': sub.status,
        'created': datetime.fromtimestamp(sub.created),
        'trial_start': datetime.fromtimestamp(sub.trial_start) if sub.trial_start else None,
        'trial_end': datetime.fromtimestamp(sub.trial_end) if sub.trial_end else None,
        'current_period_start': datetime.fromtimestamp(sub.current_period_start),
        'current_period_end': datetime.fromtimestamp(sub.current_period_end),
        'plan_id': sub.items.data[0].price.id if sub.items.data else None,
        'amount': sub.items.data[0].price.unit_amount / 100 if sub.items.data else 0,
        'currency': sub.currency,
        'cancel_at_period_end': sub.cancel_at_period_end,
        'canceled_at': datetime.fromtimestamp(sub.canceled_at) if sub.canceled_at else None
    }
    
    # Check if this subscription had a trial
    if sub.trial_start:
        trial_subs.append(sub_data)
    else:
        direct_subs.append(sub_data)

print(f"\nSubscriptions with trials: {len(trial_subs)}")
print(f"Direct subscriptions (no trial): {len(direct_subs)}")

# Convert to DataFrames for analysis
trial_df = pd.DataFrame(trial_subs)
direct_df = pd.DataFrame(direct_subs)

# Analyze trial conversions
if len(trial_df) > 0:
    print("\n=== TRIAL SUBSCRIPTION ANALYSIS ===")
    
    # Status breakdown
    print("\nTrial subscription status breakdown:")
    trial_status = trial_df['status'].value_counts()
    for status, count in trial_status.items():
        pct = count / len(trial_df) * 100
        print(f"  {status}: {count} ({pct:.1f}%)")
    
    # Calculate conversion rates
    active_trials = len(trial_df[trial_df['status'].isin(['active', 'trialing'])])
    failed_trials = len(trial_df[trial_df['status'].isin(['canceled', 'incomplete', 'past_due', 'unpaid'])])
    
    print(f"\nTrial outcomes:")
    print(f"  Successful/Active: {active_trials} ({active_trials/len(trial_df)*100:.1f}%)")
    print(f"  Failed/Canceled: {failed_trials} ({failed_trials/len(trial_df)*100:.1f}%)")
    
    # Trial length analysis
    completed_trials = trial_df[trial_df['trial_end'].notna()]
    if len(completed_trials) > 0:
        completed_trials['trial_length_days'] = (completed_trials['trial_end'] - completed_trials['trial_start']).dt.days
        avg_trial_length = completed_trials['trial_length_days'].mean()
        print(f"\nAverage trial length: {avg_trial_length:.1f} days")

# Analyze direct subscriptions
if len(direct_df) > 0:
    print("\n=== DIRECT SUBSCRIPTION ANALYSIS ===")
    
    print("\nDirect subscription status breakdown:")
    direct_status = direct_df['status'].value_counts()
    for status, count in direct_status.items():
        pct = count / len(direct_df) * 100
        print(f"  {status}: {count} ({pct:.1f}%)")
    
    active_direct = len(direct_df[direct_df['status'] == 'active'])
    failed_direct = len(direct_df[direct_df['status'].isin(['canceled', 'incomplete', 'past_due', 'unpaid'])])
    
    print(f"\nDirect subscription outcomes:")
    print(f"  Successful/Active: {active_direct} ({active_direct/len(direct_df)*100:.1f}%)")
    print(f"  Failed/Canceled: {failed_direct} ({failed_direct/len(direct_df)*100:.1f}%)")

# Now let's look at recent customer payment failures
print("\n\n=== RECENT PAYMENT FAILURES (Last 30 days) ===")

# Get charges from the last 30 days
thirty_days_ago = int((datetime.now() - timedelta(days=30)).timestamp())
failed_charges = stripe.Charge.list(
    limit=100,
    created={'gte': thirty_days_ago},
    status='failed'
)

print(f"\nTotal failed charges in last 30 days: {len(failed_charges.data)}")

# Analyze failure reasons
failure_reasons = {}
for charge in failed_charges.data:
    reason = charge.failure_code or 'unknown'
    failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

print("\nTop failure reasons:")
for reason, count in sorted(failure_reasons.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"  {reason}: {count}")

# Get customer details for recent signups with trials
print("\n\n=== MAY 2025 TRIAL CUSTOMER DETAILS ===")

may_start = int(datetime(2025, 5, 1).timestamp())
may_end = int(datetime(2025, 5, 31, 23, 59, 59).timestamp())

may_trial_subs = [s for s in trial_subs if may_start <= s['created'].timestamp() <= may_end]
print(f"\nTrial subscriptions created in May 2025: {len(may_trial_subs)}")

if may_trial_subs:
    may_trial_df = pd.DataFrame(may_trial_subs)
    
    # Status breakdown for May trials
    print("\nMay trial subscription statuses:")
    may_status = may_trial_df['status'].value_counts()
    for status, count in may_status.items():
        pct = count / len(may_trial_df) * 100
        print(f"  {status}: {count} ({pct:.1f}%)")
    
    # Calculate May trial failure rate
    may_failed = len(may_trial_df[may_trial_df['status'].isin(['canceled', 'incomplete', 'past_due', 'unpaid'])])
    may_success = len(may_trial_df[may_trial_df['status'].isin(['active', 'trialing'])])
    
    print(f"\nMay trial outcomes:")
    print(f"  Failed/Canceled: {may_failed} ({may_failed/len(may_trial_df)*100:.1f}%)")
    print(f"  Active/Trialing: {may_success} ({may_success/len(may_trial_df)*100:.1f}%)")

# Save detailed data
if trial_subs:
    trial_df.to_csv('stripe_trial_subscriptions.csv', index=False)
    print("\n\nDetailed trial subscription data saved to 'stripe_trial_subscriptions.csv'")

print("\n=== SUMMARY ===")
if len(trial_df) > 0 and len(direct_df) > 0:
    trial_fail_rate = len(trial_df[trial_df['status'].isin(['canceled', 'incomplete', 'past_due', 'unpaid'])]) / len(trial_df) * 100
    direct_fail_rate = len(direct_df[direct_df['status'].isin(['canceled', 'incomplete', 'past_due', 'unpaid'])]) / len(direct_df) * 100
    
    print(f"\nOverall failure rates:")
    print(f"  Trial subscriptions: {trial_fail_rate:.1f}%")
    print(f"  Direct subscriptions: {direct_fail_rate:.1f}%")
    
    if trial_fail_rate > 0 and direct_fail_rate > 0:
        ratio = trial_fail_rate / direct_fail_rate
        print(f"\n💡 Trial subscriptions are {ratio:.1f}x more likely to fail than direct subscriptions!") 