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
        self.processed_ids = set()
        self.batch_ids = set()
        self.driver = webdriver.Chrome()
        self.await_login()
        self.main_loop()

    def await_login(self):
        """
        Waits for the user to login to Banner
        :return: None
        """
        self.driver.get("https://prodbanner.montana.edu/applicationNavigator/seamless")
        WebDriverWait(self.driver, 300).until(EC.title_is("Application Navigator"))
        print("Banner Login Successful")
        self.driver.get("https://prodbanner.montana.edu/BannerAdmin?form=SRIPREL&vpdi_code="
                        "BZ&appnav_vpdi_code=BZ&ban_args=&ban_mode=xe")

    def main_loop(self):
        """
        The main loop of the program
        :return: None
        """
        print("Main Loop")
        filter_again(self.driver)
        time.sleep(100)
        # self.batch_ids = get_prospect_ids(self.driver)
        # print(self.batch_ids)

        # for prospect_id in self.batch_ids:
        #     ...
        # if self.batch_ids.issubset(self.processed_ids):
        #     print("No new prospects found")
        #     return
