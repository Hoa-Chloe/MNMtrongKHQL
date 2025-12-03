import getpass
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- 1. NHẬP DATA ---
print("--- AUTO LOGIN HUTECH (FIXED ID) ---")
mssv = input("Nhập MSSV/Email: ")
password_user = getpass.getpass("Nhập Mật khẩu: ")

# --- 2. SETUP ---
gecko_path = r"C:\Users\NHU\OneDrive\Documents\VSC\MNM\Selenium\geckodriver.exe"
ser = Service(gecko_path)
options = webdriver.FirefoxOptions()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
driver = webdriver.Firefox(service=ser, options=options)

try:
    # --- 3. VÀO TRANG ĐĂNG NHẬP ---
    url = 'https://apps.lms.hutech.edu.vn/authn/login'
    print(f"1. Đang truy cập: {url}")
    driver.get(url)
    driver.maximize_window()
    
    wait = WebDriverWait(driver, 10)

    # --- 4. ĐIỀN MSSV ---
    print("2. Đang tìm ô MSSV theo ID 'emailOrUsername'...")
    
    user_field = wait.until(EC.visibility_of_element_located((By.ID, "emailOrUsername")))
   
    user_field.clear()
    user_field.send_keys(mssv)

    # --- 5. ĐIỀN PASSWORD ---
    print("3. Đang điền Mật khẩu...")

    pass_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    pass_field.clear()
    pass_field.send_keys(password_user)

    # --- 6. ENTER ĐỂ ĐĂNG NHẬP ---
    pass_field.send_keys(Keys.ENTER)

    # --- 7. KIỂM TRA ---
    time.sleep(5)
    print("\n-------------------------------")
    if "authn" not in driver.current_url:
        print("ĐÃ ĐĂNG NHẬP THÀNH CÔNG!")
        print(f"{driver.title}")
    else:
        print("Hãy kiểm tra lại Mật khẩu?")
    print("-------------------------------")

    time.sleep(10)

except Exception as e:
    print(f"\n[LỖI]: {e}")

finally:
    driver.quit()