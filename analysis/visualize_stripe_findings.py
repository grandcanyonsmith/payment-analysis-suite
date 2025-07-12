import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Create figure with multiple subplots
fig = plt.figure(figsize=(15, 10))

# Define colors
trial_color = '#e74c3c'
direct_color = '#27ae60'
no_sub_color = '#95a5a6'
delinquent_color = '#c0392b'
active_color = '#2ecc71'

# 1. Customer Type Pie Chart
ax1 = plt.subplot(2, 3, 1)
sizes = [188, 2, 170]
labels = ['Free Trials\n188 (98.9%)', 'Direct Signups\n2 (1.1%)', 'No Subscription\n170']
colors = [trial_color, direct_color, no_sub_color]
explode = (0.1, 0.3, 0)  # Explode the tiny direct slice

wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=colors, 
                                    autopct='', startangle=90, explode=explode)
ax1.set_title('May 2025: Customer Subscription Types', fontsize=14, fontweight='bold')

# Add arrow pointing to tiny direct slice
ax1.annotate('Only 2 direct\nsignups!', xy=(0.8, 0.3), xytext=(1.2, 0.5),
            arrowprops=dict(arrowstyle='->', color='red', lw=2),
            fontsize=12, fontweight='bold', color='red')

# 2. Delinquency Comparison
ax2 = plt.subplot(2, 3, 2)
categories = ['Free Trials', 'Direct Signups']
delinquency_rates = [22.9, 0]
bars = ax2.bar(categories, delinquency_rates, color=[trial_color, direct_color], alpha=0.8)

ax2.set_ylabel('Delinquency Rate (%)', fontsize=12)
ax2.set_title('Delinquency Rates by Type', fontsize=14, fontweight='bold')
ax2.set_ylim(0, 30)

# Add value labels
for bar, rate in zip(bars, delinquency_rates):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
             f'{rate}%', ha='center', va='bottom', fontsize=14, fontweight='bold')

# 3. Revenue per Customer
ax3 = plt.subplot(2, 3, 3)
revenue_categories = ['Free Trials', 'Direct Signups']
avg_revenue = [316.19, 757.49]
bars = ax3.bar(revenue_categories, avg_revenue, color=[trial_color, direct_color], alpha=0.8)

ax3.set_ylabel('Average Revenue per Customer ($)', fontsize=12)
ax3.set_title('Revenue Generation by Type', fontsize=14, fontweight='bold')

# Add value labels
for bar, rev in zip(bars, avg_revenue):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 10,
             f'${rev:.2f}', ha='center', va='bottom', fontsize=12, fontweight='bold')

# Add comparison text
ax3.text(0.5, 0.85, '2.4x more\nrevenue!', ha='center', transform=ax3.transAxes,
         fontsize=12, fontweight='bold', color='green',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.5))

# 4. Trial Status Breakdown
ax4 = plt.subplot(2, 3, 4)
trial_statuses = ['Active', 'Past Due', 'Trialing']
trial_counts = [144, 43, 5]
colors_status = [active_color, delinquent_color, '#f39c12']

bars = ax4.bar(trial_statuses, trial_counts, color=colors_status, alpha=0.8)
ax4.set_ylabel('Number of Customers', fontsize=12)
ax4.set_title('Trial Customer Status Breakdown', fontsize=14, fontweight='bold')

# Add value labels
for bar, count in zip(bars, trial_counts):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + 1,
             f'{count}', ha='center', va='bottom', fontsize=12, fontweight='bold')

# 5. Recent Trend Warning
ax5 = plt.subplot(2, 3, 5)
months = ['May 2025', 'July 2025\n(Recent)']
trial_percentages = [98.9, 100]
bars = ax5.bar(months, trial_percentages, color=['#e67e22', '#c0392b'], alpha=0.8)

ax5.set_ylabel('% Customers Using Trials', fontsize=12)
ax5.set_title('Trial Usage Trend - Getting WORSE!', fontsize=14, fontweight='bold', color='red')
ax5.set_ylim(95, 101)

# Add value labels
for bar, pct in zip(bars, trial_percentages):
    height = bar.get_height()
    ax5.text(bar.get_x() + bar.get_width()/2., height + 0.1,
             f'{pct}%', ha='center', va='bottom', fontsize=14, fontweight='bold')

# 6. Financial Impact
ax6 = plt.subplot(2, 3, 6)
impact_categories = ['Monthly Loss', 'Annual Loss', 'Lifetime Loss\n(12 months)']
impact_amounts = [9688, 116256, 1400000]
colors_impact = ['#e74c3c', '#c0392b', '#7f1e1e']

bars = ax6.bar(impact_categories, impact_amounts, color=colors_impact, alpha=0.8)
ax6.set_ylabel('Revenue Loss ($)', fontsize=12)
ax6.set_title('Financial Impact of Trial Failures', fontsize=14, fontweight='bold')
ax6.set_yscale('log')  # Log scale for better visualization

# Add value labels
for bar, amount in zip(bars, impact_amounts):
    height = bar.get_height()
    if amount < 1000000:
        label = f'${amount:,.0f}'
    else:
        label = f'${amount/1000000:.1f}M'
    ax6.text(bar.get_x() + bar.get_width()/2., height * 1.1,
             label, ha='center', va='bottom', fontsize=11, fontweight='bold')

# Overall title
fig.suptitle('URGENT: Free Trials Are Destroying Your Revenue', 
             fontsize=18, fontweight='bold', color='red')

# Add key insights text
fig.text(0.5, 0.02, 
         '⚠️  98.9% of paying customers use trials • 22.9% fail to pay • 100% of recent signups are trials • Direct customers pay 2.4x more',
         ha='center', fontsize=12, fontweight='bold', 
         bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8))

plt.tight_layout()
plt.subplots_adjust(top=0.93, bottom=0.08)
plt.savefig('stripe_api_findings.png', dpi=300, bbox_inches='tight')
plt.show()

print("Visualization saved as 'stripe_api_findings.png'") 