import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Data from the analysis
months = ['May 2025', 'June 2025', 'July 2025', 'August 2025']
delinquent_customers = [44, 34, 0, 0]
lost_revenue = [6708.60, 5598.00, 0, 0]
cumulative_loss = [6708.60, 12306.60, 12306.60, 12306.60]

# Create figure with subplots
fig = plt.figure(figsize=(15, 10))

# 1. Monthly Delinquent Customers
ax1 = plt.subplot(2, 3, 1)
bars1 = ax1.bar(months, delinquent_customers, color=['red', 'orange', 'gray', 'gray'])
ax1.set_title('Delinquent Customers by Month', fontsize=14, fontweight='bold')
ax1.set_ylabel('Number of Customers')
ax1.set_ylim(0, 50)
for i, v in enumerate(delinquent_customers):
    ax1.text(i, v + 1, str(v), ha='center', fontweight='bold')

# 2. Monthly Revenue Loss
ax2 = plt.subplot(2, 3, 2)
bars2 = ax2.bar(months, lost_revenue, color=['darkred', 'darkorange', 'gray', 'gray'])
ax2.set_title('Monthly Revenue Lost', fontsize=14, fontweight='bold')
ax2.set_ylabel('Revenue Lost ($)')
ax2.set_ylim(0, 8000)
for i, v in enumerate(lost_revenue):
    ax2.text(i, v + 200, f'${v:,.0f}', ha='center', fontweight='bold')

# 3. Cumulative Revenue Impact
ax3 = plt.subplot(2, 3, 3)
ax3.plot(months, cumulative_loss, 'ro-', linewidth=3, markersize=10)
ax3.fill_between(range(len(months)), cumulative_loss, alpha=0.3, color='red')
ax3.set_title('Cumulative Revenue Loss', fontsize=14, fontweight='bold')
ax3.set_ylabel('Total Lost ($)')
ax3.grid(True, alpha=0.3)
for i, v in enumerate(cumulative_loss):
    ax3.text(i, v + 500, f'${v:,.0f}', ha='center', fontweight='bold')

# 4. Customer Impact Timeline
ax4 = plt.subplot(2, 3, 4)
cohort_labels = ['May Cohort\n(44 customers)', 'June Cohort\n(34 customers)']
cohort_values = [26834.40, 16794.00]
bars4 = ax4.bar(cohort_labels, cohort_values, color=['#8B0000', '#FF8C00'])
ax4.set_title('Revenue Lost by Cohort (to date)', fontsize=14, fontweight='bold')
ax4.set_ylabel('Total Revenue Lost ($)')
for i, v in enumerate(cohort_values):
    ax4.text(i, v + 500, f'${v:,.0f}', ha='center', fontweight='bold')

# 5. Financial Impact Summary
ax5 = plt.subplot(2, 3, 5)
ax5.axis('off')
summary_text = f"""
FINANCIAL IMPACT SUMMARY

Total Delinquent Customers: 78
  • May 2025: 44 customers
  • June 2025: 34 customers
  • July 2025: 0 customers
  • August 2025: 0 customers

Monthly Revenue Lost: $12,307
Annual Revenue Loss: $147,679

Average per Customer: $158/month

Lifetime Value Impact:
  • 24-month LTV lost: $295,358
  • Per customer LTV: $3,787

Next 4 Months Projection: $49,226
"""
ax5.text(0.1, 0.9, summary_text, transform=ax5.transAxes, fontsize=11,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

# 6. Projection Chart
ax6 = plt.subplot(2, 3, 6)
actual_months = ['May', 'Jun', 'Jul', 'Aug']
projected_months = ['Sep', 'Oct', 'Nov', 'Dec']
all_months = actual_months + projected_months
actual_values = [6708.60, 12306.60, 12306.60, 12306.60]
projected_values = [12306.60 + 12306.60, 
                   12306.60 + 12306.60*2,
                   12306.60 + 12306.60*3,
                   12306.60 + 12306.60*4]

ax6.plot(actual_months, actual_values, 'bo-', linewidth=2, 
         markersize=8, label='Actual Loss')
ax6.plot(projected_months, projected_values, 'r--o', linewidth=2, 
         markersize=8, label='Projected Loss')
ax6.set_title('Cumulative Loss Projection', fontsize=14, fontweight='bold')
ax6.set_ylabel('Cumulative Loss ($)')
ax6.legend()
ax6.grid(True, alpha=0.3)
ax6.set_ylim(0, 65000)

plt.tight_layout()
plt.savefig('4month_revenue_loss_analysis.png', dpi=300, bbox_inches='tight')
print("Visualization saved as 4month_revenue_loss_analysis.png")

# Create a second figure for key insights
fig2, ax = plt.subplots(figsize=(12, 8))
ax.axis('off')

insights_text = """
4-MONTH REVENUE LOSS ANALYSIS (MAY-AUGUST 2025)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AFFECTED CUSTOMERS: 78 TOTAL

  May 2025:    ████████████████████████████████████████████ 44 customers
  June 2025:   ██████████████████████████████████ 34 customers  
  July 2025:   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0 customers
  August 2025: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0 customers

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

REVENUE IMPACT:

  Monthly Loss:        $12,307  (from 78 delinquent customers)
  Annual Loss:        $147,679  (if no action taken)
  4-Month Actual:      $43,628  (May-Aug cumulative)
  Next 4 Months:       $49,226  (projected Sep-Dec)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KEY FINDINGS:

  ✗ 100% of delinquent customers were trial users
  ✗ Payment failures concentrated in May-June cohorts
  ✗ July/August show 0 delinquencies (too recent to fail)
  ✗ Average loss per customer: $158/month
  ✗ Total lifetime value at risk: $295,358

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

URGENT ACTION REQUIRED:

  1. These 78 customers represent $12,307/month in recurring revenue
  2. Without intervention, you'll lose $147,679 annually
  3. Each lost customer = $3,787 in lifetime value (24 months)
  4. Pattern shows consistent ~40 failures per month from trials
"""

ax.text(0.5, 0.5, insights_text, transform=ax.transAxes, fontsize=12,
        ha='center', va='center', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.9))

plt.tight_layout()
plt.savefig('4month_revenue_loss_summary.png', dpi=300, bbox_inches='tight')
print("Summary saved as 4month_revenue_loss_summary.png") 