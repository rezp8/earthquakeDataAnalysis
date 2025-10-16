from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time

driver = webdriver.Chrome()
url = "https://www.emsc.eu/Earthquake_information/"
driver.get(url)

time.sleep(3)
try:
    cookies_button = driver.find_element(By.CLASS_NAME, "cookieButton")
    cookies_button.click()
    print("Cookies were accepted")
except:
    print("There was no cookies pop up")

time.sleep(3)
start_date = driver.find_element(By.ID, "datemin")
start_date.send_keys("15/09/2025")
end_date = driver.find_element(By.ID, "datemax")
end_date.send_keys("14/10/2025")
lat_min = driver.find_element(By.ID, "latmin")
lat_min.send_keys("24")
lat_max = driver.find_element(By.ID, "latmax")
lat_max.send_keys("46")
long_min = driver.find_element(By.ID, "lonmin")
long_min.send_keys("123")
long_max = driver.find_element(By.ID, "lonmax")
long_max.send_keys("146")

time.sleep(3)
search_button = driver.find_element(By.CSS_SELECTOR, "input[value=Search]")
search_button.click()

time.sleep(3)
magnitude_expand_button = driver.find_element(
    By.CLASS_NAME, "tbmag").find_element(By.CSS_SELECTOR, "th > span")
magnitude_expand_button.click()


time.sleep(3)
try:
    all_rows_info = []
    while True:
        data_table = driver.find_element(
            By.CSS_SELECTOR, "table.eqs.table-scroll")
        data_rows = data_table.find_elements(By.TAG_NAME, "tr")[1:]
        for row in data_rows:
            date_time = row.find_element(By.CLASS_NAME, "tbdat").text
            # date_time = row.find_element(By.CLASS_NAME, "tbdat").text.split()
            # date_ = date_time[0]
            # time_ = date_time[1]
            latitude_deg = row.find_element(By.CLASS_NAME, "tblat").text
            longitude_deg = row.find_element(By.CLASS_NAME, "tblon").text
            depth_km = row.find_element(By.CLASS_NAME, "tbdep").text
            magnitude_type = row.find_element(By.CLASS_NAME, "tbmagtyp").text
            magnitude_value = row.find_element(By.CLASS_NAME, "tbmag").text
            region = row.find_element(By.CLASS_NAME, "tbreg").text
            earthquake_info = {"date_time_UTC": date_time, "latitude_deg": latitude_deg, "longitude_deg": longitude_deg,
                               "depth_km": depth_km, "magnitude_value": magnitude_value, "magnitude_type": magnitude_type,
                               "region": region}
            # earthquake_info = {"date": date_, "time_UTC": time_, "latitude_deg": latitude_deg, "longitude_deg": longitude_deg,
            #                    "depth_km": depth_km, "magnitude_value": magnitude_value, "magnitude_type": magnitude_type,
            #                    "region": region}
            all_rows_info.append(earthquake_info)
        next_page_button = driver.find_element(
            By.CSS_SELECTOR, "div.spes.spes1.pag")
        next_page_button.click()
        time.sleep(10)
except:
    print("This was the last page")

print(f"Details of {len(all_rows_info)} events were successfully extracted")
print(f"First event: {all_rows_info[-1]}")
print(f"Last event: {all_rows_info[0]}")


time.sleep(2)
earthquakes_table = pd.DataFrame(all_rows_info)
# print(earthquakes_table)
earthquakes_table.to_csv(
    "earthquakeDataAnalysis/JAPAN_EMSC.csv", encoding='utf-8-sig', index=False)

driver.quit()
