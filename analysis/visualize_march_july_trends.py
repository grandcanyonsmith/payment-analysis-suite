import matplotlib.pyplot as plt
import numpy as np

# Data from the analysis
months = ['March', 'April', 'May', 'June', 'July']
new_customers = [394, 357, 362, 482, 228]
trial_customers = [186, 182, 187, 357, 211]
delinquent_total = [92, 72, 68, 37, 0]
trial_delinquent = [64, 52, 44, 34, 0]
direct_delinquent = [28, 20, 24, 3, 0]
lost_revenue = [12635.00, 7933.10, 6708.60, 5598.00, 0]

# Create figure with subplots
fig = plt.figure(figsize=(16, 12))

# 1. Customer Acquisition Trends
ax1 = plt.subplot(3, 3, 1)
x = np.arange(len(months))
width = 0.35
bars1 = ax1.bar(x - width/2, new_customers, width, label='Total New', color='lightblue')
bars2 = ax1.bar(x + width/2, trial_customers, width, label='Trials', color='orange')
ax1.set_title('Customer Acquisition by Month', fontsize=14, fontweight='bold')
ax1.set_ylabel('Number of Customers')
ax1.set_xticks(x)
ax1.set_xticklabels(months)
ax1.legend()

# 2. Delinquent Customers Breakdown
ax2 = plt.subplot(3, 3, 2)
width = 0.35
bars3 = ax2.bar(x - width/2, trial_delinquent, width, label='Trial', color='red')
bars4 = ax2.bar(x + width/2, direct_delinquent, width, label='Direct', color='darkred')
ax2.set_title('Delinquent Customers by Type', fontsize=14, fontweight='bold')
ax2.set_ylabel('Number of Delinquent')
ax2.set_xticks(x)
ax2.set_xticklabels(months)
ax2.legend()

# 3. Revenue Loss Trend
ax3 = plt.subplot(3, 3, 3)
ax3.plot(months, lost_revenue, 'bo-', linewidth=3, markersize=10)
ax3.fill_between(range(len(months)), lost_revenue, alpha=0.3, color='blue')
ax3.set_title('Monthly Revenue Loss Trend', fontsize=14, fontweight='bold')
ax3.set_ylabel('Revenue Lost ($)')
ax3.grid(True, alpha=0.3)
for i, v in enumerate(lost_revenue):
    ax3.text(i, v + 300, f'${v:,.0f}', ha='center', fontsize=9)

# 4. Failure Rate Trends
ax4 = plt.subplot(3, 3, 4)
overall_failure_rates = [(d/n)*100 if n > 0 else 0 for d, n in zip(delinquent_total, new_customers)]
trial_failure_rates = [0, 28.0, 24.2, 18.2, 0]  # From the analysis output
ax4.plot(months, overall_failure_rates, 'ro-', linewidth=2, markersize=8, label='Overall')
ax4.plot(months, trial_failure_rates, 'go-', linewidth=2, markersize=8, label='Trial')
ax4.set_title('Failure Rate Trends', fontsize=14, fontweight='bold')
ax4.set_ylabel('Failure Rate (%)')
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.set_ylim(0, 30)

# 5. Cumulative Revenue Impact
ax5 = plt.subplot(3, 3, 5)
cumulative_revenue = []
cumulative_sum = 0
for i, rev in enumerate(lost_revenue):
    # Each month's loss continues for remaining months
    months_remaining = len(months) - i
    cumulative_sum += rev * months_remaining
    cumulative_revenue.append(cumulative_sum)

ax5.bar(months, cumulative_revenue, color=['darkred' if i < 2 else 'orange' for i in range(len(months))])
ax5.set_title('Cumulative Revenue Impact', fontsize=14, fontweight='bold')
ax5.set_ylabel('Total Revenue Lost ($)')
for i, v in enumerate(cumulative_revenue):
    ax5.text(i, v + 1000, f'${v:,.0f}', ha='center', fontsize=9, fontweight='bold')

# 6. Trial vs Direct Split
ax6 = plt.subplot(3, 3, 6)
labels = ['Trial\n(194 customers)', 'Direct\n(75 customers)']
sizes = [194, 75]
colors = ['#ff9999', '#66b3ff']
explode = (0.05, 0.05)
ax6.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax6.set_title('5-Month Delinquent Split', fontsize=14, fontweight='bold')

