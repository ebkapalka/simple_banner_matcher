from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
from pprint import pprint
import atexit

from browsercontrol.goamtch_navigator import (
    get_potential_match_attributes,
    get_prospect_attributes,
    select_matched_record,
    select_by_match_id,
    create_new_record,
    handle_popup,
    skip_record
)
from browsercontrol.sriprel_navigator import (
    select_by_prospect_id,
    get_prospect_ids,
    select_and_nav,
    filter_again
)
from utilities.comparison_tool import compare_prospects


class BannerDriver:
    """
    This class is used to control the Banner web page.
    """

    def __init__(self, env="prod"):
        self.env = env
        self.options = webdriver.ChromeOptions()
        prefs = {
            'profile.default_content_setting_values.automatic_downloads': 1,
            'profile.password_manager_enabled': False,
            'credentials_enable_service': False,
            'autofill.profile_enabled': False,
        }
        self.options.add_experimental_option('prefs', prefs)
        self.options.add_argument("--disable-save-password-bubble")
        self.options.add_argument("--disable-autofill-keyboard-accessory-view")
        self.options.add_argument("--disable-prompt-on-repost")
        self.options.add_argument("--disable-autofill")
        self.driver = webdriver.Chrome(options=self.options)
        self.actions = ActionChains(self.driver)
        self.seen_prospects = set()
        self.stats = {
            "new person": 0,
            "skip": 0,
            "match": 0,
        }
        self.await_login()
        atexit.register(self.print_stats)
        self.main_loop()

    def await_login(self):
        """
        Waits for the user to log into Banner
        :return: None
        """
        print("Please log into Banner")
        self.driver.get(f"https://{self.env}banner.montana.edu/applicationNavigator/seamless")
        WebDriverWait(self.driver, 300).until(EC.title_is("Application Navigator"))
        print("Banner Login Successful")

    def main_loop(self):
        """
        The main loop of the program
        :return: None
        """
        page_number = 1
        while True:
            filter_again(self.driver, self.env)
            batch_ids = get_prospect_ids(self.driver)
            if not batch_ids:
                print("No suspended records found")
                return

            # handle multiple pages of skipped records
            prev_batch_ids = batch_ids.copy()
            while set(batch_ids).issubset(self.seen_prospects):
                button_next = self.driver.find_element(By.XPATH, '//span[@aria-label="Next Page"]')
                button_next.click()  # TODO: this is preventing graceful exit
                batch_ids = get_prospect_ids(self.driver)
                if batch_ids == prev_batch_ids:
                    print("No new records found")
                    return
                prev_batch_ids = batch_ids.copy()

            # handle each record on the page
            for index, prospect_id in enumerate(set(batch_ids)):
                if prospect_id in self.seen_prospects:
                    continue
                self.seen_prospects.add(prospect_id)
                elem = select_by_prospect_id(self.driver, prospect_id)
                select_and_nav(self.driver, self.actions, elem)
                prospect = get_prospect_attributes(self.driver)
                matches = get_potential_match_attributes(self.driver)
                match_gid = compare_prospects(prospect, matches)

                # handle the match
                if match_gid == "new person":
                    print(f"Pg:{page_number} #{index+1:>02} - Creating new record")
                    self.stats["new person"] += 1
                    create_new_record(self.driver)
                elif match_gid == "skip":
                    print(f"Pg:{page_number} #{index+1:>02} - Skipping record")
                    self.stats["skip"] += 1
                    skip_record(self.driver)
                    continue
                else:
                    print(f"Pg:{page_number} #{index+1:>02} - Selecting match {match_gid}")
                    self.stats["match"] += 1
                    select_by_match_id(self.driver, self.actions, match_gid)
                    select_matched_record(self.driver)
                handle_popup(self.driver)
            page_number += 1

    def print_stats(self):
        """
        Print the statistics of the BannerDriver
        :return: None
        """
        pprint(self.stats)
