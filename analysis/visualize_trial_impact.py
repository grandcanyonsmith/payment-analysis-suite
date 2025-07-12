import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Create figure with subplots
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Free Trial vs Direct Subscription Analysis - May 2025', fontsize=16, fontweight='bold')

# 1. Delinquency Rate Comparison
categories = ['Trial Conversions', 'Direct Subscriptions']
delinquency_rates = [88.5, 8.2]
colors = ['#e74c3c', '#27ae60']

bars1 = ax1.bar(categories, delinquency_rates, color=colors, alpha=0.8)
ax1.set_ylabel('Delinquency Rate (%)', fontsize=12)
ax1.set_title('Delinquency Rate: Trial vs Direct', fontsize=14, fontweight='bold')
ax1.set_ylim(0, 100)

# Add value labels on bars
for bar, rate in zip(bars1, delinquency_rates):
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 2,
             f'{rate}%', ha='center', va='bottom', fontsize=12, fontweight='bold')

# Add comparison text
ax1.text(0.5, 50, '10.8x\nhigher', ha='center', transform=ax1.transAxes,
         fontsize=14, fontweight='bold', color='red',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.3))

# 2. Customer Breakdown
sizes = [26, 98, 5, 56]
labels = ['Trial Conversions\n(26)', 'Direct Paid\n(98)', 'Currently Trialing\n(5)', 'No Plan/Other\n(56)']
colors_pie = ['#e74c3c', '#27ae60', '#f39c12', '#95a5a6']
explode = (0.1, 0, 0, 0)  # Explode trial conversions

wedges, texts, autotexts = ax2.pie(sizes, labels=labels, colors=colors_pie, autopct='%1.1f%%',
                                    startangle=90, explode=explode, shadow=True)
ax2.set_title('Paid Subscriber Breakdown', fontsize=14, fontweight='bold')

# 3. Revenue Impact
revenue_categories = ['Trial Conv.\nDelinquent', 'Direct Sub.\nDelinquent', 'Successful\nPayments']
revenue_amounts = [3381, 1176, 50061]  # Approximate based on analysis
colors_rev = ['#e74c3c', '#e67e22', '#27ae60']

bars3 = ax3.bar(revenue_categories, revenue_amounts, color=colors_rev, alpha=0.8)
ax3.set_ylabel('Monthly Revenue ($)', fontsize=12)
ax3.set_title('Revenue Impact by Customer Type', fontsize=14, fontweight='bold')

# Add value labels
for bar, amount in zip(bars3, revenue_amounts):
    height = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2., height + 500,
             f'${amount:,}', ha='center', va='bottom', fontsize=10)

# 4. Delinquency by Customer Age
age_groups = ['Day 0', 'Days 1-3', 'Days 4-7', 'Days 8-14', 'Days 15-31']
delinquency_by_age = [42.9, 23.3, 11.1, 21.1, 26.4]

line = ax4.plot(age_groups, delinquency_by_age, marker='o', linewidth=3, markersize=10, color='#e74c3c')
ax4.fill_between(range(len(age_groups)), delinquency_by_age, alpha=0.3, color='#e74c3c')
ax4.set_ylabel('Delinquency Rate (%)', fontsize=12)
ax4.set_xlabel('Customer Age', fontsize=12)
ax4.set_title('Delinquency Rate by Customer Age', fontsize=14, fontweight='bold')
ax4.set_ylim(0, 50)
ax4.grid(True, alpha=0.3)

# Add annotations for key points
ax4.annotate('Initial failures', xy=(0, 42.9), xytext=(0.5, 45),
            arrowprops=dict(arrowstyle='->', color='red', lw=2),
            fontsize=10, fontweight='bold')
ax4.annotate('Trial conversions', xy=(4, 26.4), xytext=(3.5, 35),
            arrowprops=dict(arrowstyle='->', color='red', lw=2),
            fontsize=10, fontweight='bold')

# Adjust layout
plt.tight_layout()
plt.savefig('trial_conversion_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# Create a summary statistics table
print("\n=== TRIAL CONVERSION IMPACT SUMMARY ===")
print("\nComparison Metrics:")
print("-" * 50)
print(f"{'Metric':<30} {'Trial Conv.':<15} {'Direct Sub.':<15}")
print("-" * 50)
print(f"{'Total Customers':<30} {'26':<15} {'98':<15}")
print(f"{'Delinquent Customers':<30} {'23 (88.5%)':<15} {'8 (8.2%)':<15}")
print(f"{'Success Rate':<30} {'11.5%':<15} {'91.8%':<15}")
print(f"{'Monthly Revenue at Risk':<30} {'$3,381':<15} {'$1,176':<15}")
print(f"{'Avg Revenue per Customer':<30} {'$147':<15} {'$147':<15}")
print("-" * 50)

print("\n💡 KEY INSIGHT: Free trial customers are 10.8x more likely to become delinquent!")
print("\n📊 RECOMMENDATION: Consider eliminating free trials or requiring upfront payment validation.") 