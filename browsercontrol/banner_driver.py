from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
import time

from browsercontrol.sriprel_navigator import (filter_again, get_prospect_ids,
                                              select_by_prospect_id, select_and_nav)
from browsercontrol.goamtch_navigator import (get_prospect_attributes,
                                              get_potential_match_attributes)


class BannerDriver:
    """
    This class is used to control the Banner web page.
    """
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.actions = ActionChains(self.driver)
        self.await_login()
        self.main_loop()

    def await_login(self):
        """
        Waits for the user to log into Banner
        :return: None
        """
        print("Please log into Banner")
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
                elem = select_by_prospect_id(self.driver, prospect_id)
                select_and_nav(self.driver, self.actions, elem)
                print(get_prospect_attributes(self.driver))
                get_potential_match_attributes(self.driver)
                time.sleep(1000)
