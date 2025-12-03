from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver import ActionChains
import time
import pandas as pd

# Đường dẫn đến file thực thi geckodriver
gecko_path = r"C:\Users\NHU\OneDrive\Documents\VSC\MNM\Selenium\geckodriver.exe"

# Khởi tởi đối tượng dịch vụ với đường geckodriver
ser = Service(gecko_path)

# Tạo tùy chọn
options = webdriver.firefox.options.Options();
options.binary_location =r"C:\Program Files\Mozilla Firefox\firefox.exe"
# Thiết lập firefox chỉ hiện thị giao diện
options.headless = False

# Khởi tạo driver
driver = webdriver.Firefox(options = options)


# --- TRUY CẬP TRANG SẢN PHẨM ---
url = 'https://gochek.vn/collections/all'
driver.get(url)
print(f"Đang truy cập: {url}")
time.sleep(3)

# --- KHỞI TẠO LIST DỮ LIỆU ---
stt_list = []
ten_san_pham = []
gia_ban = []
hinh_anh = []
danh_muc = []

page_count = 1
idx_global = 1

while True:
    print(f"\n--- TRANG {page_count} ---")
    
    # Cuộn trang để load ảnh
    body = driver.find_element(By.TAG_NAME, "body")
    for _ in range(10):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.3)
    time.sleep(1)
    
    # Lấy danh sách sản phẩm
    products = driver.find_elements(By.CSS_SELECTOR, "div.pro-loop")
    print(f"Tìm thấy {len(products)} sản phẩm trên trang này.")

    for prod in products:
        try:
            # Tên sản phẩm
            try:
                tsp = prod.find_element(By.CSS_SELECTOR, "h3.pro-name a").text
            except:
                tsp = ""
            # Giá sản phẩm
            try:
                gsp = prod.find_element(By.CSS_SELECTOR, "p.pro-price").text.replace("\n", " ").strip()
            except:
                gsp = "Liên hệ"
            # Ảnh sản phẩm
            try:
                img_tag = prod.find_element(By.CSS_SELECTOR, "div.product-img img")
                ha = img_tag.get_attribute("data-src") or img_tag.get_attribute("src") or ""
                if ha.startswith("//"):
                    ha = "https:" + ha
            except:
                ha = ""
            # Danh mục (mặc định)
            dm = "Gochek Việt Nam"

            if tsp:
                stt_list.append(idx_global)
                ten_san_pham.append(tsp)
                gia_ban.append(gsp)
                hinh_anh.append(ha)
                danh_muc.append(dm)

                # In ra console
                print(f"{idx_global}. {tsp} | {gsp} | {dm} | {ha}")

                idx_global += 1

        except Exception as e:
            print(f"Lỗi lấy sản phẩm: {e}")
            continue

    # Chuyển trang
    try:
        next_btn = driver.find_elements(By.XPATH, "//a[contains(@class, 'next')]")
        if next_btn and next_btn[0].is_displayed():
            print("-> Chuyển trang tiếp theo...")
            driver.execute_script("arguments[0].click();", next_btn[0])
            time.sleep(3)
            page_count += 1
        else:
            print("-> Hết trang. Hoàn tất cào dữ liệu!")
            break
    except Exception as e:
        print(f"Lỗi chuyển trang: {e}")
        break

# Lưu Excel (nếu muốn)
df = pd.DataFrame({
    "STT": stt_list,
    "Tên sản phẩm": ten_san_pham,
    "Danh mục": danh_muc,
    "Giá bán": gia_ban,
    "Hình ảnh": hinh_anh
})
df.to_excel('danh_sach_gochek_all.xlsx', index=False)
print(f"Đã lưu file Excel thành công: danh_sach_gochek_all.xlsx")

driver.quit()
