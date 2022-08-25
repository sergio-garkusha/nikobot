from datetime import datetime
import pytz

# EET - Estern European Time (EEST, summertime, can be ignore since we care only about days)
date = "2022-08-18T20:51:07+00:00"
UATZ = pytz.timezone('EET')

today = datetime.now(UATZ)
date = datetime.fromisoformat(date)
delta = today - date

print(delta.days)
