# Payment Analysis & Email Validation Suite

A comprehensive repository containing tools for email validation and in-depth Stripe payment analysis, focusing on trial conversion failures and revenue loss prevention.

## 🎯 Key Findings Summary

### Critical Business Metrics
- **$12,307/month** in lost recurring revenue (annualized: $147,679)
- **78.3%** trial customer failure rate vs 5.6% for direct subscribers
- **14.1x** higher delinquency rate for trial customers
- **78 customers** lost over 4 months (May-August 2025)

### Root Causes Identified
1. **No payment validation** at trial signup
2. **Prepaid cards** causing 55% failure rate
3. **Invalid payment methods** discovered only after 30-day trials
4. **No dunning process** for failed payments

## 📁 Repository Structure

```
email-validator/
├── src/                    # Source code
│   ├── email_validator.py  # Email validation tool
│   └── validate_csv.py     # CSV validation utility
├── analysis/              # Analysis scripts
│   ├── stripe_*.py        # Stripe API analysis
│   ├── analyze_*.py       # Data analysis scripts
│   └── visualize_*.py     # Visualization scripts
├── reports/               # Analysis reports
│   ├── final_trial_analysis_summary.md
│   ├── 4month_revenue_loss_report.md
│   └── payment_failure_summary.md
├── visualizations/        # Charts and graphs
├── data/                  # CSV data files
├── presentation/          # Key findings presentation
└── requirements.txt       # Python dependencies
```

## 🚀 Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Configuration
Set up your Mailgun API credentials as environment variables:

```bash
export MAILGUN_API_KEY="your-mailgun-api-key-here"
export MAILGUN_PUBLIC_KEY="your-mailgun-public-key-here"
```

Or create a `.env` file:
```
MAILGUN_API_KEY=your-mailgun-api-key-here
MAILGUN_PUBLIC_KEY=your-mailgun-public-key-here
```

### Email Validator
```bash
python src/email_validator.py
```

### Run Analysis
```bash
python analysis/stripe_trial_analysis.py
```

## 💡 Immediate Action Items

### 1. Payment Validation (Highest Priority)
- Implement $1 authorization hold at trial signup
- Block prepaid and virtual cards
- Require 3D Secure authentication

### 2. Trial Strategy Overhaul
- Reduce trial period from 30 to 7-14 days
- Require valid payment method upfront
- Consider eliminating trials for high-risk segments

### 3. Recovery Campaign
- Contact all 78 delinquent customers
- Offer incentives to reactivate
- Each recovered customer = $3,787 lifetime value

## 📊 Key Visualizations

- Trial conversion failure analysis
- 4-month revenue loss trends
- Geographic distribution of failures
- Payment method failure rates
- Delinquent customer timelines

## 🔧 Technologies Used

- **Python 3.6+** - Core language
- **Stripe API** - Payment data analysis
- **Mailgun API** - Email validation
- **Pandas** - Data manipulation
- **Matplotlib/Seaborn** - Data visualization
- **Requests** - API interactions

## 📈 Business Impact

Without immediate action, the business will continue losing ~$12,307/month. The solution is straightforward: validate payment methods at signup. This single change could recover the majority of the $295,358 in lifetime value currently being lost.

---

For detailed analysis and methodology, see the reports in the `/reports` directory. 