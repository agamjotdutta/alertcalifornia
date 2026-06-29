import pandas as pd

# Load the data
df = pd.read_csv("data.csv")

# Convert day to datetime
df['day'] = pd.to_datetime(df['day'])

# Define a failure as uptime below 95%
df['is_failure'] = df['uptimePct'] < 95.0

print("=== COUNTY ANALYSIS ===")
county = df.groupby('countyName').agg(
    avg_uptime=('uptimePct', 'mean'),
    failure_rate=('is_failure', 'mean'),
    total_days=('uptimePct', 'count')
).reset_index()
county['failure_rate'] = county['failure_rate'] * 100
county = county.sort_values('avg_uptime')
print(county.head(10))

print("\n=== SPONSOR ANALYSIS ===")
sponsor = df.groupby('sponsorName').agg(
    avg_uptime=('uptimePct', 'mean'),
    failure_rate=('is_failure', 'mean'),
    total_days=('uptimePct', 'count')
).reset_index()
sponsor['failure_rate'] = sponsor['failure_rate'] * 100
sponsor = sponsor.sort_values('avg_uptime')
print(sponsor)

print("\n=== WISP ANALYSIS ===")
wisp = df.groupby('wispName').agg(
    avg_uptime=('uptimePct', 'mean'),
    failure_rate=('is_failure', 'mean'),
    total_days=('uptimePct', 'count')
).reset_index()
wisp['failure_rate'] = wisp['failure_rate'] * 100
wisp = wisp.sort_values('avg_uptime')
print(wisp.head(10))

print("\n=== CAMERA AGE ANALYSIS ===")
df['streamDetectedOn'] = pd.to_datetime(df['streamDetectedOn'])
df['camera_age_years'] = (pd.Timestamp.now(tz='UTC') - df['streamDetectedOn']).dt.days / 365

df['age_bucket'] = pd.cut(df['camera_age_years'],
                           bins=[0, 1, 2, 3, 4, 5, 6, 7, 10],
                           labels=['0-1yr', '1-2yr', '2-3yr', '3-4yr', '4-5yr', '5-6yr', '6-7yr', '7+yr'])

age = df.groupby('age_bucket').agg(
    avg_uptime=('uptimePct', 'mean'),
    failure_rate=('is_failure', 'mean'),
    total_cameras=('streamId', 'nunique')
).reset_index()
age['failure_rate'] = age['failure_rate'] * 100
print(age)

print("\n=== CAMERA MODEL ANALYSIS ===")
model = df.groupby('model').agg(
    avg_uptime=('uptimePct', 'mean'),
    failure_rate=('is_failure', 'mean'),
    total_cameras=('streamId', 'nunique')
).reset_index()
model['failure_rate'] = model['failure_rate'] * 100
model = model.sort_values('avg_uptime')
print(model)

print("\n=== ELEVATION ANALYSIS ===")

# Pull elevation from cameras data - need to add it to fetch_data.py first
# For now load cameras separately
import requests
from io import StringIO

API_KEY = "FOMVwCXRM2Bh7vsiTj4nDMou29SSEC6m"
BASE_URL = "https://analytics.alertcalifornia.org/v1"
headers = {"X-Api-Key": API_KEY}

cameras_response = requests.get(f"{BASE_URL}/cameras", headers=headers)
cameras_df = pd.DataFrame(cameras_response.json())

# Merge elevation into main df
df_elev = df.merge(
    cameras_df[['deviceId', 'elevation']],
    on='deviceId',
    how='left'
)

# Create elevation buckets
df_elev['elev_bucket'] = pd.cut(df_elev['elevation'],
    bins=[0, 500, 1000, 1500, 2000, 2500, 5000],
    labels=['0-500m', '500-1000m', '1000-1500m', '1500-2000m', '2000-2500m', '2500m+'])

elev = df_elev.groupby('elev_bucket').agg(
    avg_uptime=('uptimePct', 'mean'),
    failure_rate=('is_failure', 'mean'),
    total_cameras=('streamId', 'nunique')
).reset_index()
elev['failure_rate'] = elev['failure_rate'] * 100
print(elev)

print("\n=== RECOVERY TIME ANALYSIS ===")

# Find days where camera was failing (below 95%)
# Then look at consecutive failures to estimate outage duration
df_sorted = df.sort_values(['streamId', 'day'])
df_sorted['prev_failure'] = df_sorted.groupby('streamId')['is_failure'].shift(1)

# Find start of outages (failure that wasn't failing day before)
df_sorted['outage_start'] = (df_sorted['is_failure'] == True) & (df_sorted['prev_failure'] == False)

# Count consecutive failure days per stream
df_sorted['outage_id'] = df_sorted.groupby('streamId')['outage_start'].cumsum()

# Only look at failure periods
failures_only = df_sorted[df_sorted['is_failure'] == True]

outage_length = failures_only.groupby(['streamId', 'outage_id']).agg(
    outage_days=('day', 'count'),
    county=('countyName', 'first'),
    sponsor=('sponsorName', 'first')
).reset_index()

print("Average outage length by county:")
county_recovery = outage_length.groupby('county')['outage_days'].mean().sort_values(ascending=False)
print(county_recovery.head(10))

print("\nLongest individual outages:")
print(outage_length.sort_values('outage_days', ascending=False).head(10))