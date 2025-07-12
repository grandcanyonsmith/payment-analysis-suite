import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# Data from the delinquent accounts analysis
total_delinquent = 37
trial_delinquent = 34
direct_delinquent = 3

# Revenue breakdown
trial_297_count = 4
trial_147_count = 30
direct_0_count = 3

trial_revenue_lost = 5598.00
direct_revenue_lost = 0.00

# Create figure with subplots
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('June 2025 Delinquent Accounts Analysis', fontsize=16, fontweight='bold')

# 1. Delinquent Account Types
labels = ['Trial', 'Direct']
sizes = [trial_delinquent, direct_delinquent]
colors = ['#ff9999', '#66b3ff']
explode = (0.05, 0.05)

ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.0f%%',
        shadow=True, startangle=90)
ax1.set_title(f'Delinquent Account Distribution\n(Total: {total_delinquent} accounts)')

# 2. Revenue Lost by Type
revenue_data = [trial_revenue_lost, direct_revenue_lost]
bars = ax2.bar(labels, revenue_data, color=['coral', 'lightgreen'])
ax2.set_ylabel('Monthly Revenue Lost ($)')
ax2.set_title('Revenue Impact by Customer Type')
ax2.set_ylim(0, 6000)

# Add value labels on bars
for bar, value in zip(bars, revenue_data):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 50,
             f'${value:,.0f}', ha='center', fontweight='bold')

# 3. Trial Customer Price Points
price_points = ['$297/mo', '$147/mo']
counts = [trial_297_count, trial_147_count]
ax3.bar(price_points, counts, color=['purple', 'orange'])
ax3.set_ylabel('Number of Delinquent Accounts')
ax3.set_title('Trial Customer Price Distribution')
ax3.set_ylim(0, 35)

for i, count in enumerate(counts):
    ax3.text(i, count + 0.5, str(count), ha='center', fontweight='bold')

# 4. Key insights text
ax4.axis('off')
insights_text = """
KEY FINDINGS - JUNE 2025 DELINQUENT ACCOUNTS:

1. ACCOUNT BREAKDOWN:
   • 34 Trial customers (91.9%)
   • 3 Direct customers (8.1%)
   • All delinquent after 2 months

2. REVENUE IMPACT:
   • Total lost: $5,598/month
   • All from trial customers
   • Direct customers: $0 (no subscriptions)

3. PRICE POINT ANALYSIS:
   • 4 customers at $297/mo
   • 30 customers at $147/mo
   • Average: $164.65 per trial

4. PAYMENT STATUS:
   • All marked as "past_due"
   • No payment method info available
   • Failed after trial period ended

5. PATTERN INSIGHTS:
   • Trials signed up early June
   • Failed in early August
   • Consistent 2-month trial period
   
CRITICAL OBSERVATION:
Direct "delinquent" customers have $0 revenue
because they never had active subscriptions.
These are likely abandoned signups.
"""

ax4.text(0.05, 0.95, insights_text, transform=ax4.transAxes, fontsize=10,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('june_delinquent_analysis.png', dpi=300, bbox_inches='tight')
print("Visualization saved as june_delinquent_analysis.png")

# Create detailed timeline
fig2, ax = plt.subplots(figsize=(12, 8))

# Sample of delinquent customers with their timelines
customers = [
    ('michaelosby00@gmail.com', '2025-06-09', '$297'),
    ('joeddie.delatorre@gmail.com', '2025-06-08', '$297'),
    ('contactmyhost@gmail.com', '2025-06-04', '$297'),
    ('nebrotishin@gmail.com', '2025-06-01', '$297'),
    ('cperk769@gmail.com', '2025-06-12', '$147'),
    ('wyldermylove@gmail.com', '2025-06-12', '$147'),
    ('goldnpassive@gmail.com', '2025-06-11', '$147'),
    ('jonas.man69@gmail.com', '2025-06-11', '$147'),
]

# Create timeline visualization
y_positions = range(len(customers))
for i, (email, signup_date, price) in enumerate(customers):
    # Convert date
    signup = datetime.strptime(signup_date, '%Y-%m-%d')
    delinquent = datetime(2025, 8, int(signup_date.split('-')[2]))
    
    # Plot timeline
    ax.plot([signup, delinquent], [i, i], 'o-', linewidth=2,
            color='red' if price == '$297' else 'orange',
            markersize=8)
    
    # Add labels
    ax.text(signup - pd.Timedelta(days=2), i, email.split('@')[0][:15] + '...',
            ha='right', va='center', fontsize=9)
    ax.text(delinquent + pd.Timedelta(days=1), i, price,
            ha='left', va='center', fontsize=9, fontweight='bold')

ax.set_yticks(y_positions)
ax.set_yticklabels([])
ax.set_xlabel('Date')
ax.set_title('Sample Delinquent Customer Timeline (Signup → Past Due)', fontsize=14)
ax.grid(True, alpha=0.3)

# Add legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
           markersize=8, label='$297/mo customers'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', 
           markersize=8, label='$147/mo customers')
]
ax.legend(handles=legend_elements, loc='upper right')

# Set x-axis limits
ax.set_xlim(datetime(2025, 5, 25), datetime(2025, 8, 20))

plt.tight_layout()
plt.savefig('june_delinquent_timeline.png', dpi=300, bbox_inches='tight')
print("Timeline saved as june_delinquent_timeline.png") 