#!/usr/local/bin/python3
from playsound import playsound
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import sched
import time

FREQ = 10
LOG = False


def find_appt():
    driver.refresh()
    WebDriverWait(driver, 5).until(
        ec.presence_of_element_located((By.XPATH, "//figure/div"))
    )
    search_page()


def search_page():
    global found
    global t
    try:
        driver.find_element(By.XPATH, '//*[@ data-test="timesgrid-timeslot"]')
        print(f"availability found at {time.ctime(time.time())}")
        if LOG:
            f = open("findVaccLog.txt", "a")
            f.write(f"{time.ctime(time.time())}\n")
        found = True
        return
    except NoSuchElementException:
        print("no timesgrid")
        try:
            # search for next appointment
            #     if found click yes, scroll, click next appointment, search page

            element = driver.find_element(By.XPATH, '//*[@ data-test="next-availability-button"]')
            print(f"next availability found at {time.ctime(time.time())}")

            yes = driver.find_element(By.XPATH, '//*[@ data-test="modal-primary-button"]')
            yes.click()

            ActionChains(driver).move_to_element(element)
            element.click()
            print("searching page")
            time.sleep(1)
            search_page()
            return

        except NoSuchElementException:
            pass

    print(f"no appointment found at {time.ctime(time.time())}")
    t += FREQ


def get_time():
    tm = time.time()
    return tm - (tm % FREQ)


if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.zocdoc.com/wl/tuftscovid19vaccination/patientvaccine")
    s = sched.scheduler(time.time, time.sleep)
    found = False
    t = get_time()
    while not found:
        s.enterabs(t + FREQ, 1, find_appt)
        s.run()
        if LOG:
            found = False

    for _ in range(0, 3):
        playsound('SonicRing.mp3')
