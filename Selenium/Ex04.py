from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time
import getpass

# Nhap thong tin nguoi dung
my_username = input('Please provide your username:')
my_password = getpass.getpass('Please provide your password:')

# Cấu hình để trình duyệt không tự tắt ngay lập tức nếu lỗi
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True) 

# Tắt thông báo "Chrome is being controlled by automated software" để đỡ bị Reddit soi
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=options)
driver.maximize_window()

print("--- BẮT ĐẦU ---")

# try:
# 1. MỞ TRANG ĐĂNG NHẬP
url = 'https://www.reddit.com/login/'
driver.get(url)
print("Đang tải trang login...")
# ------
print("----------------------------------------------------")
print("HÃY DÙNG TAY ĐỂ XÁC MINH ROBOT VÀ ĐĂNG NHẬP TRÊN TRÌNH DUYỆT")
print("Sau khi bạn đã đăng nhập thành công và vào trang chủ Reddit...")
input("HÃY BẤM PHÍM ENTER TẠI ĐÂY ĐỂ TIẾP TỤC CHẠY TOOL...") 
print("----------------------------------------------------")
# ---------------------

# Nhập Username
print("Đang tìm ô nhập User...")
username_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, "username")) 
)
# Thay chuỗi cứng bằng biến my_username
username_input.send_keys(my_username) 
print("Đã điền User.")

# Nhập Password
print("Đang tìm ô nhập Pass...")
password_input = driver.find_element(By.NAME, "password")
# Thay chuỗi cứng bằng biến my_password
password_input.send_keys(my_password) 
print("Đã điền Pass.")

password_input.send_keys(Keys.ENTER)
print("Đã nhấn Enter. Đang chờ chuyển trang...")
    
    # Chờ 10s để xem có vào được không
time.sleep(10)
   # --- PHẦN ĐĂNG BÀI ---
try:
    driver.switch_to.default_content()

    url2 = 'https://www.reddit.com/user/chloechooha/submit/?type=TEXT'
    driver.get(url2)
    print("4. Đang vào trang đăng bài...")

    # Chờ ô nhập Title
    title_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Title*']"))
    )
    title_box.send_keys("Test Post via Selenium")
    print("Đã nhập tiêu đề.")

    # Chờ ô nhập body
    body_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
    )
    body_box.click()
    body_box.send_keys("This is the content of the automated Selenium post.")
    print("Đã nhập nội dung.")

    # Chờ nút Post hoạt động
    post_button = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.='Post']"))
    )
    post_button.click()
    print("Đã bấm Post!")

except Exception as e:
    print("\n[LỖI]:", e)

finally:
    print("Đợi 120s để xem kết quả rồi thoát...")
    time.sleep(120)
    driver.quit()

