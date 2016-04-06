import unittest
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import HTMLTestRunner


class Map(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Chrome('../chromedriver')

    def test_p1(self):
        browser = self.browser
        browser.get('http://localhost:8000/posts/walkscore/')

        browser.maximize_window()
        print(browser.page_source)

        el = browser.find_element_by_id('houseaddress')
        el.send_keys('1400 Fruitdale ave, San Jose, CA')
        el.send_keys(Keys.ENTER)

        sleep(2)

        try:
            WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "bk-plot")))
        except:
            print("Cannot Plot the data within 10 seconds or Graph not available")

    def tearDown(self):
        self.browser.close()
        self.browser.quit()


if __name__ == "__main__":
    HTMLTestRunner.main()
