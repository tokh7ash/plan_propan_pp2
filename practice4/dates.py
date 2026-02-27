from datetime import datetime, timedelta, timezone
#1
today = datetime.now()
five_days_ago = today - timedelta(days=5)
print("1)", five_days_ago.strftime("%Y-%m-%d"))
#2
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)
print("2)", yesterday.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d"), tomorrow.strftime("%Y-%m-%d"))
#3
no_microseconds = today.replace(microsecond=0)
print("3)", no_microseconds.strftime("%Y-%m-%d %H:%M:%S"))
#4
date1 = datetime(2024, 1, 1, tzinfo=timezone.utc)
date2 = datetime(2024, 3, 1, tzinfo=timezone.utc)
diff = date2 - date1
print("4)", int(diff.total_seconds()), "seconds")