import requests
import re
from datetime import datetime, timezone
import numpy
from scipy.signal import argrelextrema

def _is_leap_year(year):
  return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def get_perigees():
  url = "https://aa.usno.navy.mil/calculated/positions/geocentric"  

  start_date = datetime.now(timezone.utc).date().replace(day = 1) # start on first day of month
  start_month = start_date.month
  start_year = start_date.year
  reps = 8760

  # if current month is jan and current year is LEAP
  # or current month is feb and (current year OR next year are LEAPS)
  # or current month is > feb and next year is LEAP
  if (start_month == 1 and _is_leap_year(start_year)) \
  or (start_month == 2 and (_is_leap_year(start_year) or _is_leap_year(start_year + 1))) \
  or (start_month > 2 and _is_leap_year(start_year + 1)):
    reps += 24
    

  payload = {
    "ID": "AA",
    "task": "6",
    "body": "11",
    "date": start_date,
    "time": "00:00:00.000",
    "intv_mag": "1.00",
    "intv_unit": "2",
    "reps": reps, # number of iterations ... hours in a year
    "submit": "Get Data"
  }

  r = requests.get(url, params=payload)

  pattern = '^(\d{4}\s[A-Za-z]{3}\s[0-9]{2}).*?(\d+\.\d{3})$'

  results = re.findall(pattern, r.text, flags=re.MULTILINE)

  dates = []
  distances = []
  for result in results:
    date = datetime.strptime(result[0], '%Y %b %d')
    dates.append(date)
    distances.append(float(result[1]))

  x = numpy.array(distances)
  indices = argrelextrema(x, numpy.less)


  perigee_dates = []
  for i in indices[0]:
    perigee_dates.append(dates[i])

  return perigee_dates
