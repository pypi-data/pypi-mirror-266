# lunar perigees

a packages that uses infrastructure provided by the U.S. Naval Observatory to calculate lunar perigees.

utilizing the package will provide perigee data from the first of the current month through one year into the future.

eg: if today is April 9 2024, perigee data will be provided from April 1 2024 through March 31 2025

instructions:

`pip install lunar_perigees`

`from lunar_perigees import lunar_perigees`

eg: `print(lunar_perigees.get_perigees())`
