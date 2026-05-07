import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker
import uuid

# Initialize Faker for realistic name generation
fake = Faker()

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_energy_data(num_records=5000):
    """
    Generate synthetic energy consumption data matching the exact structure
    but with Lusaka-specific regions
    """
    
    # Lusaka-specific regions/suburbs
    lusaka_regions = [
        'CBD', 'Woodlands', 'Kabulonga', 'Ibex Hill', 'Rhodes Park',
        'Northmead', 'Olympia', 'Roma', 'Avondale', 'Lilayi',
        'Chilenje', 'Fairview', 'Longacres', 'Makeni', 'Lusaka West',
        'Mass Media', 'Thornpark', 'Kalingalinga', 'Matero', 'Chawama',
        'Kanyama', 'Mtendere', 'Mandevu', 'Garden', 'Chaisa',
        'John Laing', 'George', 'Chunga', 'Bauleni', 'Chazanga'
    ]
    
    # Lusaka-specific dwelling types
    dwelling_types = ['House', 'Apartment', 'Flat', 'Compound']
    
    # Lusaka-specific business types
    business_types = [
        'Retail', 'Wholesale', 'Manufacturing', 'Transportation',
        'Hospitality', 'Technology', 'Textiles', 'Agriculture'
    ]
    
    # Lusaka-specific facility types
    facility_types = [
        'Shopping Mall', 'Office Complex', 'Factory', 'Warehouse',
        'School', 'Hospital', 'Hotel', 'Restaurant', 'Supermarket'
    ]
    
    # Tariff plans (could be ZESCO-specific)
    tariff_plans = {
        'residential': ['R1', 'R2', 'R3'],
        'commercial': ['C1', 'C2', 'C3'],
        'industrial': ['I1', 'I2', 'I3']
    }
    
    # Payment statuses
    payment_statuses = ['paid', 'partial', 'unpaid']
    
    # Meter ID prefixes
    meter_prefixes = ['RES', 'COM', 'IND']
    
    data = []
    
    for i in range(num_records):
        # Determine usage type with realistic distribution
        usage_type = np.random.choice(
            ['residential', 'commercial', 'industrial'],
            p=[0.6, 0.25, 0.15]  # More residential in Lusaka
        )
        
        # Generate meter ID
        prefix = 'RES' if usage_type == 'residential' else 'COM' if usage_type == 'commercial' else 'IND'
        meter_id = f"{prefix}{i:05d}"
        
        # Generate timestamp (spread across 2 years for meaningful patterns)
        days_back = np.random.randint(0, 730)
        hours = np.random.randint(0, 24)
        minutes = np.random.randint(0, 60)
        seconds = np.random.randint(0, 60)
        
        timestamp = datetime.now() - timedelta(days=days_back, hours=hours, 
                                               minutes=minutes, seconds=seconds)
        
        # Extract date components
        month = timestamp.month
        hour = timestamp.hour
        date = timestamp.date()
        
        # Determine if peak hour (Lusaka peak hours: 5-9am and 5-9pm)
        is_peak_hour = (hour in [5,6,7,8,9,17,18,19,20,21])
        
        # Initialize common fields
        record = {
            'Meter_ID': meter_id,
            'Usage_Type': usage_type,
            'Name': '',
            'Address': '',
            'Phone_Number': '',
            'Region': np.random.choice(lusaka_regions),
            'Tariff_Plan': '',
            'Email': '',
            'Household_Size': '',
            'Dwelling_Type': '',
            'Energy_Consumption_kWh': 0,
            'Payment_Status': np.random.choice(payment_statuses, p=[0.7, 0.2, 0.1]),
            'Timestamp': timestamp,
            'Business_Name': '',
            'Business_Address': '',
            'Contact_Number': '',
            'Business_Type': '',
            'Contact_Email': '',
            'Operating_Hours': '',
            'Floor_Area': '',
            'Facility_Name': '',
            'Facility_Address': '',
            'Industry_Type': '',
            'Production_Capacity': '',
            'Operating_Shifts': '',
            'Production_Volume': '',
            'Month': month,
            'Hour': hour,
            'Date': date,
            'Is_Peak_Hour': is_peak_hour,
            'Peak_hour_usage_ratio': 0,
            'Usage_consistency_score': 0
        }
        
        # Generate values based on usage type
        if usage_type == 'residential':
            # Residential-specific fields
            record['Name'] = fake.name()
            record['Address'] = fake.street_address() + ', Lusaka'
            record['Phone_Number'] = f"+260{np.random.randint(95, 98)}{np.random.randint(1000000, 9999999)}"
            record['Tariff_Plan'] = np.random.choice(tariff_plans['residential'])
            record['Email'] = f"{record['Name'].lower().replace(' ', '')}@gmail.com"
            record['Household_Size'] = np.random.randint(1, 8)
            record['Dwelling_Type'] = np.random.choice(dwelling_types)
            
            # Residential consumption: typically 5-80 kWh
            base_consumption = np.random.normal(18, 8)
            if is_peak_hour:
                base_consumption *= np.random.uniform(1.1, 1.4)
            record['Energy_Consumption_kWh'] = max(1, base_consumption)
            
        elif usage_type == 'commercial':
            # Commercial-specific fields
            business_names = ['Chikuni General Dealers', 'Mosi Beverages', 'Great North Electronics',
                            'Zambezi Agro Ltd', 'Copperbelt Traders', 'Lusaka Hardware',
                            'Luangwa Motors', 'Solwezi Boutique']
            
            record['Business_Name'] = np.random.choice(business_names)
            record['Business_Address'] = f"Plot {np.random.randint(1, 500)}, {fake.street_name()}, Lusaka"
            record['Contact_Number'] = f"+260{np.random.randint(95, 98)}{np.random.randint(1000000, 9999999)}"
            record['Business_Type'] = np.random.choice(business_types)
            record['Contact_Email'] = f"{record['Business_Name'].lower().replace(' ', '')}@gmail.com"
            record['Operating_Hours'] = f"{np.random.randint(8, 24)} hours"
            record['Floor_Area'] = np.random.randint(50, 500)
            
            # Commercial consumption: typically 10-300 kWh
            base_consumption = np.random.normal(60, 30)
            if is_peak_hour and hour in [8,9,10,11,12,13,14,15,16,17]:
                base_consumption *= np.random.uniform(1.2, 1.8)
            record['Energy_Consumption_kWh'] = max(5, base_consumption)
            
        else:  # industrial
            # Industrial-specific fields
            facility_names = ['Lusaka Energy Hub', 'Ndola Textile Plant', 'Chipata Milling Station',
                            'Mansa Agro Facility', 'Kitwe Water Works', 'Solwezi Industrial Park']
            industry_types = ['Mining', 'Processing', 'Manufacturing', 'Agriculture']
            
            record['Facility_Name'] = np.random.choice(facility_names)
            record['Facility_Address'] = f"Plot {np.random.randint(1, 100)}, Industrial Area, Lusaka"
            record['Contact_Number'] = f"+260{np.random.randint(95, 98)}{np.random.randint(1000000, 9999999)}"
            record['Industry_Type'] = np.random.choice(industry_types)
            record['Production_Capacity'] = np.random.randint(100, 1000)
            record['Operating_Shifts'] = np.random.choice(['1 shift', '2 shifts', '3 shifts'])
            record['Production_Volume'] = np.random.randint(100, 10000)
            
            # Industrial consumption: typically 50-1000 kWh
            base_consumption = np.random.normal(250, 150)
            if is_peak_hour and hour in [6,7,8,9,10,11,12,13,14,15,16,17]:
                base_consumption *= np.random.uniform(0.9, 1.3)  # Industrial may have different patterns
            record['Energy_Consumption_kWh'] = max(20, base_consumption)
        
        # Generate derived metrics
        record['Peak_hour_usage_ratio'] = round(np.random.uniform(0.1, 3.0), 2)
        record['Usage_consistency_score'] = round(np.random.uniform(0, 50), 2)
        
        data.append(record)
    
    return pd.DataFrame(data)

