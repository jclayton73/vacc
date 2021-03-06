# FindVaccAppt
    
Python program that watches the Tufts Medical Center Vaccine appointments page for new availability. 

## Installation
Clone the repo, install dependencies.

Dependencies:
- python3
- Chromium
- selenium
- playsound
- sched
- argparse

## Usage
> python3 findVaccAppt.py [-h] [--log] [--day DAY] [-endday ENDDAY] [-frequency FREQUENCY]

If your python is in /usr/local/bin/python3
> ./findVaccAppt.py [-h] [--log] [--day DAY] [-endday ENDDAY] [-frequency FREQUENCY]


### Arguments
| Flag | Description |
| ---- | ----------- |
| --day, -d | find appointment for specific date - MMDDYYYY <br> if -e option is used, finds appointment between dates |
| --endday, -e | find appointment before date - MMDDYYYY |
| --frequency, -f | frequency to check for appointments, in seconds |
| --log, -l | instead of finding an appointment and finishing, writes the time that the appointment was found and continues. used to find the best frequency to check for appointments. |
