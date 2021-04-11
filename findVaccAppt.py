#!/usr/local/bin/python3
from playsound import playsound
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import sched
import time

FREQ = 10
LOG = True


def find_appt(t):
    driver.refresh()
    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.XPATH, "//figure/div"))
    )
    search_page(t)


def search_page(t):
    try:
        driver.find_element(By.XPATH, '//*[@ data-test="timesgrid-timeslot"]')
        if LOG:
            f = open("findVaccLog.txt", "a")
            f.write(f"{time.ctime(time.time())}\n")
            s.enterabs(t + FREQ, 1, find_appt, argument=((t + FREQ),))
            s.run()
        else:
            for _ in range(0, 3):
                playsound('SonicRing.mp3')
        return
    except NoSuchElementException:
        try:
            # search for next appointment
            #     if found click yes, scroll, click next appointment, search page

            element = driver.find_element(By.XPATH, '//*[@ data-test="next-availability-button"]')
            print(f"next availability found at {time.ctime(time.time())}")
            if LOG:
                f = open("findVaccLog.txt", "a")
                f.write(f"{time.ctime(time.time())}\n")
                s.enterabs(t + FREQ, 1, find_appt, argument=((t + FREQ),))
                s.run()
            else:
                for _ in range(0, 3):
                    playsound('SonicRing.mp3')
            return

            # for _ in range(0, 3):
            #     playsound('SonicRing.mp3')
            # f = open("findVaccLog.txt", "a")
            # f.write(f"{time.ctime(time.time())}")
            # return


            # yes = driver.find_element(By.XPATH, '//*[@ data-test="modal-primary-button"]')
            # yes.click()
            # book_online = driver.find_element(By.XPATH, '//*[@ data-test="book-online-button"]')
            # book_online.click()
            # element.click()
            #
            # search_page(t)
            return
            # playsound('SonicRing.mp3')
            # search_page(t)
            # return
        except NoSuchElementException:
            pass

    print(f"no appointment found at {time.ctime(time.time())}")
    s.enterabs(t + FREQ, 1, find_appt, argument=((t + FREQ),))
    s.run()


def get_time():
    t = time.time()
    return t - (t % FREQ)


if __name__ == '__main__':
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.zocdoc.com/wl/tuftscovid19vaccination/patientvaccine")
    s = sched.scheduler(time.time, time.sleep)
    s.enter(0, 1, find_appt, argument=(get_time(),))
    s.run()

"""
    found = false
    while not found
        schedule and run
"""