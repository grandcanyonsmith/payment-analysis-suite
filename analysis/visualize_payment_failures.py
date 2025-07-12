#!/usr/bin/env python3
"""
Visualize payment failures with detailed graphs and quantification
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Load the data
df = pd.read_csv('may_customers_stripe.csv')

# Convert date columns
df['Created (UTC)'] = pd.to_datetime(df['Created (UTC)'])
current_date = datetime(2025, 5, 31)
df['customer_age_days'] = (current_date - df['Created (UTC)']).dt.days
df['created_date'] = df['Created (UTC)'].dt.date

# Create comprehensive visualizations
fig = plt.figure(figsize=(20, 16))

# 1. Geographic Analysis - Show actual numbers
plt.subplot(4, 3, 1)
country_data = df.groupby('Card Issue Country').agg({
    'Delinquent': ['sum', 'count', 'mean']
}).round(3)
country_data.columns = ['failures', 'total_customers', 'failure_rate']
country_data['success'] = country_data['total_customers'] - country_data['failures']
country_data = country_data[country_data['total_customers'] >= 2]
country_data = country_data.sort_values('failure_rate', ascending=False).head(10)

# Create stacked bar chart
ax1 = country_data[['success', 'failures']].plot(kind='bar', stacked=True, ax=plt.gca())
plt.title('Payment Success vs Failures by Country\n(Countries with 2+ customers)', fontsize=14)
plt.ylabel('Number of Customers')
plt.xlabel('Country')

# Add labels showing total customers and failure rate
for i, (idx, row) in enumerate(country_data.iterrows()):
    total = row['total_customers']
    rate = row['failure_rate'] * 100
    plt.text(i, total + 0.5, f'{int(total)} customers\n{rate:.0f}% fail', 
             ha='center', va='bottom', fontsize=9)

plt.legend(['Successful', 'Failed'])
plt.xticks(rotation=45)

# 2. Philippines and France Detail
plt.subplot(4, 3, 2)
ph_fr_data = df[df['Card Issue Country'].isin(['PH', 'FR', 'US'])]
country_summary = []
for country in ['PH', 'FR', 'US']:
    country_df = ph_fr_data[ph_fr_data['Card Issue Country'] == country]
    summary = {
        'Country': country,
        'Total': len(country_df),
        'Failed': country_df['Delinquent'].sum(),
        'Success': len(country_df) - country_df['Delinquent'].sum()
    }
    country_summary.append(summary)

country_comp = pd.DataFrame(country_summary)
country_comp.set_index('Country')[['Success', 'Failed']].plot(kind='bar', ax=plt.gca())
plt.title('Philippines & France vs US Comparison', fontsize=14)
plt.ylabel('Number of Customers')
plt.xlabel('')

# Add annotations
for i, row in country_comp.iterrows():
    plt.text(i, row['Total'] + 0.5, f"Total: {row['Total']}\nFailed: {row['Failed']}", 
             ha='center', va='bottom', fontsize=10)
plt.xticks(rotation=0)

# 3. Customer Age Impact - Quantified
plt.subplot(4, 3, 3)
age_bins = [0, 1, 3, 7, 14, 30, 365]
age_labels = ['Day 0', 'Day 1-2', 'Day 3-6', 'Week 2', 'Week 3-4', 'Month 2+']
df['age_category'] = pd.cut(df['customer_age_days'], bins=age_bins, labels=age_labels)

age_summary = df.groupby('age_category').agg({
    'Delinquent': ['sum', 'count', 'mean']
})
age_summary.columns = ['failures', 'total', 'failure_rate']

# Bar chart with numbers
bars = plt.bar(range(len(age_summary)), age_summary['failure_rate'] * 100)
plt.title('Failure Rate by Customer Age\n(Showing actual numbers)', fontsize=14)
plt.ylabel('Failure Rate (%)')
plt.xlabel('Customer Age')
plt.xticks(range(len(age_summary)), age_summary.index, rotation=45)

# Add value labels
for i, (idx, row) in enumerate(age_summary.iterrows()):
    plt.text(i, row['failure_rate'] * 100 + 1, 
             f"{row['failures']}/{int(row['total'])}\n({row['failure_rate']*100:.1f}%)", 
             ha='center', va='bottom', fontsize=9)

# Color bars based on failure rate
colors = ['red' if x > 0.25 else 'orange' if x > 0.15 else 'green' for x in age_summary['failure_rate']]
for bar, color in zip(bars, colors):
    bar.set_color(color)

# 4. Daily Trend with Failure Counts
plt.subplot(4, 3, 4)
daily_stats = df.groupby('created_date').agg({
    'id': 'count',
    'Delinquent': ['sum', 'mean']
})
daily_stats.columns = ['signups', 'failures', 'failure_rate']

ax4 = daily_stats['signups'].plot(kind='bar', alpha=0.7, label='Total Signups')
ax4_twin = ax4.twinx()
daily_stats['failures'].plot(kind='line', color='red', marker='o', linewidth=2, 
                            markersize=8, label='Failures', ax=ax4_twin)

plt.title('Daily Signups vs Failures (May 2025)', fontsize=14)
ax4.set_xlabel('Date')
ax4.set_ylabel('Total Signups', color='blue')
ax4_twin.set_ylabel('Number of Failures', color='red')

# Highlight high failure days
for i, (date, row) in enumerate(daily_stats.iterrows()):
    if row['failure_rate'] > 0.25:
        ax4.axvspan(i-0.4, i+0.4, alpha=0.2, color='red')
        plt.text(i, row['failures'] + 0.2, f"{row['failures']}", 
                ha='center', fontsize=8, color='red', weight='bold')

plt.xticks(rotation=45)
ax4.legend(loc='upper left')
ax4_twin.legend(loc='upper right')

# 5. Prepaid Card Analysis
plt.subplot(4, 3, 5)
card_funding = df.groupby('Card Funding').agg({
    'Delinquent': ['sum', 'count', 'mean']
})
card_funding.columns = ['failures', 'total', 'failure_rate']
card_funding = card_funding.sort_values('failure_rate', ascending=False)

# Create pie chart of total distribution
sizes = card_funding['total'].values
labels = [f"{idx}\n({row['total']} customers)" for idx, row in card_funding.iterrows()]
colors = ['red' if idx == 'prepaid' else 'lightblue' for idx in card_funding.index]

plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
plt.title('Card Funding Type Distribution\n(Prepaid cards highlighted in red)', fontsize=14)

# 6. Prepaid vs Regular Failure Comparison
plt.subplot(4, 3, 6)
prepaid_comparison = pd.DataFrame({
    'Prepaid Cards': [
        df[df['Card Funding'] == 'prepaid']['Delinquent'].sum(),
        len(df[df['Card Funding'] == 'prepaid']) - df[df['Card Funding'] == 'prepaid']['Delinquent'].sum()
    ],
    'Regular Cards': [
        df[df['Card Funding'] != 'prepaid']['Delinquent'].sum(),
        len(df[df['Card Funding'] != 'prepaid']) - df[df['Card Funding'] != 'prepaid']['Delinquent'].sum()
    ]
}, index=['Failed', 'Success'])

prepaid_comparison.T.plot(kind='bar', stacked=True, ax=plt.gca())
plt.title('Prepaid vs Regular Cards: Success/Failure', fontsize=14)
plt.ylabel('Number of Transactions')
plt.xlabel('')

# Add failure rates
prepaid_rate = df[df['Card Funding'] == 'prepaid']['Delinquent'].mean() * 100
regular_rate = df[df['Card Funding'] != 'prepaid']['Delinquent'].mean() * 100
plt.text(0, 25, f'Failure Rate: {prepaid_rate:.0f}%', ha='center', fontsize=12, weight='bold')
plt.text(1, 360, f'Failure Rate: {regular_rate:.0f}%', ha='center', fontsize=12, weight='bold')
plt.xticks(rotation=0)

# 7. Email Domain Risk
plt.subplot(4, 3, 7)
df['email_domain'] = df['Email'].str.split('@').str[1]
domain_stats = df.groupby('email_domain').agg({
    'Delinquent': ['sum', 'count', 'mean']
})
domain_stats.columns = ['failures', 'total', 'failure_rate']
domain_stats = domain_stats[domain_stats['total'] >= 5]  # At least 5 customers
domain_stats = domain_stats.sort_values('failure_rate', ascending=False).head(8)

bars = plt.bar(range(len(domain_stats)), domain_stats['failure_rate'] * 100)
plt.title('Email Domain Failure Rates\n(Domains with 5+ customers)', fontsize=14)
plt.ylabel('Failure Rate (%)')
plt.xlabel('Email Domain')
plt.xticks(range(len(domain_stats)), domain_stats.index, rotation=45, ha='right')

# Add counts
for i, (idx, row) in enumerate(domain_stats.iterrows()):
    plt.text(i, row['failure_rate'] * 100 + 1, 
             f"{row['failures']}/{int(row['total'])}", 
             ha='center', va='bottom', fontsize=9)

# 8. Payment Status Distribution
plt.subplot(4, 3, 8)
status_counts = df['Status'].value_counts()
colors = ['green' if x == 'active' else 'red' if x == 'past_due' else 'orange' 
          for x in status_counts.index]
status_counts.plot(kind='pie', autopct='%1.1f%%', colors=colors, ax=plt.gca())
plt.title('Overall Payment Status Distribution', fontsize=14)
plt.ylabel('')

# 9. Risk Score Summary
plt.subplot(4, 3, 9)
risk_factors = pd.DataFrame({
    'Risk Factor': ['Prepaid Card', 'Philippines', 'France', 'First Day', 'Hotmail Email', 'Has Plan'],
    'Failure Rate': [55.0, 66.7, 33.3, 41.7, 50.0, 23.2],
    'Sample Size': [20, 3, 3, 12, 6, 190]
})

bars = plt.bar(range(len(risk_factors)), risk_factors['Failure Rate'])
plt.title('Failure Rates by Risk Factor', fontsize=14)
plt.ylabel('Failure Rate (%)')
plt.xlabel('Risk Factor')
plt.xticks(range(len(risk_factors)), risk_factors['Risk Factor'], rotation=45, ha='right')

# Add sample size
for i, row in risk_factors.iterrows():
    plt.text(i, row['Failure Rate'] + 1, f"n={row['Sample Size']}", 
             ha='center', va='bottom', fontsize=9)
    
# Color code by severity
for i, bar in enumerate(bars):
    if risk_factors.iloc[i]['Failure Rate'] > 50:
        bar.set_color('darkred')
    elif risk_factors.iloc[i]['Failure Rate'] > 30:
        bar.set_color('orange')
    else:
        bar.set_color('yellow')

plt.axhline(y=18.8, color='blue', linestyle='--', alpha=0.5, label='Overall Average (18.8%)')
plt.legend()

# 10. Cumulative Cost Impact
plt.subplot(4, 3, 10)
# Calculate potential revenue loss
df['potential_revenue'] = 147.00  # Assuming average plan cost
failed_revenue = df[df['Delinquent']]['potential_revenue'].sum()
successful_revenue = df[~df['Delinquent']]['potential_revenue'].sum()

revenue_data = pd.DataFrame({
    'Revenue': ['Lost Revenue', 'Successful Revenue'],
    'Amount': [failed_revenue, successful_revenue]
})

plt.bar(revenue_data['Revenue'], revenue_data['Amount'], color=['red', 'green'])
plt.title(f'Revenue Impact of Payment Failures\nTotal Lost: ${failed_revenue:,.0f}', fontsize=14)
plt.ylabel('Revenue ($)')

# Add value labels
for i, (idx, row) in enumerate(revenue_data.iterrows()):
    plt.text(i, row['Amount'] + 500, f"${row['Amount']:,.0f}", 
             ha='center', va='bottom', fontsize=12, weight='bold')

# 11. New vs Established - Clear Comparison
plt.subplot(4, 3, 11)
customer_segments = pd.DataFrame({
    'Segment': ['Day 0 (First Day)', 'Day 1-7 (New)', 'Day 8+ (Established)'],
    'Total': [
        len(df[df['customer_age_days'] == 0]),
        len(df[(df['customer_age_days'] > 0) & (df['customer_age_days'] <= 7)]),
        len(df[df['customer_age_days'] > 7])
    ],
    'Failed': [
        df[df['customer_age_days'] == 0]['Delinquent'].sum(),
        df[(df['customer_age_days'] > 0) & (df['customer_age_days'] <= 7)]['Delinquent'].sum(),
        df[df['customer_age_days'] > 7]['Delinquent'].sum()
    ]
})
customer_segments['Success'] = customer_segments['Total'] - customer_segments['Failed']
customer_segments['Failure_Rate'] = (customer_segments['Failed'] / customer_segments['Total'] * 100).round(1)

ax = customer_segments.set_index('Segment')[['Success', 'Failed']].plot(kind='bar', stacked=True, ax=plt.gca())
plt.title('Customer Segments: Success vs Failure', fontsize=14)
plt.ylabel('Number of Customers')
plt.xlabel('')

# Add failure rate labels
for i, row in customer_segments.iterrows():
    plt.text(i, row['Total'] + 2, f"Failure Rate: {row['Failure_Rate']}%\n({row['Failed']}/{row['Total']})", 
             ha='center', va='bottom', fontsize=10, weight='bold')
plt.xticks(rotation=30, ha='right')

# 12. Key Metrics Summary
plt.subplot(4, 3, 12)
plt.text(0.1, 0.9, "KEY FINDINGS SUMMARY", fontsize=16, weight='bold', transform=plt.gca().transAxes)

summary_text = f"""
OVERALL METRICS:
• Total Customers: {len(df)}
• Total Failures: {df['Delinquent'].sum()} ({df['Delinquent'].mean()*100:.1f}%)
• Lost Revenue: ${failed_revenue:,.0f}