def add_seasonal_patterns(df):
    """
    Add realistic seasonal patterns to the data
    """
    # Zambia seasons: Hot dry (Aug-Oct), Rainy (Nov-Apr), Cool dry (May-Jul)
    hot_dry_months = [8, 9, 10]
    rainy_months = [11, 12, 1, 2, 3, 4]
    cool_dry_months = [5, 6, 7]
    
    # Adjust consumption based on season (higher in hot months due to cooling)
    for idx, row in df.iterrows():
        if row['Month'] in hot_dry_months:
            df.at[idx, 'Energy_Consumption_kWh'] *= np.random.uniform(1.2, 1.5)
        elif row['Month'] in cool_dry_months:
            df.at[idx, 'Energy_Consumption_kWh'] *= np.random.uniform(0.8, 1.0)
    
    return df

def add_weekend_patterns(df):
    """
    Add weekend vs weekday patterns
    """
    for idx, row in df.iterrows():
        date_obj = pd.to_datetime(row['Date'])
        is_weekend = date_obj.weekday() >= 5
        
        if is_weekend:
            if row['Usage_Type'] == 'commercial':
                # Commercial lower on weekends
                df.at[idx, 'Energy_Consumption_kWh'] *= np.random.uniform(0.4, 0.7)
            elif row['Usage_Type'] == 'residential':
                # Residential slightly higher on weekends during day
                if 10 <= row['Hour'] <= 20:
                    df.at[idx, 'Energy_Consumption_kWh'] *= np.random.uniform(1.1, 1.3)
    
    return df

