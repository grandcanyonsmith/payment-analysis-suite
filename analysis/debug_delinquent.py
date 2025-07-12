import pandas as pd

df = pd.read_csv('may_customers_stripe.csv')

print("Unique values in Delinquent column:")
print(df['Delinquent'].value_counts())
print("\nNull values:", df['Delinquent'].isnull().sum())
print("\nData type:", df['Delinquent'].dtype)

# Show some examples of delinquent customers
delinquent_samples = df[df['Delinquent'] == True].head(5)
print("\nExample delinquent customers:")
print(delinquent_samples[['Email', 'Name', 'Delinquent', 'Status']])

# Count by status
print("\nStatus counts for delinquent customers:")
print(df[df['Delinquent'] == True]['Status'].value_counts()) 