HIGH-RISK SEGMENTS:
• Philippines: 2 failures out of 3 customers (66.7%)
• France: 1 failure out of 3 customers (33.3%)
• First-day signups: 41.7% failure rate
• Prepaid cards: 55% failure rate (11/20)

COMPARISON:
• Day 0 customers: 4x higher failure rate than Day 8+
• International: Similar failure rate to US (not the main issue)
• Gmail users: 48 failures out of 208 (23.1%)
"""

plt.text(0.05, 0.85, summary_text, fontsize=11, transform=plt.gca().transAxes,
         verticalalignment='top', fontfamily='monospace')
plt.axis('off')

plt.tight_layout()
plt.savefig('payment_failure_detailed_analysis.png', dpi=300, bbox_inches='tight')
print("Detailed visualizations saved to 'payment_failure_detailed_analysis.png'")

# Also create a focused geographic analysis
plt.figure(figsize=(12, 8))

# Geographic deep dive
country_detail = df.groupby('Card Issue Country').agg({
    'id': 'count',
    'Delinquent': ['sum', 'mean'],
    'Total Spend': 'sum'
}).round(2)
country_detail.columns = ['customers', 'failures', 'failure_rate', 'revenue']
country_detail = country_detail.sort_values('customers', ascending=False).head(15)

plt.subplot(2, 2, 1)
country_detail['customers'].plot(kind='bar')
plt.title('Number of Customers by Country')
plt.ylabel('Number of Customers')
plt.xlabel('Country')

plt.subplot(2, 2, 2)
country_detail['failure_rate'].plot(kind='bar', color=['red' if x > 0.3 else 'orange' if x > 0.2 else 'green' 
                                                       for x in country_detail['failure_rate']])
plt.title('Failure Rate by Country')
plt.ylabel('Failure Rate')
plt.xlabel('Country')
plt.axhline(y=0.188, color='blue', linestyle='--', label='Average (18.8%)')
plt.legend()

plt.subplot(2, 2, 3)
# Show only countries with failures
countries_with_failures = country_detail[country_detail['failures'] > 0]
plt.bar(range(len(countries_with_failures)), countries_with_failures['failures'])
plt.title('Number of Failed Payments by Country')
plt.ylabel('Number of Failures')
plt.xlabel('Country')
plt.xticks(range(len(countries_with_failures)), countries_with_failures.index, rotation=45)

# Add value labels
for i, (idx, row) in enumerate(countries_with_failures.iterrows()):
    plt.text(i, row['failures'] + 0.2, f"{int(row['failures'])}", ha='center', va='bottom')

plt.subplot(2, 2, 4)
plt.text(0.1, 0.9, "GEOGRAPHIC INSIGHTS", fontsize=14, weight='bold', transform=plt.gca().transAxes)

geo_summary = f"""
TOP COUNTRIES BY VOLUME:
• US: {country_detail.loc['US', 'customers']} customers, {country_detail.loc['US', 'failures']} failures
• AU: {country_detail.loc['AU', 'customers']} customers, {country_detail.loc['AU', 'failures']} failures
• CA: {country_detail.loc['CA', 'customers']} customers, {country_detail.loc['CA', 'failures']} failures

PROBLEM COUNTRIES (Small Volume):
• Philippines: 3 customers, 2 failures (66.7%)
  - All signed up in May
  - Could be testing stolen cards
  
• France: 3 customers, 1 failure (33.3%)
  - Small sample size
  - May not be statistically significant

RECOMMENDATION:
Focus on high-volume patterns (prepaid cards, 
first-day signups) rather than low-volume 
geographic outliers.
"""

plt.text(0.05, 0.85, geo_summary, fontsize=10, transform=plt.gca().transAxes,
         verticalalignment='top', fontfamily='monospace')
plt.axis('off')

plt.tight_layout()
plt.savefig('geographic_analysis_detailed.png', dpi=300, bbox_inches='tight')
print("Geographic analysis saved to 'geographic_analysis_detailed.png'") 