import os

print("=== ExpiryEngine Daily Run ===")

os.system("python H:/ExpiryEngine/downloader/download_daily.py")
os.system("python H:/ExpiryEngine/cleaner/clean_raw.py")
os.system("python H:/ExpiryEngine/cleaner/update_master.py")
os.system("python H:/ExpiryEngine/expiry/build_weekly.py")
os.system("python H:/ExpiryEngine/expiry/build_monthly.py")

print("=== DONE ===")
