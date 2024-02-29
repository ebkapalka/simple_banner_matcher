"""
The table navigator expects that the curtrently active page is
the verifier page (Electronic Prospect Inquiry; SRIPREL).
"""
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
import sys


def wait_for_verifier_load(driver: webdriver, timeout=300):
    """
    Wait for the verifier page to load, checking multiple elements for specific text.
    :param driver: webdriver
    :param timeout: time to wait for the page to load
    :return: None
    """
    def any_element_contains_text(driver) -> bool:
        """
        Check if any of the elements contain the text "SRIPREL"
        :return: whether any of the elements contain the text "SRIPREL"
        """
        elements = driver.find_elements(By.CLASS_NAME, "workspace-title")
        return any("SRIPREL" in element.text for element in elements)

    print("Waiting for verifier page to load...")
    WebDriverWait(driver, timeout).until(any_element_contains_text)
    print("Verifier page loaded")


def filter_again(driver: webdriver, timeout=300):
    """
    Set the configuration for the verifier page
    :param driver: webdriver
    :param timeout: time to wait for the page to load
    :return: None
    """
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
            input_box = elem.find_elements(
                *selector_text_input)[1]
            input_box.click()
            cmd = "arguments[0].value = 'Suspense';"
            driver.execute_script(cmd, input_box)
            btn.click()
            break


def get_prospect_ids(driver: webdriver, timeout=300) -> list[str]:
    """
    Fetch the rows from the verifier page
    :param driver: webdriver
    :param timeout: time to wait for the page to load
    :return: list of WebElements
    """
    prospect_ids = []
    wait_for_verifier_load(driver)
    print("Fetching Prospect IDs from verifier page...")
    time.sleep(10)
    rows = driver.find_elements(By.XPATH, '//div[@onmousedown="Frames.DataGrid.selection(this);"]')
    print(len(rows))
    for row in rows:
        try:
            child_div = row.find_element(By.XPATH, ".//div[1]/div[1]")
        except:
            child_div = row.find_element(By.XPATH, ".//div[1]/input[1]")
        prospect_id = child_div.text
        print(prospect_id)
        prospect_ids.append(prospect_id)


def select_row_by_prospect_id(driver: webdriver, prospect_id: str, timeout=300) -> WebElement:
    ...
