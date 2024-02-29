from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
import time

from browsercontrol.sriprel_navigator import filter_again, get_prospect_ids


class BannerDriver:
    """
    This class is used to control the Banner web page.
    """
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.await_login()
        self.main_loop()

    def await_login(self):
        """
        Waits for the user to log into Banner
        :return: None
        """
        self.driver.get("https://prodbanner.montana.edu/applicationNavigator/seamless")
        WebDriverWait(self.driver, 300).until(EC.title_is("Application Navigator"))
        print("Banner Login Successful")

    def main_loop(self):
        """
        The main loop of the program
        :return: None
        """
        while True:
            filter_again(self.driver)
            batch_ids = get_prospect_ids(self.driver)
            if not batch_ids:
                print("No suspended records found")
                return
            for prospect_id in set(batch_ids):
                print(prospect_id)
                # TODO: navigate to it and do stuff
