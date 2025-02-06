import schedule
import datetime

import initialise

def test(message):
    print(message)


schedule.every().monday.at("00:00").do(initialise.run)

while True:
    schedule.run_pending()
