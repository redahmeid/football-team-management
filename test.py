import pandas as pd

# Load the data (assuming it's in a CSV format for this example)
data = pd.read_csv('data.txt')

# Convert the Time column to numeric values, just in case they're not
data['Time'] = pd.to_numeric(data['Time'], errors='coerce')

# Group by Player_ID and sum the Time values
total_minutes = data.groupby('Player_ID')['Time'].sum()

# The result will be a series with Player_ID as the index and their total minutes on the pitch as the values
print(total_minutes)