# 7. Monthly Summary Table
ax7 = plt.subplot(3, 3, 7)
ax7.axis('off')
summary_text = """
MARCH-JULY 2025 SUMMARY

Total Customers: 1,823
Trial Customers: 1,123 (61.6%)
Total Delinquent: 269

Revenue Impact:
• Monthly Loss: $32,875
• Annual Loss: $394,496
• Cumulative: $126,229

Key Patterns:
• March had highest failures (92)
• Declining trend over time
• June spike in signups (482)
• July: Too recent to fail
"""
ax7.text(0.1, 0.9, summary_text, transform=ax7.transAxes, fontsize=11,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# 8. Trial Performance
ax8 = plt.subplot(3, 3, 8)
trial_conversion_rate = [(t-td)/t*100 if t > 0 else 100 for t, td in zip(trial_customers, trial_delinquent)]
ax8.bar(months, trial_conversion_rate, color=['green' if r > 80 else 'orange' if r > 70 else 'red' for r in trial_conversion_rate])
ax8.set_title('Trial Success Rate', fontsize=14, fontweight='bold')
ax8.set_ylabel('Conversion Rate (%)')
ax8.set_ylim(0, 110)
ax8.axhline(y=80, color='green', linestyle='--', alpha=0.5, label='Target 80%')
for i, v in enumerate(trial_conversion_rate):
    ax8.text(i, v + 2, f'{v:.1f}%', ha='center', fontsize=9)

# 9. Key Insights
ax9 = plt.subplot(3, 3, 9)
ax9.axis('off')
insights_text = """
KEY FINDINGS:

1. DECLINING FAILURE TREND
   March: 92 → July: 0
   Shows improvement

2. TRIAL FAILURE RATES
   • April: 28.0%
   • May: 24.2%
   • June: 18.2%
   Steady improvement

3. REVENUE LOSS PATTERN
   March: $12,635 (highest)
   June: $5,598 (lowest active)
   
4. CUSTOMER TYPE SHIFT
   Direct failures dropped:
   March: 28 → June: 3

5. $126,229 TOTAL LOST
   Over 5 months
"""
ax9.text(0.1, 0.9, insights_text, transform=ax9.transAxes, fontsize=10,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

plt.tight_layout()
plt.savefig('march_july_trends_analysis.png', dpi=300, bbox_inches='tight')
print("Visualization saved as march_july_trends_analysis.png")

# Create a second detailed view
fig2, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
fig2.suptitle('March-July 2025: Detailed Revenue Loss Analysis', fontsize=16, fontweight='bold')

# 1. Stacked area chart of customer types
ax1.fill_between(range(len(months)), [0]*5, trial_delinquent, 
                 color='red', alpha=0.7, label='Trial Delinquent')
ax1.fill_between(range(len(months)), trial_delinquent, delinquent_total, 
                 color='darkred', alpha=0.7, label='Direct Delinquent')
ax1.set_xticks(range(len(months)))
ax1.set_xticklabels(months)
ax1.set_ylabel('Delinquent Customers')
ax1.set_title('Delinquent Customer Composition')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. Revenue per delinquent
revenue_per_delinquent = [r/d if d > 0 else 0 for r, d in zip(lost_revenue, delinquent_total)]
ax2.bar(months, revenue_per_delinquent, color=['purple' if v > 100 else 'orange' for v in revenue_per_delinquent])
ax2.set_title('Average Revenue per Delinquent Customer')
ax2.set_ylabel('Revenue per Customer ($)')
for i, v in enumerate(revenue_per_delinquent):
    ax2.text(i, v + 5, f'${v:.0f}', ha='center', fontweight='bold')

# 3. Trial vs Total customer ratio
trial_percentage = [(t/n)*100 if n > 0 else 0 for t, n in zip(trial_customers, new_customers)]
ax3.plot(months, trial_percentage, 'go-', linewidth=3, markersize=10)
ax3.set_title('Trial Customer Percentage of New Signups')
ax3.set_ylabel('Trial Percentage (%)')
ax3.set_ylim(0, 100)
ax3.grid(True, alpha=0.3)
for i, v in enumerate(trial_percentage):
    ax3.text(i, v + 2, f'{v:.1f}%', ha='center', fontsize=9)

# 4. Financial impact summary
ax4.axis('off')
impact_text = f"""
FINANCIAL IMPACT BREAKDOWN

March 2025:
  Customers lost: 92 (64 trial, 28 direct)
  Revenue lost: $12,635/month
  5-month impact: $63,175

April 2025:
  Customers lost: 72 (52 trial, 20 direct)
  Revenue lost: $7,933/month
  4-month impact: $31,732

May 2025:
  Customers lost: 68 (44 trial, 24 direct)
  Revenue lost: $6,709/month
  3-month impact: $20,127

June 2025:
  Customers lost: 37 (34 trial, 3 direct)
  Revenue lost: $5,598/month
  2-month impact: $11,196

July 2025:
  Too recent for failures

TOTAL CUMULATIVE LOSS: $126,229
PROJECTED ANNUAL LOSS: $394,496

Average per delinquent: $122.21
Trial average: $169.41
Direct average: $0.13 (mostly $0)
"""
ax4.text(0.05, 0.95, impact_text, transform=ax4.transAxes, fontsize=10,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))

plt.tight_layout()
plt.savefig('march_july_detailed_analysis.png', dpi=300, bbox_inches='tight')
print("Detailed analysis saved as march_july_detailed_analysis.png") 