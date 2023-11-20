from datetime import datetime

# Unix timestamp
timestamp = 1700182777

# Convert the timestamp to a datetime object
dt_object = datetime.utcfromtimestamp(timestamp)

# Format the datetime object to a string, if desired
formatted_date = dt_object.strftime("%Y-%m-%d %H:%M:%S")

print("Date and Time:", formatted_date)
print((datetime.utcnow().timestamp() - timestamp)/60)