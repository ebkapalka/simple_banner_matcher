from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
import time

from browsercontrol.goamtch_navigator import wait_for_spinner


def wait_for_verifier_load(driver: webdriver, timeout=300):
    """
    Wait for the verifier page to load, checking multiple elements for specific text.
    :param driver: webdriver
    :param timeout: time to wait for the page to load
    :return: None
    """

    def any_element_contains_text(dr: webdriver) -> bool:
        """
        Check if any of the elements contain the text "SRIPREL"
        :return: whether any of the elements contain the text "SRIPREL"
        """
        elements = dr.find_elements(By.CLASS_NAME, "workspace-title")
        return any("SRIPREL" in element.text for element in elements)

    WebDriverWait(driver, timeout).until(any_element_contains_text)


def filter_again(driver: webdriver, env: str, timeout=300):
    """
    Set the configuration for the verifier page
    :param driver: webdriver
    :param env: environment to use
    :param timeout: time to wait for the page to load
    :return: None
    """
    driver.get(f"https://{env}banner.montana.edu/BannerAdmin?form=SRIPREL")
    wait_for_verifier_load(driver)
    selector_filter_elements = (By.CLASS_NAME, 'middleDivRow')
    selector_text_input = (By.XPATH, ".//input")
    selector_button_go = (By.CLASS_NAME, "ui-buttonGo")
    btn = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable(selector_button_go))
    elems = driver.find_elements(*selector_filter_elements)
    for index, elem in enumerate(elems):
        try:
            elem_labels = elem.find_elements(By.XPATH, ".//label")
            elem_label_text = elem_labels[2].text
        except NoSuchElementException:
            continue
        except IndexError:
            continue

        if "Match Status" in elem_label_text:
            cmd = "arguments[0].value = 'Suspense';"
            input_box = elem.find_elements(*selector_text_input)[1]
            while input_box.get_attribute("value") != "Suspense":
                input_box.click()
                driver.execute_script(cmd, input_box)
                time.sleep(1)
            btn.click()
            break


def get_prospect_ids(driver: webdriver, timeout=5) -> list[str]:
    """
    Fetch the rows from the verifier page
    :param driver: webdriver
    :param timeout: time to wait for the page to load
    :return: list of WebElements
    """
    prospect_ids = []
    wait_for_verifier_load(driver)

    # try to get the rows
    rows_xpath = '//div[@onmousedown="Frames.DataGrid.selection(this);"]'
    try:
        rows = WebDriverWait(driver, timeout).until(
            lambda dr: dr.find_elements(By.XPATH, rows_xpath)
            if len(dr.find_elements(By.XPATH, rows_xpath)) >= 2
            else False
        )
    except TimeoutException:
        rows = []
    if len(rows) <= 1:
        rows = driver.find_elements(By.XPATH, rows_xpath)

    # get the prospect ids
    for row in rows:
        try:
            child_div = row.find_element(By.XPATH, ".//div[1]/div[1]")
            prospect_id = child_div.text
        except NoSuchElementException:
            child_div = row.find_element(By.XPATH, ".//div[1]/input[1]")
            prospect_id = child_div.get_attribute("value")
        prospect_ids.append(prospect_id)
    return prospect_ids


def select_by_prospect_id(driver: webdriver, prospect_id: str) -> WebElement | None:
    """
    Select a row by the prospect id
    :param driver: webdriver
    :param prospect_id: id to search for
    :return: element if found, None if not found
    """
    wait_for_verifier_load(driver)
    elems = driver.find_elements(By.XPATH, '//div[@onmousedown="Frames.'
                                           'DataGrid.selection(this);"]')
    for elem in elems:
        try:
            child_div = elem.find_element(By.XPATH, ".//div[1]/div[1]")
            elem_id = child_div.text
        except:
            child_div = elem.find_element(By.XPATH, ".//div[1]/input[1]")
            elem_id = child_div.get_attribute("value")
        if elem_id == prospect_id:
            return elem
    print(f"Could not find prospect id {prospect_id}")
    time.sleep(500_000)
    return None


def select_and_nav(driver: webdriver, actions: ActionChains, elem: WebElement, timeout=30):
    def await_menu_related(dr: webdriver):
        """
        Used to check for the menu related element
        :param dr: webdriver
        :return:
        """
        menu_elem = dr.find_element(By.ID, 'menu-related')
        if "menu-open" not in menu_elem.get_attribute("class"):
            actions.key_down(Keys.ALT).key_down(Keys.SHIFT)
            actions.send_keys('r')
            actions.key_up(Keys.SHIFT).key_up(Keys.ALT)
            actions.perform()
            time.sleep(0.1)
            return False
        return True

    try:
        while elem.get_attribute("aria-selected") != "true":
            time.sleep(.1)
            elem.click()
    except:
        pass

    WebDriverWait(driver, timeout).until(await_menu_related)
    driver.find_element("xpath", '//*[@data-action="GOTO_MATCH"]').click()
    continue_btn = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@data-member="SPAIDEN_ASSOCIATE_PERSON_BTN"]')))
    continue_btn.click()
    continue_btn = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@data-member="EXECUTE_BTN"]')))
    continue_btn.click()
    continue_btn = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@data-member="CHECK_BTN"]')))
    wait_for_spinner(driver, 300)
    continue_btn.click()
    wait_for_spinner(driver, 300)
