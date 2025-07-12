import matplotlib.pyplot as plt
import numpy as np

# Data from our analysis
months = ['May', 'June', 'July']
total_customers = [190, 482, 227]
trial_percentages = [98.9, 74.1, 92.5]
direct_percentages = [1.1, 25.9, 7.5]
trial_delinquency = [22.9, 9.5, 0.0]
direct_delinquency = [0.0, 2.4, 0.0]
avg_trial_revenue = [316.00, 50.50, 3.06]
avg_direct_revenue = [757.00, 7.30, 4.75]
lost_revenue = [9688, 1898, 0]

# Create figure with subplots
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Stripe Customer Analysis: May-July 2025 Trends', fontsize=16, fontweight='bold')

# 1. Customer Acquisition Trends
ax1.bar(months, total_customers, color='lightblue', edgecolor='navy')
ax1.set_ylabel('Total Customers')
ax1.set_title('Customer Acquisition by Month')
for i, v in enumerate(total_customers):
    ax1.text(i, v + 10, str(v), ha='center', fontweight='bold')

# 2. Trial vs Direct Signup Percentages
x = np.arange(len(months))
width = 0.35
ax2.bar(x - width/2, trial_percentages, width, label='Trial %', color='coral')
ax2.bar(x + width/2, direct_percentages, width, label='Direct %', color='lightgreen')
ax2.set_ylabel('Percentage')
ax2.set_title('Customer Type Distribution')
ax2.set_xticks(x)
ax2.set_xticklabels(months)
ax2.legend()
ax2.set_ylim(0, 110)
for i, (t, d) in enumerate(zip(trial_percentages, direct_percentages)):
    ax2.text(i - width/2, t + 2, f'{t:.1f}%', ha='center', fontsize=9)
    ax2.text(i + width/2, d + 2, f'{d:.1f}%', ha='center', fontsize=9)

# 3. Delinquency Rates
x = np.arange(len(months))
ax3.plot(x, trial_delinquency, 'o-', color='red', linewidth=2, 
         markersize=8, label='Trial Delinquency')
ax3.plot(x, direct_delinquency, 's-', color='green', linewidth=2, 
         markersize=8, label='Direct Delinquency')
ax3.set_ylabel('Delinquency Rate (%)')
ax3.set_title('Payment Failure Rates by Customer Type')
ax3.set_xticks(x)
ax3.set_xticklabels(months)
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.set_ylim(-1, 25)
for i, (t, d) in enumerate(zip(trial_delinquency, direct_delinquency)):
    ax3.text(i, t + 1, f'{t:.1f}%', ha='center', fontsize=9)
    if d > 0:
        ax3.text(i, d + 1, f'{d:.1f}%', ha='center', fontsize=9)

# 4. Average Revenue per Customer
x = np.arange(len(months))
width = 0.35
ax4.bar(x - width/2, avg_trial_revenue, width, label='Trial Revenue', color='purple')
ax4.bar(x + width/2, avg_direct_revenue, width, label='Direct Revenue', color='orange')
ax4.set_ylabel('Average Monthly Revenue ($)')
ax4.set_title('Revenue per Customer by Type')
ax4.set_xticks(x)
ax4.set_xticklabels(months)
ax4.legend()
ax4.set_ylim(0, 800)
for i, (t, d) in enumerate(zip(avg_trial_revenue, avg_direct_revenue)):
    ax4.text(i - width/2, t + 20, f'${t:.0f}', ha='center', fontsize=9)
    ax4.text(i + width/2, d + 20, f'${d:.0f}', ha='center', fontsize=9)

plt.tight_layout()
plt.savefig('june_july_trends.png', dpi=300, bbox_inches='tight')
print("Visualization saved as june_july_trends.png")

# Additional summary statistics
fig2, ax = plt.subplots(1, 1, figsize=(10, 6))
ax.axis('off')

summary_text = f"""
KEY FINDINGS - MAY TO JULY 2025 TRENDS:

1. CUSTOMER ACQUISITION:
   • June saw massive growth: 482 customers (2.5x May)
   • July dropped to 227 customers (53% decrease from June)
   • Total Q2/Q3 customers: 899

2. TRIAL VS DIRECT SIGNUP TRENDS:
   • May: 98.9% trials (almost exclusively trials)
   • June: 74.1% trials (significant increase in direct signups)
   • July: 92.5% trials (reverted to mostly trials)

3. PAYMENT FAILURE RATES:
   • Trial delinquency improving: 22.9% → 9.5% → 0%
   • Direct signups remain reliable: 0% → 2.4% → 0%
   • July had ZERO delinquencies (possibly too recent)

4. REVENUE PER CUSTOMER:
   • May trials: $316/month average
   • June trials: $50.50/month (84% decrease)
   • July trials: $3.06/month (94% decrease from June)
   
   • Direct signups volatile: $757 → $7.30 → $4.75
   • Direct signup quality degraded significantly

5. FINANCIAL IMPACT:
   • Total revenue lost (May-July): $11,586/month
   • Projected annual loss: $46,342
   • June direct signups only brought in $7.30/customer vs $757 in May

CRITICAL INSIGHTS:
• June's surge in direct signups (125 vs 2 in May) brought low-quality customers
• Average revenue per customer collapsed across both segments
• July's 0% delinquency may be misleading (too recent to fail)
• Business appears to be attracting lower-value customers over time
"""

ax.text(0.05, 0.95, summary_text, transform=ax.transAxes, fontsize=11,
        verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('june_july_summary.png', dpi=300, bbox_inches='tight')
print("Summary saved as june_july_summary.png") 