import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


def fetch_earthquake_data(datemin='2025-09-15', datemax='2025-10-19', latmax=46,
                          lonmin=123, lonmax=146, latmin=24, magmin=0, fmt='html', nmax=1000):
    """
    Fetch earthquake data from GEOFON for Japan region.
    """
    base_url = 'https://geofon.gfz.de/eqinfo/list.php'

    params = {
        'datemin': datemin,
        'datemax': datemax,
        'latmax': latmax,
        'lonmin': lonmin,
        'lonmax': lonmax,
        'latmin': latmin,
        'magmin': magmin,
        'fmt': fmt,
        'nmax': nmax
    }

    print(f"Fetching data from {base_url}...")
    response = requests.get(base_url, params=params)
    response.raise_for_status()  # Raise an error for bad status codes
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the earthquake list container
    eqlist = soup.find('div', {'id': 'eqlist'})
    if not eqlist:
        print("No earthquake data found in the response")
        return pd.DataFrame()

    # Get number of events based on our filters. We need this for unittest.
    total_events_count = len(soup.find_all('div', class_=[
        'flex-row row eqinfo-all evnrow', 'flex-row row eqinfo-all oddrow']))
    print(f"Total events based on our filters: {total_events_count}")

    earthquakes = []

    # Each earthquake is in a div with class "flex-row row eqinfo-all"
    # Find even and odd rows separately
    evn_event_rows = soup.find_all(
        'div', class_='flex-row row eqinfo-all evnrow')
    odd_event_rows = soup.find_all(
        'div', class_='flex-row row eqinfo-all oddrow')

    # Create alternating sequence: first from even, then odd, then even, etc.
    event_rows = []
    max_length = max(len(evn_event_rows), len(odd_event_rows))

    for i in range(max_length):
        if i < len(evn_event_rows):
            event_rows.append(evn_event_rows[i])
        if i < len(odd_event_rows):
            event_rows.append(odd_event_rows[i])

    for row in event_rows:
        try:
            # Extract magnitude from the magbox span
            mag_span = row.find('span', class_='magbox')
            if not mag_span:
                continue
            magnitude = float(mag_span.get_text(strip=True))

            # Extract region from the strong tag
            region_strong = row.find('strong')
            if not region_strong:
                continue
            region = region_strong.get_text(strip=True)

            # Extract coordinates from the title attribute
            region_div = row.find('div', title=True)
            coordinates = region_div.get('title', '') if region_div else ''

            latitude = None
            longitude = None
            if coordinates:
                try:
                    # Split by comma
                    parts = coordinates.split(', ')
                    if len(parts) == 2:
                        lon_part = parts[0].replace('°E', '').replace('°W', '')
                        lat_part = parts[1].replace('°N', '').replace('°S', '')
                        longitude = float(lon_part)
                        latitude = float(lat_part)
                except (ValueError, IndexError):
                    pass

            # Extract time and depth from the second row
            time_depth_row = row.find_all('div', class_='row')[1]
            time_depth_text = time_depth_row.get_text(strip=True)

            # Parse time and depth
            # checking the format: "2025-10-11 14:24:22.4 (≤2 h ago) 86*"
            time_text = ""
            depth_text = ""

            # Split by the pull-right span to separate time and depth
            time_span = time_depth_row.find('span', class_='pull-right')
            if time_span:
                # Remove the pull-right span to get time
                time_span.extract()
                time_text = time_depth_row.get_text(strip=True)
                # Clean up time text (remove relative time info)
                time_text = str(time_text.split(
                    '(')[0].strip().split('.')[0].strip())
                depth_text = str(time_span.get_text(
                    strip=True).replace('*', '').strip())
            else:
                # Fallback: try to extract from the full text
                time_text = str(time_depth_text.split(
                    '(')[0].strip().split('.')[0].strip())

                import re
                depth_match = re.search(r'(\d+)\*?$', time_depth_text)
                if depth_match:
                    depth_text = str(depth_match.group(1))

            # Extract event ID from the parent link
            parent_link = row.find_parent('a')
            event_id = ""
            if parent_link and parent_link.get('href'):
                href = parent_link.get('href')
                # Extract ID from URL like "event.php?id=gfz2025tydw"
                if 'id=' in href:
                    event_id = href.split('id=')[1]

            earthquakes.append({
                'Magnitude': magnitude,
                'Region': region,
                'DateTime_UTC': time_text,
                'Depth_km': depth_text if depth_text else None,
                'Latitude': latitude,
                'Longitude': longitude,
                'Event_ID': event_id
            })

        except (ValueError, AttributeError, IndexError) as e:
            print(f"Error parsing earthquake data: {e}")
            continue

    df = pd.DataFrame(earthquakes)
    extracted_events_count = len(df)
    print(f"Successfully fetched {extracted_events_count} earthquake records")
    df.to_csv('earthquakeDataAnalysis/JAPAN_GEOFON.csv',
              index=False, encoding='utf-8')
    print("Data saved to 'JAPAN_GEOFON.csv'")

    return total_events_count, extracted_events_count


if __name__ == "__main__":
    fetch_earthquake_data()
