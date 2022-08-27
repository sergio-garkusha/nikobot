from datetime import datetime
import pytz

# https://strftime.org/
# EET - Estern European Time (EEST, summertime, can be ignore since we care only about days)
date = "2022-08-18T20:51:07+00:00"
UATZ = pytz.timezone('EET')

today = datetime.now(UATZ)
date = datetime.fromisoformat(date)
delta = today - date
print("delta.days:", delta.days)

# Convert date from timestamp to our DB format
d = datetime.fromtimestamp(1661471395)
# https://strftime.org/
d_for_record = f'{d:%Y-%m-%d}T{d:%H:%M:%S}+00:00'
print("formatted date as a string:", d_for_record)
print("date for record:", datetime.fromisoformat(d_for_record))
