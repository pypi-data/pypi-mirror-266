import requests
import re
from datetime import datetime, timezone
import numpy
from scipy.signal import argrelextrema

def get_perigees():
  url = "https://aa.usno.navy.mil/calculated/positions/geocentric"

  payload = {
    "ID": "AA",
    "task": "5",
    "body": "11",
    "date": datetime.now(timezone.utc).date().replace(day = 1), # start on first day of month
    "time": datetime.now(timezone.utc).time(),
    "intv_mag": "1.00",
    "intv_unit": "1",
    "reps": "365", # number of iterations
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
