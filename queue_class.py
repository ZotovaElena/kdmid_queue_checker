# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotVisibleException
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


import base64
from io import BytesIO

from PIL import Image

import cv2
import numpy as np 
import pytesseract
from image_processing import removeIsland
import config
import time 
import datetime
import sys 

import logging


logging.basicConfig(filename='queue.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH



class QueueChecker: 
    def __init__(self, kdmid_subdomain, order_id, code):
        self.kdmid_subdomain = kdmid_subdomain 
        self.order_id = order_id 
        self.code = code
        self.url = 'http://'+self.kdmid_subdomain+'.kdmid.ru/queue/OrderInfo.aspx?id='+self.order_id+'&cd='+self.code
        self.image_name = 'captcha_processed.png'
        self.screen_name = "screenshot0.png"
        self.button_dalee = "//input[@id='ctl00_MainContent_ButtonA']"
        self.button_b = "//input[@id='ctl00_MainContent_ButtonB']"
        self.main_button_id = "//input[@id='ctl00_MainContent_Button1']" 
        self.text_form = "//input[@id='ctl00_MainContent_txtCode']"
        self.checkbox = "//input[@id='ctl00_MainContent_RadioButtonList1_0']" 
        self.error_code = "//span[@id='ctl00_MainContent_Label_Message']"


    def write_success_file(self, text): 
        with open(self.order_id+"_"+self.code+"_success.txt", mode = "w", encoding="utf-8") as f:
            f.write(text)       
        
    def check_exists_by_xpath(self, xpath, driver):
        mark = False
        try:
            driver.find_element(By.XPATH, xpath)
            mark = True
            return mark
        except NoSuchElementException:
            return mark
       
    # def get_driver(self): 
    #     option = webdriver.ChromeOptions()
    #     option.add_argument("start-maximized")
    #     driver = webdriver.Chrome(ChromeDriverManager(driver_version='119.0.6045.124').install(), options=option)
    #     # driver = webdriver.Chrome(ChromeDriverManager(driver_version='114.0.5735.90').install()), options=option)
    #     driver.get('https://www.google.com/')
    #     return driver
    
    def screenshot_captcha(self, driver, error_screen=False): 
		   # make a screenshot of the window, crop the image to get captcha only, 
		   # process the image: remove grey background, make letters black
        driver.save_screenshot("screenshot.png")
        
        screenshot = driver.get_screenshot_as_base64()
        img = Image.open(BytesIO(base64.b64decode(screenshot)))
		

        element = driver.find_element(By.XPATH, '//img[@id="ctl00_MainContent_imgSecNum"]')
        loc  = element.location
        size = element.size

        left = loc['x']
        top = loc['y']
        right = (loc['x'] + size['width'])
        bottom = (loc['y'] + size['height'])
        screenshot = driver.get_screenshot_as_base64()
		  #Get size of the part of the screen visible in the screenshot
        screensize = (driver.execute_script("return document.body.clientWidth"), 
		              driver.execute_script("return window.innerHeight"))
        img = img.resize(screensize)
        
        box = (int(left), int(top), int(right), int(bottom))
        area = img.crop(box)
        area.save(self.screen_name, 'PNG')
        
        img  = cv2.imread(self.screen_name)
        # Convert to grayscale
        c_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        # Median filter
        out = cv2.medianBlur(c_gray,1)
        # Image thresholding 
        a = np.where(out>228, 1, out)
        out = np.where(a!=1, 0, a)
        # Islands removing with threshold = 30
        out = removeIsland(out, 30)
        # Median filter
        out = cv2.medianBlur(out,3)
        cv2.imwrite(self.image_name, out*255)
    
    def recognize_image(self): 
        digits = pytesseract.image_to_string(self.image_name, config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
        return digits

    def check_queue(self): 
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(ChromeDriverManager(driver_version='119.0.6045.124').install(), options=chrome_options)
        driver.maximize_window()
        driver.get(self.url) 
            
        error = True
        error_screen = False
        # iterate until captcha is recognized 
        while error: 
            
            self.screenshot_captcha(driver, error_screen)
            digits = self.recognize_image()
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, self.text_form))).send_keys(str(digits))
            time.sleep(3)       
            if self.check_exists_by_xpath(self.button_dalee, driver): 
                driver.find_element(By.XPATH, self.button_dalee).click()
            
            if self.check_exists_by_xpath(self.button_b, driver): 
                driver.find_element(By.XPATH, self.button_b).click()

            if self.error_code: 
                logging.info('Защитный код заявки задан неверно. Проверьте правильность введенных данных')
                sys.exit('Защитный код заявки задан неверно. Проверьте правильность введенных данных')

            window_after = driver.window_handles[0]
            driver.switch_to.window(window_after)
            
            error = False
            
            try: 
               driver.find_element(By.XPATH, self.main_button_id)    
            except: 
                error = True
                error_screen = True
                driver.find_element(By.XPATH, self.text_form).clear()
				
        if self.check_exists_by_xpath(self.checkbox, driver): 			
            driver.find_element(By.XPATH,self.checkbox).click()
            check_box = driver.find_element(By.XPATH, self.checkbox)
            val = check_box.get_attribute("value")
            logging.info('Appointment at: {}'.format(val))
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, self.main_button_id))).click()           
            self.write_success_file(str(val))			
        else: 
            logging.info('{} - no free timeslots for now'.format(datetime.date.today()))
            
        driver.quit()
