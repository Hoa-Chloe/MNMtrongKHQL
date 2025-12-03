import getpass
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 1. NHẬP DATA ---
print("--- AUTO LOGIN FACEBOOK + SCRAPE POSTS ---")
email = input("Nhập Email/SĐT Facebook: ")
password_user = getpass.getpass("Nhập Mật khẩu: ")

# --- 2. SETUP FIREFOX ---
gecko_path = r"C:\Users\NHU\OneDrive\Documents\VSC\MNM\Selenium\geckodriver.exe"
ser = Service(gecko_path)
options = webdriver.FirefoxOptions()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"

driver = webdriver.Firefox(service=ser, options=options)

try:
    # --- 3. VÀO TRANG ĐĂNG NHẬP FB ---
    url = 'https://www.facebook.com/login'
    print(f"1. Đang truy cập: {url}")
    driver.get(url)
    driver.maximize_window()
    
    wait = WebDriverWait(driver, 15)

    # --- 4. NHẬP EMAIL ---
    user_field = wait.until(
        EC.visibility_of_element_located((By.ID, "email"))
    )
    user_field.clear()
    user_field.send_keys(email)

    # --- 5. NHẬP PASSWORD ---
    pass_field = driver.find_element(By.ID, "pass")
    pass_field.clear()
    pass_field.send_keys(password_user)

    # --- 6. ENTER ĐỂ LOGIN ---
    pass_field.send_keys(Keys.ENTER)

    # --- 7. CHỜ LOAD ---
    time.sleep(5)
    print("\n-------------------------------")
    if "login" not in driver.current_url:
        print("ĐÃ ĐĂNG NHẬP THÀNH CÔNG!")
    else:
        print("ĐĂNG NHẬP THẤT BẠI!")
        driver.quit()
        exit()
    print("-------------------------------")

    # ---------------------------------------------
    # --- 8. ĐI ĐẾN TRANG CẦN CÀO ---
    # ---------------------------------------------
    fb_page = "https://www.facebook.com/tintuconlinevnn?locale=vi_VN"  
    print(f"4. Đang mở trang cần cào: {fb_page}")
    driver.get(fb_page)
    time.sleep(5)

    # --- 9. CUỘN TRANG ĐỂ HIỆN NHIỀU BÀI ---
    print("5. Đang cuộn trang để load nhiều bài viết...")

    for i in range(5):
        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(3)

    # --- 10. LẤY BÀI VIẾT ---
    print("6. Đang thu thập bài viết...")

    posts = wait.until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//div[@data-ad-preview='message']")
        )
    )

    print(f"Đã lấy được {len(posts)} bài viết!")

    # --- 11. LƯU KẾT QUẢ ---
    scraped = []
    for p in posts:
        scraped.append(p.text)

    print("\n======= DANH SÁCH BÀI VIẾT =======")
    for i, content in enumerate(scraped):
        print(f"\n--- Bài {i+1} ---")
        print(content)

    print("\nDONE!")

    time.sleep(10)

except Exception as e:
    print(f"\n[LỖI]: {e}")

finally:
    driver.quit()
