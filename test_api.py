import requests
import pandas as pd

API_KEY = "FOMVwCXRM2Bh7vsiTj4nDMou29SSEC6m"
BASE_URL = "https://analytics.alertcalifornia.org/v1"

response = requests.get(
    f"{BASE_URL}/uptime/daily",
    headers={"X-Api-Key": API_KEY},
    params={"format": "csv"}
)

from io import StringIO
df = pd.read_csv(StringIO(response.text))

print(df.shape)
print(df.head())