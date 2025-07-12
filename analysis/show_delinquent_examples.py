import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Read the detailed delinquent data
df = pd.read_csv('delinquent_reasons_detailed.csv')

# Create visualization showing specific customer examples
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
fig.suptitle('Real Examples: Why 269 Customers Became Delinquent', fontsize=18, fontweight='bold')

# Top panel - Show no payment method examples
ax1.axis('off')
no_payment_examples = df[df['failure_reason'] == 'no_payment_method'].head(15)

examples_text = "NO PAYMENT METHOD - 252 CUSTOMERS (93.7%)\n"
examples_text += "="*80 + "\n\n"

for i, (_, customer) in enumerate(no_payment_examples.iterrows()):
    created = customer['created'].split(' ')[0]
    trial_end = customer['trial_end'].split(' ')[0] if pd.notna(customer['trial_end']) else 'N/A'
    examples_text += f"{i+1}. {customer['email']:<45} Created: {created}\n"
    examples_text += f"   Revenue Lost: ${customer['monthly_revenue']:<8.2f} Trial End: {trial_end}\n"
    examples_text += f"   Status: NO PAYMENT METHOD PROVIDED AT SIGNUP\n\n"

ax1.text(0.05, 0.95, examples_text, transform=ax1.transAxes, fontsize=9,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='#ffe6e6', alpha=0.9))

# Bottom panel - Show actual card failures
ax2.axis('off')
card_failures = df[df['failure_reason'] != 'no_payment_method'].head(15)

failures_text = "ACTUAL CARD FAILURES - 17 CUSTOMERS (6.3%)\n"
failures_text += "="*80 + "\n\n"

for i, (_, customer) in enumerate(card_failures.iterrows()):
    created = customer['created'].split(' ')[0]
    failures_text += f"{i+1}. {customer['email']:<45} Created: {created}\n"
    failures_text += f"   Card: {customer['card_brand']} {customer['card_last4']} "
    if 'card_funding' in customer and pd.notna(customer['card_funding']):
        failures_text += f"({customer['card_funding']})\n"
    else:
        failures_text += "\n"
    failures_text += f"   Failure: {customer['failure_reason']}\n"
    if 'failure_message' in customer and pd.notna(customer['failure_message']):
        failures_text += f"   Message: {customer['failure_message']}\n"
    failures_text += "\n"

ax2.text(0.05, 0.95, failures_text, transform=ax2.transAxes, fontsize=9,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='#e6ffe6', alpha=0.9))

plt.tight_layout()
plt.savefig('delinquent_customer_examples.png', dpi=300, bbox_inches='tight')
print("Customer examples saved as delinquent_customer_examples.png")

# Create a summary comparison chart
fig2, ax = plt.subplots(figsize=(12, 8))

# Data for the comparison
categories = ['No Payment\nMethod', 'Card\nDeclined', 'Payment\nFailed', 'Provider\nDecline', 'Unknown']
counts = [252, 8, 4, 3, 2]
revenues = [32092.70, 244.00, 244.00, 0, 294.00]

# Create bars
x = range(len(categories))
bars = ax.bar(x, counts, color=['red', 'orange', 'orange', 'orange', 'gray'])

# Highlight the main issue
bars[0].set_color('#ff0000')
bars[0].set_edgecolor('darkred')
bars[0].set_linewidth(3)

# Add count labels
for i, (count, revenue) in enumerate(zip(counts, revenues)):
    ax.text(i, count + 5, f'{count}\ncustomers', ha='center', fontweight='bold')
    ax.text(i, count/2, f'${revenue:,.0f}', ha='center', color='white', fontweight='bold')

ax.set_xticks(x)
ax.set_xticklabels(categories)
ax.set_ylabel('Number of Delinquent Customers', fontsize=14)
ax.set_title('Why Did 269 Customers Become Delinquent?', fontsize=16, fontweight='bold')
ax.set_ylim(0, 280)

# Add percentage annotations
for i, (count, cat) in enumerate(zip(counts, categories)):
    percentage = (count / sum(counts)) * 100
    ax.text(i, -20, f'{percentage:.1f}%', ha='center', fontweight='bold', fontsize=12)

# Add key message
message = """93.7% of delinquencies are NOT payment failures -
they're customers who never provided ANY payment method!"""
ax.text(0.5, 0.85, message, transform=ax.transAxes, ha='center', fontsize=14,
        fontweight='bold', color='red',
        bbox=dict(boxstyle='round,pad=1', facecolor='yellow', alpha=0.8))

plt.tight_layout()
plt.savefig('delinquent_comparison_chart.png', dpi=300, bbox_inches='tight')
print("Comparison chart saved as delinquent_comparison_chart.png") 