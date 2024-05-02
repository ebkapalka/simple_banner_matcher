from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
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
    Get the attributes of the prospect from the GOAMTCH page using JavaScript
    :param driver: webdriver
    :param timeout: time to wait for the page to load
    :return: dictionary of attributes
    """
    WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.XPATH, '//*[@data-member="LAST_NAME"]')))
    wait_for_spinner(driver, 300)

    js_script = """
    var data = {};
    data['last name'] = document.getElementById('inp:gotcmme_lastName').title;
    data['first name'] = document.getElementById('inp:gotcmme_gotcmmeFirstName').title;
    data['middle name'] = document.getElementById('inp:gotcmme_gotcmmeMi').title;
    data['street 1'] = document.getElementById('inp:gotcmme_gotcmmeStreetLine1').title;
    data['city'] = document.getElementById('inp:gotcmme_gotcmmeCity').title;
    data['state'] = document.getElementById('inp:gotcmme_gotcmmeStatCode').title;
    data['zipcode'] = document.getElementById('inp:gotcmme_gotcmmeZip').title.substring(0, 5);
    data['dd'] = document.getElementById('inp:gotcmme_gotcmmeBirthDay').title;
    data['mm'] = document.getElementById('inp:gotcmme_gotcmmeBirthMon').title;
    data['yyyy'] = document.getElementById('inp:gotcmme_gotcmmeBirthYear').title;
    data['phone area'] = document.getElementById('inp:gotcmme_gotcmmePhoneArea').value;
    data['phone number'] = document.getElementById('inp:gotcmme_gotcmmePhoneNumber').value;
    data['email'] = document.getElementById('inp:gotcmme_gotcmmeEmailAddress').title.toLowerCase();
    return data;
    """

    attributes = driver.execute_script(js_script)
    return attributes


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

    # iterate through match rows and add to dictionary
    all_data = {}
    num_pages = driver.find_elements(By.CLASS_NAME, 'ui-total-pages')[1].text
    for page in range(int(num_pages)):
        rows_data = driver.execute_script(
            """
            var rows = [];
            var container = document.getElementById('grdGovcmid');            
            var matchRows = container.querySelectorAll('div[onmousedown="Frames.DataGrid.selection(this);"]');
            matchRows.forEach(row => {
                var cols = row.children;
                var data = {};
                
                data.name = (cols[0].querySelector('input') || cols[0].querySelector('div')).title;
                data.name_alt = data.name;
                data.birthday = (cols[1].querySelector('input') || cols[1].querySelector('div')).title;
        
                var addressTitle = (cols[2].querySelector('input') || cols[2].querySelector('div')).title;
                if (addressTitle.includes('=')) {
                    var parts = addressTitle.split('=');
                    if (parts.length > 1) {
                        data.address = parts[1].split(' ').slice(0, -1).join(' ');
                    } else {
                        data.address = ''; // or some default value
                    }
                } else {
                    data.address = '';
                }
        
                var phoneTitle = (cols[3].querySelector('input') || cols[3].querySelector('div')).title;
                if (phoneTitle.includes('=')) {
                    data.phone = phoneTitle.split('=')[1];
                } else {
                    data.phone = '';
                }
        
                var emailTitle = (cols[4].querySelector('input') || cols[4].querySelector('div')).title.toLowerCase();
                if (emailTitle.includes('=')) {
                    data.email = emailTitle.split('=')[1];
                } else {
                    data.email = '';
                }
        
                data.gid = (cols[5].querySelector('input') || cols[5].querySelector('div')).title;
                data.gender = (cols[6].querySelector('input') || cols[6].querySelector('div')).title;
        
                rows.push(data);
            });
            return rows;
            """
        )

        page_data = {row['gid']: row for row in rows_data}
        all_data.update(page_data)
        next_page(driver, direction="FWD")
    return all_data


def find_matched_element(driver: webdriver, prospect_id: str) -> WebElement | None:
    """
    Find the matched element by the prospect id
    :param driver: webdriver
    :param prospect_id: gid to search for
    :return: web element
    """
    match_container = driver.find_element(By.ID, "grdGovcmid")
    match_rows = match_container.find_elements(
        By.XPATH, './/div[@onmousedown="Frames.DataGrid.selection(this);"]')
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
    :param actions: ActionChains
    :param prospect_id: id to search for
    :return: None
    """
    matched_elem = find_matched_element(driver, prospect_id)
    if matched_elem:
        try:
            try_count = 0
            while matched_elem.get_attribute("aria-selected") != "true":
                try:
                    matched_elem.click()
                except:
                    if try_count < 10:
                        # normal attempt to scroll to the element
                        actions.move_to_element(matched_elem).perform()
                    else:
                        # use JavaScript to scroll to the element
                        # TODO: test to see if this even works
                        driver.execute_script("arguments[0].click();", matched_elem)
                    try_count += 1
                    print("    Tries:", try_count)
                time.sleep(.1)
                wait_for_spinner(driver, 300)
        except StaleElementReferenceException:
            matched_elem = find_matched_element(driver, prospect_id)  # Refetch the element
            actions.move_to_element(matched_elem).perform()
            if matched_elem:
                matched_elem.click()
                wait_for_spinner(driver, 300)
        wait_for_spinner(driver, 300)
    else:
        print("No match found")


def next_page(driver: webdriver, direction="FWD") -> None:
    """
    Click the next page button
    :param driver: webdriver
    :param direction: FWD or BACK
    :return: None
    """
    initial_page = int(driver.find_elements(
        By.CLASS_NAME, 'ui-input-paging')[1].get_attribute("value"))
    current_page = initial_page
    if direction == "FWD":
        selector_button = (By.CLASS_NAME, 'ui-grid-pager-next')
        button = driver.find_elements(*selector_button)[1]
    else:
        selector_button = (By.CLASS_NAME, 'ui-grid-pager-previous')
        button = driver.find_elements(*selector_button)[1]

    if "ui-state-disabled" not in button.get_attribute("class"):
        print("Multiple pages of matches detected...")
        while initial_page == current_page:
            try:
                button.click()
                wait_for_spinner(driver, 300)
                current_page = int(driver.find_elements(
                    By.CLASS_NAME, 'ui-input-paging')[1].get_attribute("value"))
            except:
                pass


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


def select_matched_record(driver: webdriver) -> None:
    """
    Click the select button
    :param driver: webdriver
    :return: None
    """
    button_select = driver.find_element(By.ID, 'selectBtn')
    button_select.click()


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
    WebDriverWait(driver, timeout).until_not(
        EC.text_to_be_present_in_element(
            (By.XPATH, '//*[@id="status"]/div/span[4]'),
            "executing action"
        )
    )