# Generate the data
print("Generating synthetic energy consumption data for Lusaka...")
df = generate_energy_data(num_records=5000)

# Apply patterns
print("Adding seasonal and weekend patterns...")
df = add_seasonal_patterns(df)
df = add_weekend_patterns(df)

# Round numeric columns
df['Energy_Consumption_kWh'] = df['Energy_Consumption_kWh'].round(6)
df['Peak_hour_usage_ratio'] = df['Peak_hour_usage_ratio'].round(2)
df['Usage_consistency_score'] = df['Usage_consistency_score'].round(2)

# Fill NaN values appropriately
df = df.fillna('')

# Sort by timestamp
df = df.sort_values('Timestamp')

# Reorder columns to match original structure
column_order = [
    'Meter_ID', 'Usage_Type', 'Name', 'Address', 'Phone_Number', 'Region',
    'Tariff_Plan', 'Email', 'Household_Size', 'Dwelling_Type',
    'Energy_Consumption_kWh', 'Payment_Status', 'Timestamp', 'Business_Name',
    'Business_Address', 'Contact_Number', 'Business_Type', 'Contact_Email',
    'Operating_Hours', 'Floor_Area', 'Facility_Name', 'Facility_Address',
    'Industry_Type', 'Production_Capacity', 'Operating_Shifts',
    'Production_Volume', 'Month', 'Hour', 'Date', 'Is_Peak_Hour',
    'Peak_hour_usage_ratio', 'Usage_consistency_score'
]

df = df[column_order]

# Save to CSV
output_file = 'lusaka_energy_data.csv'
df.to_csv(output_file, index=False)

print(f"\n✅ Data generation complete!")
print(f"📊 Generated {len(df)} records")
print(f"💾 Saved to: {output_file}")
print(f"\nData Summary:")
print(f"  Residential: {len(df[df['Usage_Type'] == 'residential'])} records")
print(f"  Commercial:  {len(df[df['Usage_Type'] == 'commercial'])} records")
print(f"  Industrial:  {len(df[df['Usage_Type'] == 'industrial'])} records")
print(f"  Date range:  {df['Date'].min()} to {df['Date'].max()}")
print(f"  Regions:     {df['Region'].nunique()} Lusaka suburbs")
print(f"\nFirst 5 rows preview:")
print(df.head().to_string())

# Optional: Create a smaller sample for testing
sample_df = df.sample(n=100, random_state=42)
sample_df.to_csv('lusaka_energy_data_sample.csv', index=False)
print(f"\n📊 Sample file (100 records) saved to: lusaka_energy_data_sample.csv")