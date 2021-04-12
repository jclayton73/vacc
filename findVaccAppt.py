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
import argparse
import pyttsx3

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
        element = driver.find_element(By.XPATH, '//*[@ data-test="timesgrid-timeslot"]')
        print(f"availability found at {time.ctime(time.time())}\n    for {element.get_attribute('data-starttime')}")
        if LOG:
            f = open("findVaccLog.txt", "a")
            f.write(f"{time.ctime(time.time())}\n")
        found = element.get_attribute("data-starttime")
        return
    except NoSuchElementException:
        try:
            # search for next appointment
            #     if found click yes, scroll, click next appointment, search page

            element = driver.find_element(By.XPATH, '//*[@ data-test="next-availability-button"]')
            print(f"next availability found at {time.ctime(time.time())}")

            yes = driver.find_element(By.XPATH, '//*[@ data-test="modal-primary-button"]')
            yes.click()

            ActionChains(driver).move_to_element(element)
            element.click()
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


def strToDate(sdate):
    if len(sdate) != 8 \
            or not sdate.isnumeric() \
            or int(sdate[0:2]) not in range(1, 12) \
            or int(sdate[2:4]) not in range(1, 31):
        raise TypeError
    return int(sdate)


#     compare to current date
#     make sure all numbers are within range

def inDateRange(starttime, day, endday):
    intstarttime = int(starttime[0:10].replace("-", ""))
    return day <= intstarttime <= endday


def sameDate(starttime, day):
    return int(starttime[0:10].replace("-", "")) == day


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Find a vaccine appointment from Tufts Med')
    parser.add_argument("--log", "-l", help="log appointments",
                        action="store_true")
    parser.add_argument("--day", "-d", type=strToDate, help="find appointment for specific date - MMDDYYYY\n"
                                                            "if -e option is used, finds appointment between dates")
    parser.add_argument("-endday", "-e", type=strToDate, help="find appointment before date - MMDDYYYY")
    args = parser.parse_args()

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)
    driver.get("https://www.zocdoc.com/wl/tuftscovid19vaccination/patientvaccine")

    s = sched.scheduler(time.time, time.sleep)
    found = ""
    t = get_time()
    LOG = args.log
    while not found:
        s.enterabs(t + FREQ, 1, find_appt)
        s.run()
        if LOG:
            found = None
        if found:
            if args.day is not None:
                if args.endday is not None:
                    if not inDateRange(found, args.day, args.endday):
                        found = ""
                else:
                    if not sameDate(found, args.day):
                        found = ""

    driver.switch_to.window(driver.current_window_handle)
    for _ in range(0, 3):
        playsound('SonicRing.mp3')
