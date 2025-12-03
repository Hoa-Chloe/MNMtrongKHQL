from selenium import webdriver
from selenium.webdriver.firefox.service import Service
import time

# Duong dan den file thuc thi Geckodriver
gecko_path = r"C:\Users\NHU\OneDrive\Documents\VSC\MNM\Selenium\geckodriver.exe"

# Khoi toi doi tuong dich vu voi duong geckodriver
ser = Service(gecko_path)

# Tao tuy chon
options = webdriver.firefox.options.Options()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"

# Thiet lap firefox chi hien thi giao dien
options.headless = False

# Khoi tao driver
driver = webdriver.Firefox(options = options, service=ser)

# Tao url
url = 'http://pythonscraping.com/pages/javascript/ajaxDemo.html'
# Truy cap
driver.get(url)

# In ra noi dung cua trang web
print("Before: ###########################################################\n")
print(driver.page_source)

# Tam dung khoang 3 giay
time.sleep(3)

# In lai
print("\n\n\n\nAfter: ===================================================\n")
print(driver.page_source)

#Dong
driver.quit()