"""
The table navigator expects that the curtrently active page is
the verifier page (Electronic Prospect Inquiry; SRIPREL).
"""
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
import time


def wait_for_verifier_load(driver: webdriver, timeout=300):
    selector_workspace_title = ("body > nav.workspace-header.navbar.navbar-default.navbar-expand-lg.navbar-fixed-top > "
                                "div > div.navbar-header > ul > li:nth-child(3) > h2")
    WebDriverWait(driver, timeout).until(
        lambda d: "SRIPREL" in d.find_element(By.CSS_SELECTOR, selector_workspace_title).text
    )


def configure_verifier(driver: webdriver, timeout=300):
    """
    Set the configuration for the verifier page
    :return: None
    """
    wait_for_verifier_load(driver)
    selector_match_status = "#frames16_ac"
    selector_go_button = ("#frames3_content > div.filterForm.ui-widget.ui-filterpanel.ui-basic-filter-mode > div > "
                          "div.legendDown > span > button.primary-button.ui-buttonGo")
    input_match_status = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, selector_match_status)))
    driver.execute_script("arguments[0].value = arguments[1];",
                          input_match_status, "Suspense")
    button_go = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, selector_go_button)))
    button_go.click()
    time.sleep(100)


def get_rows(driver: webdriver, timeout=300) -> list[WebElement]:
    wait_for_verifier_load(driver)


def next_page(driver: webdriver, timeout=300):
    wait_for_verifier_load(driver)
