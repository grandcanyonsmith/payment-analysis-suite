import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Create figure
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
fig.suptitle('Corrected Analysis: Free Trials vs Direct Subscriptions - May 2025', 
             fontsize=16, fontweight='bold')

# Data
trial_total = 46
trial_delinquent = 36
trial_success = 10

direct_total = 144
direct_delinquent = 8
direct_success = 136

# Chart 1: Customer counts and failure rates
categories = ['Free Trials\n(46 customers)', 'Direct Signups\n(144 customers)']
success_counts = [trial_success, direct_success]
failure_counts = [trial_delinquent, direct_delinquent]

# Create stacked bar chart
bar_width = 0.6
bars1 = ax1.bar(categories, success_counts, bar_width, label='Successful', color='#27ae60')
bars2 = ax1.bar(categories, failure_counts, bar_width, bottom=success_counts, 
                 label='Delinquent', color='#e74c3c')

# Add percentage labels
for i, (success, failure, total) in enumerate([(trial_success, trial_delinquent, trial_total),
                                               (direct_success, direct_delinquent, direct_total)]):
    # Success percentage
    ax1.text(i, success/2, f'{success}\n({success/total*100:.1f}%)', 
             ha='center', va='center', fontweight='bold', color='white')
    # Failure percentage
    ax1.text(i, success + failure/2, f'{failure}\n({failure/total*100:.1f}%)', 
             ha='center', va='center', fontweight='bold', color='white')

ax1.set_ylabel('Number of Customers', fontsize=12)
ax1.set_title('Customer Success/Failure Breakdown', fontsize=14)
ax1.legend()
ax1.set_ylim(0, 160)

# Add comparison callout
ax1.text(0.5, 0.9, '14.1x higher\nfailure rate!', ha='center', transform=ax1.transAxes,
         fontsize=14, fontweight='bold', color='red',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.5))

# Chart 2: Revenue impact
revenue_categories = ['Trial Failures', 'Direct Failures', 'Successful\nRevenue']
revenue_amounts = [5542, 1076, 43362]  # Approximate successful revenue
colors = ['#e74c3c', '#e67e22', '#27ae60']

bars = ax2.bar(revenue_categories, revenue_amounts, color=colors, alpha=0.8)
ax2.set_ylabel('Monthly Revenue ($)', fontsize=12)
ax2.set_title('Revenue Impact Analysis', fontsize=14)

# Add value labels
for bar, amount in zip(bars, revenue_amounts):
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height + 500,
             f'${amount:,}', ha='center', va='bottom', fontsize=11, fontweight='bold')

# Add total loss annotation
total_loss = 5542 + 1076
ax2.text(0.5, 0.85, f'Total Monthly\nRevenue Lost:\n${total_loss:,}', 
         ha='center', transform=ax2.transAxes,
         fontsize=12, fontweight='bold', color='red',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig('corrected_trial_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# Print summary
print("\n=== CORRECTED ANALYSIS SUMMARY ===")
print(f"\nFree Trials: {trial_total} customers")
print(f"  ✗ Failed: {trial_delinquent} (78.3%)")
print(f"  ✓ Successful: {trial_success} (21.7%)")
print(f"\nDirect Signups: {direct_total} customers")
print(f"  ✗ Failed: {direct_delinquent} (5.6%)")
print(f"  ✓ Successful: {direct_success} (94.4%)")
print(f"\n💡 Trial customers are 14.1x more likely to fail!")
print(f"\n💰 Monthly revenue lost:")
print(f"   - From trial failures: $5,542")
print(f"   - From direct failures: $1,076")
print(f"   - Total: $6,618") 