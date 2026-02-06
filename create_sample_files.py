import pandas as pd
import numpy as np

# Create sample sales data
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=100, freq='D')
data = {
    'Date': dates,
    'Product': np.random.choice(['Laptop', 'Phone', 'Tablet', 'Monitor', 'Keyboard'], 100),
    'Region': np.random.choice(['North', 'South', 'East', 'West'], 100),
    'Sales': np.random.randint(1000, 10000, 100),
    'Quantity': np.random.randint(1, 50, 100),
    'Discount': np.random.uniform(0, 0.3, 100).round(2)
}

df = pd.DataFrame(data)
df['Revenue'] = (df['Sales'] * df['Quantity'] * (1 - df['Discount'])).round(2)

# Save as Excel
df.to_excel('sample_data/sales_sample.xlsx', index=False, sheet_name='Sales Data')
print("✓ Created sales_sample.xlsx")

# Save as JSON
df.to_json('sample_data/sales_sample.json', orient='records', indent=2)
print("✓ Created sales_sample.json")

print(f"\nGenerated {len(df)} records with columns: {', '.join(df.columns)}")
