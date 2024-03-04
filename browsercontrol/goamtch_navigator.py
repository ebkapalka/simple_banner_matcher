from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from pprint import pprint
import time


def get_prospect_attributes(driver: webdriver, timeout=300) -> dict[str, str]:
    """
    Get the attributes of the prospect from the GOAMTCH page
    :param driver: webdriver
    :param timeout: time to wait for the page to load
    :return: dictionary of attributes
    """
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, '//*[@data-member="LAST_NAME"]')))
    wait_for_spinner(driver, 300)
    return {
        "last name": driver.find_element(By.ID, 'inp:gotcmme_lastName').get_attribute('title'),
        "first name": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeFirstName').get_attribute('title'),
        "middle name": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeMi').get_attribute('title'),
        "street 1": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeStreetLine1').get_attribute('title'),
        "city": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeCity').get_attribute('title'),
        "state": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeStatCode').get_attribute('title'),
        "zipcode": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeZip').get_attribute('title')[:5],
        "dd": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeBirthDay').get_attribute('title'),
        "mm": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeBirthMon').get_attribute('title'),
        "yyyy": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeBirthYear').get_attribute('title'),
        "phone area": driver.find_element(By.ID, 'inp:gotcmme_gotcmmePhoneArea').get_attribute('value'),
        "phone number": driver.find_element(By.ID, 'inp:gotcmme_gotcmmePhoneNumber').get_attribute('value'),
        "email": driver.find_element(By.ID, 'inp:gotcmme_gotcmmeEmailAddress').get_attribute('title').lower()
    }


def get_potential_match_attributes(driver: webdriver) -> dict:
    """
    Get the attributes of the potential matches from the GOAMTCH page
    :param driver: webdriver
    :return: dictionary of attributes
    """
    wait_for_spinner(driver, 300)
    match_tab = driver.find_element(By.ID, "tabGoamtchTabCanvas_tab1")
    while match_tab.get_attribute("aria-selected") != "true":
        time.sleep(.1)
        match_tab.click()
        wait_for_spinner(driver, 300)

    match_container = driver.find_element(By.ID, "grdGovcmid")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, ".//div[contains(@class, 'active') and "
                                                  "@onmousedown='Frames.DataGrid.selection(this);']")))
    match_rows = match_container.find_elements(By.XPATH, './/div[@onmousedown="Frames'
                                                         '.DataGrid.selection(this);"]')
    all_data = {}
    for row in match_rows:
        cols = row.find_elements(By.XPATH, './div')
        gid = cols[5].find_element(
            By.XPATH, './*').get_attribute("title")
        all_data[gid] = {
            "name": cols[0].text,
            "birthday": cols[1].text,
            "address": '='.join(cols[2].text.split('=')[1:]),
            "phone": '='.join(cols[3].text.split('=')[1:]),
            "email": '='.join(cols[4].text.split('=')[1:]).lower(),
            "gender": cols[6].text,
        }
    button_next = driver.find_elements(By.CLASS_NAME, 'ui-grid-pager-next')[1]
    if "ui-state-disabled" not in button_next.get_attribute("class"):
        print("Multiple pages of matches detected...")
        time.sleep(10)
        wait_for_spinner(driver, 300)
        button_next.click()
        all_data.update(get_potential_match_attributes(driver))
    return all_data


def select_by_match_id(driver: webdriver, prospect_id: str) -> None:
    """
    Select a row by the prospect id
    :param driver: webdriver
    :param prospect_id: prospect id to search for
    :return: WebElement if found, None if not found
    """
    if not prospect_id:
        button_new_record = driver.find_element(By.ID, "createBtn")
        button_new_record.click()
    else:
        match_container = driver.find_element(By.ID, "grdGovcmid")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, ".//div[contains(@class, 'active') and "
                                                      "@onmousedown='Frames.DataGrid.selection(this);']")))
        match_rows = match_container.find_elements(By.XPATH, './/div[@onmousedown="Frames'
                                                             '.DataGrid.selection(this);"]')
        matched_elem = None
        for row in match_rows:
            cols = row.find_elements(By.XPATH, './div')
            gid = cols[5].find_element(
                By.XPATH, './*').get_attribute("title")
            if gid == prospect_id:
                matched_elem = row
                break
        # TODO: add page navigation logic for multiple pages of matches

        if matched_elem:
            while matched_elem.get_attribute("aria-selected") != "true":
                time.sleep(.1)
                matched_elem.click()
                wait_for_spinner(driver, 300)
            button_save = driver.find_element(By.XPATH, '//a[@data-action="SAVE"]')
            wait_for_spinner(driver, 300)
            button_save.click()
        else:
            print("No match found")

    window_popup = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.CLASS_NAME, "workspace-notifications-menu")))
    button_popup = window_popup.find_element(By.XPATH, './/button')
    wait_for_spinner(driver, 300)
    button_popup.click()


def wait_for_spinner(driver: webdriver, timeout=300):
    """
    Wait for the spinner to disappear
    :param driver: webdriver
    :param timeout: time to wait for the spinner to disappear
    :return: None
    """
    WebDriverWait(driver, timeout).until(
        EC.invisibility_of_element((By.CLASS_NAME, "fa-spinner")))
