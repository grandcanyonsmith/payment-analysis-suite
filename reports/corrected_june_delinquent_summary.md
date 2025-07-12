# June 2025 Delinquent Accounts - Corrected Analysis

## Key Correction
The trial periods are **30 days** as expected, not 2 months. The confusion arose from misreading the billing period dates.

## Accurate Timeline for Delinquent Accounts

Using jonas.man69@gmail.com as an example:
- **Sign up**: June 11, 2025
- **Trial period**: 30 days (June 11 → July 11)
- **Trial ends**: July 11, 2025
- **First payment attempt**: July 11, 2025 (FAILED)
- **Status**: Past due since July 11

## Summary of 37 Delinquent Accounts

### Breakdown
- **34 Trial customers** (91.9%)
  - All had 30-day trials (92.5% of June trials were 30 days)
  - All failed their first payment when trial ended
  - 4 at $297/month tier
  - 30 at $147/month tier

- **3 Direct signups** (8.1%)
  - Never had active subscriptions ($0 revenue)
  - Likely abandoned signups or invalid payment methods

### Financial Impact
- **Monthly revenue lost**: $5,598
- **Average per delinquent trial customer**: $164.65

### Pattern Analysis
All trial delinquent customers follow the same pattern:
1. Sign up in early June with 30-day trial
2. No valid payment method captured
3. Trial ends 30 days later
4. First payment attempt fails immediately
5. Account becomes past_due

### Root Causes
- Invalid or missing payment methods at signup
- Possible use of prepaid/virtual cards
- No payment method validation during trial signup

## Exceptions Found
While 92.5% had standard 30-day trials, some outliers exist:
- 10 customers with trials >30 days (including 90-day and 91-day trials)
- 4 customers with 0-day trials
- Various shorter trials (14, 21, 29 days)

These exceptions suggest inconsistent trial period configuration or special promotional offers. 