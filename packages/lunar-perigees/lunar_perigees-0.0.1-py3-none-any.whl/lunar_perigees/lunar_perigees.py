import requests
import re
from datetime import datetime, timezone

def get_perigees():
  url = "https://aa.usno.navy.mil/calculated/positions/geocentric"

  payload = {
    "ID": "AA",
    "task": "5",
    "body": "11",
    "date": datetime.now(timezone.utc).date(),
    "time": datetime.now(timezone.utc).time(),
    "intv_mag": "1.00",
    "intv_unit": "1",
    "reps": "365", # number of iterations
    "submit": "Get Data"
  }

  r = requests.get(url, params=payload)

  pattern = '^(\d{4}\s[A-Za-z]{3}\s[0-9]{2}).*?(\d+\.\d{3})$'

  results = re.findall(pattern, r.text, flags=re.MULTILINE)

  grouped = {}
  for result in results:

    date = datetime.strptime(result[0], '%Y %b %d')
    day = date.day
    month = date.month
    year = date.year
    
    if year not in grouped:
      grouped[year] = {}

    if month not in grouped[year]:
      grouped[year][month] = {}

    grouped[year][month][day] = float(result[1])

  perigees = {}
  for year in grouped:
    if year not in perigees:
      perigees[year] = {}
    
    for month in grouped[year]:

      if month not in perigees[year]:
        perigees[year][month] = {}

      perigee_distance = min(grouped[year][month].values())

      perigee_day = ''
      for key, value in grouped[year][month].items():
        if value == perigee_distance:
          perigee_day = key
          break
      
      perigees[year][month][perigee_day] = perigee_distance

  return perigees
