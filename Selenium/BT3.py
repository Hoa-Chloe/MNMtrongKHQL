from selenium import webdriver
from selenium.webdriver.common.by import By
import time

#Khoi tao Webdriver
driver = webdriver.Chrome()

#Mo trang
url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22P%22"
driver.get(url)

#Doi trang tai
time.sleep(2)

#Lay ra tat ca the ul trong div.div-col
ul_tags = driver.find_elements(By.CSS_SELECTOR, "div.div-col ul")
print("Số lượng <ul> trong div.div-col:", len(ul_tags))

titles = []
links = []

# Duyệt tất cả <ul>
for ul in ul_tags:
    li_tags = ul.find_elements(By.TAG_NAME, "li")
    for li in li_tags:
        try:
            a = li.find_element(By.TAG_NAME, "a")
            titles.append(a.get_attribute("title"))
            links.append(a.get_attribute("href"))
        except:
            pass  # nếu li không có <a> thì bỏ qua

# In kết quả
print("\nTitles:")
for t in titles:
    print(t)

print("\nLinks:")
for l in links:
    print(l)

#Dong webdriver
driver.quit()
