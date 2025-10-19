from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time


def webscraping_selenium():
    while True:
        try:
            driver = webdriver.Chrome()
            url = "https://www.emsc.eu/Earthquake_information/"
            driver.get(url)
        except:
            reload_button = driver.find_element(
                By.CSS_SELECTOR, "button[id=reload-button]")
            reload_button.click()
        if driver.title == "Earthquake information":
            print("The website is loaded successfully.")
            break
        else:
            if driver:
                driver.quit()
            time.sleep(5)

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
    end_date.send_keys("19/10/2025")
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

    # Get number of events based on our filters. We need this for unittest.
    time.sleep(2)
    results_count = driver.find_element(By.CSS_SELECTOR, "div[id=nbres]")
    total_events_count = int(results_count.text.split()[1])

    time.sleep(2)
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
                date_time = row.find_element(
                    By.CLASS_NAME, "tbdat").text.split()[0:2]
                date_time = " ".join(date_time)
                latitude_deg = row.find_element(By.CLASS_NAME, "tblat").text
                longitude_deg = row.find_element(By.CLASS_NAME, "tblon").text
                depth_km = row.find_element(By.CLASS_NAME, "tbdep").text
                magnitude_type = row.find_element(
                    By.CLASS_NAME, "tbmagtyp").text
                magnitude_value = row.find_element(By.CLASS_NAME, "tbmag").text
                region = row.find_element(By.CLASS_NAME, "tbreg").text
                earthquake_info = {"date_time_UTC": date_time, "latitude_deg": latitude_deg, "longitude_deg": longitude_deg,
                                   "depth_km": depth_km, "magnitude_value": magnitude_value, "magnitude_type": magnitude_type,
                                   "region": region}

                all_rows_info.append(earthquake_info)
            next_page_button = driver.find_element(
                By.CSS_SELECTOR, "div.spes.spes1.pag")
            next_page_button.click()
            time.sleep(10)
    except:
        print("This was the last page")

    extracted_events_count = len(all_rows_info)
    print(
        f"A total of {extracted_events_count} records have been extracted successfully.")

    time.sleep(2)
    earthquakes_table = pd.DataFrame(all_rows_info)
    earthquakes_table.to_csv(
        "earthquakeDataAnalysis/JAPAN_EMSC.csv", encoding='utf-8-sig', index=False)

    driver.quit()

    return total_events_count, extracted_events_count


if __name__ == "__main__":
    webscraping_selenium()
