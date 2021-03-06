#!/usr/local/bin/python3
from playsound import playsound
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import sched
import time
import argparse
from enum import Enum


class Mode(Enum):
    ANY = 1
    DAY = 2
    SPAN = 3


found = ""


def main():
    global found
    parser = argparse.ArgumentParser(description='Find a vaccine appointment '
                                                 'from Tufts Med')
    parser.add_argument("--log", "-l", help="log appointments",
                        action="store_true")
    parser.add_argument("--day", "-d", type=strToDate,
                        help="find appointment for specific date - MMDDYYYY\n"
                             "if -e option is used, finds appointment between "
                             "dates")
    parser.add_argument("-endday", "-e", type=strToDate,
                        help="find appointment before date - MMDDYYYY")
    parser.add_argument("-frequency", "-f", type=int, default=10,
                        help="frequency to check appointments, in seconds")
    args = parser.parse_args()

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=chrome_options)

    login(driver)

    driver.get("https://www.zocdoc.com/wl/tuftscovid19vaccination/patientvaccine")

    mode = get_mode(args.day, args.endday)

    s = sched.scheduler(time.time, time.sleep)
    found = ""
    freq = args.frequency
    t = get_time(freq) + freq

    while not found:
        s.enterabs(t, 1, find_appt, argument=(args.day, args.endday,
                                              mode, args.log, driver))
        s.run()
        t += freq

    driver.switch_to.window(driver.current_window_handle)
    for _ in range(0, 3):
        playsound('SonicRing.mp3')


def find_appt(day, endday, mode, log, driver):
    driver.refresh()
    try:
        WebDriverWait(driver, 5).until(
            ec.presence_of_element_located((By.XPATH, "//figure/div"))
        )
        search_page(day, endday, mode, log, driver)
    except TimeoutException:
        if driver.title == "Oops, page not found - 404 Error - Zocdoc":
            print(f"\r\033[34m404 Error - Trying again\033[0m\033[K")
            driver.get("https://www.zocdoc.com/wl/tuftscovid19vaccination/patientvaccine")
            find_appt(day, endday, mode, log, driver)
        else:
            raise TimeoutException


def search_page(day, endday, mode, log, driver):
    global found
    try:
        driver.find_element(By.XPATH, '//*[@ data-test="timesgrid-timeslot"]')
        for e in driver.find_elements(By.XPATH, '//*[@ data-test="timesgrid-timeslot"]'):
            print(f"\r\033[1m{time.ctime(time.time())}\033[0m --- "
                  f"\033[32mappointment found!\033[0m\033[K\n"
                  f"{' ' * 25}{e.get_attribute('aria-label')}")
            starttime = e.get_attribute("data-starttime")
            if validate_apt(mode, starttime, day, endday):
                found = starttime
                break
        if log:
            f = open("findVaccLog.txt", "a")
            f.write(f"{time.ctime(time.time())}\n")
            found = ""
        return
    except NoSuchElementException:
        try:
            element = driver.find_element(By.XPATH, '//*[@ data-test="next-availability-button"]')
            print(f"\r\033[1m{time.ctime(time.time())}\033[0m --- "
                  f"\033[33mnext appointment found\033[0m\033[K")

            yes = driver.find_element(By.XPATH, '//*[@ data-test="modal-primary-button"]')
            yes.click()

            ActionChains(driver).move_to_element(element)
            element.click()
            time.sleep(1)
            search_page(day, endday, mode, log, driver)
            return

        except NoSuchElementException:
            pass
    print(f"\r\033[1m{time.ctime(time.time())}\033[0m --- "
          f"\033[31mno appointment found\033[0m\033[K", end="", flush=True)


def get_time(freq):
    tm = time.time()
    return tm - (tm % freq)


def get_mode(d, e):
    if d is not None:
        if e is not None:
            return Mode.SPAN
        else:
            return Mode.DAY
    else:
        return Mode.ANY


def validate_apt(mode, apt_starttime, day, endday):
    if mode == Mode.ANY:
        return True
    elif mode == Mode.DAY:
        return sameDate(apt_starttime, day)
    else:
        return inDateRange(apt_starttime, day, endday)


def strToDate(sdate):
    if len(sdate) != 8 \
            or not sdate.isnumeric() \
            or int(sdate[0:2]) not in range(1, 12) \
            or int(sdate[2:4]) not in range(1, 31):
        raise TypeError
    return int(sdate[4:8]+sdate[0:2]+sdate[2:4])


def inDateRange(starttime, day, endday):
    intstarttime = int(starttime[0:10].replace("-", ""))
    return day <= intstarttime <= endday


def sameDate(starttime, day):
    return int(starttime[0:10].replace("-", "")) == day


def login(driver):
    print("First, login to zocdoc. This will make the appointment signup faster.")
    driver.get("https://www.zocdoc.com/signin")
    input("Press enter to continue")

    def insurance_prompt():
        b = input("It is even faster if you put in your insurance information and "
                  "address.\nWould you like to do that now? [y/N] ")
        if b.lower() == "y":
            driver.get("https://www.zocdoc.com/patient/editprofile")
            input("press enter to continue")
        elif b.lower() == "n" or not b:
            pass
        else:
            print(f"{b} is not a valid answer.")
            insurance_prompt()

    insurance_prompt()
    print("Looking for appointments...")


if __name__ == '__main__':
    main()
