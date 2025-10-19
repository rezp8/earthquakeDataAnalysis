import requests
from datetime import datetime, timedelta

# end_date = datetime.today().date()
# start_date = end_date - timedelta(days=30)
def api_saving():
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "csv",
        "starttime": "2025-9-15",
        "endtime": "2025-10-19",
        "minlatitude": 24,
        "maxlatitude": 46,
        "minlongitude": 123,
        "maxlongitude": 146,
        "minmagnitude": 0
    }
    response = requests.get(url, params=params)
    with open("JAPAN_USGS.csv", "w", encoding="utf-8") as f:
            f.write(response.text)

api_saving()