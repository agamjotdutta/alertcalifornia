import requests
import pandas as pd
from io import StringIO

API_KEY = "FOMVwCXRM2Bh7vsiTj4nDMou29SSEC6m"
BASE_URL = "https://analytics.alertcalifornia.org/v1"

headers = {"X-Api-Key": API_KEY}

# Pull bulk historical uptime data
print("Pulling uptime data...")
uptime_response = requests.get(
    f"{BASE_URL}/uptime/daily",
    headers=headers,
    params={"format": "csv", "limit": 10000}
)
uptime_df = pd.read_csv(StringIO(uptime_response.text))
print(f"Uptime data: {uptime_df.shape}")

# Pull stream metadata
print("Pulling stream metadata...")
streams_response = requests.get(
    f"{BASE_URL}/streams",
    headers=headers,
    params={"is_mobile": "false"}
)
streams_df = pd.DataFrame(streams_response.json())
print(f"Stream data: {streams_df.shape}")

# Pull camera metadata (has installedOn)
print("Pulling camera metadata...")
cameras_response = requests.get(
    f"{BASE_URL}/cameras",
    headers=headers
)
cameras_df = pd.DataFrame(cameras_response.json())
print(f"Camera data: {cameras_df.shape}")

# Merge uptime with stream metadata on streamId
merged_df = uptime_df.merge(
    streams_df[['streamId', 'deviceId', 'countyName', 'sponsorName', 'wispName', 'manufacturer', 'model', 'streamDetectedOn']],
    on='streamId',
    how='left'
)

# Then merge with camera metadata to get installedOn
merged_df = merged_df.merge(
    cameras_df[['deviceId', 'installedOn']],
    on='deviceId',
    how='left'
)

print(f"Merged data: {merged_df.shape}")
print(merged_df.head())

merged_df.to_csv("data.csv", index=False)
print("Saved to data.csv")