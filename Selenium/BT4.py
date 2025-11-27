from builtins import range
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
# Khoi tao Webdriver
driver = webdriver.Chrome()

for i in range(65, 91):
    url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22"+chr(i)+"%22"
    try:
        # mo trang
        driver.get(url)
        # Doi 1 chut de tai trang
        time.sleep(3)
        # # Lay ra tat cac ca the url
        # ul_tags = driver.find_elements(By.XPATH, "//div[contains(@class,'div-col')]//li")
        # print(len(ul_tags))
        # # Chon the ul thu 21
        # ul_painters = ul_tags[20] 
        # Lay ra tat ca the <li> thuoc ul_painters
        li_tags = driver.find_elements(By.XPATH, "//div[contains(@class,'div-col')]//li")
        print("Số họa sĩ:", len(li_tags))
        # Tao danh sach cac url
        titles = [tag.find_element(By.TAG_NAME, "a").get_attribute("title") for tag in li_tags]
        # In ra title
        for title in titles:
            print(title)
    except:
        print("Error!")
# Dong webdriver
driver.quit()