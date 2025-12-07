from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re

############################################################################
# I. Tao dataframe rong va khoi tao driver
d = pd.DataFrame({'name': [], 'birth': [], 'death': [], 'nationality': []})
all_links = []

driver = webdriver.Chrome()

############################################################################
# II. Lay ra tat ca duong dan (Phase 1)
print("--- Đang lấy danh sách links ---")
try:
    # URL danh sach hoa si bat dau bang chu "F" (ban co the doi thanh chu khac)
    url = "https://en.wikipedia.org/wiki/List_of_painters_by_name_beginning_with_%22F%22"
    driver.get(url)
    time.sleep(3)

    # Lay vung chua noi dung chinh
    content_div = driver.find_element(By.CLASS_NAME, "mw-parser-output")
    
    # Lay tat ca cac the ul
    ul_tags = content_div.find_elements(By.TAG_NAME, "ul")

    for ul in ul_tags:
        li_tags = ul.find_elements(By.TAG_NAME, "li")
        # Chi lay nhung list dai (list hoa si thuong dai hon 5-10 dong)
        if len(li_tags) > 5: 
            for tag in li_tags:
                try:
                    link = tag.find_element(By.TAG_NAME, "a").get_attribute("href")
                    
                    # === KHÚC QUAN TRỌNG NHẤT: BỘ LỌC LINK ===
                    # 1. Phai co "/wiki/"
                    # 2. Khong chua "List_of_painters" (De tranh lay nham link A, B, C, D...)
                    # 3. Khong chua "cite_note" (tranh link chu thich)
                    # 4. Khong chua "Category", "Special", "Help" (link he thong)
                    if ("/wiki/" in link) and \
                       ("List_of_painters" not in link) and \
                       ("cite_note" not in link) and \
                       ("Category:" not in link) and \
                       ("Special:" not in link) and \
                       ("Help:" not in link):
                        
                        all_links.append(link)
                except:
                    pass
    
    # Xoa cac link trung nhau neu co
    all_links = list(set(all_links))
    print(f"Tim thay {len(all_links)} hoa si thuc su.")

except Exception as e:
    print("Error getting links:", e)

############################################################################
# III. Duyet qua tung link va lay thong tin (Phase 2)

count = 0
for link in all_links:
    # # --- TEST 5 NGUOI DAU TIEN ---
    # if count >= 5:
    #     break
    count += 1

    print(f"({count}) Dang xu ly: {link}")
    
    try:
        driver.get(link)
        time.sleep(1) # Giam thoi gian cho xuong 1s cho nhanh

        # 1. Lay ten hoa si
        try:
            name = driver.find_element(By.ID, "firstHeading").text
        except:
            name = ""

        # 2. Lay ngay sinh
        try:
            birth_element = driver.find_element(By.XPATH, "//th[text()='Born']/following-sibling::td")
            birth = birth_element.text
            # Regex tim ngay thang nam
            res = re.findall(r'[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}', birth)
            birth = res[0] if res else birth # Neu regex ko ra thi lay text goc
        except:
            birth = ""

        # 3. Lay ngay mat
        try:
            death_element = driver.find_element(By.XPATH, "//th[text()='Died']/following-sibling::td")
            death = death_element.text
            res = re.findall(r'[0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4}', death)
            death = res[0] if res else death
        except:
            death = ""

        # 4. Lay quoc tich
        try:
            nationality_element = driver.find_element(By.XPATH, "//th[text()='Nationality']/following-sibling::td")
            nationality = nationality_element.text.strip()
        except:
            nationality = ""

        # Tao dictionary thong tin
        painter = {'name': name, 'birth': birth, 'death': death, 'nationality': nationality}

        # Chuyen doi thanh DataFrame
        painter_df = pd.DataFrame([painter])

        # Them vao DF chinh
        d = pd.concat([d, painter_df], ignore_index=True)

    except Exception as e:
        print(f"Loi tai link {link}: {e}")

############################################################################
# IV. Ket thuc
driver.quit()

print("\n--- KET QUA ---")
print(d)

d.to_excel("Painters_Fixed.xlsx", index=False)
print("File saved successfully.")