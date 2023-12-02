import cv2
import numpy as np 
import pytesseract
import config
import time 
import datetime
import os
import json

import selenium
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

import base64
from io import BytesIO
from PIL import Image

from core.image_processing import removeIsland
import config

import logging
logging.basicConfig(filename='queue.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)


class QueueChecker: 
    def __init__(self, kdmid_subdomain, order_id, code):
        self.kdmid_subdomain = kdmid_subdomain
        self.order_id = order_id
        self.code = code
        self.directory = os.path.join('userdata', f"{self.order_id}_{self.code}")
        self.url = 'http://'+self.kdmid_subdomain+'.kdmid.ru/queue/OrderInfo.aspx?id='+self.order_id+'&cd='+self.code
        self.image_name = 'captcha_processed.png'
        self.screen_name = "screenshot0.png"
        self.button_dalee = "//input[@id='ctl00_MainContent_ButtonA']"
        self.button_inscribe = "//input[@id='ctl00_MainContent_ButtonB']"
        self.main_button_id = "//input[@id='ctl00_MainContent_Button1']" 
        self.text_form = "//input[@id='ctl00_MainContent_txtCode']"
        self.checkbox = "//input[@id='ctl00_MainContent_RadioButtonList1_0']" 
        self.error_code = "//span[@id='ctl00_MainContent_Label_Message']"
        self.captcha_error = "//span[@id='ctl00_MainContent_lblCodeErr']"
        self.main_content = "//span[@id='ctl00_MainContent_Content']" # span id="ctl00_MainContent_Content"

    def write_success_file(self, text, status): 
        d ={}
        d['status'] = status
        d['message'] = text

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
            
        if d['status'] == 'success':
            with open(os.path.join(self.directory, "success.json"), 'w', encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False)
        elif d['status'] == 'error':
            with open(os.path.join(self.directory, "error.json"), 'w', encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False)
        
    def check_exists_by_xpath(self, xpath, driver):
        mark = False
        try:
            driver.find_element(By.XPATH, xpath)
            mark = True
            return mark
        except NoSuchElementException:
            return mark
    
    def screenshot_captcha(self, driver, error_screen=None): 
		# make a screenshot of the window, crop the image to get captcha only, 
		# process the image: remove grey background, make letters black
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        driver.save_screenshot(os.path.join(self.directory, "screenshot.png"))
        
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
        area.save(os.path.join(self.directory, self.screen_name), 'PNG')
        
        img  = cv2.imread(os.path.join(self.directory, self.screen_name))
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
        cv2.imwrite(os.path.join(self.directory, self.image_name), out*255)
    
    def recognize_image(self): 
        digits = pytesseract.image_to_string(os.path.join(self.directory, self.image_name), config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
        return digits

    def check_queue(self): 
        message = ''
        status = ''
        print('Checking queue for: {} - {}'.format(self.order_id, self.code))
        logging.info('Checking queue for: {} - {}'.format(self.order_id, self.code))
        # set Chrome options and driver
        chrome_options = Options()
        chrome_options.add_argument("--headless") # imitation of browser
        driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", options=chrome_options)
        driver.maximize_window()
        driver.get(self.url)     
        error = True
        error_screen = False # error if captcha is not recognized
        # iterate until captcha is recognized 
        while error: 
            self.screenshot_captcha(driver, error_screen)
            digits = self.recognize_image()
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, self.text_form))).send_keys(str(digits))
            time.sleep(1)       

            # imitate clicks on the buttons
            if self.check_exists_by_xpath(self.button_dalee, driver): 
                driver.find_element(By.XPATH, self.button_dalee).click()

            if self.check_exists_by_xpath(self.button_inscribe, driver): 
                driver.find_element(By.XPATH, self.button_inscribe).click()
            # go to the next page
            window_after = driver.window_handles[0]
            driver.switch_to.window(window_after)

            error = False # stop the iteration 
            
            try: 
                driver.find_element(By.XPATH, self.main_button_id)    # check if there is main button to click, if not, return to captcha
            except: 
                error = True
                error_screen = True
                # if the text form to write captcha is not found, probably, it is "not a robot" captcha
                try:
                    element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, self.text_form))
                    )
                except:
                    
                    print('HERE')
                    if self.check_exists_by_xpath(self.main_content, driver): 
                        element = driver.find_element(By.XPATH, self.main_content)
                        message = element.text
                        status = 'error'
                        self.write_success_file(message, status)
                        logging.warning(f'{message}')
                        logging.warning(f'{driver.page_source}')
                        return message
                    
                    print("Element not found, probably 'not a robot' check")
                    message = 'Что-то пошло не так, возможно, проблемы с сайтом, попробуйте еще раз позже.'
                    status = 'error'
                    self.write_success_file(message, status)
                    logging.warning(f'{message}')
                    logging.warning(f'{driver.page_source}')
                    return message
                
                # clear the text form and repeat the process
                driver.find_element(By.XPATH, self.text_form).clear()

        # we are on the page with calendar, if the checkbox is found, click it and write the success file, 
        # else send a message to the user that there are no free timeslots
        try: 
            if self.check_exists_by_xpath(self.checkbox, driver): 			
                driver.find_element(By.XPATH,self.checkbox).click()
                check_box = driver.find_element(By.XPATH, self.checkbox)
                
                val = check_box.get_attribute("value")
                message = 'Appointment date: {}, time: {}, purpose: {}'.format(
                    val.split('|')[1].split('T')[0], 
                    val.split('|')[1].split('T')[1], 
                    val.split('|')[-1]
                    )
                logging.info(message)
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, self.main_button_id))).click()  
                status = 'success'         
                self.write_success_file(message, str(status))			
            else: 
                message = '{} - no free timeslots for now. Next check in {} hours'.format(datetime.date.today(), config.EVERY_HOURS)
                print(message)
                logging.info(message)
        except: 
            message = '{} --- no free timeslots for now'.format(datetime.date.today())
            logging.info(message)
            
        driver.quit()

        return message

