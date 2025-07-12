import pandas as pd
import matplotlib.pyplot as plt

# Load the delinquent customers data
print("Loading delinquent customers data...")
delinquent_df = pd.read_csv('delinquent_reasons_detailed.csv')

# Filter for customers with no payment method
no_payment_df = delinquent_df[
    delinquent_df['failure_reason'] == 'no_payment_method'
].copy()

# Convert created date to datetime
no_payment_df['created'] = pd.to_datetime(no_payment_df['created'])

# Create month column
no_payment_df['month'] = no_payment_df['created'].dt.to_period('M')

# Group by month
monthly_stats = no_payment_df.groupby('month').agg({
    'customer_id': 'count',
    'monthly_revenue': 'sum'
}).reset_index()

monthly_stats.columns = ['month', 'count', 'lost_revenue']

# Add percentage of total
total_no_payment = len(no_payment_df)
monthly_stats['pct_of_total'] = (
    monthly_stats['count'] / total_no_payment * 100
).round(1)

# Calculate cumulative stats
monthly_stats['cumulative_count'] = monthly_stats['count'].cumsum()
monthly_stats['cumulative_revenue'] = monthly_stats['lost_revenue'].cumsum()

print("\n=== NO PAYMENT METHOD SIGNUPS BY MONTH ===\n")
print(f"Total customers without payment method: {total_no_payment}")
total_revenue_lost = no_payment_df['monthly_revenue'].sum()
print(f"Total monthly revenue lost: ${total_revenue_lost:,.2f}")
print("\nMonthly Breakdown:")
print("-" * 80)
header = f"{'Month':<12} {'Count':>8} {'% of Total':>12} "
header += f"{'Lost Revenue':>15} {'Cumulative':>15}"
print(header)
print("-" * 80)

for _, row in monthly_stats.iterrows():
    line = f"{str(row['month']):<12} {row['count']:>8} "
    line += f"{row['pct_of_total']:>11.1f}% "
    line += f"${row['lost_revenue']:>14,.2f} "
    line += f"{row['cumulative_count']:>15}"
    print(line)

# Create visualizations
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# 1. Bar chart of count by month
months = [str(m) for m in monthly_stats['month']]
ax1.bar(months, monthly_stats['count'], color='#ff6b6b', alpha=0.8)
ax1.set_title('No Payment Method Signups by Month', 
              fontsize=14, fontweight='bold')
ax1.set_xlabel('Month')
ax1.set_ylabel('Number of Customers')
ax1.grid(axis='y', alpha=0.3)

# Add value labels
for i, v in enumerate(monthly_stats['count']):
    ax1.text(i, v + 1, str(v), ha='center', va='bottom')

# 2. Line chart showing trend
ax2.plot(months, monthly_stats['count'], marker='o', 
         linewidth=3, markersize=10, color='#ff6b6b')
ax2.fill_between(range(len(months)), monthly_stats['count'], 
                 alpha=0.3, color='#ff6b6b')
ax2.set_title('Trend of No Payment Method Signups', 
              fontsize=14, fontweight='bold')
ax2.set_xlabel('Month')
ax2.set_ylabel('Number of Customers')
ax2.grid(True, alpha=0.3)

# 3. Revenue impact by month
ax3.bar(months, monthly_stats['lost_revenue'], color='#845EC2', alpha=0.8)
ax3.set_title('Monthly Revenue Lost from No Payment Method', 
              fontsize=14, fontweight='bold')
ax3.set_xlabel('Month')
ax3.set_ylabel('Lost Revenue ($)')
ax3.grid(axis='y', alpha=0.3)

# Add value labels
for i, v in enumerate(monthly_stats['lost_revenue']):
    ax3.text(i, v + 100, f'${v:,.0f}', ha='center', 
             va='bottom', fontsize=9)

# 4. Cumulative impact
ax4_twin = ax4.twinx()
ax4.bar(months, monthly_stats['cumulative_count'], alpha=0.5, 
        color='#ff6b6b', label='Cumulative Count')
ax4_twin.plot(months, monthly_stats['cumulative_revenue'], color='#845EC2', 
              marker='o', linewidth=3, markersize=8, 
              label='Cumulative Revenue Lost')

ax4.set_title('Cumulative Impact of No Payment Method Signups', 
              fontsize=14, fontweight='bold')
ax4.set_xlabel('Month')
ax4.set_ylabel('Cumulative Customer Count', color='#ff6b6b')
ax4_twin.set_ylabel('Cumulative Revenue Lost ($)', color='#845EC2')
ax4.tick_params(axis='y', labelcolor='#ff6b6b')
ax4_twin.tick_params(axis='y', labelcolor='#845EC2')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('no_payment_method_by_month.png', dpi=300, bbox_inches='tight')
print("\nVisualization saved as 'no_payment_method_by_month.png'")

# Additional analysis - growth rate
print("\n=== MONTH-OVER-MONTH GROWTH ===")
print("-" * 50)
for i in range(1, len(monthly_stats)):
    prev_count = monthly_stats.iloc[i-1]['count']
    curr_count = monthly_stats.iloc[i]['count']
    if prev_count > 0:
        growth_rate = (curr_count - prev_count) / prev_count * 100
    else:
        growth_rate = 0
    sign = '+' if growth_rate >= 0 else ''
    prev_month = monthly_stats.iloc[i-1]['month']
    curr_month = monthly_stats.iloc[i]['month']
    print(f"{prev_month} → {curr_month}: "
          f"{sign}{growth_rate:.1f}% "
          f"({prev_count} → {curr_count})")

# Peak analysis
peak_month = monthly_stats.loc[monthly_stats['count'].idxmax()]
print(f"\nPeak Month: {peak_month['month']} with "
      f"{peak_month['count']} no payment signups")
print(f"Peak Revenue Loss: ${peak_month['lost_revenue']:,.2f}")

# Average stats
avg_monthly_count = monthly_stats['count'].mean()
avg_monthly_revenue = monthly_stats['lost_revenue'].mean()
print("\nAverage per month:")
print(f"  - Customers without payment: {avg_monthly_count:.1f}")
print(f"  - Revenue lost: ${avg_monthly_revenue:,.2f}")

print("\n✅ Analysis complete!") 