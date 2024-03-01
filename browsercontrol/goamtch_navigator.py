from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from pprint import pprint


def get_prospect_attributes(driver: webdriver, timeout=300) -> dict[str, str]:
    """
    Get the attributes of the prospect from the GOAMTCH page
    :param driver: webdriver
    :param timeout: time to wait for the page to load
    :return: dictionary of attributes
    """
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, '//*[@data-member="LAST_NAME"]')))
    return {
        "last name": driver.find_element(By.ID, 'inp:gotcmme_lastName').get_attribute('title'),
        "first name": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeFirstName').get_attribute('title'),
        "middle name": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeMi').get_attribute('title'),
        "street 1": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeStreetLine1').get_attribute('title'),
        "city": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeCity').get_attribute('title'),
        "state": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeStatCode').get_attribute('title'),
        "zipcode": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeZip').get_attribute('title'),
        "dd": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeBirthDay').get_attribute('title'),
        "mm": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeBirthMon').get_attribute('title'),
        "yyyy": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeBirthYear').get_attribute('title'),
        "phone area": driver.find_element(By.ID, 'inp:gotcmme_gotcmmePhoneArea').get_attribute('value'),
        "phone number": driver.find_element(By.ID, 'inp:gotcmme_gotcmmePhoneNumber').get_attribute('value'),
        "email": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeEmailAddress').get_attribute('title')
    }


def get_potential_match_attributes(driver: webdriver) -> dict:
    """
    Get the attributes of the potential matches from the GOAMTCH page
    :param driver: webdriver
    :return: dictionary of attributes
    """
    match_container = driver.find_element(By.ID, "grdGovcmid")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, ".//div[contains(@class, 'active') and "
                                                  "@onmousedown='Frames.DataGrid.selection(this);']")))
    match_rows = match_container.find_elements(By.XPATH, './/div[@onmousedown="Frames'
                                                         '.DataGrid.selection(this);"]')
    all_data = {}
    for row in match_rows:
        cols = row.find_elements(By.XPATH, './div')
        title_attribute = cols[5].find_element(
            By.XPATH, './*').get_attribute("title")
        all_data[title_attribute] = {
            "name": cols[0].text,
            "birthday": cols[1].text,
            "address": cols[2].text,
            "phone": cols[3].text,
            "email": cols[4].text,
            "gender": cols[6].text,
        }
        pprint(all_data)
    return all_data
