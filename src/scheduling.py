import schedule
import datetime

import initialise

def test(message):
    print(message)


schedule.every(10).minutes.do(initialise.run)

while True:
    schedule.run_pending()
