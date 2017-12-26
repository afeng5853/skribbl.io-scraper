import sys
import os
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from PIL import Image
from StringIO import StringIO


class wait_for_image(object):
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        try:
            element = EC._find_element(driver, self.locator)
            return element.text != ''  and int(element.text) >= 1 and int(element.text) <= 2
        except StaleElementReferenceException:
            return False
        
class wait_for_result(object):
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        try:
            element = EC._find_element(driver, self.locator)
            return "The word was:" in element.text
        except StaleElementReferenceException:
            return False

def play(driver, username):
    """
    Driver goes to skribbl.io, enters a username, and presses the play button
    
    :param driver: WebDriver
    :param username: Username to play the game with (empty string for random name)
    :returns: None
    """
    driver.get("https://skribbl.io/")
    actions = ActionChains(driver)
    name = driver.find_element_by_id("inputName")
    play = driver.find_element_by_class_name("btn-success")
    actions.click(name).send_keys(username)
    actions.click(play)
    actions.perform()

def createFolder(directory):
    """
    Creates a folder at the specified directory if it doesn't exist
    :param directory: the specified directory as a string
    :returns: None
    """
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' +  directory)

def get_image(driver):
    """
    Waits for an image to be finished by a player and screenshots the browser
    :param driver: WebDriver
    :returns: a jpg of the browser
    """
    wait = WebDriverWait(driver, 80)
    try:
        if(wait.until(wait_for_image((By.XPATH, "//*[@id='timer']"))) == False):
             return None
    except TimeoutException:
        logging.warning('Timeout Exception for getting image')
        return None
    return driver.get_screenshot_as_png()

def get_word_of_image(driver):
    """
    Waits for the result overlay to pop up and grabs the word of the image
    :param driver: WebDriver
    :returns: the string of the word of the image
    """
    wait = WebDriverWait(driver, 10)
    try:
        if(wait.until(wait_for_result((By.XPATH, "//*[@id='overlay']/div/div[1]"))) == False):
            return None
    except TimeoutException:
        logging.warning('Timeout Exception for getting word of image')
        return None
    result = driver.find_element(By.XPATH, "//*[@id='overlay']/div/div[1]")
    return result.text.split(": ",1)[1]

def save_image(img, img_word):
    """
    Saves a jpg in the folder called img_word at a hard-coded directory
    :param img: jpg
    :param img_word: word of img
    :returns: None
    """
    createFolder("C:\\Python27\\img\\" + img_word)
    id = 0
    dir = "C:\\Python27\\img\\" + img_word + "\\" + str(id) + ".png"
    while (os.path.exists(dir)):
        id += 1
        dir = "C:\\Python27\\img\\" + img_word + "\\" + str(id) + ".png"
    img.save(dir)
    logging.info("Saving image of " + img_word + " to " + dir)

def bot(driver):
    """
    A bot that scrapes images and the correspodning word of the image
    :param driver: WebDriver
    :returns: None
    """
    while (True):
        play(driver, "ml-scraper")
        img_jpg = get_image(driver)
        if img_jpg is None:
            continue

        img_word = get_word_of_image(driver)
        if img_word is None:
            continue

        image = Image.open(StringIO(img_jpg))
        cropped_image = image.crop((265, 154, 1078, 764))
        
        save_image(cropped_image, img_word)


def main():
    #logging configuration
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.basicConfig(filename='events.log',level=logging.DEBUG)

    #chrome configratuions
    chrome_options = Options()  
    chrome_options.add_argument("--headless")

    #driver configuration
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.set_window_size(1500, 1000)
    
    bot(driver)
    pass

if __name__ == '__main__':
    print("start")
    sys.exit(main())
