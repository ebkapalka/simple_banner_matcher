from selenium.webdriver.support import expected_conditions as EC
from selenium.common import StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium import webdriver
import time

# TODO: refactor the way multiple pages of matches are handled,
#  so that the potential matches are checked before navigating
#  to the next page of matches

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

    # click the match tab if it is not already selected
    match_tab = driver.find_element(By.ID, "tabGoamtchTabCanvas_tab1")
    while match_tab.get_attribute("aria-selected") != "true":
        time.sleep(.1)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "tabGoamtchTabCanvas_tab1")))
        try:
            match_tab.click()
        except:
            pass
        wait_for_spinner(driver, 300)

    # find match rows in match container

    # iterate through match rows and add to dictionary
    all_data = {}
    num_pages = driver.find_elements(By.CLASS_NAME, 'ui-total-pages')[1].text
    for page in range(int(num_pages)):
        match_container = driver.find_element(By.ID, "grdGovcmid")
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, ".//div[contains(@class, 'active') and "
                                                  "@onmousedown='Frames.DataGrid.selection(this);']")))
        match_rows = match_container.find_elements(By.XPATH, './/div[@onmousedown="Frames'
                                                             '.DataGrid.selection(this);"]')
        page_data = {}
        for row in match_rows:
            cols = row.find_elements(By.XPATH, './div')
            gid = cols[5].find_element(
                By.XPATH, './*').get_attribute("title")
            page_data[gid] = {
                "name": cols[0].text,
                "name_alt": cols[0].text,
                "birthday": cols[1].text,
                "address": '='.join(cols[2].text.split('=')[1:]),
                "phone": '='.join(cols[3].text.split('=')[1:]),
                "email": '='.join(cols[4].text.split('=')[1:]).lower(),
                "gender": cols[6].text,
            }
        all_data.update(page_data)
        next_page(driver, direction="FWD")

    return all_data


def find_matched_element(driver, prospect_id):
    match_container = driver.find_element(By.ID, "grdGovcmid")
    match_rows = match_container.find_elements(By.XPATH, './/div[@onmousedown="Frames.DataGrid.selection(this);"]')
    for row in match_rows:
        cols = row.find_elements(By.XPATH, './div')
        gid = cols[5].find_element(By.XPATH, './*').get_attribute("title")
        if gid == prospect_id:
            return row
    return None


def select_by_match_id(driver: webdriver, actions: ActionChains, prospect_id: str) -> None:
    """
    Select a row by the prospect id
    :param driver: webdriver
    :param prospect_id: id to search for
    :return: None
    """
    matched_elem = find_matched_element(driver, prospect_id)
    if matched_elem:
        try:
            while matched_elem.get_attribute("aria-selected") != "true":
                try:
                    matched_elem.click()
                except:
                    actions.move_to_element(matched_elem).perform()
                time.sleep(.1)
                wait_for_spinner(driver, 300)
        except StaleElementReferenceException:
            matched_elem = find_matched_element(driver, prospect_id)  # Refetch the element
            if matched_elem:
                matched_elem.click()
                wait_for_spinner(driver, 300)
        wait_for_spinner(driver, 300)
        button_select = driver.find_element(By.ID, 'selectBtn')
        button_select.click()
    else:
        print("No match found")


def next_page(driver: webdriver, direction="FWD") -> None:
    """
    Click the next page button
    :param driver: webdriver
    :param direction: FWD or BACK
    :return: None
    """
    if direction == "FWD":
        selector_button = (By.CLASS_NAME, 'ui-grid-pager-next')
        button = driver.find_elements(*selector_button)[1]
    else:
        selector_button = (By.CLASS_NAME, 'ui-grid-pager-previous')
        button = driver.find_elements(*selector_button)[1]

    if "ui-state-disabled" not in button.get_attribute("class"):
        print("Multiple pages of matches detected...")
        wait_for_spinner(driver, 300)
        try:
            button.click()
        except:
            pass
        # time.sleep(1000)
        # sys.exit()


def create_new_record(driver: webdriver) -> None:
    """
    Click the new record button
    :param driver: webdriver
    :return: None
    """
    button_new_record = driver.find_element(By.ID, "createBtn")
    button_new_record.click()


def skip_record(driver: webdriver) -> None:
    """
    Click the close GOAMTCH button
    :param driver: webdriver
    :return: None
    """
    button_close = driver.find_element(By.XPATH, '//a[@title="Close (Ctrl+Q)"]')
    button_close.click()


def handle_popup(driver: webdriver) -> None:
    """
    Handle the popup that appears when a new record is created or when a record is saved
    :param driver: webdriver
    :return: None
    """
    window_popup = WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.CLASS_NAME, "workspace-notifications-menu")))
    try:
        button_popup = window_popup.find_element(By.XPATH, './/button')
        wait_for_spinner(driver, 300)
        button_popup.click()
    except:
        time.sleep(0.5)


def wait_for_spinner(driver: webdriver, timeout=300):
    """
    Wait for the spinner to disappear
    :param driver: webdriver
    :param timeout: time to wait for the spinner to disappear
    :return: None
    """
    WebDriverWait(driver, timeout).until(
        EC.invisibility_of_element((By.CLASS_NAME, "fa-spinner")))
